from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from stellar_sdk import Keypair, Server
from decimal import Decimal
from django.utils.functional import cached_property
from django.conf import settings
from django.db.models import F


def validate_positive(value):
    if value <= 0:
        raise ValidationError('Amount must be positive.')


def clean(self):
    if self.transaction_type == 'withdrawal' and self.amount > self.wallet.balance:
        raise ValidationError("Insufficient balance for this withdrawal.")


SECRET_KEY = Fernet.generate_key()  # Secure this in settings/environment variables
cipher_suite = Fernet(SECRET_KEY)


def encrypt_token(token):
    return cipher_suite.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token):
    return cipher_suite.decrypt(encrypted_token.encode()).decode()


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[validate_positive])
    currency = models.CharField(max_length=3, default='USD')
    stellar_public_key = models.CharField(max_length=56, blank=True, null=True)  # Stellar public key
    stellar_private_key = models.CharField(max_length=56, blank=True, null=True)  # Stellar private key (encrypted)

    def save(self, *args, **kwargs):
        # Generate Stellar keypair on wallet creation if not already present
        if not self.stellar_public_key or not self.stellar_private_key:
            keypair = Keypair.random()
            self.stellar_public_key = keypair.public_key
            self.stellar_private_key = encrypt_token(keypair.secret)  # Encrypt the private key
        super().save(*args, **kwargs)

    def update_balance_from_stellar(self):
        try:
            stellar_balance = get_stellar_balance(self.stellar_public_key)
            self.balance = stellar_balance
            self.save()
        except Exception as e:
            # Log the error and handle it appropriately
            print(f"Error updating balance from Stellar: {e}")

    @cached_property
    def decrypted_private_key(self):
        return decrypt_token(self.stellar_private_key)

    def update_wallet_balance(self, amount):
        Wallet.objects.filter(pk=self.pk).update(balance=F('balance') + amount)


# Helper function to get Stellar balance
def get_stellar_balance(public_key):
    server = Server("https://horizon-testnet.stellar.org")
    account = server.accounts().account_id(public_key).call()

    # Retrieve the USDT balance (can be XLM or any other asset code you're using)
    for balance in account['balances']:
        if balance['asset_code'] == 'USDT':
            return Decimal(balance['balance'])
    return Decimal(0)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)  # Optional field for additional notes


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    uri = models.URLField(max_length=500)
    connected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id} for user {self.user.username}"


class CryptoWalletConnectTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.CharField(max_length=10)
    date = models.DateTimeField()
    status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} for user {self.user.username}"


class CryptoWalletConnectConnection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=255)
    connection_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Connection to wallet {self.wallet_address} for user {self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE)  # Associate with Wallet
    mono_user_id = models.CharField(max_length=255, null=True, blank=True)  # For Mono user ID
    plaid_user_id = models.CharField(max_length=255, null=True, blank=True)  # For Plaid user ID
    country = models.TextField(max_length=56, blank=True, null=True)

    def __str__(self):
        return self.user.username

    # Optionally, you can add methods to interact with the Wallet if needed
    def get_wallet_balance(self):
        return self.wallet.balance

    def update_wallet_balance(self, amount):
        self.wallet.update_balance(amount)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Your Website Title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@yourdomain.com",
        # to:
        [reset_password_token.user.email]
    )
