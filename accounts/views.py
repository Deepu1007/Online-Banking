
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import UserRegisterForm, ChildAccountForm
from .models import CustomerProfile
from transactions.models import Transaction
import random


# -------------------
# Home page
# -------------------
def home(request):
    return render(request, "home.html")


# -------------------
# Register new user
# -------------------
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Wait for admin approval.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# -------------------
# Login view
# -------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


# -------------------
# Logout view
# -------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# -------------------
# Dashboard
# -------------------
@login_required
def dashboard(request):
    try:
        profile = request.user.customerprofile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "No customer profile found. Please contact support.")
        return redirect("home")

    if not profile.is_approved:
        return render(request, 'accounts/pending.html', {'profile': profile})
    if profile.is_closed:
        return render(request, 'accounts/closed.html', {'profile': profile})

    # recent transactions
    txs = Transaction.objects.filter(sender=profile) | Transaction.objects.filter(receiver=profile)
    txs = txs.order_by('-timestamp')[:10]

    # fetch child accounts if parent
    child_accounts = CustomerProfile.objects.filter(parent=profile) if profile.is_parent else None

    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'transactions': txs,
        'child_accounts': child_accounts
    })


# -------------------
# Create Child Account (Parent Only)
# -------------------
@login_required
def create_child_account(request):
    try:
        parent_profile = request.user.customerprofile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "No customer profile found.")
        return redirect("dashboard")

    if not parent_profile.is_parent:
        messages.error(request, "Only parents can create child accounts.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ChildAccountForm(request.POST)
        if form.is_valid():
            # Create child user
            child_user = form.save(commit=False)
            child_user.set_password(form.cleaned_data["password"])
            child_user.save()

            # Generate unique account number
            while True:
                acc = str(random.randint(10**7, 10**8 - 1))
                if not CustomerProfile.objects.filter(account_number=acc).exists():
                    break

            # Create child profile linked to parent
            CustomerProfile.objects.create(
                user=child_user,
                account_number=acc,
                account_type="CHILD",   # ✅ FIXED uppercase
                balance=0.00,
                is_approved=True,  # auto-approved by parent
                parent=parent_profile,
                spending_limit=form.cleaned_data.get("spending_limit", 0),
            )

            messages.success(request, f"Child account '{child_user.username}' created successfully!")
            return redirect("dashboard")
    else:
        form = ChildAccountForm()

    return render(request, "accounts/create_child.html", {"form": form})


# -------------------
# Child Account Transactions (Parent Only)
# -------------------
@login_required
def child_transactions(request, pk):
    parent_profile = request.user.customerprofile
    child_profile = get_object_or_404(CustomerProfile, pk=pk, parent=parent_profile)

    txs = Transaction.objects.filter(sender=child_profile) | Transaction.objects.filter(receiver=child_profile)
    txs = txs.order_by('-timestamp')
    return render(request, 'accounts/child_transactions.html', {
        'child': child_profile,
        'transactions': txs
    })


# -------------------
# Lock/Unlock Child Account (Parent Only)
# -------------------
@login_required
def toggle_child_account(request, pk):
    parent_profile = request.user.customerprofile
    child_profile = get_object_or_404(CustomerProfile, pk=pk, parent=parent_profile)

    child_profile.is_closed = not child_profile.is_closed
    child_profile.save()
    status = "locked" if child_profile.is_closed else "unlocked"
    messages.success(request, f"Child account {status} successfully.")
    return redirect('dashboard')


# -------------------
# Staff Section
# -------------------
def staff_check(user):
    return user.is_staff

@user_passes_test(staff_check)
def customer_list(request):
    customers = CustomerProfile.objects.select_related('user').all()
    return render(request, 'accounts/staff_customer_list.html', {'customers': customers})

@user_passes_test(staff_check)
def approve_customer(request, pk):
    cp = get_object_or_404(CustomerProfile, pk=pk)
    cp.is_approved = True
    cp.save()
    messages.success(request, f"Approved {cp.user.username}")
    return redirect('staff_customers')

@user_passes_test(staff_check)
def reject_customer(request, pk):
    cp = get_object_or_404(CustomerProfile, pk=pk)
    user = cp.user
    cp.delete()
    user.delete()
    messages.success(request, "Customer rejected and removed.")
    return redirect('staff_customers')

@user_passes_test(staff_check)
def open_close_account(request, pk):
    cp = get_object_or_404(CustomerProfile, pk=pk)
    cp.is_closed = not cp.is_closed
    cp.save()
    status = "closed" if cp.is_closed else "opened"
    messages.success(request, f"Account {status} for {cp.user.username}")
    return redirect('staff_customers')


# -------------------
# Terminate Child Account (Parent Only)
# -------------------
@login_required
def terminate_child(request, child_id):
    parent_profile = request.user.customerprofile
    # ✅ FIXED: ensure child belongs to this parent & account_type is correct
    child = get_object_or_404(CustomerProfile, id=child_id, account_type="CHILD", parent=parent_profile)

    if request.method == "POST":
        reason = request.POST.get("reason", "No reason provided")
        child.is_terminated = True
        child.termination_reason = reason
        child.save()
        messages.success(request, f"Child account {child.user.username} terminated successfully.")
        return redirect("dashboard")

    return render(request, "accounts/terminate_child.html", {"child": child})


    # accounts/views.py
#deposite and withdraw pages

def deposit(request):
    profile = request.user.customerprofile
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        if amount > 0:
            profile.balance += amount
            profile.save()
            # Save transaction
            Transaction.objects.create(
                sender=None,
                receiver=profile,
                amount=amount,
                transaction_type='DEPOSIT'
            )
            messages.success(request, f"₹{amount:.2f} deposited successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Enter a valid amount.")
    return render(request, 'accounts/deposit.html', {'profile': profile})

def withdraw(request):
    profile = request.user.customerprofile
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        if 0 < amount <= profile.balance:
            profile.balance -= amount
            profile.save()
            # Save transaction
            Transaction.objects.create(
                sender=profile,
                receiver=None,
                amount=amount,
                transaction_type='WITHDRAW'
            )
            messages.success(request, f"₹{amount:.2f} withdrawn successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Enter a valid amount within your balance.")
    return render(request, 'accounts/withdraw.html', {'profile': profile})
