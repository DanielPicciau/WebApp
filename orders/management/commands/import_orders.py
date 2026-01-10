import pandas as pd
from django.core.management.base import BaseCommand
from orders.models import Order, LineItem
import os

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
            order, created = Order.objects.get_or_create(
                order_number=order_number,
                defaults={
                    'customer_name': row['Shipping Name'],
                    'shipping_address': f"{row['Shipping Address1']} {row['Shipping Address2']} {row['Shipping City']} {row['Shipping Zip']}".strip(),
                    'is_fulfilled': row['Fulfillment Status'] == 'fulfilled'
                }
            )
            
            # If the order was just created and we missed shipping info (unlikely if sorted), 
            # or if we want to update it just in case:
            if not created and not order.customer_name and row['Shipping Name']:
                 order.customer_name = row['Shipping Name']
                 order.shipping_address = f"{row['Shipping Address1']} {row['Shipping Address2']} {row['Shipping City']} {row['Shipping Zip']}".strip()
                 order.save()

            # Create Line Item
            # Basic check to avoid duplicates if running multiple times? 
            # Since we don't have unique IDs for line items easily, we might duplicate if we run this command twice.
            # For this "quick app", let's assume we run it once or clear the DB.
            # Or we can check if a line item with same product/sku exists for this order.
            
            # Let's purge items for the order if created (fresh start for that order) - wait, no, because we loop rows.
            
            # Check if exists
            exists = LineItem.objects.filter(
                order=order,
                product_name=row['Lineitem name'],
                sku=row['Lineitem sku']
            ).exists()

            if not exists and row['Lineitem name']:
                quantity = 1
                if row['Lineitem quantity']:
                    try:
                        quantity = int(float(row['Lineitem quantity']))
                    except:
                        pass
                
                LineItem.objects.create(
                    order=order,
                    product_name=row['Lineitem name'],
                    quantity=quantity,
                    sku=row['Lineitem sku']
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully imported orders'))
