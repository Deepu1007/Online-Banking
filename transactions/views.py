from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from accounts.models import CustomerProfile
from .models import Transaction
from .forms import TransferForm, DepositForm, WithdrawForm


# Helper to get customer profile safely
def get_customer_profile(user):
    try:
        return user.customerprofile
    except CustomerProfile.DoesNotExist:
        return None


@login_required
def transfer_money(request):
    profile = get_customer_profile(request.user)
    if not profile:
        messages.error(request, "Your account is not set up. Contact admin.")
        return redirect('dashboard')
    
    if not profile.is_approved or profile.is_closed:
        messages.error(request, "Account not active.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = TransferForm(request.POST, sender_profile=profile)
        if form.is_valid():
            receiver_acc = form.cleaned_data['receiver_acc_no']
            amount = form.cleaned_data['amount']

            # Check if receiver exists
            try:
                receiver = CustomerProfile.objects.get(account_number=receiver_acc)
            except CustomerProfile.DoesNotExist:
                messages.error(request, "Receiver account not found.")
                return redirect('transfer')

            if receiver.is_closed or not receiver.is_approved:
                messages.error(request, "Receiver account is not active.")
                return redirect('transfer')

            # ========== ATOMIC UPDATE ==========
            with db_transaction.atomic():
                profile.balance -= amount
                receiver.balance += amount
                profile.save()
                receiver.save()
                Transaction.objects.create(
                    transaction_type='TRF',
                    sender=profile,
                    receiver=receiver,
                    amount=amount,
                    description=f"Transfer to {receiver.account_number}"
                )
            messages.success(request, "Transfer successful.")
            return redirect('history')
    else:
        form = TransferForm(sender_profile=profile)

    return render(request, 'transactions/transfer.html', {'form': form})


@login_required
def deposit(request):
    profile = get_customer_profile(request.user)
    if not profile:
        messages.error(request, "Your account is not set up. Contact admin.")
        return redirect('dashboard')

    if not profile.is_approved or profile.is_closed:
        messages.error(request, "Account not active.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            with db_transaction.atomic():
                profile.balance += amount
                profile.save()
                Transaction.objects.create(
                    transaction_type='DEP',
                    receiver=profile,
                    amount=amount,
                    description="Deposit"
                )
            messages.success(request, f"Deposited ₹{amount}")
            return redirect('history')
    else:
        form = DepositForm()

    return render(request, 'transactions/deposit.html', {'form': form})


@login_required
def withdraw(request):
    profile = get_customer_profile(request.user)
    if not profile:
        messages.error(request, "Your account is not set up. Contact admin.")
        return redirect('dashboard')

    if not profile.is_approved or profile.is_closed:
        messages.error(request, "Account not active.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if profile.balance < amount:
                messages.error(request, "Insufficient balance.")
                return redirect('withdraw')

            with db_transaction.atomic():
                profile.balance -= amount
                profile.save()
                Transaction.objects.create(
                    transaction_type='WDR',
                    sender=profile,
                    amount=amount,
                    description="Withdraw"
                )
            messages.success(request, f"Withdrew ₹{amount}")
            return redirect('history')
    else:
        form = WithdrawForm()

    return render(request, 'transactions/withdraw.html', {'form': form})


@login_required
def history(request):
    profile = get_customer_profile(request.user)
    if not profile:
        messages.error(request, "Your account is not set up. Contact admin.")
        return redirect('dashboard')

    txs = Transaction.objects.filter(sender=profile) | Transaction.objects.filter(receiver=profile)
    txs = txs.order_by('-timestamp')
    return render(request, 'transactions/history.html', {'transactions': txs})
