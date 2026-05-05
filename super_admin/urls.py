from django.urls import path
from . import views

urlpatterns = [
    path('', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('create/', views.create_school, name='create_school'),
]
