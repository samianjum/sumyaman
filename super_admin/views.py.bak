from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import SchoolClient
from django.db import connection
from django.utils import timezone
from apsokara.models import Student, Teacher

def is_super_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
@never_cache
def super_admin_dashboard(request):
    import psutil
    schools = SchoolClient.objects.all()
    db_stats = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT datname, pg_database_size(datname) FROM pg_database")
            for row in cursor.fetchall():
                db_stats[row[0]] = f"{round(row[1] / (1024 * 1024), 2)} MB"
    except: pass
    for s in schools:
        s.size = db_stats.get(f"{s.slug}_db", "0 MB")
    health = {'cpu': psutil.cpu_percent(), 'ram': psutil.virtual_memory().percent, 'disk': psutil.disk_usage('/').percent}
    return render(request, 'super_admin/dashboard.html', {'schools': schools, 'health': health})

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
@never_cache
def school_detail(request, slug):
    school = get_object_or_404(SchoolClient, slug=slug)
    if slug not in settings.DATABASES:
        db_conf = settings.DATABASES['default'].copy()
        db_conf['NAME'] = f"{slug}_db"
        settings.DATABASES[slug] = db_conf
    stats = {'students': 0, 'teachers': 0}
    try:
        stats['students'] = Student.objects.using(slug).count()
        stats['teachers'] = Teacher.objects.using(slug).count()
    except: pass
    diff = timezone.now() - school.created_at
    return render(request, 'super_admin/school_detail.html', {'school': school, 'days_active': diff.days + 1, 'stats': stats})

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
def toggle_school_status(request, slug):
    school = get_object_or_404(SchoolClient, slug=slug)
    school.is_active = not school.is_active
    school.save()
    return redirect('school_detail', slug=slug)

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
def update_school_logo(request, school_slug):
    school = get_object_or_404(SchoolClient, slug=school_slug)
    if request.method == "POST" and request.FILES.get('logo'):
        school.logo = request.FILES.get('logo')
        school.save()
    return redirect('school_detail', slug=school_slug)

@user_passes_test(is_super_admin, login_url='/hq-admin/login/')
def create_school(request):
    if request.method == "POST":
        SchoolClient.objects.create(
            name=request.POST.get('name'),
            slug=request.POST.get('slug'),
            school_type=request.POST.get('school_type'),
            db_name=f"{request.POST.get('slug')}_db"
        )
        return redirect('super_admin_dashboard')
    return render(request, 'super_admin/create_school.html')
