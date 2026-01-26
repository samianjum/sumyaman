from django.shortcuts import render, get_object_or_404
from .models import Student, Attendance

def student_profile_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendance_history = Attendance.objects.filter(student=student).order_by('-date')
    
    context = {
        'student': student,
        'attendance_history': attendance_history,
        'c_name': student.student_class,
        's_name': student.student_section,
        'w_name': student.wing,
        'p_phone': student.parents_phone,
        'dob': student.dob,
    }
    return render(request, 'hq_admin_custom/student_profile.html', context)
