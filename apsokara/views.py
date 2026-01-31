from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Student, Teacher, Attendance, SchoolNews
from django.db.models import Count, Q

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
        'classes': classes_data, 'today_date': target_date, 
        'present': p, 'absent': a, 'leave': l, 'total_students': Student.objects.count()
    })

@login_required
def mark_attendance_view(request, class_name, section_name, wing_name):
    if not request.user.is_superuser:
        try:
            teacher = request.user.teacher
            if teacher.assigned_class != class_name or teacher.assigned_section != section_name:
                from django.core.exceptions import PermissionDenied; raise PermissionDenied()
        except:
            from django.core.exceptions import PermissionDenied; raise PermissionDenied()
    today = timezone.now().date()
    students = Student.objects.filter(student_class=class_name, student_section=section_name, wing__iexact=wing_name)
    attendance_data = []
    for s in students:
        record = Attendance.objects.filter(student=s, date=today).first()
        if record: attendance_data.append(record)
        else: attendance_data.append({'student': s, 'status': 'Not Marked'})
    return render(request, 'hq_admin_custom/classroom_detail.html', {
        'attendance_data': attendance_data, 'class_name': class_name, 'section_name': section_name,
        'present': Attendance.objects.filter(student__in=students, date=today, status__iexact='Present').count(),
        'absent': Attendance.objects.filter(student__in=students, date=today, status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(student__in=students, date=today, status__iexact='Leave').count(),
        'total_count': students.count(), 'today_date': today
    })

@login_required
def boys_wing_view(request):
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact='Boys')
    return render(request, 'hq_admin_custom/wing_detail.html', {
        'wing_title': 'BOYS WING HQ', 'wing_slug': 'Boys', 'theme_color': '#1e3a8a',
        'class_sections': students.values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class'),
        'present': Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Leave').count(),
        'total_students': students.count()
    })

@login_required
def girls_wing_view(request):
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact='Girls')
    return render(request, 'hq_admin_custom/wing_detail.html', {
        'wing_title': 'GIRLS WING HQ', 'wing_slug': 'Girls', 'theme_color': '#701a75',
        'class_sections': students.values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class'),
        'present': Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Leave').count(),
        'total_students': students.count()
    })

@login_required
def student_master_list(request):
    query = request.GET.get('q', '')
    wing_filter = request.GET.get('wing', '')
    class_filter = request.GET.get('class', '')
    students_list = Student.objects.all().order_by('student_class', 'full_name')
    if query: students_list = students_list.filter(Q(full_name__icontains=query) | Q(roll_number__icontains=query))
    if wing_filter: students_list = students_list.filter(wing=wing_filter)
    if class_filter: students_list = students_list.filter(student_class=class_filter)
    paginator = Paginator(students_list, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'hq_admin_custom/students_list.html', {
        'page_obj': page_obj, 'wings_list': Student.objects.values_list('wing', flat=True).distinct().order_by('wing'),
        'classes_list': Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class'),
        'selected_wing': wing_filter, 'selected_class': class_filter, 'query': query,
    })

@login_required
def student_profile_view(request, student_id):
    s = get_object_or_404(Student, id=student_id)
    history = Attendance.objects.filter(student=s).order_by('-date')
    t_count = history.count()
    p_count = history.filter(status__iexact='Present').count()
    perc = (p_count / t_count * 100) if t_count > 0 else 0
    return render(request, 'hq_admin_custom/student_profile.html', {
        's': s, 'attendance_history': history, 'present_count': p_count,
        'absent_count': history.filter(status__iexact='Absent').count(),
        'leave_count': history.filter(status__iexact='Leave').count(),
        'total_days': t_count, 'percentage': round(perc, 1),
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

# --- NEWS MANAGER START ---
@login_required
@login_required
def news_manager_view(request):
    today = timezone.now().date()
    if request.method == 'POST':
        content = request.POST.get('content')
        target = request.POST.get('target_role')
        s_date = request.POST.get('start_date')
        e_date = request.POST.get('end_date')
        SchoolNews.objects.create(content=content, target_role=target, start_date=s_date, end_date=e_date)
        return redirect('news_manager')
        n_id = request.POST.get('news_id')
        data = {
            'content': request.POST.get('content'),
            'target_role': request.POST.get('target_role'),
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date')
        }
        if n_id: SchoolNews.objects.filter(id=n_id).update(**data)
        return redirect('news_manager')
    
    # Admin ko sab dikhao taake wo manage kar sake
    active_news = SchoolNews.objects.filter(end_date__gte=today).order_by('-created_at')
    expired_news = SchoolNews.objects.filter(end_date__lt=today).order_by('-end_date')
    return render(request, 'hq_admin_custom/news_manager.html', {'active_news': active_news, 'expired_news': expired_news, 'today': today.strftime('%Y-%m-%d')})

    # Logic: Sirf wahi jo aaj ke din active hon (Date filter)
    all_n = SchoolNews.objects.all().order_by('-created_at')
    active_news = [n for n in all_n if n.start_date <= today <= n.end_date]
    expired_news = [n for n in all_n if n.end_date < today]

    return render(request, 'hq_admin_custom/news_manager.html', {
        'active_news': active_news,
        'expired_news': expired_news,
        'today': today.strftime('%Y-%m-%d')
    })

    # Date logic: Start date aaj ya purani ho, aur End date aaj ya future ki ho
    active_news = SchoolNews.objects.filter(start_date__lte=today, end_date__gte=today).order_by('-created_at')
    upcoming_news = SchoolNews.objects.filter(start_date__gt=today).order_by('start_date')
    expired_news = SchoolNews.objects.filter(end_date__lt=today).order_by('-end_date')

    return render(request, 'hq_admin_custom/news_manager.html', {
        'active_news': active_news,
        'upcoming_news': upcoming_news,
        'expired_news': expired_news,
        'today': today.strftime('%Y-%m-%d')
    })
def delete_news(request, news_id):
    get_object_or_404(SchoolNews, id=news_id).delete()
    return redirect('news_manager')
