#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fulfillment_project.settings')
django.setup()

from orders.models import Order, LineItem
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone

# Check order dates
print('=== Sample Orders with order_date ===')
for o in Order.objects.all()[:5]:
    print(f'{o.order_number}: order_date={o.order_date}')

print()

# Check December 16-31, 2025 specifically
start = timezone.make_aware(datetime(2025, 12, 16, 0, 0, 0))
end = timezone.make_aware(datetime(2026, 1, 1, 0, 0, 0))

dec_items = LineItem.objects.filter(
    product_name__icontains='Through Bear',
    order__order_date__gte=start,
    order__order_date__lt=end
)
print(f'=== December 16-31, 2025 ===')
print(f'Items: {dec_items.count()}')
print(f'Sum: {dec_items.aggregate(Sum("quantity"))}')

# Check all months
print()
print('=== By Month ===')
for month in range(10, 13):
    m_start = timezone.make_aware(datetime(2025, month, 1, 0, 0, 0))
    if month == 12:
        m_end = timezone.make_aware(datetime(2026, 1, 1, 0, 0, 0))
    else:
        m_end = timezone.make_aware(datetime(2025, month+1, 1, 0, 0, 0))
    items = LineItem.objects.filter(
        product_name__icontains='Through Bear',
        order__order_date__gte=m_start,
        order__order_date__lt=m_end
    )
    total = items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    print(f'{month}/2025: {total} books')
