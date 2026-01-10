from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.order_list, name='order_list'),
    path('toggle/<int:order_id>/', views.toggle_order, name='toggle_order'),
]
