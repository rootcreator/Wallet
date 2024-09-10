from django.contrib import admin
from .models import Wallet, Transaction, LinkedAccount, UserProfile


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'currency')
    search_fields = ('user__username',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'timestamp')
    search_fields = ('wallet__user__username', 'transaction_type')


@admin.register(LinkedAccount)
class LinkedAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'account_id', 'linked_at')
    search_fields = ('user__username', 'provider', 'account_id')

    def get_access_token(self, obj):
        return obj.get_access_token()

    get_access_token.short_description = 'Access Token'

    def get_refresh_token(self, obj):
        return obj.get_refresh_token()

    get_refresh_token.short_description = 'Refresh Token'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet', 'mono_user_id', 'plaid_user_id')
    search_fields = ('user__username', 'mono_user_id', 'plaid_user_id')
