from django.db import models
from accounts.models import CustomerProfile

TRANSACTION_TYPES = (
    ('DEP', 'Deposit'),
    ('WDR', 'Withdraw'),
    ('TRF', 'Transfer'),
)

class Transaction(models.Model):
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    sender = models.ForeignKey(CustomerProfile, related_name='sent_transactions', null=True, blank=True, on_delete=models.SET_NULL)
    receiver = models.ForeignKey(CustomerProfile, related_name='received_transactions', null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_transaction_type_display()} ₹{self.amount} at {self.timestamp}"
