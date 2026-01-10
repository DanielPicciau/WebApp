#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fulfillment_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from orders.models import Order

print("All orders in the database:")
for o in Order.objects.all():
    print(f'{o.order_number} - order_date: {o.order_date}')
