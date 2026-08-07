from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile
import random

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"}),
        label="Confirm Password"
    )
    account_type = forms.ChoiceField(
        choices=CustomerProfile._meta.get_field("account_type").choices,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Account Type"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"}),
        }
        labels = {
            "username": "Username",
            "email": "Email",
        }
        help_texts = {
            "username": None,
            "email": None,
            "password": None,
        }

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm_password = cleaned.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # generate unique account number
            while True:
                acc = str(random.randint(10**7, 10**8 - 1))
                if not CustomerProfile.objects.filter(account_number=acc).exists():
                    break
            CustomerProfile.objects.create(
                user=user,
                account_number=acc,
                account_type=self.cleaned_data["account_type"],
                balance=0.00,
                is_approved=False
            )
        return user


# 🔹 New Form for Creating Child Accounts
class ChildAccountForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"}),
        label="Confirm Password"
    )
    spending_limit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter spending limit (₹)"}),
        label="Spending Limit (₹)"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Child username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Child email"}),
        }
        labels = {
            "username": "Child Username",
            "email": "Child Email",
        }
        help_texts = {
            "username": None,
            "email": None,
        }

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm_password = cleaned.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
