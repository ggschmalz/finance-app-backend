from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from transactions.models import Profile, Transaction, CreditCardInvoice, CreditCardTransaction

class ProfileSignalTest(TestCase):
    def test_user_creation_creates_profile(self):
        user = User.objects.create_user(username='john', email='john@example.com', password='password123')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'UNASSIGNED')


class TransactionViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.user1.profile.role = 'STANDARD'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password123')
        self.user2.profile.role = 'STANDARD'
        self.user2.profile.save()

        self.t1 = Transaction.objects.create(
            user=self.user1,
            description='Salário',
            amount=5000.00,
            type='INCOME',
            category='Salário',
            date=date(2026, 8, 1)
        )

        self.t2 = Transaction.objects.create(
            user=self.user2,
            description='Mercado',
            amount=300.00,
            type='EXPENSE',
            category='Alimentação',
            date=date(2026, 8, 2)
        )

    def test_user_isolation(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['description'], 'Salário')

    def test_create_transaction_assigns_authenticated_user(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'description': 'Aluguel',
            'amount': 1500.00,
            'type': 'EXPENSE',
            'category': 'Moradia',
            'date': '2026-08-05'
        }
        response = self.client.post('/api/transactions/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.filter(user=self.user1).count(), 2)


class UserManagementAndPermissionsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(username='admin', email='admin@example.com')
        self.admin.profile.role = 'ADMIN'
        self.admin.profile.save()

        self.standard = User.objects.create_user(username='std', email='std@example.com')
        self.standard.profile.role = 'STANDARD'
        self.standard.profile.save()

        self.unassigned = User.objects.create_user(username='pending', email='pending@example.com')
        # Role defaults to UNASSIGNED

    def test_unassigned_user_blocked(self):
        self.client.force_authenticate(user=self.unassigned)
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_user_cannot_access_user_list(self):
        self.client.force_authenticate(user=self.standard)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_and_update_user_role(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update role of unassigned user
        patch_res = self.client.patch(f'/api/users/{self.unassigned.id}/', {'role': 'STANDARD'}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        
        self.unassigned.profile.refresh_from_db()
        self.assertEqual(self.unassigned.profile.role, 'STANDARD')

    def test_admin_can_delete_user(self):
        self.client.force_authenticate(user=self.admin)
        del_res = self.client.delete(f'/api/users/{self.unassigned.id}/')
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.unassigned.id).exists())


class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='dash', email='dash@example.com')
        self.user.profile.role = 'STANDARD'
        self.user.profile.save()

        Transaction.objects.create(
            user=self.user,
            description='Job Freelance',
            amount=2000.00,
            type='INCOME',
            category='Freelance',
            date=date(2026, 8, 10)
        )

    def test_dashboard_metrics(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/dashboard/?year=2026')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertEqual(response.data['summary']['total_income'], 2000.00)
        self.assertIn('monthly_evolution', response.data)
        self.assertIn('category_distribution', response.data)


class CreditCardViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='crd_user1', email='crd1@example.com', password='password123')
        self.user1.profile.role = 'STANDARD'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username='crd_user2', email='crd2@example.com', password='password123')
        self.user2.profile.role = 'STANDARD'
        self.user2.profile.save()

    def test_create_and_list_invoices(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.post('/api/credit-cards/invoices/', {
            'description': 'Fatura Outubro 2026',
            'due_date': '2026-10-10'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['description'], 'Fatura Outubro 2026')
        self.assertEqual(res.data['total_amount'], 0.0)

        # Listagem
        list_res = self.client.get('/api/credit-cards/invoices/')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        results = list_res.data.get('results', list_res.data)
        self.assertEqual(len(results), 1)

    def test_toggle_invoice_payment_status(self):
        self.client.force_authenticate(user=self.user1)
        inv = CreditCardInvoice.objects.create(
            user=self.user1,
            description='Fatura Novembro 2026',
            due_date=date(2026, 11, 10),
            is_paid=False
        )
        patch_res = self.client.patch(f'/api/credit-cards/invoices/{inv.id}/', {'is_paid': True}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        inv.refresh_from_db()
        self.assertTrue(inv.is_paid)

    def test_add_and_edit_card_expense(self):
        self.client.force_authenticate(user=self.user1)
        inv = CreditCardInvoice.objects.create(
            user=self.user1,
            description='Fatura Dezembro 2026',
            due_date=date(2026, 12, 10)
        )
        # Lançar despesa
        res = self.client.post('/api/credit-cards/transactions/', {
            'invoice': inv.id,
            'description': 'Supermercado Central',
            'amount': 250.00,
            'category': 'Alimentação',
            'date': '2026-11-15'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(inv.total_amount, 250.00)

        tx_id = res.data['id']
        # Editar despesa
        patch_res = self.client.patch(f'/api/credit-cards/transactions/{tx_id}/', {
            'amount': 300.00
        }, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(inv.total_amount, 300.00)

        # Excluir despesa
        del_res = self.client.delete(f'/api/credit-cards/transactions/{tx_id}/')
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(inv.total_amount, 0.0)

    def test_dashboard_card_appropriation_due_date_regime(self):
        self.client.force_authenticate(user=self.user1)
        # Fatura com vencimento em Fevereiro (mês 2)
        inv = CreditCardInvoice.objects.create(
            user=self.user1,
            description='Fatura Fevereiro 2026',
            due_date=date(2026, 2, 10)
        )
        # Despesa efetuada em Janeiro (mês 1)
        CreditCardTransaction.objects.create(
            invoice=inv,
            description='Notebook',
            amount=1500.00,
            category='Eletrônicos',
            date=date(2026, 1, 15)
        )
        res = self.client.get('/api/dashboard/?year=2026')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        # Mês 1 não deve ter a despesa do cartão
        m1 = next(item for item in res.data['monthly_evolution'] if item['month'] == 1)
        self.assertEqual(m1['expense'], 0.0)
        
        # Mês 2 (mês de vencimento da fatura) deve ter a despesa de 1500
        m2 = next(item for item in res.data['monthly_evolution'] if item['month'] == 2)
        self.assertEqual(m2['expense'], 1500.0)

        # Categoria 'Cartão de Crédito' deve estar na distribuição
        cat = next((c for c in res.data['category_distribution'] if c['category'] == 'Cartão de Crédito'), None)
        self.assertIsNotNone(cat)
        self.assertEqual(cat['amount'], 1500.0)
