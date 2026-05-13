from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('STANDARD', 'Padrão'),
        ('UNASSIGNED', 'Aguardando Atribuição'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='UNASSIGNED')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

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