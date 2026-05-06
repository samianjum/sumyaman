from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Wrapper to strip school_slug before passing to admin login
def admin_login_wrapper(request, school_slug=None, **kwargs):
    return admin.site.login(request, **kwargs)

urlpatterns = [
    path('hq-admin/', admin.site.urls), # Main Master Admin
    path('super-admin/', include('super_admin.urls')),
    path('s/<slug:school_slug>/update-logo/', include('super_admin.urls_logo')), # Simplified for now 
    
    # Dynamic Tenant Admin - Fixed with wrapper
    path('s/<slug:school_slug>/admin/login/', admin_login_wrapper),
    path('s/<slug:school_slug>/admin/', admin.site.urls), 
    
    path('s/<slug:school_slug>/', include('apsokara.urls')), 
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)