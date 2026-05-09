from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User
from .models import SchoolClient
import os


def is_super_admin(user):
    return user.is_authenticated and user.is_superuser
@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
@never_cache
def super_admin_dashboard(request):
    schools = SchoolClient.objects.all()
    return render(request, 'super_admin/dashboard.html', {'schools': schools})

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
@never_cache
def create_school(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug').lower().replace(' ', '_')
        school_type = request.POST.get('school_type')
        admin_user = request.POST.get('admin_user')
        admin_pass = request.POST.get('admin_pass')
        
        db_name = f"{slug}_school.sqlite3"
        tenants_dir = os.path.join(settings.BASE_DIR, 'tenants')
        if not os.path.exists(tenants_dir):
            os.makedirs(tenants_dir)
            
        db_path = os.path.join(tenants_dir, db_name)
        
        # Save record in Main DB
        school = SchoolClient.objects.get_or_create(
            slug=slug, 
            defaults={'name': name, 'db_name': db_name, 'school_type': school_type}
        )

        # Inject DB config temporarily
        if slug not in settings.DATABASES:
            new_db_config = settings.DATABASES['default'].copy()
            new_db_config['NAME'] = db_path
            settings.DATABASES[slug] = new_db_config

        # 1. Run Migrations
        call_command('migrate', database=slug, interactive=False)

        # 2. Create Superuser (Correct Method: db_manager)
        manager = User.objects.db_manager(slug)
        if not manager.filter(username=admin_user).exists():
            manager.create_superuser(
                username=admin_user, 
                password=admin_pass,
                email=f"admin@{slug}.com"
            )

        return redirect('super_admin_dashboard')
    
    return render(request, 'super_admin/create_school.html')


from django.http import JsonResponse
@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
def update_school_logo(request, school_slug):
    if request.method == "POST":
        try:
            school = SchoolClient.objects.get(slug=school_slug)
            if "remove" in request.POST:
                if school.logo:
                    school.logo.delete()
                school.logo = None
            elif request.FILES.get("logo"):
                school.logo = request.FILES["logo"]
            school.save()
        except Exception as e:
            print(f"Logo update error: {e}")
        
        # Success ke baad wapis usi page pe bhejna jahan se request ayi thi
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect(f'/s/{school_slug}/')
    return JsonResponse({"error": "Invalid request"})

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
@never_cache
def school_detail(request, slug):
    from django.utils import timezone
    school = SchoolClient.objects.get(slug=slug)
    diff = timezone.now() - school.created_at
    # Agar 24 hours se kam hain toh 1 day dikhaye, warna total days + 1
    days_active = diff.days + 1
    return render(request, 'super_admin/school_detail.html', {
        'school': school, 
        'days_active': days_active
    })
