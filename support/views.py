from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import TicketForm
from .models import Ticket

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            messages.success(request, "Ticket submitted.")
            return redirect('support_list')
    else:
        form = TicketForm()
    return render(request, 'support/create_ticket.html', {'form': form})

@login_required
def support_list(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support/my_tickets.html', {'tickets': tickets})

# staff views
def staff_check(user):
    return user.is_staff

@user_passes_test(staff_check)
def all_tickets(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'support/all_tickets.html', {'tickets': tickets})

@user_passes_test(staff_check)
def update_ticket_status(request, pk, status):
    t = get_object_or_404(Ticket, pk=pk)
    t.status = status
    t.save()
    messages.success(request, "Ticket updated.")
    return redirect('all_tickets')
