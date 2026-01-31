from django.shortcuts import render
from .models import Student, Attendance
from django.contrib.auth.models import User
from datetime import date

def hq_dashboard(request):
    today = date.today()
    
    # Real data from Database
    total_students = Student.objects.count()
    faculty_count = User.objects.count()
    
    # Today's attendance filter
    today_att = Attendance.objects.filter(date=today)
    present = today_att.filter(status__iexact='PRESENT').count()
    
    # Calculate real percentage
    perc = round((present / total_students * 100), 1) if total_students > 0 else 0
    
    # Get last 5 real attendance entries for the table
    recent_activity = Attendance.objects.select_related('student').order_by('-id')[:5]
    
    # Real Wing counts
    boys_count = Student.objects.filter(wing__iexact='BOYS').count()
    girls_count = Student.objects.filter(wing__iexact='GIRLS').count()

    
    today = timezone.now().date()
    from .models import SchoolNews
    from django.db.models import Q
    user_role = 'All'
    if hasattr(request.user, 'teacher'):
        user_role = request.user.teacher.role # Assuming role field exists
    
    news = SchoolNews.objects.filter(
        Q(target_role='All') | Q(target_role=user_role) | Q(target_role__icontains='Teacher'),
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-created_at')
    
    
    from .models import SchoolNews
    from django.utils import timezone
    from django.db.models import Q
    today = timezone.now().date()
    # Strict Audience Filter: Role matching + Date Validity
    news = SchoolNews.objects.filter(
        Q(target_role='All') | Q(target_role='Class Teacher'),
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-created_at')
    
    context = { 'news': news,  'news': news, 
        'total': total_students,
        'faculty_count': faculty_count,
        'present': present,
        'perc': perc,
        'recent_activity': recent_activity,
        'boys': boys_count,
        'girls': girls_count,
        'today': today,
    }
    return render(request, 'hq_admin_custom/dashboard.html', context)
