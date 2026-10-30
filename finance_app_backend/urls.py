from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from transactions.views import (
    TransactionViewSet,
    GoogleLoginView,
    DashboardView,
    UserListView,
    UserDetailView
)

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Rota do Dashboard
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),

    # Rotas de Gestão de Usuários (Admin)
    path('api/users/', UserListView.as_view(), name='user_list'),
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),

    # Rotas de Autenticação JWT e Google
    path('api/auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]