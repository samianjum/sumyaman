from django.conf import settings
from django.shortcuts import redirect
from .router import set_current_db
from super_admin.models import SchoolClient

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path_parts = request.path.strip('/').split('/')
        
        if len(path_parts) >= 2 and path_parts[0] == 's':
            slug = path_parts[1]
            
            # SQLite file check ki jagah hum DB check karenge
            try:
                school_exists = SchoolClient.objects.filter(slug=slug).exists()
                if school_exists:
                    # Yahan hum Dynamic DB routing ka logic use karenge
                    set_current_db(slug)
                    
                    if not request.user.is_authenticated and 'login' not in request.path:
                        return redirect(f'/s/{slug}/admin/login/')
                else:
                    set_current_db('default')
            except:
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
        return response
