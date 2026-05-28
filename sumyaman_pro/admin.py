from django.contrib.admin import AdminSite
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

class TenantAwareAdminSite(AdminSite):
    """Admin site that ignores extra keyword arguments (like school_slug)."""

    def admin_view(self, view, cacheable=False):
        # Wrapper to discard the school_slug keyword argument
        def wrapper(request, *args, **kwargs):
            kwargs.pop('school_slug', None)
            return view(request, *args, **kwargs)
        return super().admin_view(wrapper, cacheable)

    @method_decorator(csrf_protect)
    def login(self, request, extra_context=None):
        return super().login(request, extra_context)

    @method_decorator(never_cache)
    def index(self, request, extra_context=None):
        return super().index(request, extra_context)

# Instantiate the custom admin site
admin_site = TenantAwareAdminSite(name='tenant_admin')
