from django.urls import path
from . import views

urlpatterns = [
    path('', views.hq_dashboard, name='hq_dashboard'),
    path('attendance/', views.attendance_view, name='hq_attendance'),
    path('attendance/boys-wing/', views.boys_wing_view, name='boys_wing'),
    path('attendance/girls-wing/', views.girls_wing_view, name='girls_wing'),
]
