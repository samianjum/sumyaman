from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Teacher
from django.db.models import Q

@login_required
def teacher_master_list(request):
    query = request.GET.get('q', '').strip()
    teachers = Teacher.objects.all().order_by('full_name')
    
    if query:
        teachers = teachers.filter(
            Q(full_name__icontains=query) | 
            Q(employee_id__icontains=query) | 
            Q(phone_number__icontains=query)
        )
    
    return render(request, 'hq_admin_custom/teachers_list.html', {
        'teachers': teachers,
        'query': query,
        'total_count': teachers.count()
    })

@login_required
def teacher_profile_view(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    return render(request, 'hq_admin_custom/teacher_profile.html', {'t': teacher})
