from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Entrada'),
        ('EXPENSE', 'Saída'),
    ]

    # Agora o usuário é obrigatório para novas transações
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} ({self.user.username})"