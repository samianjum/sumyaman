from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Student, Teacher, Attendance
from django.utils import timezone
from django.db.models import Count

@login_required
def hq_dashboard(request):
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
    }
    return render(request, 'hq_admin_custom/dashboard.html', context)

@login_required
def attendance_view(request):
    today = timezone.now().date()
    
    # Global Stats
    total_students = Student.objects.count()
    attendance_today = Attendance.objects.filter(date=today)
    
    present_today = attendance_today.filter(status__iexact='Present').count()
    absent_today = attendance_today.filter(status__iexact='Absent').count()
    leave_today = attendance_today.filter(status__iexact='Leave').count()

    context = {
        'total_students': total_students,
        'present': present_today,
        'absent': absent_today,
        'leave': leave_today,
        'today_date': today,
    }
    return render(request, 'hq_admin_custom/attendance.html', context)
