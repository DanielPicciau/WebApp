from django import forms
from django.forms import inlineformset_factory
from .models import Order, LineItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'subtotal', 'currency']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'value': 'GBP'}),
        }

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
