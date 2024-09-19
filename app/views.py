from django.db import transaction, DatabaseError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wallet, Transaction, UserProfile
from .serializers import WalletSerializer, TransactionSerializer, DepositSerializer, WithdrawSerializer, \
    TransferSerializer, UserProfileSerializer
from .services.stellar_services import stellar_deposit, stellar_withdraw, stellar_transfer
from django.db import transaction as db_transaction
import logging

logger = logging.getLogger(__name__)


def csrf_token_view(request):
    return JsonResponse({'csrf_token': get_token(request)})


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            try:
                response = stellar_deposit(wallet, amount)
                wallet.update_balance()
                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='deposit',
                    status='completed',
                    stellar_transaction_hash=response['hash']
                )
                return Response({'status': 'success', 'new_balance': wallet.balance}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Deposit failed for user {request.user.id}: {str(e)}")
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            destination = serializer.validated_data['destination']
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            if wallet.balance < amount:
                return Response({'status': 'error', 'message': 'Insufficient funds'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                response = stellar_withdraw(wallet, amount, destination)
                wallet.update_balance()
                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='withdrawal',
                    status='completed',
                    stellar_transaction_hash=response['hash']
                )
                return Response({'status': 'success', 'new_balance': wallet.balance}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Withdrawal failed for user {request.user.id}: {str(e)}")
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            destination = serializer.validated_data['destination']
            wallet = Wallet.objects.select_for_update().get(user=request.user)

            if wallet.balance < amount:
                return Response({'status': 'error', 'message': 'Insufficient funds'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                response = stellar_transfer(wallet, amount, destination)
                wallet.update_balance()
                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='transfer',
                    status='completed',
                    stellar_transaction_hash=response['hash']
                )
                return Response({'status': 'success', 'new_balance': wallet.balance}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Transfer failed for user {request.user.id}: {str(e)}")
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        # Fetch transactions related to the authenticated user's wallet
        return Transaction.objects.filter(wallet__user=self.request.user).order_by('-timestamp')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Get the wallet linked to the authenticated user
        wallet = Wallet.objects.get(user=request.user)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            transaction_type = serializer.validated_data['transaction_type']

            # Additional logic for transaction_type (e.g., 'deposit', 'withdraw', 'transfer') can be added here
            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=transaction_type
            )

            # Update wallet balance here if needed
            wallet.update_balance()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def history(self, request):
        # Custom action to retrieve transaction history
        transactions = self.get_queryset()
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        profile = self.get_queryset().first()
        serializer = self.get_serializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    wallet = request.user.wallet
    wallet.update_balance()
    return Response({'balance': wallet.balance})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    transactions = Transaction.objects.filter(wallet=request.user.wallet).order_by('-timestamp')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)
