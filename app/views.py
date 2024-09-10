from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from app import serializers
from app.link_mono_client import (
    authenticate, set_user_id, get_account, get_transactions, get_statement,
    get_credits, get_debits, get_identity, bvn_lookup
)
from app.link_plaid_client import create_link_token, exchange_public_token
from app.link_walletconnect import wc
from app.models import LinkedAccount, Wallet, Transaction, CryptoWalletConnectSession, CryptoWalletConnectTransaction
from app.serializers import WalletSerializer, TransactionSerializer
from app.stellar_anchors import ANCHORS
from app.stellar_services import stellar_deposit, stellar_transfer
logger = logging.getLogger(__name__)


def get_anchor_for_user(user):
    country = user.profile.country
    if country in ['NG', 'ZA', 'GH']:
        return ANCHORS['AF']  # Flutterwave for Africa
    elif country == 'US':
        return ANCHORS['US']  # Circle for US
    elif country in ['FR', 'DE', 'ES']:  # Europe
        return ANCHORS['EU']  # Tempo for Europe
    elif country == 'UK':
        return ANCHORS['UK']  # Settle for UK
    elif country == 'CA':
        return ANCHORS['CA']  # VirgoCX for Canada
    return None


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='USD')


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'status': 'error', 'message': serializer.errors})

        wallet = Wallet.objects.get(user=request.user)
        amount = serializer.validated_data['amount']
        currency = serializer.validated_data['currency']

        try:
            response = initiate_deposit(request.user, amount, currency)
            wallet.update_balance_from_stellar()
            return Response({'status': 'success', 'response': response})
        except Exception as e:
            logger.error(f"Deposit failed for user {request.user.id}: {str(e)}")
            return Response({'status': 'error', 'message': str(e)})


def initiate_deposit(user, amount, currency):
    anchor = get_anchor_for_user(user)
    if not anchor:
        raise ValueError("No anchor found for user region")

    # Call the anchor's deposit method
    return anchor['deposit_method'](user, amount, currency)


@login_required
def deposit_view(request, amount):
    wallet = Wallet.objects.get(user=request.user)
    try:
        response = stellar_deposit(wallet, amount)
        wallet.update_balance_from_stellar()  # Sync the wallet balance after the transaction
        return HttpResponse(f"Deposit successful: {response}")
    except Exception as e:
        return HttpResponse(f"Deposit failed: {str(e)}")


class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet = get_object_or_404(Wallet, user=request.user)
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'USD')  # Default to 'USD' if not provided
        destination_public_key = request.data.get('destination_public_key')

        try:
            response = initiate_withdrawal(request.user, amount, currency)
            wallet.update_balance_from_stellar()  # Sync the wallet balance after the transaction
            return Response({'status': 'success', 'response': response})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)})


def initiate_withdrawal(user, amount, currency):
    anchor = get_anchor_for_user(user)  # This function selects the anchor based on user region
    if not anchor:
        raise ValueError("No anchor found for user's region")

    # Call the anchor's withdrawal method
    withdraw_method = anchor['withdraw_method']
    return withdraw_method(user, amount, currency)


@login_required
def withdrawal_view(request, amount):
    user = request.user
    try:
        response = initiate_withdrawal(user, amount, 'USD')  # Use user's preferred currency
        if response.get('status') == 'success':
            return HttpResponse(f"Withdrawal successful: {response}")
        else:
            return HttpResponse(f"Withdrawal failed: {response.get('message')}")
    except Exception as e:
        return HttpResponse(f"Withdrawal error: {str(e)}")


class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet = get_object_or_404(Wallet, user=request.user)
        amount = request.data.get('amount')
        destination_wallet_id = request.data.get('destination_wallet_id')
        destination_wallet = get_object_or_404(Wallet, id=destination_wallet_id)
        try:
            response = stellar_transfer(wallet, amount, destination_wallet)
            wallet.update_balance_from_stellar()  # Sync the wallet balance after the transaction
            destination_wallet.update_balance_from_stellar()  # Sync destination wallet balance
            return Response({'status': 'success', 'response': response})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)})


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class CreateLinkTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        link_token = create_link_token()
        return Response({'link_token': link_token})


class PlaidWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Handle Plaid webhooks here
        return Response({'status': 'success'})


class MonoWebhookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Handle Mono webhooks here
        return Response({'status': 'success'})


class ExchangePublicTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        public_token = request.data.get('public_token')
        access_token = exchange_public_token(public_token)
        return Response({'access_token': access_token})


class AuthenticateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mono_code = request.data.get('mono_code')
        data, status = authenticate(mono_code)
        return Response({'data': data, 'status': status})


class SetUserIdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('user_id')
        set_user_id(user_id)
        return Response({'status': 'success'})


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = get_account()
        return Response({'account': account})


class TransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.GET.get('start', '')
        end = request.GET.get('end', '')
        narration = request.GET.get('narration', '')
        types = request.GET.get('types', '')
        paginate = request.GET.get('paginate', 'false')
        transactions = get_transactions(start, end, narration, types, paginate)
        return Response({'transactions': transactions})


class StatementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.GET.get('month', '')
        output = request.GET.get('output', 'json')
        statement = get_statement(month, output)
        return Response({'statement': statement})


class CreditsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        credits = get_credits()
        return Response({'credits': credits})


class DebitsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        debits = get_debits()
        return Response({'debits': debits})


class IdentityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        identity = get_identity()
        return Response({'identity': identity})


class BvnLookupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        bvn = request.data.get('bvn')
        result = bvn_lookup(bvn)
        return Response({'result': result})


class LinkAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, pk=request.data.get('user_id'))
        provider = request.data.get('provider')
        access_token = request.data.get('access_token')
        account_id = request.data.get('account_id')

        linked_account, created = LinkedAccount.objects.get_or_create(
            user=user,
            provider=provider,
            account_id=account_id,
            defaults={'access_token': access_token}
        )

        if not created:
            linked_account.access_token = access_token
            linked_account.save()

        return Response({'status': 'success', 'linked_account': str(linked_account)})


class UnlinkAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, pk=request.data.get('user_id'))
        provider = request.data.get('provider')
        account_id = request.data.get('account_id')

        linked_account = get_object_or_404(LinkedAccount, user=user, provider=provider, account_id=account_id)
        linked_account.delete()

        return Response({'status': 'success', 'message': 'Account unlinked successfully'})


class CryptoWalletConnectInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Create a WalletConnect URI for the client to scan
        wc_uri = wc.create_session()
        return Response({'wc_uri': wc_uri})


class CryptoWalletConnectCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Handle WalletConnect session callbacks
        data = request.data
        wc.handle_session_request(data)
        return Response({'status': 'success'})


def create_walletconnect_session(user, session_id, uri):
    session = CryptoWalletConnectSession.objects.create(
        user=user,
        session_id=session_id,
        uri=uri
    )
    return session


def update_session_status(session_id, connected):
    try:
        session = CryptoWalletConnectSession.objects.get(session_id=session_id)
        session.connected = connected
        session.save()
    except CryptoWalletConnectSession.DoesNotExist:
        # Handle session not found
        pass


def record_transaction(user, transaction_id, amount, currency, date, status, description):
    transaction = CryptoWalletConnectTransaction.objects.create(
        user=user,
        transaction_id=transaction_id,
        amount=amount,
        currency=currency,
        date=date,
        status=status,
        description=description
    )
    return transaction
