from django.shortcuts import render
from .models import Student, Teacher
from django.db.models import Q

def global_search(request):
    query = request.GET.get('q', '').strip()
    student_results = []
    teacher_results = []
    module_results = []

    if query:
        # 1. Search Students (Name or CNIC)
        student_results = Student.objects.filter(
            Q(full_name__icontains=query) | Q(cnic__icontains=query)
        )[:10]

        # 2. Search Teachers (Name or CNIC)
        teacher_results = Teacher.objects.filter(
            Q(full_name__icontains=query) | Q(cnic__icontains=query)
        )[:10]

        # 3. Smart Module Search (Static links)
        modules = [
            {'name': 'Attendance HQ Portal', 'url': '/hq-portal/attendance/', 'tags': 'mark attendance record'},
            {'name': 'Boys Wing Section', 'url': '/hq-portal/attendance/boys-wing/', 'tags': 'boys male wing'},
            {'name': 'Girls Wing Section', 'url': '/hq-portal/attendance/girls-wing/', 'tags': 'girls female wing'},
            {'name': 'Main Dashboard', 'url': '/hq-portal/', 'tags': 'home dashboard stats'},
        ]
        module_results = [m for m in modules if query.lower() in m['name'].lower() or query.lower() in m['tags']]

    context = {
        'query': query,
        'students': student_results,
        'teachers': teacher_results,
        'modules': module_results,
        'total_found': len(student_results) + len(teacher_results) + len(module_results)
    }
    return render(request, 'hq_admin_custom/search_results.html', context)
