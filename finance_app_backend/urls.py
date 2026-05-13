from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# A importação das views DEVE estar aqui
from transactions.views import TransactionViewSet, GoogleLoginView, DashboardView, UserListView 

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Rota do Dashboard
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),

    # Rota de Listagem de Usuários (Admin)
    path('api/users/', UserListView.as_view(), name='user_list'),

    # Rota de Autenticação do Google
    path('api/auth/google/', GoogleLoginView.as_view(), name='google_login'),
]