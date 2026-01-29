from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Student, Teacher, Attendance
from django.db.models import Count, Q

@login_required
def hq_dashboard(request):
    return render(request, 'hq_admin_custom/dashboard.html', {
        'total_students': Student.objects.count(),
        'boys': Student.objects.filter(wing__iexact='Boys').count(),
        'girls': Student.objects.filter(wing__iexact='Girls').count(),
        'faculty_count': Teacher.objects.count(),
    })

@login_required
def attendance_view(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
    else:
        target_date = timezone.now().date()

    presents = Attendance.objects.filter(date=target_date, status__iexact='Present').count()
    absents = Attendance.objects.filter(date=target_date, status__iexact='Absent').count()
    leaves = Attendance.objects.filter(date=target_date, status__iexact='Leave').count()
    
    classes_data = Student.objects.values('student_class', 'student_section', 'wing').annotate(
        total=Count('id')
    ).order_by('student_class', 'student_section')
    
    return render(request, 'hq_admin_custom/attendance.html', {
        'classes': classes_data,
        'today_date': target_date,
        'present': presents,
        'absent': absents,
        'leave': leaves,
        'total_marked': presents + absents + leaves,
        'total_students': Student.objects.count()
    })

@login_required
def boys_wing_view(request):
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact='Boys')
    classes = students.values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class')
    
    p = Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Present').count()
    a = Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Absent').count()
    l = Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Leave').count()

    return render(request, 'hq_admin_custom/wing_detail.html', {
        'wing_title': 'BOYS WING HQ',
        'theme_color': '#1e3a8a',
        'class_sections': classes,
        'present': p,
        'absent': a,
        'leave': l,
        'total_students': students.count(),
        'today_date': today
    })

@login_required
def girls_wing_view(request):
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact='Girls')
    classes = students.values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class')
    
    p = Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Present').count()
    a = Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Absent').count()
    l = Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Leave').count()

    return render(request, 'hq_admin_custom/wing_detail.html', {
        'wing_title': 'GIRLS WING HQ',
        'theme_color': '#701a75',
        'class_sections': classes,
        'present': p,
        'absent': a,
        'leave': l,
        'total_students': students.count(),
        'today_date': today
    })

@login_required
def student_master_list(request):
    return render(request, 'hq_admin_custom/students_list.html', {
        'students': Student.objects.all().order_by('student_class')
    })

@login_required
def student_profile_view(request, student_id):
    s = get_object_or_404(Student, id=student_id)
    history = Attendance.objects.filter(student=s).order_by('-date')
    return render(request, 'hq_admin_custom/student_profile.html', {
        's': s, 
        'attendance_history': history
    })

@login_required
def teacher_master_list(request):
    return render(request, 'hq_admin_custom/teachers_list.html', {
        'teachers': Teacher.objects.all()
    })

@login_required
def teacher_profile_view(request, teacher_id):
    t = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'hq_admin_custom/teacher_profile.html', {'t': t})

@login_required
def mark_attendance_view(request, class_name, section_name):
    today = timezone.now().date()
    students = Student.objects.filter(student_class=class_name, student_section=section_name)
    attendance_data = []
    for s in students:
        record, _ = Attendance.objects.get_or_create(student=s, date=today)
        attendance_data.append(record)
    return render(request, 'hq_admin_custom/classroom_detail.html', {
        'attendance_data': attendance_data, 
        'class_name': class_name, 
        'section_name': section_name
    })

@login_required
def global_search(request):
    return render(request, 'hq_admin_custom/search_results.html')
