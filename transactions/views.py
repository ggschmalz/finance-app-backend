from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

from .models import Transaction, Profile, CreditCardInvoice, CreditCardTransaction
from .serializers import (
    TransactionSerializer,
    UserSerializer,
    CreditCardInvoiceSerializer,
    CreditCardTransactionSerializer
)
from .permissions import IsAdminUser, IsStandardOrAdmin

class UserListView(generics.ListAPIView):
    """
    Listagem de usuários para administradores.
    """
    queryset = User.objects.all().select_related('profile').order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Visualização, alteração de função (role) e remoção de usuários para administradores.
    """
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class TransactionViewSet(viewsets.ModelViewSet):
    """
    Gerencia o CRUD de transações com isolamento de usuário.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsStandardOrAdmin]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreditCardInvoiceViewSet(viewsets.ModelViewSet):
    """
    Gerencia o CRUD de faturas de cartão de crédito.
    """
    serializer_class = CreditCardInvoiceSerializer
    permission_classes = [IsStandardOrAdmin]

    def get_queryset(self):
        return CreditCardInvoice.objects.filter(user=self.request.user).order_by('-due_date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreditCardTransactionViewSet(viewsets.ModelViewSet):
    """
    Gerencia o lançamento, edição e exclusão de gastos de cartão vinculados a faturas.
    """
    serializer_class = CreditCardTransactionSerializer
    permission_classes = [IsStandardOrAdmin]

    def get_queryset(self):
        qs = CreditCardTransaction.objects.filter(invoice__user=self.request.user).order_by('-date')
        invoice_id = self.request.query_params.get('invoice')
        if invoice_id:
            qs = qs.filter(invoice_id=invoice_id)
        return qs

    def perform_create(self, serializer):
        invoice = serializer.validated_data.get('invoice')
        if invoice.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para lançar despesas nesta fatura.")
        serializer.save()


class DashboardView(APIView):
    """
    Endpoint que retorna dados agregados para o Dashboard,
    incorporando despesas convencionais e apropriação de despesas de cartão pelo mês de vencimento.
    """
    permission_classes = [IsStandardOrAdmin]

    def get(self, request):
        user = request.user
        
        # Filtro de ano (padrão: ano atual)
        year = request.query_params.get('year', timezone.now().year)
        try:
            year = int(year)
        except ValueError:
            year = timezone.now().year

        transactions = Transaction.objects.filter(user=user, date__year=year)
        card_transactions = CreditCardTransaction.objects.filter(
            invoice__user=user,
            invoice__due_date__year=year
        )

        # 1. Resumo Geral (Total Income, Total Expense, Balance)
        summary = transactions.values('type').annotate(total=Sum('amount'))
        
        total_income = next((item['total'] for item in summary if item['type'] == 'INCOME'), 0) or 0
        conventional_expense = next((item['total'] for item in summary if item['type'] == 'EXPENSE'), 0) or 0
        total_card_expense = card_transactions.aggregate(total=Sum('amount'))['total'] or 0

        total_expense = float(conventional_expense) + float(total_card_expense)
        balance = float(total_income) - float(total_expense)

        # 2. Evolução Mensal (Janeiro a Dezembro)
        monthly_evolution = []
        for month in range(1, 13):
            month_trans = transactions.filter(date__month=month)
            m_income = month_trans.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
            m_conv_expense = month_trans.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
            m_card_expense = card_transactions.filter(invoice__due_date__month=month).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_evolution.append({
                "month": month,
                "income": float(m_income),
                "expense": float(m_conv_expense) + float(m_card_expense)
            })

        # 3. Distribuição por Categoria (Gastos)
        category_distribution = transactions.filter(type='EXPENSE').values('category').annotate(
            amount=Sum('amount')
        ).order_by('-amount')

        categories_list = [
            {"category": item['category'], "amount": float(item['amount'])}
            for item in category_distribution
        ]

        if total_card_expense > 0:
            categories_list.append({
                "category": "Cartão de Crédito",
                "amount": float(total_card_expense)
            })

        return Response({
            "year": year,
            "summary": {
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "balance": float(balance)
            },
            "monthly_evolution": monthly_evolution,
            "category_distribution": categories_list
        }, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    """
    Endpoint que converte o token do Google em uma sessão JWT do Django.
    """
    authentication_classes = [] 
    permission_classes = [AllowAny] # Permite acesso sem token para login

    def post(self, request):
        token = request.data.get('credential')
        
        if not token:
            return Response({'error': 'Token não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validação oficial com os servidores do Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )

            # Extração de dados para o perfil e persistência
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            picture_url = idinfo.get('picture', '') # Captura a URL da foto de perfil

            # Busca ou cria o usuário no banco local (PostgreSQL)
            user, created = User.objects.get_or_create(
                username=email, 
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )

            # Geração dos tokens para o Interceptor do Frontend
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'picture': picture_url,
                    'role': user.profile.role
                }
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({'error': 'Token do Google inválido ou expirado'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': f'Erro interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)