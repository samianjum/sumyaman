from django.urls import path
from . import views

urlpatterns = [
    path('', views.hq_dashboard, name='hq_dashboard'),
    path('students/', views.student_master_list, name='student_master_list'),
    path('teachers/', views.teacher_master_list, name='teacher_master_list'),
    path('attendance/', views.attendance_view, name='hq_attendance'),
    path('search/', views.global_search, name='global_search'),
    path('attendance/boys-wing/', views.boys_wing_view, name='boys_wing'),
    path('attendance/girls-wing/', views.girls_wing_view, name='girls_wing'),
    path('attendance/mark/<str:class_name>/<str:section_name>/', views.mark_attendance_view, name='mark_attendance'),
    path('student/profile/<int:student_id>/', views.student_profile_view, name='student_profile'), # Temporary mapped to dashboard
]
