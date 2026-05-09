from django.contrib import admin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Wrapper to strip school_slug before passing to admin login
def admin_login_wrapper(request, school_slug=None, **kwargs):
    # KICKOUT: If already logged in, go to dashboard immediately
    if request.user.is_authenticated and school_slug:
        return redirect(f'/s/{school_slug}/')
        
    if not request.GET.get('next') and school_slug:
        request.GET = request.GET.copy()
        request.GET['next'] = f'/s/{school_slug}/'
    return admin.site.login(request, **kwargs)


def admin_logout_view(request, school_slug=None):
    logout(request)
    if school_slug:
        return redirect(f'/s/{school_slug}/admin/login/')
    return redirect('/hq-admin/login/')

urlpatterns = [
    path('s/<slug:school_slug>/admin/logout/', admin_logout_view, name='admin_logout'),
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