from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('analytics/', views.analytics, name='analytics'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
]
