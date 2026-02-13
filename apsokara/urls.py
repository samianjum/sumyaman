from django.urls import path
from . import views

urlpatterns = [
    path('exams/analytics/<int:exam_id>/', views.exam_analytics_view, name='exam_analytics'),
    # Exam System (Priority)
    path('exams/', views.exam_window_view, name='exam_window'),
    path('exams/create/', views.create_exam_view, name='create_exam'),
    path('exams/delete/<int:exam_id>/', views.delete_exam_view, name='delete_exam'),
    path('exams/subjects/<int:exam_id>/', views.manage_subjects_view, name='manage_subjects'),
    path('exams/toggle/<int:exam_id>/', views.toggle_exam_status, name='toggle_exam'),


    # News & Dashboard
    path('news-manager/', views.news_manager_view, name='news_manager'),
    path('news-delete/<int:news_id>/', views.delete_news, name='delete_news'),
    
    # Students
    path('students/', views.student_master_list, name='student_master_list'),
    path('student/profile/<int:student_id>/', views.student_profile_view, name='student_profile'),
    
    # Teachers
    path('teachers/', views.teacher_master_list, name='teacher_master_list'),
    path('teachers/profile/<int:teacher_id>/', views.teacher_profile_view, name='teacher_profile'),
    
    # Attendance & Wings
    path('attendance/', views.attendance_view, name='hq_attendance'),
    path('attendance/boys-wing/', views.boys_wing_view, name='boys_wing'),
    path('attendance/girls-wing/', views.girls_wing_view, name='girls_wing'),
    path('attendance/mark/<str:class_name>/<str:section_name>/<str:wing_name>/', views.mark_attendance_view, name='mark_attendance'),
    
    # Search
    path('search/', views.global_search, name='global_search'),
    
    # Main Dashboard (Empty path at the end)
    path('', views.hq_dashboard, name='hq_dashboard'),
]
