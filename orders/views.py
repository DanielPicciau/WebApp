from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import Order
from .forms import OrderForm, LineItemFormSet
import re
import time

def check_updates(request):
    """Returns the timestamp of the last updated order to trigger frontend refreshes."""
    last_order = Order.objects.all().order_by('-updated_at').first()
    if last_order:
        timestamp = last_order.updated_at.timestamp()
    else:
        timestamp = 0
    return JsonResponse({'last_updated': timestamp})

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
    sort_option = request.GET.get('sort', 'oldest')
    
    if filter_status == 'packed':
        orders = Order.objects.filter(is_packed=True)
    else:
        orders = Order.objects.filter(is_packed=False)

    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(shipping_address__icontains=search_query)
        )
        
    # Apply Sorting
    if sort_option == 'newest':
        orders = orders.order_by('-created_at')
    elif sort_option == 'value_high':
        orders = orders.order_by('-subtotal')
    elif sort_option == 'value_low':
        orders = orders.order_by('subtotal')
    else: # oldest
        orders = orders.order_by('created_at')

    # Limit results if not searching and not explicitly viewing all
    view_all = request.GET.get('view_all') == 'true'
    total_count = orders.count()
    showing_limited = False

    if not search_query and not view_all:
        if total_count > 5:
            orders = orders[:5]
            showing_limited = True

    return render(request, 'orders/order_list.html', {
        'orders': orders, 
        'filter_status': filter_status,
        'search_query': search_query,
        'sort_option': sort_option,
        'showing_limited': showing_limited,
        'total_count': total_count
    })

@user_passes_test(lambda u: u.is_superuser)
def toggle_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_packed = not order.is_packed
    order.save()
    
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('order_list')

from django.core.paginator import Paginator

@user_passes_test(lambda u: u.is_superuser)
def simplified_view(request):
    search_query = request.GET.get('q', '')
    sort_option = request.GET.get('sort', 'oldest')

    # Base Query: Only unpacked orders
    orders_list = Order.objects.filter(is_packed=False)

    # Search
    if search_query:
        orders_list = orders_list.filter(
            Q(order_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(shipping_address__icontains=search_query)
        )

    # Sort
    if sort_option == 'newest':
        orders_list = orders_list.order_by('-created_at')
    elif sort_option == 'value_high':
        orders_list = orders_list.order_by('-subtotal')
    elif sort_option == 'value_low':
        orders_list = orders_list.order_by('subtotal')
    else: # oldest
        orders_list = orders_list.order_by('created_at')
    
    paginator = Paginator(orders_list, 1) # Show 1 order per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'orders/simplified.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_option': sort_option
    })



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
