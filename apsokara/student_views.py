from django.shortcuts import render, get_object_or_404
from .models import Student, Attendance

def student_profile_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendance_history = Attendance.objects.filter(student=student).order_by('-date')
    
    
    from .models import SchoolNews
    from django.utils import timezone
    from django.db.models import Q
    today = timezone.now().date()
    # Strict Audience Filter: Role matching + Date Validity
    news = SchoolNews.objects.filter(
        Q(target_role='All') | Q(target_role='Student'),
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-created_at')
    
    context = { 'news': news, 
        'student': student,
        'attendance_history': attendance_history,
        'c_name': student.student_class,
        's_name': student.student_section,
        'w_name': student.wing,
        'p_phone': student.parents_phone,
        'dob': student.dob,
    }
    
    today = timezone.now().date()
    from .models import SchoolNews
    from django.db.models import Q
    news = SchoolNews.objects.filter(
        Q(target_role='All') | Q(target_role='Student'),
        start_date__lte=today,
        end_date__gte=today
    ).order_by('-created_at')
    
    return render(request, 'hq_admin_custom/student_profile.html', context)
