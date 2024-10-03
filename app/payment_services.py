from abc import ABC, abstractmethod

import requests
from django.conf import settings
from stellar_sdk import Server, Keypair, Network


class PaymentService(ABC):
    @abstractmethod
    def initiate_deposit(self, user, amount):
        pass

    @abstractmethod
    def initiate_withdrawal(self, user, amount):
        pass

    @abstractmethod
    def check_transaction_status(self, transaction_id):
        pass


class StellarAnchorService(PaymentService):
    def __init__(self):
        self.network = Network.PUBLIC_NETWORK_PASSPHRASE
        self.server = Server("https://horizon.stellar.org")
        self.platform_keypair = Keypair.from_secret(settings.STELLAR_PLATFORM_SECRET)
        self.anchor_url = settings.ANCHOR_URL
        self.asset_code = "USDC"
        self.asset_issuer = settings.USDC_ISSUER_PUBLIC_KEY

    def initiate_deposit(self, user, amount):
        fee_percentage = settings.DEPOSIT_FEE_PERCENTAGE
        fee = amount * (fee_percentage / 100)
        net_amount = amount - fee

        jwt_token = self.get_auth_token(user)
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        data = {
            "asset_code": self.asset_code,
            "account": self.platform_keypair.public_key,
            "net_amount": str(net_amount)
        }
        response = requests.post(f"{self.anchor_url}/transactions/deposit/interactive", headers=headers, json=data)
        return response.json() if response.status_code == 200 else {"error": "Failed to initiate deposit"}

    def initiate_withdrawal(self, user, amount):
        fee_percentage = settings.DEPOSIT_FEE_PERCENTAGE
        fee = amount * (fee_percentage / 100)
        net_amount = amount - fee

        jwt_token = self.get_auth_token(user)
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        data = {
            "asset_code": self.asset_code,
            "account": self.platform_keypair.public_key,
            "net_amount": str(net_amount)
        }
        response = requests.post(f"{self.anchor_url}/transactions/withdraw/interactive", headers=headers, json=data)
        return response.json() if response.status_code == 200 else {"error": "Failed to initiate withdrawal"}

    def check_transaction_status(self, transaction_id):
        jwt_token = self.get_auth_token(None)  # You might need to adjust this depending on your auth strategy
        headers = {"Authorization": f"Bearer {jwt_token}"}
        response = requests.get(f"{self.anchor_url}/transaction/{transaction_id}", headers=headers)
        return response.json() if response.status_code == 200 else {"error": "Failed to check transaction status"}

    def get_auth_token(self, user):
        # Implement your authentication logic here
        # This should return a JWT token that the anchor will use to authenticate the request
        pass


class FlutterwaveAnchorBridge(PaymentService):
    def __init__(self):
        self.flutterwave_service = FlutterwaveService()
        self.stellar_service = StellarAnchorService()

    def initiate_deposit(self, user, amount):
        # First, initiate the deposit with Flutterwave
        flutterwave_response = self.flutterwave_service.initiate_deposit(user, amount)
        if 'error' in flutterwave_response:
            return flutterwave_response

        # If Flutterwave deposit is successful, initiate the deposit with the Stellar anchor
        stellar_response = self.stellar_service.initiate_deposit(user, amount)
        if 'error' in stellar_response:
            # You might want to cancel the Flutterwave transaction here
            return stellar_response

        return {
            'flutterwave_response': flutterwave_response,
            'stellar_response': stellar_response
        }

    def initiate_withdrawal(self, user, amount):
        # First, initiate the withdrawal with the Stellar anchor
        stellar_response = self.stellar_service.initiate_withdrawal(user, amount)
        if 'error' in stellar_response:
            return stellar_response

        # If Stellar withdrawal is successful, initiate the withdrawal with Flutterwave
        flutterwave_response = self.flutterwave_service.initiate_withdrawal(user, amount)
        if 'error' in flutterwave_response:
            # You might want to cancel the Stellar transaction here
            return flutterwave_response

        return {
            'stellar_response': stellar_response,
            'flutterwave_response': flutterwave_response
        }

    def check_transaction_status(self, transaction_id):
        # Check status with both Flutterwave and Stellar
        flutterwave_status = self.flutterwave_service.check_transaction_status(transaction_id)
        stellar_status = self.stellar_service.check_transaction_status(transaction_id)

        return {
            'flutterwave_status': flutterwave_status,
            'stellar_status': stellar_status
        }


class TempoAnchorBridge(PaymentService):
    def __init__(self):
        self.tempo_service = TempoService()
        self.stellar_service = StellarAnchorService()

    def initiate_deposit(self, user, amount):
        # First, initiate the deposit with Tempo
        tempo_response = self.tempo_service.initiate_deposit(user, amount)
        if 'error' in tempo_response:
            return tempo_response

        # If Tempo deposit is successful, initiate the deposit with the Stellar anchor
        stellar_response = self.stellar_service.initiate_deposit(user, amount)
        if 'error' in stellar_response:
            # Optionally cancel the Tempo transaction here
            return stellar_response

        return {
            'tempo_response': tempo_response,
            'stellar_response': stellar_response
        }

    def initiate_withdrawal(self, user, amount):
        # First, initiate the withdrawal with the Stellar anchor
        stellar_response = self.stellar_service.initiate_withdrawal(user, amount)
        if 'error' in stellar_response:
            return stellar_response

        # If Stellar withdrawal is successful, initiate the withdrawal with Tempo
        tempo_response = self.tempo_service.initiate_withdrawal(user, amount)
        if 'error' in tempo_response:
            # Optionally cancel the Stellar transaction here
            return tempo_response

        return {
            'stellar_response': stellar_response,
            'tempo_response': tempo_response
        }

    def check_transaction_status(self, transaction_id):
        # Check status with both Tempo and Stellar
        tempo_status = self.tempo_service.check_transaction_status(transaction_id)
        stellar_status = self.stellar_service.check_transaction_status(transaction_id)

        return {
            'tempo_status': tempo_status,
            'stellar_status': stellar_status
        }


class CircleAnchorBridge(PaymentService):
    def __init__(self):
        self.circle_service = CircleService()
        self.stellar_service = StellarAnchorService()

    def initiate_deposit(self, user, amount):
        # First, initiate the deposit with Circle
        circle_response = self.circle_service.initiate_deposit(user, amount)
        if 'error' in circle_response:
            return circle_response

        # If Circle deposit is successful, initiate the deposit with the Stellar anchor
        stellar_response = self.stellar_service.initiate_deposit(user, amount)
        if 'error' in stellar_response:
            # Optionally cancel the Circle transaction here
            return stellar_response

        return {
            'circle_response': circle_response,
            'stellar_response': stellar_response
        }

    def initiate_withdrawal(self, user, amount):
        # First, initiate the withdrawal with the Stellar anchor
        stellar_response = self.stellar_service.initiate_withdrawal(user, amount)
        if 'error' in stellar_response:
            return stellar_response

        # If Stellar withdrawal is successful, initiate the withdrawal with Circle
        circle_response = self.circle_service.initiate_withdrawal(user, amount)
        if 'error' in circle_response:
            # Optionally cancel the Stellar transaction here
            return circle_response

        return {
            'stellar_response': stellar_response,
            'circle_response': circle_response
        }

    def check_transaction_status(self, transaction_id):
        # Check status with both Circle and Stellar
        circle_status = self.circle_service.check_transaction_status(transaction_id)
        stellar_status = self.stellar_service.check_transaction_status(transaction_id)

        return {
            'circle_status': circle_status,
            'stellar_status': stellar_status
        }


class SettleNetworkAnchorBridge(PaymentService):
    def __init__(self):
        self.SettleNetwork = SettleNetworkService()
        self.stellar_service = StellarAnchorService()

    def initiate_deposit(self, user, amount):
        # First, initiate the deposit with Tempo
        SettleNetwork_response = self.SettleNetwork_service.initiate_deposit(user, amount)
        if 'error' in SettleNetwork_response:
            return SettleNetwork_response

        # If Tempo deposit is successful, initiate the deposit with the Stellar anchor
        stellar_response = self.stellar_service.initiate_deposit(user, amount)
        if 'error' in stellar_response:
            # Optionally cancel the Tempo transaction here
            return stellar_response

        return {
            'SettleNetwork_response': SettleNetwork_response,
            'stellar_response': stellar_response
        }

    def initiate_withdrawal(self, user, amount):
        # First, initiate the withdrawal with the Stellar anchor
        stellar_response = self.stellar_service.initiate_withdrawal(user, amount)
        if 'error' in stellar_response:
            return stellar_response

        SettleNetwork_response = self.SettleNetwork_service.initiate_withdrawal(user, amount)
        if 'error' in SettleNetwork_response:
            # Optionally cancel the Stellar transaction here
            return SettleNetwork_response

        return {
            'stellar_response': stellar_response,
            'SettleNetwork_response': SettleNetwork_response
        }

    def check_transaction_status(self, transaction_id):
        # Check status with both Tempo and Stellar
        SettleNetwork_status = self.SettleNetwork_service.check_transaction_status(transaction_id)
        stellar_status = self.stellar_service.check_transaction_status(transaction_id)

        return {
            'tempo_status': SettleNetwork_status,
            'stellar_status': stellar_status
        }


class AlchemyPayAnchorBridge(PaymentService):
    def __init__(self):
        self.AlchemyPay_service = AlchemyPayService()
        self.stellar_service = StellarAnchorService()

    def initiate_deposit(self, user, amount):
        # First, initiate the deposit with Circle
        AlchemyPay_response = self.AlchemyPay_service.initiate_deposit(user, amount)
        if 'error' in AlchemyPay_response:
            return AlchemyPay_response

        # If Circle deposit is successful, initiate the deposit with the Stellar anchor
        stellar_response = self.stellar_service.initiate_deposit(user, amount)
        if 'error' in stellar_response:
            # Optionally cancel the Circle transaction here
            return stellar_response

        return {
            'AlchemyPay_response': AlchemyPay_response,
            'stellar_response': stellar_response
        }

    def initiate_withdrawal(self, user, amount):
        # First, initiate the withdrawal with the Stellar anchor
        stellar_response = self.stellar_service.initiate_withdrawal(user, amount)
        if 'error' in stellar_response:
            return stellar_response

        # If Stellar withdrawal is successful, initiate the withdrawal with Circle
        AlchemyPay_response = self.circle_service.initiate_withdrawal(user, amount)
        if 'error' in AlchemyPay_response:
            # Optionally cancel the Stellar transaction here
            return AlchemyPay_response

        return {
            'stellar_response': stellar_response,
            'circle_response': AlchemyPay_response
        }

    def check_transaction_status(self, transaction_id):
        # Check status with both Circle and Stellar
        AlchemyPay_status = self.AlchemyPay_service.check_transaction_status(transaction_id)
        stellar_status = self.stellar_service.check_transaction_status(transaction_id)

        return {
            'AlchemyPay_status': AlchemyPay_status,
            'stellar_status': stellar_status
        }


class MoneyGramAnchorBridge(PaymentService):
    def __init__(self):
        self.MoneyGram_service = MoneyGramService()
        self.stellar_service = StellarAnchorService()

    def initiate_deposit(self, user, amount):
        # First, initiate the deposit with Monwygram
        MoneyGram_response = self.MoneyGram_service.initiate_deposit(user, amount)
        if 'error' in MoneyGram_response:
            return MoneyGram_response

        # If Moneygram deposit is successful, initiate the deposit with the Stellar anchor
        stellar_response = self.stellar_service.initiate_deposit(user, amount)
        if 'error' in stellar_response:
            # Optionally cancel the Circle transaction here
            return stellar_response

        return {
            'circle_response': MoneyGram_response,
            'stellar_response': stellar_response
        }

    def initiate_withdrawal(self, user, amount):
        # First, initiate the withdrawal with the Stellar anchor
        stellar_response = self.stellar_service.initiate_withdrawal(user, amount)
        if 'error' in stellar_response:
            return stellar_response

        # If Stellar withdrawal is successful, initiate the withdrawal with Moneygram
        MoneyGram_response = self.MoneyGram_service.initiate_withdrawal(user, amount)
        if 'error' in MoneyGram_response:
            # Optionally cancel the Stellar transaction here
            return MoneyGram_response

        return {
            'stellar_response': stellar_response,
            'MoneyGram_response': MoneyGram_response
        }

    def check_transaction_status(self, transaction_id):
        # Check status with both Moneygram and Stellar
        MoneyGram_status = self.MoneyGram_service.check_transaction_status(transaction_id)
        stellar_status = self.stellar_service.check_transaction_status(transaction_id)

        return {
            'circle_status': MoneyGram_status,
            'stellar_status': stellar_status
        }


class FlutterwaveService(PaymentService):
    BASE_URL = "https://api.flutterwave.com/v3"
    SECRET_KEY = "YOUR_FLUTTERWAVE_SECRET_KEY"

    def initiate_deposit(self, user, amount):
        url = f"{self.BASE_URL}/payments"
        headers = {
            "Authorization": f"Bearer {self.SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "tx_ref": "transaction_ref_here",
            "amount": amount,
            "currency": "USD",
            "redirect_url": "your_redirect_url_here",
            "payment_type": "card",
            "customer": {
                "email": user.email,
                "name": user.username
            }
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def initiate_withdrawal(self, user, amount):
        # Implement the Flutterwave withdrawal logic here
        pass

    def check_transaction_status(self, transaction_id):
        url = f"{self.BASE_URL}/transactions/{transaction_id}/verify"
        headers = {"Authorization": f"Bearer {self.SECRET_KEY}"}
        response = requests.get(url, headers=headers)
        return response.json()


class TempoService(PaymentService):
    BASE_URL = "https://tempo-api.com"
    API_KEY = "YOUR_TEMPO_API_KEY"

    def initiate_deposit(self, user, amount):
        # Tempo deposit logic using Tempo API
        pass

    def initiate_withdrawal(self, user, amount):
        # Tempo withdrawal logic using Tempo API
        pass

    def check_transaction_status(self, transaction_id):
        # Tempo transaction status logic using Tempo API
        pass


class CircleService(PaymentService):
    BASE_URL = "https://api-sandbox.circle.com/v1"
    SECRET_KEY = "YOUR_CIRCLE_API_KEY"

    def initiate_deposit(self, user, amount):
        # Circle deposit logic using Circle API
        pass

    def initiate_withdrawal(self, user, amount):
        # Circle withdrawal logic using Circle API
        pass

    def check_transaction_status(self, transaction_id):
        # Circle transaction status logic using Circle API
        pass


class SettleNetworkService(PaymentService):
    BASE_URL = "https://api-sandbox.circle.com/v1"
    SECRET_KEY = "YOUR_CIRCLE_API_KEY"

    def initiate_deposit(self, user, amount):
        # Circle deposit logic using Circle API
        pass

    def initiate_withdrawal(self, user, amount):
        # Circle withdrawal logic using Circle API
        pass

    def check_transaction_status(self, transaction_id):
        # Circle transaction status logic using Circle API
        pass


class AlchemyPayService(PaymentService):
    BASE_URL = "https://api-sandbox.circle.com/v1"
    SECRET_KEY = "YOUR_CIRCLE_API_KEY"

    def initiate_deposit(self, user, amount):
        # Circle deposit logic using Circle API
        pass

    def initiate_withdrawal(self, user, amount):
        # Circle withdrawal logic using Circle API
        pass

    def check_transaction_status(self, transaction_id):
        # Circle transaction status logic using Circle API
        pass


class MoneyGramService(PaymentService):
    BASE_URL = "https://api-sandbox.circle.com/v1"
    SECRET_KEY = "YOUR_CIRCLE_API_KEY"

    def initiate_deposit(self, user, amount):
        # Circle deposit logic using Circle API
        pass

    def initiate_withdrawal(self, user, amount):
        # Circle withdrawal logic using Circle API
        pass

    def check_transaction_status(self, transaction_id):
        # Circle transaction status logic using Circle API
        pass
