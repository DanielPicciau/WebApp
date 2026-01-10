from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_order, name='add_order'),
    path('simplified/', views.simplified_view, name='simplified_view'),
    path('', views.order_list, name='order_list'),
    path('toggle/<int:order_id>/', views.toggle_order, name='toggle_order'),
]
