from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    # Traz todas as transações, ordenadas da mais recente para a mais antiga
    queryset = Transaction.objects.all().order_by('-date', '-created_at')
    serializer_class = TransactionSerializer