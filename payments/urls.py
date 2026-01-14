from django.urls import path
from . import views

urlpatterns = [
    path('', views.payments_dashboard, name='payments'),
    path('mark-paid/<int:period_id>/', views.mark_paid, name='mark_paid'),
    path('mark-unpaid/<int:period_id>/', views.mark_unpaid, name='mark_unpaid'),
    path('update-amount/<int:period_id>/', views.update_amount, name='update_amount'),
]
