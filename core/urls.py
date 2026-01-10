from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('analytics/', views.analytics, name='analytics'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
    path('dashboard/', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
]
