from django.conf import settings
from django.shortcuts import redirect
from .router import set_current_db
import os

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path_parts = request.path.strip('/').split('/')
        
        # Check if we are in a school context (/s/slug/...)
        if len(path_parts) >= 2 and path_parts[0] == 's':
            slug = path_parts[1]
            db_file = f"{slug}_school.sqlite3"
            db_path = os.path.join(settings.BASE_DIR, 'tenants', db_file)
            
            if os.path.exists(db_path):
                if slug not in settings.DATABASES:
                    new_config = settings.DATABASES['default'].copy()
                    new_config['NAME'] = db_path
                    settings.DATABASES[slug] = new_config
                
                set_current_db(slug)
                
                # FIX: Agar user login nahi hai aur dashboard access kar raha hai
                # To usay usi school ke admin login pe bhejo, na ke default /admin/
                # STRICT LOCKDOWN: Anonymous users cannot access school paths
                is_auth_path = any(x in request.path for x in ['login', 'logout'])
                if not request.user.is_authenticated and not is_auth_path:
                    return redirect(f'/s/{slug}/admin/login/')
            else:
                set_current_db('default')
        else:
            set_current_db('default')
            
        return self.get_response(request)

from django.utils.cache import add_never_cache_headers

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/admin/') or request.path.startswith('/hq-admin/'):
            add_never_cache_headers(response)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
