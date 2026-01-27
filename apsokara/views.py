from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student, Attendance, Teacher
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator

# ... (Previous views: hq_dashboard, attendance_view, get_wing_data, etc. stay the same) ...
# I am including the full content to ensure no AttributeErrors occur again.

@login_required
def hq_dashboard(request):
    return render(request, 'hq_admin_custom/dashboard.html', {'total_students': Student.objects.count()})

@login_required
def attendance_view(request):
    today = timezone.now().date()
    return render(request, 'hq_admin_custom/attendance.html', {
        'total_students': Student.objects.count(),
        'present': Attendance.objects.filter(date=today, status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, status__iexact='Leave').count(),
        'today_date': today,
    })

def get_wing_data(wing_name):
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact=wing_name)
    class_sections = students.values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class', 'student_section')
    return {
        'total_students': students.count(),
        'present': Attendance.objects.filter(date=today, student__wing__iexact=wing_name, status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, student__wing__iexact=wing_name, status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, student__wing__iexact=wing_name, status__iexact='Leave').count(),
        'class_sections': class_sections
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
    wing_type = 'BOYS' if 'boys' in request.path.lower() else 'GIRLS'
    students = Student.objects.filter(student_class=class_name, student_section=section_name, wing__iexact=wing_type)
    attendance_records = Attendance.objects.filter(student__student_class=class_name, student__date=today)
    return render(request, 'hq_admin_custom/classroom_detail.html', {'students': students, 'today': today})

# --- TAGRA STUDENT LIST VIEW ---
@login_required
def student_master_list(request):
    student_qs = Student.objects.all().order_by('wing', 'student_class', 'roll_number')
    
    # Advanced Search & Filter
    q = request.GET.get('q', '').strip()
    wing = request.GET.get('wing', '')
    s_class = request.GET.get('class', '')
    
    if q:
        student_qs = student_qs.filter(
            Q(full_name__icontains=q) | 
            Q(roll_number__icontains=q) | 
            Q(b_form__icontains=q) |
            Q(father_name__icontains=q)
        )
    
    if wing:
        student_qs = student_qs.filter(wing__iexact=wing)
    if s_class:
        student_qs = student_qs.filter(student_class__iexact=s_class)

    # Metadata for filter dropdowns
    wings_list = Student.objects.values_list('wing', flat=True).distinct()
    classes_list = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')

    paginator = Paginator(student_qs, 25) # 25 per page for speed
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'hq_admin_custom/students_list.html', {
        'page_obj': page_obj,
        'total_count': student_qs.count(),
        'wings_list': wings_list,
        'classes_list': classes_list,
        'query': q,
        'selected_wing': wing,
        'selected_class': s_class
    })

@login_required
def student_profile_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    att_qs = Attendance.objects.filter(student=student).order_by('-date')
    s_date, e_date = request.GET.get('start_date'), request.GET.get('end_date')
    if s_date and e_date: att_qs = att_qs.filter(date__range=[s_date, e_date])
    total = att_qs.count()
    p = att_qs.filter(status__iexact='Present').count()
    return render(request, 'hq_admin_custom/student_profile.html', {
        's': student, 'total_days': total, 'presents': p, 
        'absents': att_qs.filter(status__iexact='Absent').count(),
        'leaves': att_qs.filter(status__iexact='Leave').count(),
        'percentage': round((p/total*100), 1) if total > 0 else 0, 
        'attendance_history': att_qs, 'start_date': s_date, 'end_date': e_date
    })

@login_required
def teacher_master_list(request):
    return render(request, 'hq_admin_custom/teachers_list.html', {'teachers': Teacher.objects.all()})

@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    s_res = Student.objects.filter(Q(full_name__icontains=query) | Q(roll_number__icontains=query))[:10] if query else []
    return render(request, 'hq_admin_custom/search_results.html', {'query': query, 'students': s_res, 'total_found': len(s_res)})
