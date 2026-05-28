from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path, include
from apsokara import views
from .admin import admin_site


from django.urls import path, include
from apsokara import views
from django.contrib import admin
from django.contrib.auth import logout
from django.shortcuts import redirect






urlpatterns = [
        path('hq-admin/', admin_site.urls), # Main Master Admin
    path('super-admin/', include('super_admin.urls')),
    path('s/<slug:school_slug>/update-logo/', include('super_admin.urls_logo')), # Simplified for now

    # Dynamic Tenant Admin - Fixed with wrapper
            # Custom admin redirect: send /admin/* to the same path without /admin

    # The original admin site is still available at /hq-admin/ for superusers
    path('hq-admin/', admin_site.urls),

                                path('s/<slug:school_slug>/admin/', lambda request, school_slug: redirect(f'/s/{school_slug}/')),
    path('s/<slug:school_slug>/admin/logout/', views.tenant_logout, name='admin_logout'),
    path('s/<slug:school_slug>/', include('apsokara.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
