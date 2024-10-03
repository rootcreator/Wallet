from django.contrib import admin
from .models import UserProfile, Transaction, USDAccount


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'kyc_status', 'region')
    search_fields = ('user__username',)
    list_filter = ('kyc_status', 'region')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'status', 'created_at')
    search_fields = ('user__username', 'transaction_type')
    list_filter = ('transaction_type', 'status', 'created_at')


@admin.register(USDAccount)
class USDAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at')
    search_fields = ('user__username',)
