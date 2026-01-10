from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('toggle/<int:order_id>/', views.toggle_order, name='toggle_order'),
]
