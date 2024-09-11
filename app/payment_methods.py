import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from wallet.settings import FLUTTERWAVE_API_KEY, CIRCLE_API_KEY, SETTLE_API_KEY, TEMPO_API_KEY, VIRGOCX_API_KEY


def initiate_flutterwave_deposit(user, amount, currency):
    url = "https://api.flutterwave.com/v3/payments"
    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "tx_ref": f"deposit_{user.id}_{amount}",
        "amount": amount,
        "currency": currency,
        "redirect_url": "https://yourdomain.com/callback/flutterwave",
        "payment_type": "mobilemoney",  # or 'card', 'banktransfer'
        "customer": {
            "email": user.email,
            "name": user.get_full_name()
        },
        "meta": {
            "wallet_address": user.wallet.stellar_public_key,
        },
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_circle_deposit(user, amount, currency):
    from app.stellar_anchors import ANCHORS
    url = ANCHORS['US']['deposit_url']
    headers = {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "idempotencyKey": f"{user.id}_{amount}",
        "amount": {
            "amount": amount,
            "currency": currency
        },
        "source": {
            "type": "wallet",
            "id": user.wallet.circle_wallet_id
        },
        "destination": {
            "type": "stellar",
            "stellarAccount": user.wallet.stellar_public_key
        },
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_tempo_deposit(user, amount, currency):
    from app.stellar_anchors import ANCHORS
    url = ANCHORS['EU']['deposit_url']
    headers = {
        "Authorization": f"Bearer {TEMPO_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "customer_id": user.wallet.tempo_customer_id,
        "amount": amount,
        "currency": currency,
        "bank_account": user.bank_account_details,
        "stellar_account": user.wallet.stellar_public_key,
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_settle_deposit(user, amount, currency):
    url = 'https://api.settle.network/deposit'
    headers = {
        "Authorization": f"Bearer {SETTLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "wallet_id": user.wallet.settle_wallet_id,  # UK wallet ID
        "amount": amount,
        "currency": currency,
        "stellar_account": user.wallet.stellar_public_key,
        "narration": "Deposit to Stellar wallet"
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_virgocx_deposit(user, amount, currency):
    url = 'https://api.virgocx.ca/v1/deposits'
    headers = {
        "Authorization": f"Bearer {VIRGOCX_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "amount": amount,
        "currency": currency,
        "deposit_method": "bank_account",
        "bank_account": user.bank_account_details['account_number'],
        "beneficiary_name": user.get_full_name()
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


@csrf_exempt
def flutterwave_callback(request):
    if request.method == "POST":
        data = request.json()
        if data["status"] == "successful":
            # Handle the successful deposit, update user’s Stellar wallet
            wallet_address = data["meta"]["wallet_address"]
            amount = data["amount"]
            # Update the user’s Stellar wallet balance here
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "invalid request"}, status=400)


def initiate_flutterwave_withdrawal(user, amount, currency):
    url = 'https://api.flutterwave.com/v3/transfers'
    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "account_bank": user.bank_account_details['bank_code'],  # User's bank code
        "account_number": user.bank_account_details['account_number'],  # User's bank account
        "amount": amount,
        "currency": currency,
        "reference": f"withdraw_{user.id}_{amount}",
        "narration": "Withdrawal to bank account",
        "beneficiary_name": user.get_full_name()
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_circle_withdrawal(user, amount, currency):
    url = 'https://api.circle.com/v1/payouts'
    headers = {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "idempotencyKey": f"{user.id}_{amount}",
        "amount": {
            "amount": amount,
            "currency": currency
        },
        "source": {
            "type": "wallet",
            "id": user.wallet.circle_wallet_id
        },
        "destination": {
            "type": "bankAccount",
            "id": user.bank_account_details['bank_id']  # Circle needs bank ID
        },
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_tempo_withdrawal(user, amount, currency):
    url = 'https://api.tempo.eu.com/withdraw'
    headers = {
        "Authorization": f"Bearer {TEMPO_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "customer_id": user.wallet.tempo_customer_id,
        "amount": amount,
        "currency": currency,
        "bank_account": user.bank_account_details,  # Bank account info
        "stellar_account": user.wallet.stellar_public_key
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_settle_withdrawal(user, amount, currency):
    url = 'https://api.settle.network/withdraw'
    headers = {
        "Authorization": f"Bearer {SETTLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "wallet_id": user.wallet.settle_wallet_id,  # UK wallet ID
        "amount": amount,
        "currency": currency,
        "bank_account": user.bank_account_details['account_number'],  # User's bank details
        "narration": "Withdrawal to bank"
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_virgocx_withdrawal(user, amount, currency):
    url = 'https://api.virgocx.ca/v1/withdrawals'
    headers = {
        "Authorization": f"Bearer {VIRGOCX_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "amount": amount,
        "currency": currency,
        "withdrawal_method": "bank_account",
        "bank_account": user.bank_account_details['account_number'],
        "beneficiary_name": user.get_full_name()
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()