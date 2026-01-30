from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Student, Teacher, Attendance
from django.db.models import Count

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
    date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    try:
        target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        target_date = timezone.now().date()
    
    p = Attendance.objects.filter(date=target_date, status__iexact='Present').count()
    a = Attendance.objects.filter(date=target_date, status__iexact='Absent').count()
    l = Attendance.objects.filter(date=target_date, status__iexact='Leave').count()
    
    classes_data = Student.objects.values('student_class', 'student_section', 'wing').annotate(total=Count('id')).order_by('student_class', 'student_section')
    
    return render(request, 'hq_admin_custom/attendance.html', {
        'classes': classes_data, 
        'today_date': target_date, 
        'present': p, 'absent': a, 'leave': l,
        'total_students': Student.objects.count()
    })

@login_required
def mark_attendance_view(request, class_name, section_name, wing_name):
    today = timezone.now().date()
    students = Student.objects.filter(student_class=class_name, student_section=section_name, wing__iexact=wing_name)
    
    attendance_data = []
    for s in students:
        # Check if attendance exists for today, if not, create a dummy object for the template
        record = Attendance.objects.filter(student=s, date=today).first()
        if record:
            attendance_data.append(record)
        else:
            # Create a temporary object (not saved to DB) just to show student info in the list
            attendance_data.append({'student': s, 'status': 'Not Marked'})

    p_count = Attendance.objects.filter(student__in=students, date=today, status__iexact='Present').count()
    a_count = Attendance.objects.filter(student__in=students, date=today, status__iexact='Absent').count()
    l_count = Attendance.objects.filter(student__in=students, date=today, status__iexact='Leave').count()

    return render(request, 'hq_admin_custom/classroom_detail.html', {
        'attendance_data': attendance_data,
        'class_name': class_name, 'section_name': section_name,
        'present': p_count, 'absent': a_count, 'leave': l_count,
        'total_count': students.count(), 'today_date': today
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
        'wing_title': 'BOYS WING HQ', 'wing_slug': 'Boys', 'theme_color': '#1e3a8a', 
        'class_sections': classes, 'present': p, 'absent': a, 'leave': l,
        'total_students': students.count()
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
        'wing_title': 'GIRLS WING HQ', 'wing_slug': 'Girls', 'theme_color': '#701a75', 
        'class_sections': classes, 'present': p, 'absent': a, 'leave': l,
        'total_students': students.count()
    })

@login_required
def student_master_list(request):
    query = request.GET.get('q', '')
    wing_filter = request.GET.get('wing', '')
    class_filter = request.GET.get('class', '')
    students_list = Student.objects.all().order_by('student_class', 'full_name')
    if query:
        from django.db.models import Q
        students_list = students_list.filter(Q(full_name__icontains=query) | Q(roll_number__icontains=query))
    if wing_filter:
        students_list = students_list.filter(wing=wing_filter)
    if class_filter:
        students_list = students_list.filter(student_class=class_filter)
    paginator = Paginator(students_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'hq_admin_custom/students_list.html', {
        'page_obj': page_obj,
        'wings_list': Student.objects.values_list('wing', flat=True).distinct().order_by('wing'),
        'classes_list': Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class'),
        'selected_wing': wing_filter, 'selected_class': class_filter, 'query': query,
    })

@login_required
def student_profile_view(request, student_id):
    s = get_object_or_404(Student, id=student_id)
    history = Attendance.objects.filter(student=s).order_by('-date')
    p_count = history.filter(status__iexact='Present').count()
    a_count = history.filter(status__iexact='Absent').count()
    l_count = history.filter(status__iexact='Leave').count()
    t_count = history.count()
    perc = (p_count / t_count * 100) if t_count > 0 else 0
    return render(request, 'hq_admin_custom/student_profile.html', {
        's': s, 'attendance_history': history, 'present_count': p_count,
        'absent_count': a_count, 'leave_count': l_count, 'total_days': t_count, 'percentage': round(perc, 1),
    })

@login_required
def teacher_profile_view(request, teacher_id):
    t = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'hq_admin_custom/teacher_profile.html', {'t': t})

@login_required
def teacher_master_list(request):
    return render(request, 'hq_admin_custom/teachers_list.html', {'teachers': Teacher.objects.all()})

@login_required
def global_search(request):
    query = request.GET.get('q', '')
    students = Student.objects.filter(full_name__icontains=query) if query else []
    teachers = Teacher.objects.filter(full_name__icontains=query) if query else []
    return render(request, 'hq_admin_custom/search_results.html', {'students': students, 'teachers': teachers, 'query': query})
