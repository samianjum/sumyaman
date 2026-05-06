import os
from super_admin.models import SchoolClient

def school_context(request):
    """
    Makes 'current_school' available in all templates.
    """
    path_parts = request.path.strip('/').split('/')
    
    # Check if we are in a school context (/s/slug/...)
    if len(path_parts) >= 2 and path_parts[0] == 's':
        slug = path_parts[1]
        try:
            # We must explicitly use the 'default' database to fetch SchoolClient
            school = SchoolClient.objects.using('default').get(slug=slug)
            return {
                'current_school': school,
                'school_slug': slug
            }
        except SchoolClient.DoesNotExist:
            pass
            
    return {}
