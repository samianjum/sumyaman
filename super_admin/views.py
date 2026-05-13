
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User
from .models import SchoolClient
from django.db import connection
from django.http import JsonResponse
from django.utils import timezone

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
        
        # 1. Create Database in PostgreSQL
        with connection.cursor() as cursor:
            cursor.execute("COMMIT") 
            cursor.execute(f'CREATE DATABASE {slug}_db;')
        
        # 2. Save record in Main DB
        SchoolClient.objects.get_or_create(
            slug=slug, 
            defaults={'name': name, 'db_name': f"{slug}_db", 'school_type': school_type}
        )

        # 3. Inject DB config for migration
        if slug not in settings.DATABASES:
            new_db = settings.DATABASES['default'].copy()
            new_db['NAME'] = f"{slug}_db"
            settings.DATABASES[slug] = new_db

        # 4. Run Migrations & Create User
        call_command('migrate', database=slug, interactive=False)
        
        manager = User.objects.db_manager(slug)
        if not manager.filter(username=admin_user).exists():
            manager.create_superuser(username=admin_user, password=admin_pass, email=f"admin@{slug}.com")

        return redirect('super_admin_dashboard')
    
    return render(request, 'super_admin/create_school.html')

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
@never_cache
def school_detail(request, slug):
    school = SchoolClient.objects.get(slug=slug)
    diff = timezone.now() - school.created_at
    days_active = diff.days + 1
    return render(request, 'super_admin/school_detail.html', {
        'school': school, 
        'days_active': days_active
    })

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
def update_school_logo(request, school_slug):
    if request.method == "POST":
        try:
            school = SchoolClient.objects.get(slug=school_slug)
            if "remove" in request.POST:
                if school.logo: school.logo.delete()
                school.logo = None
            elif request.FILES.get("logo"):
                school.logo = request.FILES["logo"]
            school.save()
        except Exception as e:
            print(f"Logo update error: {e}")
        
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else f'/s/{school_slug}/')
    return JsonResponse({"error": "Invalid request"})

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
def toggle_school_status(request, slug):
    school = SchoolClient.objects.get(slug=slug)
    school.is_active = not school.is_active
    school.save()
    return redirect('super_admin_dashboard')
