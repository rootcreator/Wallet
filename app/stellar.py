import requests
from urllib.parse import urljoin
from stellar_sdk import TransactionBuilder, Network, Keypair, Server
from django.conf import settings
from rest_framework.authtoken.models import Token
from app.models import Transaction


class StellarAnchorService:
    def __init__(self, anchor_url):
        self.network = Network.PUBLIC_NETWORK_PASSPHRASE
        self.server = Server("https://horizon-testnet.stellar.org")
        self.platform_keypair = Keypair.from_secret(settings.STELLAR_PLATFORM_SECRET)
        self.anchor_url = anchor_url  # Initialize anchor URL
        self.asset_code = "USDC"
        self.asset_issuer = settings.USDC_ISSUER_PUBLIC_KEY

    def initiate_deposit(self, user, amount):
        headers = {
            "Authorization": f"Bearer {Token}",
            "Content-Type": "application/json"
        }
        data = {
            "asset_code": self.asset_code,
            "account": self.platform_keypair.public_key,
            "amount": str(amount)
        }
        response = requests.post(urljoin(self.anchor_url, "/transactions/deposit/interactive"), headers=headers,
                                 json=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to initiate deposit", "details": response.text}

    def initiate_withdrawal(self, user, amount):
        headers = {
            "Authorization": f"Bearer {Token}",
            "Content-Type": "application/json"
        }
        data = {
            "asset_code": self.asset_code,
            "account": self.platform_keypair.public_key,
            "amount": str(amount)
        }
        response = requests.post(urljoin(self.anchor_url, "/transactions/withdraw/interactive"), headers=headers,
                                 json=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to initiate withdrawal", "details": response.text}

    def check_transaction_status(self, transaction_id):
        response = requests.get(urljoin(self.anchor_url, f"/transactions/{transaction_id}"))
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to check transaction status", "details": response.text}

    @staticmethod
    def process_anchor_callback(callback_data):
        transaction_id = callback_data.get('transaction_id')
        status = callback_data.get('status')

        transaction = Transaction.objects.filter(external_transaction_id=transaction_id).first()

        if transaction:
            if status == 'completed':
                transaction.status = 'completed'
                transaction.save()
                # Update user's USD account or perform other actions as necessary
            elif status == 'failed':
                transaction.status = 'failed'
                transaction.save()
                # Handle any necessary refund logic
        else:
            return {"error": "Transaction not found"}

    def send_payment(self, destination, amount):
        try:
            transaction = (
                TransactionBuilder(
                    source_account=self.server.load_account(self.platform_keypair.public_key),
                    network_passphrase=self.network,
                    base_fee=100
                )
                .append_payment_op(
                    destination=destination,
                    asset_code=self.asset_code,
                    asset_issuer=self.asset_issuer,
                    amount=str(amount)
                )
                .set_timeout(30)
                .build()
            )

            transaction.sign(self.platform_keypair)
            response = self.server.submit_transaction(transaction)
            return response
        except Exception as e:
            return {'error': str(e)}
