from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

ACCOUNT_TYPES = (
    ('SAV', 'Savings'),
    ('CUR', 'Current'),
)

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=16, unique=True)
    account_type = models.CharField(max_length=3, choices=ACCOUNT_TYPES, default='SAV')
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)   # Admin must approve account
    is_closed = models.BooleanField(default=False)     # Closed account flag

    # =========================
    # 👇 Family / Group Account Feature
    # =========================
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )  # If null → Parent account, else child account

    spending_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum balance this child account can spend"
    )

    daily_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum daily spend limit for child account"
    )

    is_locked = models.BooleanField(default=False)  # Parent can lock/unlock child account

    # =========================
    # 👇 Account Termination Fields
    # =========================
    is_terminated = models.BooleanField(default=False)
    termination_reason = models.TextField(null=True, blank=True)

    # =========================
    # 👇 Helper Methods
    # =========================
    def is_child(self):
        return self.parent is not None

    def is_parent(self):
        return self.parent is None

    def __str__(self):
        return f"{self.user.username} | {self.account_number}"
