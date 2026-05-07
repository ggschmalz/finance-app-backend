from django.db import models

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Entrada'),
        ('EXPENSE', 'Saída'),
    ]

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True, null=True) # <- NOVO CAMPO
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='EXPENSE')
    created_at = models.DateTimeField(auto_now_add=True) # Campo extra útil para auditoria

    def __str__(self):
        return f"{self.description} - R$ {self.amount}"