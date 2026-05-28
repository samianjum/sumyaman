from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import TenantAdminLoginView
from .fee_views import (
    recent_payments_api,
    fee_structure_view,
    delete_fee_structure,
    fee_collection_view,
    fee_collection_print,
    family_payment_view,
    defaulters_list,
    fee_reports,
    student_fee_view,
    generate_fees_view,
    student_search_api,
    get_pending_details,
    collect_payment_api,
    undo_payment,
    family_payment_api,
    daily_collection_summary)


urlpatterns = [
    path('exams/result/<int:student_id>/<int:exam_id>/<int:subject_id>/', views.view_student_result, name='view_student_result'),
    path('exams/analytics/<int:exam_id>/', views.exam_analytics_view, name='exam_analytics'),
    path('exams/<int:exam_id>/subject/<int:subject_id>/', views.exam_subject_analytics_view, name='exam_subject_analytics'),
    path('exams/analytics/<int:exam_id>/class/<str:class_name>/', views.exam_class_detail_view, name='exam_class_analytics'),
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
    path('attendance/class/<str:class_name>/', views.class_sections_view, name='class_sections'),
    path('attendance/boys-wing/', views.boys_wing_view, name='boys_wing'),
    path('attendance/girls-wing/', views.girls_wing_view, name='girls_wing'),
    path('attendance/mark/<str:class_name>/<str:section_name>/<path:wing_name>/', views.mark_attendance_view, name='mark_attendance'),

    # Search
    path('search/', views.global_search, name='global_search'),

    # Main Dashboard (Empty path at the end)
    path('subjects/', views.subject_manager_view, name='subject_manager'),
    path('settings/', views.school_settings_view, name='school_settings'),
    path('', views.hq_dashboard, name='hq_dashboard'),

    # Fee Management URLs
    path('fee/structure/', fee_structure_view, name='fee_structure'),
    path('fee/structure/delete/<int:pk>/', delete_fee_structure, name='delete_fee_structure'),
    path('fee/collection/', fee_collection_view, name='fee_collection'),
    path('fee/collection/print/<str:receipt_no>/', fee_collection_print, name='fee_collection_print'),
    path('fee/family/', family_payment_view, name='family_payment'),
    path('fee/defaulters/', defaulters_list, name='defaulters'),
    path('fee/reports/', fee_reports, name='fee_reports'),
    path('fee/generate/<int:year>/<int:month>/', generate_fees_view, name='generate_fees'),
    path('fee/student/<int:student_id>/', student_fee_view, name='student_fee_view'),
]

# Tenant Admin Login/Logout
urlpatterns += [
    path('admin/login/', TenantAdminLoginView.as_view(), name='tenant_admin_login'),
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='/'), name='tenant_admin_logout'),

    # Fee Collection APIs
    path('fee/student/search/', student_search_api, name='fee_student_search'),
    path('fee/student/pending/', get_pending_details, name='fee_pending_details'),
    path('fee/collect/', collect_payment_api, name='fee_collect_api'),
    path('fee/undo/<str:receipt_no>/', undo_payment, name='fee_undo'),
    path('fee/family-pay/', family_payment_api, name='family_payment_api'),
    path('fee/daily-summary/', daily_collection_summary, name='daily_summary'),
        path('fee/recent-payments/', recent_payments_api, name='fee_recent_payments'),

]
