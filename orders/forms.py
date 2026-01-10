from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import Order, LineItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'order_date', 'subtotal', 'currency']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'order_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'GBP'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default order_date to now if creating new order
        if not self.instance.pk and not self.initial.get('order_date'):
            self.initial['order_date'] = timezone.now()

LineItemFormSet = inlineformset_factory(
    Order, LineItem,
    fields=['product_name', 'quantity'],
    extra=1,
    can_delete=True,
    widgets={
        'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Qty', 'min': 1}),
    }
)
