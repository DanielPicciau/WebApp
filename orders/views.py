from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Order

@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    packed_count = Order.objects.filter(is_packed=True).count()
    unpacked_count = Order.objects.filter(is_packed=False).count()
    recent_orders = Order.objects.filter(is_packed=False).order_by('created_at')[:5]
    
    return render(request, 'orders/dashboard.html', {
        'packed_count': packed_count,
        'unpacked_count': unpacked_count,
        'recent_orders': recent_orders
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

