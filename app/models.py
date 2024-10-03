import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Change this to avoid clashes
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Change this to avoid clashes
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Add any additional fields you need

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    kyc_status = models.CharField(
        max_length=50,
        choices=[("pending", "Pending"), ("rejected", "Rejected"), ("approved", "Approved")],
        default="pending"
    )
    region = models.CharField(
        max_length=50,
        choices=[("AF", "Africa"), ("EU", "Europe"), ("US", "United States"), ("LATAM", "Latin America")]
    )

    def __str__(self):
        return f"{self.user.username} - {self.kyc_status}"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    external_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.status}"


class USDAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="usd_account")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Store in USD
    created_at = models.DateTimeField(auto_now_add=True)

    def deposit(self, amount):
        """Credit account with deposit"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        """Debit account with withdrawal"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
        self.save()

    def get_transaction_history(self):
        """Retrieve all transactions for the user's account."""
        return Transaction.objects.filter(user=self.user).order_by('-created_at')

    def __str__(self):
        return f"{self.user.username} - Balance: ${self.balance}"
