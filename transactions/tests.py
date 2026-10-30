from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from transactions.models import Profile, Transaction

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
