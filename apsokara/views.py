from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Student, Teacher, Attendance
from django.db.models import Q

@login_required
def hq_dashboard(request):
    return render(request, 'hq_admin_custom/dashboard.html', {
        'total_students': Student.objects.count(),
        'boys': Student.objects.filter(wing__iexact='Boys').count(),
        'girls': Student.objects.filter(wing__iexact='Girls').count(),
        'faculty_count': Teacher.objects.count(),
    })

@login_required
def student_master_list(request):
    students = Student.objects.all().order_by('student_class', 'student_section')
    return render(request, 'hq_admin_custom/students_list.html', {'students': students})

@login_required
def student_profile_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'hq_admin_custom/student_profile.html', {'s': student})

@login_required
def teacher_master_list(request):
    teachers = Teacher.objects.all().order_by('full_name')
    return render(request, 'hq_admin_custom/teachers_list.html', {'teachers': teachers})

@login_required
def teacher_profile_view(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'hq_admin_custom/teacher_profile.html', {'t': teacher})

@login_required
def attendance_view(request):
    return render(request, 'hq_admin_custom/attendance.html')

@login_required
def boys_wing_view(request):
    return render(request, 'hq_admin_custom/wing_detail.html', {'wing': 'Boys'})

@login_required
def girls_wing_view(request):
    return render(request, 'hq_admin_custom/wing_detail.html', {'wing': 'Girls'})

@login_required
def mark_attendance_view(request, class_name, section_name):
    today = timezone.now().date()
    wing_type = "Boys" if "boys" in request.path.lower() else "Girls"
    students = Student.objects.filter(student_class=class_name, student_section=section_name, wing__iexact=wing_type)
    
    attendance_data = []
    for s in students:
        # Priority 1: Actual status wala record
        record = Attendance.objects.filter(student=s, date=today).exclude(status='').first()
        
        # Priority 2: Agar bhara hua nahi mila, to empty wala ya naya
        if not record:
            record, created = Attendance.objects.get_or_create(student=s, date=today, defaults={'status': ''})
            
        attendance_data.append(record)

    context = {
        "attendance_data": attendance_data,
        "total_count": students.count(),
        "present_count": Attendance.objects.filter(student__in=students, date=today, status__iexact='PRESENT').count(),
        "absent_count": Attendance.objects.filter(student__in=students, date=today, status__iexact='ABSENT').count(),
        "leave_count": Attendance.objects.filter(student__in=students, date=today, status__iexact='LEAVE').count(),
        "selected_date": today.strftime('%Y-%m-%d'),
        "class_name": class_name,
        "section_name": section_name,
        "wing_name": wing_type
    }
    return render(request, "hq_admin_custom/classroom_detail.html", context)

@login_required
def global_search(request):
    query = request.GET.get('q', '')
    return render(request, 'hq_admin_custom/search_results.html', {'query': query})
