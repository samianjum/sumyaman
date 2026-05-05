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
                if not hasattr(request, 'user') or not request.user.is_authenticated and not request.path.endswith('/admin/') and 'login' not in request.path:
                    if not any(x in request.path for x in ['login', 'admin']):
                         return redirect(f'/s/{slug}/admin/login/?next={request.path}')
            else:
                set_current_db('default')
        else:
            set_current_db('default')
            
        return self.get_response(request)
