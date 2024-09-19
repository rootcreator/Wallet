from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WalletViewSet, DepositView, WithdrawView, TransferView,
    TransactionViewSet, UserProfileViewSet, get_balance, transaction_history, csrf_token_view
)

# Initialize the router for viewsets
router = DefaultRouter()

# Register viewsets
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'profile', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('api/', include(router.urls)),  # Include all viewsets with the router

    # Function-based views for specific functionality
    path('csrf-token/', csrf_token_view, name='csrf_token'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('get-balance/', get_balance, name='get_balance'),
    path('transaction-history/', transaction_history, name='transaction_history'),
]
