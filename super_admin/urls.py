from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(next_page='/hq-admin/login/'), name='super_admin_logout'),
    path('', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('create/', views.create_school, name='create_school'),
]
