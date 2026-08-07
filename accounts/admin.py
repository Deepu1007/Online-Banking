from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'account_type', 'balance', 'is_approved', 'is_closed', 'created_at')
    search_fields = ('user__username', 'account_number')
    list_filter = ('account_type', 'is_approved', 'is_closed')
