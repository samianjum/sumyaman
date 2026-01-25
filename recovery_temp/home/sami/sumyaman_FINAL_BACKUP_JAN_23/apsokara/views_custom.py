from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .models import Student, Attendance, StudentLeave
from datetime import date, timedelta
from django.db.models import Count, Q

@never_cache
def classroom_detail(request, class_name, section):
    if not request.user.is_authenticated or not request.user.is_staff: return redirect('/admin/login/')
    
    c_name, s_name = str(class_name).strip(), str(section).strip()
    today = date.today()
    
    # 1. Analytics Logic (Isolated Range)
    range_type = request.GET.get('range', 'today')
    start_date = today
    if range_type == 'weekly': start_date = today - timedelta(days=7)
    elif range_type == 'monthly': start_date = today - timedelta(days=30)

    # 2. History & Leaves Logic (Independent Date Filters)
    hist_date = request.GET.get('hist_date', str(today))
    leave_date = request.GET.get('leave_date', str(today))

    students = Student.objects.filter(student_class=c_name, student_section=s_name).order_by('full_name')
    if not students.exists(): return redirect('/gatekeeper-v3-okara-786/attendance/')
    
    wing_name = students.first().wing
    s_ids = students.values_list('id', flat=True)

    # Data Context
    history = Attendance.objects.filter(student_id__in=s_ids, date=hist_date).select_related('student')
    leaves_data = StudentLeave.objects.filter(student_id__in=s_ids).order_by('-id')

    for entry in history:
        s = entry.student
        entry.display_id = getattr(s, 'cnic', None) or getattr(s, 'b_form', None) or "N/A"

    context = {
        'class_name': c_name, 'section': s_name, 'wing_name': wing_name,
        'history': history, 'hist_date': hist_date, 'leave_date': leave_date,
        'range': range_type, 'today': today, 'leaves': leaves_data,
        'stats': {
            'total': students.count(),
            'present': Attendance.objects.filter(student_id__in=s_ids, date__range=[start_date, today], status='Present').count(),
            'absent': Attendance.objects.filter(student_id__in=s_ids, date__range=[start_date, today], status='Absent').count(),
            'leave': Attendance.objects.filter(student_id__in=s_ids, date__range=[start_date, today], status='Leave').count(),
        }
    }
    return render(request, 'apsokara/classroom_view.html', context)

# Restoration of Dashboards
def custom_dashboard_index(request): return render(request, 'apsokara/custom_admin.html', {'total_students': Student.objects.count()})
def attendance_dashboard(request): return render(request, 'apsokara/admin_attendance.html', {'today': date.today()})
def boys_wing_dashboard(request): return render_wing(request, 'Boys')
def girls_wing_dashboard(request): return render_wing(request, 'Girls')
def render_wing(request, wing_name):
    classes = Student.objects.filter(wing=wing_name).values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class', 'student_section')
    return render(request, 'apsokara/wing_attendance_base.html', {'wing_name': wing_name, 'class_list': classes})

@never_cache
def student_profile(request, student_id):
    from .models import Student, Attendance, StudentLeave
    from datetime import date
    student = get_object_or_404(Student, id=student_id)
    history = Attendance.objects.filter(student=student).order_by('-date')
    leaves = StudentLeave.objects.filter(student=student).order_by('-id')
    return render(request, 'apsokara/student_profile.html', {
        's': student, 
        'history': history, 
        'leaves': leaves, 
        'today': date.today()
    })
