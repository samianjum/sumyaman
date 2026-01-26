from apsokara import student_views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hq-portal/', include('apsokara.urls')), # Ye line saare portal ke raste khol degi
    path('hq-portal/student/profile/<int:student_id>/', student_views.student_profile_view, name='student_profile'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
