from django.urls import path

from app.payment_methods import flutterwave_callback, initiate_flutterwave_deposit
from app.views import (
    WalletViewSet, TransactionViewSet, CreateLinkTokenView, PlaidWebhookView,
    MonoWebhookView, ExchangePublicTokenView, AuthenticateView, SetUserIdView,
    AccountView, TransactionsView, StatementView, CreditsView, DebitsView,
    IdentityView, BvnLookupView, LinkAccountView, UnlinkAccountView, CryptoWalletConnectCallbackView,
    CryptoWalletConnectInitiateView
)
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'wallets', WalletViewSet)
router.register(r'transactions', TransactionViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('create-link-token/', CreateLinkTokenView.as_view(), name='create_link_token'),
    path('plaid-webhook/', PlaidWebhookView.as_view(), name='plaid_webhook'),
    path('mono-webhook/', MonoWebhookView.as_view(), name='mono_webhook'),
    path('exchange-public-token/', ExchangePublicTokenView.as_view(), name='exchange_public_token'),
    path('authenticate/', AuthenticateView.as_view(), name='authenticate'),
    path('set-user-id/', SetUserIdView.as_view(), name='set_user_id'),
    path('account/', AccountView.as_view(), name='account'),
    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('statement/', StatementView.as_view(), name='statement'),
    path('credits/', CreditsView.as_view(), name='credits'),
    path('debits/', DebitsView.as_view(), name='debits'),
    path('identity/', IdentityView.as_view(), name='identity'),
    path('bvn-lookup/', BvnLookupView.as_view(), name='bvn_lookup'),
    path('link-account/', LinkAccountView.as_view(), name='link_account'),
    path('unlink-account/', UnlinkAccountView.as_view(), name='unlink_account'),
    path('walletconnect/initiate/', CryptoWalletConnectCallbackView.as_view(), name='walletconnect_initiate'),
    path('walletconnect/callback/', CryptoWalletConnectInitiateView.as_view(), name='walletconnect_callback'),

    path('callback/flutterwave/', flutterwave_callback, name='flutterwave_callback'),
    path('deposit/flutterwave/', initiate_flutterwave_deposit, name='flutterwave_deposit'),
]

# Include the router URLs
urlpatterns += router.urls
