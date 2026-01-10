from django.db import models

class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=255)
    shipping_address = models.TextField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='GBP')
    is_fulfilled = models.BooleanField(default=False) # Represents Shopify/System status
    is_packed = models.BooleanField(default=False)    # Represents manual packing status
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number

class LineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    sku = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
