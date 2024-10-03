import requests
from django.conf import settings
import logging
from rest_framework.templatetags.rest_framework import data

logger = logging.getLogger(__name__)

...
logger.info(f"Creating payment: {data}")


class CircleClient:
    def __init__(self):
        self.api_key = settings.CIRCLE_API_KEY
        self.api_url = settings.CIRCLE_API_URL

    def create_payment(self, amount, currency, recipient):
        url = f"{self.api_url}payments"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'amount': amount,
            'currency': currency,
            'recipient': recipient
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            logger.error(f"Failed to create payment: {response.json()}")
            raise Exception(f"Error creating payment: {response.json()}")

        return response.json()

    def get_payment_status(self, payment_id):
        url = f"{self.api_url}payments/{payment_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def issue_usdc(self, amount, currency):
        """
        Issue USDC to a user.

        Args:
            amount (float): The amount of USDC to issue.
            currency (str): The currency of the payment.

        Returns:
            dict: The response from the Circle API.
        """
        url = f"{self.api_url}payments/issue"  # Hypothetical endpoint
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'amount': amount,
            'currency': currency,
            'type': 'usdc'  # Assuming this is how to specify USDC
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Error issuing USDC: {response.json()}")

        return response.json()

    def redeem_usdc(self, amount):
        """
        Redeem USDC for another currency.

        Args:
            amount (float): The amount of USDC to redeem.

        Returns:
            dict: The response from the Circle API.
        """
        url = f"{self.api_url}payments/redeem"  # Hypothetical endpoint
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'amount': amount,
            'currency': 'USD'  # Assuming you want to redeem to USD
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Error redeeming USDC: {response.json()}")

        return response.json()

