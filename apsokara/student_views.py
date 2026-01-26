from django.shortcuts import render, get_object_or_404
from .models import Student, Attendance

def student_profile_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendance_history = Attendance.objects.filter(student=student).order_by('-date')
    
    # Yahan hum check kar rahe hain ke field ka naam kya hai taake error na aaye
    c_name = getattr(student, 'current_class', getattr(student, 'class_name', 'N/A'))
    s_name = getattr(student, 'section', 'N/A')
    w_name = getattr(student, 'wing', 'General')

    breadcrumbs = [
        {'name': 'HQ Dashboard', 'url': '/hq-portal/'},
        {'name': f'{w_name} Wing', 'url': f'/hq-portal/attendance/{w_name.lower()}-wing/'},
        {'name': f'Class {c_name}-{s_name}', 'url': f'/hq-portal/attendance/mark/{c_name}/{s_name}/'},
        {'name': student.full_name, 'url': ''},
    ]
    
    context = {
        'student': student,
        'attendance_history': attendance_history,
        'breadcrumbs': breadcrumbs,
        'theme_color': '#1e293b',
        'c_name': c_name, # Template ke liye asani
    }
    return render(request, 'hq_admin_custom/student_profile.html', context)
