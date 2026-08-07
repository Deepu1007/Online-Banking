from django import forms
from django.utils import timezone
from accounts.models import CustomerProfile
from transactions.models import Transaction
from decimal import Decimal

class TransferForm(forms.Form):
    receiver_acc_no = forms.CharField(max_length=16)
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))

    def __init__(self, *args, **kwargs):
        self.sender_profile = kwargs.pop('sender_profile', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not self.sender_profile:
            return cleaned_data

        amount = cleaned_data.get("amount")

        # Skip validation if no amount yet
        if amount is None:
            return cleaned_data

        profile = self.sender_profile

        # ----------------------------
        # Child Account Limits
        # ----------------------------
        if profile.is_child():

            # 1️⃣ Check Spending Limit (Overall Spend)
            if profile.spending_limit is not None and amount > profile.spending_limit:
                raise forms.ValidationError(
                    f"Transaction denied! Your spending limit is ₹{profile.spending_limit}."
                )

            # 2️⃣ Check Daily Limit
            if profile.daily_limit is not None:
                today = timezone.now().date()
                today_spent = Transaction.objects.filter(
                    sender=profile,
                    transaction_type='TRF',
                    timestamp__date=today
                ).aggregate(total=models.Sum('amount'))['total'] or Decimal("0.00")

                if today_spent + amount > profile.daily_limit:
                    remaining = profile.daily_limit - today_spent
                    raise forms.ValidationError(
                        f"Daily limit exceeded! Remaining transfer limit for today: ₹{remaining}."
                    )

        # ----------------------------
        # Check Balance
        # ----------------------------
        if profile.balance < amount:
            raise forms.ValidationError("Insufficient balance to complete this transfer.")

        return cleaned_data


class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)


class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
