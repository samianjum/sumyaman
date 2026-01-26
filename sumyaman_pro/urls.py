from django.contrib import admin
from django.urls import path, include
from apsokara.views import hq_dashboard, attendance_view

urlpatterns = [
    path('admin/', admin.site.urls),  # Aapka original admin panel
    path('hq-portal/', hq_dashboard, name='hq_dashboard'),  # Custom Panel
    path('hq-portal/attendance/', attendance_view, name='hq_attendance'),
]
