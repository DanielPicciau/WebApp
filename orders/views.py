from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Order
from .forms import OrderForm, LineItemFormSet
import re

def get_next_order_number():
    # Find the latest created order to increment from
    last_order = Order.objects.all().order_by('created_at').last()
    if not last_order:
        return "#1001"
    
    # Try to extract numbers
    last_num_str = last_order.order_number
    match = re.search(r'\d+', last_num_str)
    if match:
        num = int(match.group())
        new_num = num + 1
        # Preserve prefix if any (e.g., "#" or "ORD")
        prefix = last_num_str[:match.start()]
        suffix = last_num_str[match.end():]
        return f"{prefix}{new_num}{suffix}"
    else:
        # Fallback if no number found, append 1
        return f"{last_num_str}-1"


@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    packed_count = Order.objects.filter(is_packed=True).count()
    unpacked_count = Order.objects.filter(is_packed=False).count()
    recent_orders = Order.objects.filter(is_packed=False).order_by('created_at')[:5]
    
    total_revenue = Order.objects.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
    
    return render(request, 'orders/dashboard.html', {
        'packed_count': packed_count,
        'unpacked_count': unpacked_count,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue
    })

# Only allow superusers (admins) to access the views
@user_passes_test(lambda u: u.is_superuser) 
def order_list(request):
    filter_status = request.GET.get('status', 'unpacked')
    search_query = request.GET.get('q', '')
    
    if filter_status == 'packed':
        orders = Order.objects.filter(is_packed=True).order_by('created_at')
    else:
        orders = Order.objects.filter(is_packed=False).order_by('created_at')


    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(shipping_address__icontains=search_query)
        )

    return render(request, 'orders/order_list.html', {
        'orders': orders, 
        'filter_status': filter_status,
        'search_query': search_query
    })

@user_passes_test(lambda u: u.is_superuser)
def toggle_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_packed = not order.is_packed
    order.save()
    return redirect('order_list')


@user_passes_test(lambda u: u.is_superuser)
def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = LineItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.order_number = get_next_order_number()
            order.save()
            
            formset.instance = order
            formset.save()
            return redirect('order_list')
    else:
        form = OrderForm()
        formset = LineItemFormSet()
        
    return render(request, 'orders/add_order.html', {
        'form': form,
        'formset': formset
    })
