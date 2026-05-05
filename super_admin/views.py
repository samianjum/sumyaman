from django.shortcuts import render, redirect
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User
from .models import SchoolClient
import os

def super_admin_dashboard(request):
    schools = SchoolClient.objects.all()
    return render(request, 'super_admin/dashboard.html', {'schools': schools})

def create_school(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug').lower().replace(' ', '_')
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
            defaults={'name': name, 'db_name': db_name}
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
