import pandas as pd
from django.core.management.base import BaseCommand
from orders.models import Order, LineItem
import os
from datetime import datetime
from django.utils import timezone


def parse_shopify_date(date_str):
    """Parse Shopify date format like '2025-10-11 16:57:10 +0100'"""
    if not date_str:
        return None
    try:
        # Parse the date string with timezone offset
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')
        return dt
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = 'Import orders from CSV'

    def handle(self, *args, **options):
        file_path = 'orders_export.csv'
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR('CSV file not found'))
            return

        # Read CSV
        # Note: We need to handle potential string/float issues with Zip codes or Phone numbers if we use them
        df = pd.read_csv(file_path, dtype=str) 
        df = df.fillna('')

        for index, row in df.iterrows():
            order_number = row['Name']
            
            if not order_number:
                continue

            # Create or Get Order
            # We rely on the first occurrence having the shipping details
            subtotal = 0.00
            if row['Subtotal']:
                 try:
                     subtotal = float(row['Subtotal'])
                 except:
                     pass

            # Parse the original order date from Shopify
            order_date = parse_shopify_date(row['Created at'])
            
            order, created = Order.objects.get_or_create(
                order_number=order_number,
                defaults={
                    'customer_name': row['Shipping Name'],
                    'shipping_address': f"{row['Shipping Address1']} {row['Shipping Address2']} {row['Shipping City']} {row['Shipping Zip']}".strip(),
                    'subtotal': subtotal,
                    'currency': row['Currency'] if row['Currency'] else 'GBP',
                    'is_fulfilled': row['Fulfillment Status'] == 'fulfilled',
                    'order_date': order_date
                }
            )
            
            # If the order was just created and we missed shipping info (unlikely if sorted), 
            # or if we want to update it just in case:
            if not created:
                has_changes = False
                if not order.customer_name and row['Shipping Name']:
                     order.customer_name = row['Shipping Name']
                     order.shipping_address = f"{row['Shipping Address1']} {row['Shipping Address2']} {row['Shipping City']} {row['Shipping Zip']}".strip()
                     has_changes = True
                
                # Update subtotal if it was 0 (or adjust logic as needed)
                if order.subtotal == 0 and row['Subtotal']:
                    try:
                        order.subtotal = float(row['Subtotal'])
                        has_changes = True
                    except:
                        pass
                
                if has_changes:
                    order.save()


            # Create Line Item
            # Basic check to avoid duplicates if running multiple times? 
            # Since we don't have unique IDs for line items easily, we might duplicate if we run this command twice.
            # For this "quick app", let's assume we run it once or clear the DB.
            # Or we can check if a line item with same product/sku exists for this order.
            
            # Let's purge items for the order if created (fresh start for that order) - wait, no, because we loop rows.
            
            # Parse quantity
            quantity = 1
            if row['Lineitem quantity']:
                try:
                    quantity = int(float(row['Lineitem quantity']))
                except:
                    pass
            
            # Check if this line item already exists for this order
            existing_item = LineItem.objects.filter(
                order=order,
                product_name=row['Lineitem name'],
                sku=row['Lineitem sku']
            ).first()

            if existing_item:
                # Add to existing quantity (handles multiple CSV rows for same product)
                existing_item.quantity += quantity
                existing_item.save()
            elif row['Lineitem name']:
                LineItem.objects.create(
                    order=order,
                    product_name=row['Lineitem name'],
                    quantity=quantity,
                    sku=row['Lineitem sku']
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully imported orders'))
