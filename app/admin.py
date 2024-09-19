from django.contrib import admin
from .models import Wallet, Transaction, UserProfile


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'stellar_public_key')
    search_fields = ('user__username', 'stellar_public_key')
    readonly_fields = ('stellar_private_key',)  # Sensitive field; prevent editing


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'timestamp', 'status', 'stellar_transaction_hash')
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = ('wallet__user__username', 'stellar_transaction_hash')
    readonly_fields = ('stellar_transaction_hash',)  # Prevent editing of hash


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'country')
    search_fields = ('user__username',)


# Register models with the admin site
admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
