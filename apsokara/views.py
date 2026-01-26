from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Student, Attendance
from django.utils import timezone
from django.db.models import Count

@login_required
def hq_dashboard(request):
    return render(request, 'hq_admin_custom/dashboard.html', {
        'total_students': Student.objects.count(),
    })

@login_required
def attendance_view(request):
    today = timezone.now().date()
    context = {
        'total_students': Student.objects.count(),
        'present': Attendance.objects.filter(date=today, status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, status__iexact='Leave').count(),
        'today_date': today,
    }
    return render(request, 'hq_admin_custom/attendance.html', context)

def get_wing_data(wing_name):
    today = timezone.now().date()
    # Filter by wing
    students = Student.objects.filter(wing__iexact=wing_name)
    
    # Corrected Field Names: student_class and student_section
    class_sections = students.values('student_class', 'student_section').annotate(
        total=Count('id')
    ).order_by('student_class', 'student_section')

    
    
    # Logical Addition: Finding classes with high absence (Alert System)
    critical_classes = []
    for cs in class_sections:
        absent_count = Attendance.objects.filter(
            date=today, 
            student__wing__iexact=wing_name,
            student__student_class=cs['student_class'],
            student__student_section=cs['student_section'],
            status__iexact='Absent'
        ).count()
        if absent_count > 0:
            cs['absent_count'] = absent_count
            critical_classes.append(cs)

    return {
        'total_students': students.count(),
        'present': Attendance.objects.filter(date=today, student__wing__iexact=wing_name, status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, student__wing__iexact=wing_name, status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, student__wing__iexact=wing_name, status__iexact='Leave').count(),
        'class_sections': class_sections,
        'critical_classes': sorted(critical_classes, key=lambda x: x['absent_count'], reverse=True)[:3]
    }

@login_required
def boys_wing_view(request):
    context = get_wing_data('Boys')
    context.update({'wing_title': 'Boys Wing', 'theme_color': '#2F3E46'})
    return render(request, 'hq_admin_custom/wing_detail.html', context)

@login_required
def girls_wing_view(request):
    context = get_wing_data('Girls')
    context.update({'wing_title': 'Girls Wing', 'theme_color': '#52796F'})
    return render(request, 'hq_admin_custom/wing_detail.html', context)
