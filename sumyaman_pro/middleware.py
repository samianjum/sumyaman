from django.conf import settings
from django.shortcuts import redirect
from .router import set_current_db
from super_admin.models import SchoolClient

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path_parts = request.path.strip('/').split('/')

        # Load all schools into settings.DATABASES if not already there
        # This ensures connections exist after server restart
        schools = SchoolClient.objects.all()
        for school in schools:
            if school.slug not in settings.DATABASES:
                db_config = settings.DATABASES['default'].copy()
                db_config['NAME'] = school.db_name
                settings.DATABASES[school.slug] = db_config

        if len(path_parts) >= 2 and path_parts[0] == 's':
            slug = path_parts[1]
            try:
                if slug in settings.DATABASES:
                    # Power Check: Is school active?
                    school = SchoolClient.objects.using('default').get(slug=slug)
                    if not school.is_active:
                        from django.http import HttpResponseForbidden
                        return HttpResponseForbidden("<h1>School Suspended</h1><p>This institution has been deactivated by the Super Admin.</p>")

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

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        return response
