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
from django.conf import settings
from django.core.validators import MinValueValidator


def validate_positive(value):
    if value <= 0:
        raise ValidationError('Amount must be positive.')


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=19, decimal_places=7, default=0.00, validators=[MinValueValidator(0)])
    stellar_public_key = models.CharField(max_length=56, unique=True)
    stellar_private_key = models.CharField(max_length=88)  # Increased length for encrypted key

    def save(self, *args, **kwargs):
        if not self.stellar_public_key or not self.stellar_private_key:
            keypair = Keypair.random()
            self.stellar_public_key = keypair.public_key
            self.stellar_private_key = self.encrypt_key(keypair.secret)
        super().save(*args, **kwargs)

    @staticmethod
    def encrypt_key(key):
        f = Fernet(settings.FERNET_KEY)
        return f.encrypt(key.encode()).decode()

    @staticmethod
    def decrypt_key(encrypted_key):
        f = Fernet(settings.FERNET_KEY)
        return f.decrypt(encrypted_key.encode()).decode()

    def get_stellar_balance(self):
        server = Server("https://horizon.stellar.org")  # Use mainnet
        account = server.accounts().account_id(self.stellar_public_key).call()
        for balance in account['balances']:
            if balance['asset_type'] == 'credit_alphanum4' and balance['asset_code'] == 'USDC':
                return Decimal(balance['balance'])
        return Decimal(0)

    def update_balance(self):
        stellar_balance = self.get_stellar_balance()
        if stellar_balance != self.balance:
            self.balance = stellar_balance
            self.save(update_fields=['balance'])


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=19, decimal_places=7, validators=[validate_positive])
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    stellar_transaction_hash = models.CharField(max_length=64, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.transaction_type == 'withdrawal' and self.amount > self.wallet.balance:
            raise ValidationError("Insufficient balance for this withdrawal.")
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE)  # Associate with Wallet
    country = models.CharField(max_length=56, blank=True, null=True)
    dob = models.DateField(max_length=500, blank=True, null=True)

    KYC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    kyc_status = models.CharField(max_length=10, choices=KYC_STATUS_CHOICES, default='pending')
    kyc_document = models.FileField(upload_to='kyc_documents/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_wallet_balance(self):
        return self.wallet.balance

    def update_wallet_balance(self, amount):
        self.wallet.update_balance(amount)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)

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
