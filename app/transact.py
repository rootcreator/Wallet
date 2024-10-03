import logging
from django.conf import settings
from django.db import transaction
from .models import USDAccount, Transaction
from .payment_services import StellarAnchorService

logger = logging.getLogger(__name__)


class InsufficientFundsError(Exception):
    pass


class UserNotVerifiedError(Exception):
    pass


class DepositService:
    def __init__(self):
        self.anchor_service = StellarAnchorService()

    def initiate_deposit(self, user, amount):
        fee_percentage = settings.DEPOSIT_FEE_PERCENTAGE
        fee = amount * (fee_percentage / 100)
        net_amount = amount - fee
        # Step 1: Initiate deposit with anchor
        anchor_response = self.anchor_service.initiate_deposit(user, net_amount)

        if 'error' in anchor_response:
            return anchor_response

        # Step 2: Create pending transaction record
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type='deposit',
            status='pending',
            external_transaction_id=anchor_response.get('id')
        )

        return {
            'status': 'initiated',
            'transaction_id': transaction.id,
            'more_info_url': anchor_response.get('url')  # URL where user completes the deposit
        }

    @staticmethod
    def process_deposit_callback(callback_data):
        # This method would be called when the anchor sends a callback
        transaction = Transaction.objects.get(external_transaction_id=callback_data['transaction_id'])

        if callback_data['status'] == 'completed':
            # Update user's USD account
            usd_account = USDAccount.objects.get(user=transaction.user)
            usd_account.deposit(transaction.amount)

            # Update transaction status
            transaction.status = 'completed'
            transaction.save()

        elif callback_data['status'] == 'failed':
            transaction.status = 'failed'
            transaction.save()

        return {'status': 'processed'}


class WithdrawalService:
    def __init__(self):
        self.anchor_service = StellarAnchorService()

    def initiate_withdrawal(self, user, amount):
        if not user.is_verified():
            return {'error': 'User not KYC verified'}
        fee_percentage = settings.DEPOSIT_FEE_PERCENTAGE
        fee = amount * (fee_percentage / 100)
        net_amount = amount - fee
        # Step 1: Check user's balance
        try:
            usd_account = USDAccount.objects.get(user=user)
            if usd_account.balance < amount:
                return {'error': 'Insufficient funds'}
        except USDAccount.DoesNotExist:
            return {'error': 'User USD account not found'}

        # Step 2: Initiate withdrawal with anchor
        anchor_response = self.anchor_service.initiate_withdrawal(user, net_amount)

        if 'error' in anchor_response:
            return anchor_response

        # Step 3: Create pending transaction record and deduct balance
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type='withdrawal',
            status='pending',
            external_transaction_id=anchor_response.get('id')
        )
        usd_account.withdraw(amount)

        return {
            'status': 'initiated',
            'transaction_id': transaction.id,
            'more_info_url': anchor_response.get('url')  # URL where user completes the withdrawal
        }

    @staticmethod
    def process_withdrawal_callback(callback_data):
        # This method would be called when the anchor sends a callback
        transaction = Transaction.objects.get(external_transaction_id=callback_data['transaction_id'])

        if callback_data['status'] == 'completed':
            # Update transaction status
            transaction.status = 'completed'
            transaction.save()
        elif callback_data['status'] == 'failed':
            # Refund the user's account and update transaction status
            usd_account = USDAccount.objects.get(user=transaction.user)
            usd_account.deposit(transaction.amount)  # Refund
            transaction.status = 'failed'
            transaction.save()

        if callback_data['status'] == 'failed':
            logger.error(f"Withdrawal failed for transaction {callback_data['transaction_id']}")
        return {'status': 'processed'}


class TransferService:
    def process_internal_transfer(self, sender, recipient, amount):
        if not sender.is_verified():
            return {'error': 'User not KYC verified'}
        fee_percentage = settings.DEPOSIT_FEE_PERCENTAGE
        fee = amount * (fee_percentage / 100)
        net_amount = amount - fee
        with transaction.atomic():
            if sender.usd_account.balance < amount:
                raise InsufficientFundsError("Insufficient funds")

            # Proceed with the transfer
            sender.usd_account.withdraw(amount)
            recipient.usd_account.deposit(net_amount)

            # Create transaction records
            self._create_transaction(sender, 'transfer', amount, f"Transfer to {recipient.username}")
            self._create_transaction(recipient, 'transfer', amount, f"Transfer from {sender.username}")

