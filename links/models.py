from cryptography.fernet import Fernet
from django.contrib.auth.models import User
from django.db import models

SECRET_KEY = Fernet.generate_key()  # Secure this in settings/environment variables
cipher_suite = Fernet(SECRET_KEY)


def encrypt_token(token):
    return cipher_suite.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token):
    return cipher_suite.decrypt(encrypted_token.encode()).decode()


class LinkedAccount(models.Model):
    PROVIDER_CHOICES = [
        ('mono', 'Mono'),
        ('plaid', 'Plaid'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=255)  # Unique identifier for the account from Mono/Plaid
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)  # Either 'mono' or 'plaid'
    access_token = models.TextField()  # Store the access token securely
    refresh_token = models.TextField(null=True, blank=True)  # Optional, for token refresh
    linked_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.access_token:
            self.access_token = encrypt_token(self.access_token)
        if self.refresh_token:
            self.refresh_token = encrypt_token(self.refresh_token)
        super().save(*args, **kwargs)

    def get_access_token(self):
        return decrypt_token(self.access_token)

    def get_refresh_token(self):
        return decrypt_token(self.refresh_token)

    def __str__(self):
        return f'{self.user.username} - {self.provider} - {self.account_id}'


class CryptoWalletConnectSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    uri = models.URLField(max_length=500)
    connected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id} for user {self.user.username}"


class CryptoWalletConnectTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.CharField(max_length=10)
    date = models.DateTimeField()
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} for user {self.user.username}"


class CryptoWalletConnectConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=255)
    connection_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Connection to wallet {self.wallet_address} for user {self.user.username}"


