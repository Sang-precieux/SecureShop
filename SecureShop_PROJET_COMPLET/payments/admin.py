from django.contrib import admin
from .models import Transaction, SecurityEvent

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'amount', 'status', 'created_at')
    readonly_fields = ('reference', 'user', 'amount', 'nonce', 'hmac_signature', 'status', 'payment_method', 'cart_snapshot', 'idempotency_key', 'created_at')

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('test_type', 'user', 'accepted', 'created_at')
