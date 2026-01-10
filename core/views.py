from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal


def homepage(request):
    """Main homepage for The Little Library Administration."""
    return render(request, 'core/homepage.html')


@login_required
def analytics(request):
    """Analytics dashboard for Through Bear's Eyes sales."""
    return render(request, 'core/analytics.html')


@login_required
def analytics_api(request):
    """API endpoint for Through Bear's Eyes analytics data."""
    from orders.models import LineItem
    
    # Get query parameters
    period = request.GET.get('period', 'month')  # day, week, month, year
    order_type = request.GET.get('type', 'all')  # all, preorder, regular
    
    today = timezone.now().date()
    
    # Calculate date range based on period
    if period == 'day':
        start_date = today
        prev_start = today - timedelta(days=1)
        prev_end = today
    elif period == 'week':
        start_date = today - timedelta(days=7)
        prev_start = today - timedelta(days=14)
        prev_end = start_date
    elif period == 'month':
        start_date = today - timedelta(days=30)
        prev_start = today - timedelta(days=60)
        prev_end = start_date
    else:  # year
        start_date = today - timedelta(days=365)
        prev_start = today - timedelta(days=730)
        prev_end = start_date
    
    # Build base queryset for Through Bear's Eyes
    def get_bear_items(start, end=None, order_type='all'):
        """Get Through Bear's Eyes line items filtered by type."""
        qs = LineItem.objects.filter(
            product_name__icontains='Through Bear'
        )
        
        if end:
            qs = qs.filter(
                order__order_date__date__gte=start,
                order__order_date__date__lt=end
            )
        else:
            qs = qs.filter(order__order_date__date__gte=start)
        
        if order_type == 'preorder':
            qs = qs.filter(product_name__icontains='Pre-Order')
        elif order_type == 'regular':
            qs = qs.exclude(product_name__icontains='Pre-Order')
        
        return qs
    
    # Current period stats
    current_items = get_bear_items(start_date, order_type=order_type)
    current_qty = current_items.aggregate(total=Sum('quantity'))['total'] or 0
    current_orders = current_items.values('order').distinct().count()
    
    # Previous period stats for comparison
    prev_items = get_bear_items(prev_start, prev_end, order_type=order_type)
    prev_qty = prev_items.aggregate(total=Sum('quantity'))['total'] or 0
    prev_orders = prev_items.values('order').distinct().count()
    
    # Calculate percentage changes
    qty_change = 0
    if prev_qty > 0:
        qty_change = round(((current_qty - prev_qty) / prev_qty) * 100, 1)
    
    order_change = 0
    if prev_orders > 0:
        order_change = round(((current_orders - prev_orders) / prev_orders) * 100, 1)
    
    # All-time stats
    all_time_items = LineItem.objects.filter(product_name__icontains='Through Bear')
    if order_type == 'preorder':
        all_time_items = all_time_items.filter(product_name__icontains='Pre-Order')
    elif order_type == 'regular':
        all_time_items = all_time_items.exclude(product_name__icontains='Pre-Order')
    
    all_time_qty = all_time_items.aggregate(total=Sum('quantity'))['total'] or 0
    all_time_orders = all_time_items.values('order').distinct().count()
    
    # Pre-order vs Regular breakdown (for all time)
    preorder_total = LineItem.objects.filter(
        product_name__icontains='Through Bear'
    ).filter(
        product_name__icontains='Pre-Order'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    regular_total = LineItem.objects.filter(
        product_name__icontains='Through Bear'
    ).exclude(
        product_name__icontains='Pre-Order'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    # Chart data - sales over time within the period
    chart_items = get_bear_items(start_date, order_type=order_type)
    
    if period == 'day':
        # Hourly breakdown not available, just show total
        chart_data = [{'label': today.strftime('%d %b'), 'value': current_qty}]
    elif period == 'week':
        # Daily breakdown
        daily_data = chart_items.annotate(
            date=TruncDate('order__order_date')
        ).values('date').annotate(
            total=Sum('quantity')
        ).order_by('date')
        chart_data = [{'label': d['date'].strftime('%a %d'), 'value': d['total']} for d in daily_data if d['date']]
    elif period == 'month':
        # Daily breakdown
        daily_data = chart_items.annotate(
            date=TruncDate('order__order_date')
        ).values('date').annotate(
            total=Sum('quantity')
        ).order_by('date')
        chart_data = [{'label': d['date'].strftime('%d %b'), 'value': d['total']} for d in daily_data if d['date']]
    else:  # year
        # Monthly breakdown
        monthly_data = chart_items.annotate(
            month=TruncMonth('order__order_date')
        ).values('month').annotate(
            total=Sum('quantity')
        ).order_by('month')
        chart_data = [{'label': d['month'].strftime('%b %Y'), 'value': d['total']} for d in monthly_data if d['month']]
    
    # Recent sales list
    recent_items = get_bear_items(start_date, order_type=order_type).select_related('order').order_by('-order__order_date')[:20]
    recent_sales = [{
        'order_number': item.order.order_number,
        'customer': item.order.customer_name,
        'product': item.product_name,
        'quantity': item.quantity,
        'date': item.order.order_date.strftime('%d %b %Y %H:%M') if item.order.order_date else 'N/A',
        'is_preorder': 'Pre-Order' in item.product_name
    } for item in recent_items]
    
    return JsonResponse({
        'period': period,
        'order_type': order_type,
        'current': {
            'books_sold': current_qty,
            'orders': current_orders,
            'qty_change': qty_change,
            'order_change': order_change,
        },
        'all_time': {
            'books_sold': all_time_qty,
            'orders': all_time_orders,
        },
        'breakdown': {
            'preorder': preorder_total,
            'regular': regular_total,
        },
        'chart': chart_data,
        'recent_sales': recent_sales,
    })
