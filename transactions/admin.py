from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'sender', 'receiver', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('sender__account_number', 'receiver__account_number', 'description')
