from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student, Attendance, Teacher
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator

@login_required
def hq_dashboard(request):
    return render(request, 'hq_admin_custom/dashboard.html', {
        'total_students': Student.objects.count(),
    })

@login_required
def attendance_view(request):
    today = timezone.now().date()
    context = { 
        'breadcrumbs': [{'name': 'Attendance HQ', 'url': '/hq-portal/attendance/'}],
        'total_students': Student.objects.count(),
        'present': Attendance.objects.filter(date=today, status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, status__iexact='Leave').count(),
        'today_date': today,
    }
    return render(request, 'hq_admin_custom/attendance.html', context)

def get_wing_data(wing_name):
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact=wing_name)
    class_sections = students.values('student_class', 'student_section').annotate(
        total=Count('id')
    ).order_by('student_class', 'student_section')
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

@login_required
def mark_attendance_view(request, class_name, section_name):
    today = timezone.now().date()
    date_str = request.GET.get('date')
    selected_date = date_str if date_str else today.strftime('%Y-%m-%d')
    wing_type = 'BOYS' if 'boys-wing' in request.path or 'boys' in request.META.get('HTTP_REFERER', '').lower() else 'GIRLS'
    students = Student.objects.filter(student_class=class_name, student_section=section_name, wing__iexact=wing_type)
    teacher_obj = Teacher.objects.filter(assigned_wing__iexact=wing_type, assigned_class=class_name, assigned_section=section_name, is_class_teacher=True).first()
    class_teacher = teacher_obj.full_name if teacher_obj else "Not Assigned"
    attendance_records = Attendance.objects.filter(student__student_class=class_name, student__student_section=section_name, student__wing__iexact=wing_type, date=selected_date)
    return render(request, 'hq_admin_custom/classroom_detail.html', {
        'class_name': class_name, 'section_name': section_name, 'wing_name': wing_type.title(), 'class_teacher': class_teacher,
        'selected_date': selected_date, 'total_count': students.count(), 'present_count': attendance_records.filter(status__iexact='Present').count(),
        'absent_count': attendance_records.filter(status__iexact='Absent').count(), 'leave_count': attendance_records.filter(status__iexact='Leave').count(),
        'attendance_data': attendance_records, 'theme_color': '#1e293b'
    })

@login_required
def student_master_list(request):
    student_qs = Student.objects.all().order_by('student_class', 'roll_number')
    wing_filter = request.GET.get('wing')
    search_query = request.GET.get('search')
    if wing_filter: student_qs = student_qs.filter(wing__iexact=wing_filter)
    if search_query: student_qs = student_qs.filter(Q(full_name__icontains=search_query) | Q(roll_number__icontains=search_query) | Q(b_form__icontains=search_query))
    paginator = Paginator(student_qs, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'hq_admin_custom/students_list.html', {'page_obj': page_obj, 'total_count': student_qs.count()})

@login_required
def teacher_master_list(request):
    return render(request, 'hq_admin_custom/teachers_list.html', {'teachers': Teacher.objects.all()})

@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    s_res = Student.objects.filter(Q(full_name__icontains=query) | Q(roll_number__icontains=query))[:10] if query else []
    t_res = Teacher.objects.filter(Q(full_name__icontains=query))[:10] if query else []
    return render(request, 'hq_admin_custom/search_results.html', {'query': query, 'students': s_res, 'teachers': t_res, 'total_found': len(s_res) + len(t_res)})

@login_required
def student_profile_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    att_qs = Attendance.objects.filter(student=student).order_by('-date')
    s_date = request.GET.get('start_date')
    e_date = request.GET.get('end_date')
    if s_date and e_date: att_qs = att_qs.filter(date__range=[s_date, e_date])
    
    total = att_qs.count()
    p = att_qs.filter(status__iexact='Present').count()
    ratio = (p / total * 100) if total > 0 else 0
    
    return render(request, 'hq_admin_custom/student_profile.html', {
        's': student, 'total_days': total, 'presents': p, 
        'absents': att_qs.filter(status__iexact='Absent').count(),
        'leaves': att_qs.filter(status__iexact='Leave').count(),
        'percentage': round(ratio, 1), 'attendance_history': att_qs,
        'start_date': s_date, 'end_date': e_date
    })
