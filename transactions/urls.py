from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

# O DefaultRouter cria as rotas automaticamente para o nosso ViewSet
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]