import logging
from django.http import HttpResponse
from django.db import transaction  # Corrected import
from app.models import Transaction
from app.services.stellar_anchors import AnchorService

logger = logging.getLogger(__name__)


def initiate_fiat_withdrawal(user, amount, currency, bank_account_details):
    # Validate withdrawal details (could be more complex depending on bank validation needs)
    if not bank_account_details:
        raise ValueError("Bank account details are required")

    with transaction.atomic():
        # Check user balance
        if user.wallet.balance < amount:
            raise ValueError("Insufficient funds")

        try:
            # Initiate withdrawal with payment processor or anchor
            withdrawal_info = AnchorService.initiate_withdrawal(
                amount=amount,
                currency=currency,
                bank_account=bank_account_details
            )

            # Create a pending transaction in your system
            New_transaction = Transaction.objects.create(
                user=user,
                amount=amount,
                currency=currency,
                type='fiat_withdrawal',
                status='pending',
                external_id=withdrawal_info['id']
            )

            # Deduct the amount from user's balance
            user.wallet.balance -= amount
            user.wallet.save()

            return withdrawal_info

        except Exception as e:
            # Log the error for troubleshooting
            logger.error(f"Error initiating withdrawal: {e}")
            raise ValueError("Withdrawal failed, please try again later")


# Webhook handler for payment processor callbacks
def handle_fiat_withdrawal_callback(request):
    data = request.data

    try:
        # Fetch the corresponding transaction
        New_transaction = Transaction.objects.get(external_id=data['id'])
    except Transaction.DoesNotExist:
        logger.error(f"Transaction with external ID {data['id']} not found.")
        return HttpResponse(status=404)

    # Use the transaction context manager here
    with transaction.atomic():
        if data['status'] == 'completed':
            transaction.status = 'completed'
        elif data['status'] == 'failed':
            transaction.status = 'failed'
            # Refund the user
            transaction.user.wallet.balance += transaction.amount
            transaction.user.wallet.save()

        transaction.save()

    return HttpResponse(status=200)
