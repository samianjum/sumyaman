from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.db import connection
from django.core.management import call_command
from django.contrib import messages
from .models import SchoolClient
from django.contrib.auth.models import User
import psutil
import os

def is_super_admin(user):
    return user.is_superuser

@user_passes_test(is_super_admin)
def super_admin_dashboard(request):
    schools = SchoolClient.objects.all()
    # Simple health stats
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    health = {'cpu': cpu, 'ram': ram, 'disk': disk}
    return render(request, 'super_admin/dashboard.html', {
        'schools': schools,
        'health': health,
    })

@user_passes_test(is_super_admin)
def create_school(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        school_type = request.POST.get('school_type', 'co-ed')
        admin_user = request.POST.get('admin_user')
        admin_pass = request.POST.get('admin_pass')

        if SchoolClient.objects.filter(slug=slug).exists():
            messages.error(request, 'Slug already exists')
            return redirect('create_school')

        # Create database name
        db_name = f"{slug}_db"

        # Create tenant record in default DB
        school = SchoolClient.objects.create(
            name=name, slug=slug, db_name=db_name, school_type=school_type
        )

        # Create physical database and run migrations
        from .views_helper import create_tenant_database, setup_tenant_schema
        create_tenant_database(db_name, 'sami_admin', 'sami123')
        setup_tenant_schema(db_name, admin_user, admin_pass)

        messages.success(request, f'School "{name}" created successfully!')
        return redirect('super_admin_dashboard')

    return render(request, 'super_admin/create_school.html')

@user_passes_test(is_super_admin)
def school_detail(request, slug):
    school = get_object_or_404(SchoolClient, slug=slug)
    # Connect to tenant DB to get stats
    from django.db import connections
    from django.apps import apps
    tenant_db = school.db_name

    # Add tenant DB to settings if not already there
    if tenant_db not in settings.DATABASES:
        db_config = settings.DATABASES['default'].copy()
        db_config['NAME'] = tenant_db
        settings.DATABASES[tenant_db] = db_config

    try:
        with connections[tenant_db].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM apsokara_student")
            student_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM apsokara_teacher")
            teacher_count = cursor.fetchone()[0]
    except Exception:
        student_count = 0
        teacher_count = 0

    # Calculate days since creation
    days_active = (timezone.now() - school.created_at).days

    stats = {'students': student_count, 'teachers': teacher_count}
    return render(request, 'super_admin/school_detail.html', {
        'school': school,
        'stats': stats,
        'days_active': days_active,
    })

@user_passes_test(is_super_admin)
def toggle_school_status(request, slug):
    school = get_object_or_404(SchoolClient, slug=slug)
    school.is_active = not school.is_active
    school.save()
    messages.success(request, f'School {school.name} status changed.')
    return redirect('school_detail', slug=slug)

@user_passes_test(is_super_admin)
def update_school_logo(request, school_slug):
    school = get_object_or_404(SchoolClient, slug=school_slug)
    if request.method == 'POST':
        if request.POST.get('remove'):
            school.logo.delete(save=False)
            school.logo = None
            school.save()
            messages.success(request, 'Logo removed.')
        elif request.FILES.get('logo'):
            school.logo = request.FILES['logo']
            school.save()
            messages.success(request, 'Logo updated.')
    return redirect('school_detail', slug=school_slug)
