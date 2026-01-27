
def get_breadcrumbs(path_list):
    crumbs = []
    if 'attendance' in path_list:
        crumbs.append({'name': 'Attendance HQ', 'url': '/hq-portal/attendance/'})
    return crumbs

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Student, Attendance, Teacher
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
    context = { 'breadcrumbs': [{'name': 'Attendance HQ', 'url': '/hq-portal/attendance/'}],
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


@login_required
def mark_attendance_view(request, class_name, section_name):
    today = timezone.now().date()
    # Get date from URL query or use today
    date_str = request.GET.get('date')
    selected_date = date_str if date_str else today.strftime('%Y-%m-%d')
    
    
    
    
    
    
    # Auto-detect wing from URL path to prevent mixing
    wing_type = 'BOYS' if 'boys-wing' in request.path or 'boys' in request.META.get('HTTP_REFERER', '').lower() else 'GIRLS'
    students = Student.objects.filter(
        student_class=class_name, 
        student_section=section_name,
        wing__iexact=wing_type
    )
    first_student = students.first()
    wing_name = first_student.wing if first_student else "Unknown"
    
    # Database Search for the actual Class Teacher
    teacher_obj = Teacher.objects.filter(
        assigned_wing__iexact=wing_type,
        assigned_class=class_name, 
        assigned_section=section_name, 
        is_class_teacher=True
    ).first()
    
    class_teacher = teacher_obj.full_name if teacher_obj else "Not Assigned"
    
    attendance_records = Attendance.objects.filter(




        student__student_class=class_name, 
        student__student_section=section_name, student__wing__iexact=wing_type,
        date=selected_date
    )

    context = { 'breadcrumbs': [{'name': 'Attendance HQ', 'url': '/hq-portal/attendance/'}],
        'class_name': class_name,
        'section_name': section_name,
        'wing_name': wing_name, 'class_teacher': class_teacher, 'breadcrumbs': [{'name': 'Attendance HQ', 'url': '/hq-portal/attendance/'}, {'name': wing_name + ' Wing', 'url': '/hq-portal/attendance/' + wing_name.lower() + '-wing/'}, {'name': f'{class_name}-{section_name}', 'url': ''} ],
        'selected_date': selected_date,

        'class_name': class_name,
        'section_name': section_name,
        'selected_date': selected_date,
        'total_count': students.count(),
        'present_count': attendance_records.filter(status__iexact='Present').count(),
        'absent_count': attendance_records.filter(status__iexact='Absent').count(),
        'leave_count': attendance_records.filter(status__iexact='Leave').count(),
        'attendance_data': attendance_records,
        'theme_color': '#1e293b'
    }
    return render(request, 'hq_admin_custom/classroom_detail.html', context)


def global_search(request):
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    student_results = []
    teacher_results = []
    module_results = []

    if query:
        # 1. Student Search (Uses Student fields)
        student_results = Student.objects.filter(
            Q(full_name__icontains=query) | Q(roll_number__icontains=query) | Q(b_form__icontains=query)
        )[:10]

        # 2. Teacher Search (Uses Teacher fields - NO roll_number here)
        teacher_results = Teacher.objects.filter(
            Q(full_name__icontains=query) | Q(cnic__icontains=query)
        )[:10]

        # 3. Quick Links
        modules = [
            {'name': 'Attendance HQ', 'url': '/hq-portal/attendance/', 'tags': 'mark attendance'},
            {'name': 'Boys Wing', 'url': '/hq-portal/attendance/boys-wing/', 'tags': 'boys'},
            {'name': 'Girls Wing', 'url': '/hq-portal/attendance/girls-wing/', 'tags': 'girls'},
            {'name': 'Dashboard', 'url': '/hq-portal/', 'tags': 'home dashboard'},
        ]
        module_results = [m for m in modules if query.lower() in m['name'].lower() or query.lower() in m['tags']]

    context = {
        'query': query,
        'students': student_results,
        'teachers': teacher_results,
        'modules': module_results,
        'total_found': len(student_results) + len(teacher_results) + len(module_results),
        'breadcrumbs': [{'name': 'Search', 'url': ''}]
    }
    return render(request, 'hq_admin_custom/search_results.html', context)

def student_master_list(request):
    from .models import Student
    students = Student.objects.all().order_by('student_class', 'roll_number')
    return render(request, 'hq_admin_custom/students_list.html', {'students': students})
