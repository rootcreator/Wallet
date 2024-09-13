from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

router = DefaultRouter()
router.register(r'wallets', WalletViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('create-link-token/', CreateLinkTokenView.as_view(), name='create-link-token'),
    path('plaid-webhook/', PlaidWebhookView.as_view(), name='plaid-webhook'),
    path('mono-webhook/', MonoWebhookView.as_view(), name='mono-webhook'),
    path('exchange-public-token/', ExchangePublicTokenView.as_view(), name='exchange-public-token'),
    path('authenticate/', AuthenticateView.as_view(), name='authenticate'),
    path('set-user-id/', SetUserIdView.as_view(), name='set-user-id'),
    path('account/', AccountView.as_view(), name='account'),
    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('statement/', StatementView.as_view(), name='statement'),
    path('credits/', CreditsView.as_view(), name='credits'),
    path('debits/', DebitsView.as_view(), name='debits'),
    path('identity/', IdentityView.as_view(), name='identity'),
    path('bvn-lookup/', BvnLookupView.as_view(), name='bvn-lookup'),
    path('link-account/', LinkAccountView.as_view(), name='link-account'),
    path('unlink-account/', UnlinkAccountView.as_view(), name='unlink-account'),
    path('deposit/<int:amount>/', deposit_view, name='deposit-view'),
    path('withdrawal/<int:amount>/', withdrawal_view, name='withdrawal-view'),

    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    path('bank_withdrawal/initiate/', initiate_fiat_withdrawal_view, name='initiate_fiat_withdrawal'),
    path('bank_withdrawal/callback/', handle_fiat_withdrawal_callback_view, name='fiat_withdrawal_callback'),
]

# Uncomment these if you decide to implement the WalletConnect functionality
# path('crypto-wallet-connect/initiate/', CryptoWalletConnectInitiateView.as_view(), name='crypto-wallet-connect-initiate'),
# path('crypto-wallet-connect/callback/', CryptoWalletConnectCallbackView.as_view(), name='crypto-wallet-connect-callback'),