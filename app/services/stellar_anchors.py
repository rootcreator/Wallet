from app.services.payment_methods import (
    initiate_flutterwave_deposit, initiate_flutterwave_withdrawal,
    initiate_circle_deposit, initiate_circle_withdrawal,
    initiate_tempo_deposit, initiate_tempo_withdrawal,
    initiate_settle_deposit, initiate_settle_withdrawal,
    initiate_virgocx_deposit, initiate_virgocx_withdrawal
)
import requests
from wallet.settings import (
    FLUTTERWAVE_API_KEY,
    CIRCLE_API_KEY,
    SETTLE_API_KEY,
    TEMPO_API_KEY,
    VIRGOCX_API_KEY,
)

ANCHORS = {
    'AF': {
        'name': 'Flutterwave',
        'currency': 'NGN',
        'deposit_url': 'https://api.flutterwave.com/v3/payments',
        'deposit_method': initiate_flutterwave_deposit,
        'withdraw_method': initiate_flutterwave_withdrawal,
    },
    'US': {
        'name': 'Circle',
        'currency': 'USD',
        'deposit_url': 'https://api.circle.com/v1/payments',
        'deposit_method': initiate_circle_deposit,
        'withdraw_method': initiate_circle_withdrawal,
    },
    'EU': {
        'name': 'Tempo',
        'currency': 'EUR',
        'deposit_url': 'https://api.tempo.eu.com/deposit',
        'deposit_method': initiate_tempo_deposit,
        'withdraw_method': initiate_tempo_withdrawal,
    },
    'UK': {
        'name': 'Settle Network',
        'currency': 'GBP',
        'deposit_url': 'https://api.settle.network/deposit',
        'deposit_method': initiate_settle_deposit,
        'withdraw_method': initiate_settle_withdrawal,
    },
    'CA': {
        'name': 'VirgoCX',
        'currency': 'CAD',
        'deposit_url': 'https://api.virgocx.ca/v1/payments',
        'deposit_method': initiate_virgocx_deposit,
        'withdraw_method': initiate_virgocx_withdrawal,
    },
}


class AnchorService:
    def __init__(self, user, amount, currency):
        self.user = user
        self.amount = amount
        self.currency = currency
        self.headers = {"Content-Type": "application/json"}

    def initiate_deposit(self, anchor_code):
        anchor = ANCHORS.get(anchor_code)
        if not anchor:
            raise ValueError("Anchor code not found.")
        method = anchor['deposit_method']
        return method(self.user, self.amount, self.currency)

    def initiate_withdrawal(self, anchor_code):
        anchor = ANCHORS.get(anchor_code)
        if not anchor:
            raise ValueError("Anchor code not found.")
        method = anchor['withdraw_method']
        return method(self.user, self.amount, self.currency)


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
        "payment_type": "mobilemoney",
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


def initiate_flutterwave_withdrawal(user, amount, currency):
    url = 'https://api.flutterwave.com/v3/transfers'
    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "account_bank": user.bank_account_details['bank_code'],
        "account_number": user.bank_account_details['account_number'],
        "amount": amount,
        "currency": currency,
        "reference": f"withdraw_{user.id}_{amount}",
        "narration": "Withdrawal to bank account",
        "beneficiary_name": user.get_full_name()
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_circle_deposit(user, amount, currency):
    url = 'https://api.circle.com/v1/payouts'
    headers = {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "idempotencyKey": f"{user.id}_{amount}",
        "amount": {"amount": amount, "currency": currency},
        "source": {"type": "wallet", "id": user.wallet.circle_wallet_id},
        "destination": {"type": "stellar", "stellarAccount": user.wallet.stellar_public_key},
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
        "amount": {"amount": amount, "currency": currency},
        "source": {"type": "wallet", "id": user.wallet.circle_wallet_id},
        "destination": {"type": "bankAccount", "id": user.bank_account_details['bank_id']},
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


def initiate_tempo_deposit(user, amount, currency):
    url = 'https://api.tempo.eu.com/deposit'
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
        "wallet_id": user.wallet.settle_wallet_id,
        "amount": amount,
        "currency": currency,
        "stellar_account": user.wallet.stellar_public_key,
        "narration": "Deposit to Stellar wallet"
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
        "wallet_id": user.wallet.settle_wallet_id,
        "amount": amount,
        "currency": currency,
        "bank_account": user.bank_account_details['account_number'],
        "narration": "Withdrawal to bank"
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
