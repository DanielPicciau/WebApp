from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PaymentPeriod
from datetime import date


@login_required
def payments_dashboard(request):
    """Main payments dashboard."""
    # Ensure all periods are created up to current month
    PaymentPeriod.get_or_create_current_periods()
    
    # Get all periods
    periods = PaymentPeriod.objects.all()
    
    # Calculate stats - need to iterate since books_sold is now a property
    total_books = sum(p.books_sold for p in periods)
    total_amount = sum(p.total_amount for p in periods)
    total_paid = sum(p.total_amount for p in periods.filter(status='paid'))
    total_outstanding = total_amount - total_paid
    
    overdue_count = periods.filter(status='overdue').count()
    due_count = periods.filter(status='due').count()
    
    context = {
        'periods': periods,
        'total_books': total_books,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'overdue_count': overdue_count,
        'due_count': due_count,
    }
    
    return render(request, 'payments/dashboard.html', context)


@login_required
def mark_paid(request, period_id):
    """Mark a period as paid."""
    period = get_object_or_404(PaymentPeriod, id=period_id)
    
    if request.method == 'POST':
        period.paid_date = date.today()
        period.status = 'paid'
        period.save()
        messages.success(request, f'{period.period_name} marked as paid (£{period.total_amount})')
    
    return redirect('payments')


@login_required
def mark_unpaid(request, period_id):
    """Mark a period as unpaid."""
    period = get_object_or_404(PaymentPeriod, id=period_id)
    
    if request.method == 'POST':
        period.paid_date = None
        period.update_status()
        messages.success(request, f'{period.period_name} marked as unpaid')
    
    return redirect('payments')
