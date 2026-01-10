#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fulfillment_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from orders.models import Order
from django.utils import timezone
from datetime import datetime

# First, update all orders where order_date is null - set it to created_at
orders_to_update = Order.objects.filter(order_date__isnull=True)
print(f'Orders with null order_date: {orders_to_update.count()}')

for order in orders_to_update:
    order.order_date = order.created_at
    order.save(update_fields=['order_date'])
    print(f'Updated order {order.order_number} with created_at: {order.created_at}')

# Now update orders 1162-1167 with date 10/01/2026
target_date = timezone.make_aware(datetime(2026, 1, 10))
for i in range(1162, 1168):
    order_num = f'#{i}'
    try:
        order = Order.objects.get(order_number=order_num)
        order.order_date = target_date
        order.save(update_fields=['order_date'])
        print(f'Set order {order_num} date to 10/01/2026')
    except Order.DoesNotExist:
        print(f'Order {order_num} not found')

print('Done!')
