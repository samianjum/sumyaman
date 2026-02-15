import json
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Student, Teacher, Attendance, SchoolNews
from django.db.models import Count, Q

@login_required
def hq_dashboard(request):
    from .models import Attendance
    total = Student.objects.count()
    present = Attendance.objects.filter(date=timezone.now().date(), status__iexact='Present').count()
    perc = round((present / total * 100), 1) if total > 0 else 0
    return render(request, 'hq_admin_custom/dashboard.html', {
        'total': total,
        'boys': Student.objects.filter(wing__iexact='Boys').count(),
        'girls': Student.objects.filter(wing__iexact='Girls').count(),
        'faculty_count': Teacher.objects.count(),
        'present': present,
        'perc': perc,
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


import sqlite3
from django.utils import timezone
from .models import Student


@login_required
def exam_window_view(request):
    import sqlite3
    from django.utils import timezone
    conn = sqlite3.connect('db.sqlite3', timeout=20)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    today = timezone.now().date().isoformat()
    c.execute("SELECT * FROM exams ORDER BY created_at DESC")
    exams_raw = c.fetchall()
    
    running_exams = []
    pending_exams = []
    expired_exams = []
    
    for row in exams_raw:
        exam = dict(row)
        sd = str(exam.get('start_date', ''))
        ed = str(exam.get('end_date', ''))
        
        # Calculate Progress
        c.execute("SELECT COUNT(*) FROM exam_subjects WHERE exam_id = ?", (exam['id'],))
        t_sub = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT subject_id) FROM student_marks WHERE exam_id = ?", (exam['id'],))
        u_sub = c.fetchone()[0]
        exam['progress'] = int((u_sub/t_sub)*100) if t_sub > 0 else 0
        exam['uploaded_subs'] = u_sub
        exam['total_subs'] = t_sub

        # Categorization Logic
        if today > ed:
            exam['status_label'], exam['status_class'] = "EXPIRED", "secondary"
            expired_exams.append(exam)
        elif today < sd:
            exam['status_label'], exam['status_class'] = "UPCOMING", "warning"
            pending_exams.append(exam)
        else:
            exam['status_label'], exam['status_class'] = "RUNNING", "success"
            running_exams.append(exam)
            
    distinct_classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')
    conn.close()
    
    return render(request, 'hq_admin_custom/exam_window.html', {
        'running_exams': running_exams,
        'pending_exams': pending_exams,
        'expired_exams': expired_exams,
        'class_list': distinct_classes,
        'today': today
    })


@login_required
def create_exam_view(request):
    if request.method == 'POST':
        name = request.POST.get('exam_name')
        group = request.POST.get('class_group')
        s_date = request.POST.get('start_date')
        e_date = request.POST.get('end_date')
        if name and group and s_date and e_date:
            conn = sqlite3.connect('db.sqlite3', timeout=20)
            c = conn.cursor()
            c.execute("INSERT INTO exams (name, class_group, start_date, end_date) VALUES (?, ?, ?, ?)", 
                      (name, group, s_date, e_date))
            conn.commit()
            conn.close()
    return redirect('exam_window')

@login_required
def delete_exam_view(request, exam_id):
    import sqlite3
    conn = sqlite3.connect('db.sqlite3', timeout=20)
    c = conn.cursor()
    c.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    # Saath hi us exam ke saare marks bhi delete ho jayein (Cleanup)
    c.execute("DELETE FROM exam_marks WHERE exam_id = ?", (exam_id,))
    conn.commit()
    conn.close()
    return redirect('exam_window')



@login_required
def toggle_exam_status(request, exam_id):
    import sqlite3
    from django.shortcuts import redirect
    
    db_path = 'db.sqlite3'
    conn = sqlite3.connect(db_path, timeout=30)
    try:
        conn.execute('PRAGMA journal_mode=WAL;')
        c = conn.cursor()
        
        # Current status check
        c.execute("SELECT is_active FROM exams WHERE id = ?", (exam_id,))
        row = c.fetchone()
        if row:
            # Toggle logic: 1 to 0, 0 to 1
            new_status = 0 if row[0] == 1 else 1
            c.execute("UPDATE exams SET is_active = ? WHERE id = ?", (new_status, exam_id))
            conn.commit()
            print(f"--- SUCCESS: Exam {exam_id} set to {new_status} ---")
    except Exception as e:
        print(f"--- ERROR: {e} ---")
    finally:
        conn.close()
    return redirect('exam_window')



@login_required
def manage_subjects_view(request, exam_id):
    import sqlite3
    conn = sqlite3.connect('db.sqlite3', timeout=20)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if request.method == 'POST':
        sub_name = request.POST.get('subject_name')
        t_marks = request.POST.get('total_marks')
        p_marks = request.POST.get('passing_marks')
        c.execute("INSERT INTO exam_subjects (exam_id, subject_name, total_marks, passing_marks) VALUES (?, ?, ?, ?)", 
                  (exam_id, sub_name, t_marks, p_marks))
        conn.commit()
    
    c.execute("SELECT * FROM exam_subjects WHERE exam_id = ?", (exam_id,))
    subjects = c.fetchall()
    c.execute("SELECT name FROM exams WHERE id = ?", (exam_id,))
    exam_name = c.fetchone()[0]
    conn.close()
    return render(request, 'hq_admin_custom/manage_subjects.html', {'subjects': subjects, 'exam_id': exam_id, 'exam_name': exam_name})

@login_required


@login_required

@login_required

@login_required

@login_required

@login_required

@login_required

@login_required
def exam_analytics_view(request, exam_id):
    from django.db.models import Sum, Avg, Max, Count
    from .models import Student, Teacher
    import sqlite3

    # 1. Fetch Exam (Using raw for the 'exams' table since it's outside standard models)
    import os
    from django.conf import settings
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
    exam = c.fetchone()
    conn.close()

    # 2. STRICT TOP 3 - Using Django ORM for safety
    # We calculate based on student_marks table
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT st.id, st.full_name, st.father_name, st.roll_number, st.student_class, 
                   st.student_section, st.wing,
                   SUM(m.obtained_marks) as grand_total
            FROM apsokara_student st
            JOIN student_marks m ON st.id = m.student_id
            WHERE m.exam_id = %s
            GROUP BY st.id
            ORDER BY grand_total DESC
            LIMIT 3
        """, [exam_id])
        toppers = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    # 3. Subject-wise + ALL Faculty Names (Safe check for field names)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.name as subject_name, 
                   AVG(m.obtained_marks) as avg_m, 
                   MAX(m.obtained_marks) as max_m
            FROM student_marks m
            JOIN apsokara_subject s ON m.subject_id = s.id
            WHERE m.exam_id = %s
            GROUP BY s.id
        """, [exam_id])
        stats_raw = cursor.fetchall()
        
        stats = []
        for row in stats_raw:
            sub_name = row[0]
            # Get all teachers for this subject - Safe filtering
            teachers = Teacher.objects.filter(Q(assignments__subject__name__icontains=sub_name) | Q(assigned_class__icontains=exam['class_group'] if exam else ""))
            teacher_list = ", ".join([t.full_name for t in teachers])
            stats.append({
                'subject_name': sub_name,
                'avg_m': row[1],
                'max_m': row[2],
                'teacher_names': teacher_list if teacher_list else "No Faculty Assigned"
            })

    # 4. Deep Class/Section/Wing Breakdown
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT st.student_class, st.student_section, st.wing,
                   COUNT(DISTINCT st.id) as total_students,
                   AVG(m.obtained_marks) as class_avg
            FROM apsokara_student st
            JOIN student_marks m ON st.id = m.student_id
            WHERE m.exam_id = %s
            GROUP BY st.student_class, st.student_section, st.wing
        """, [exam_id])
        class_breakdown = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    
    # --- PRO ANALYTICS START ---
    radar_labels = []
    radar_scores = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.name, AVG(m.obtained_marks) 
            FROM student_marks m 
            JOIN apsokara_subject s ON m.subject_id = s.id 
            WHERE m.exam_id = %s GROUP BY s.id
        """, [exam_id])
        for row in cursor.fetchall():
            radar_labels.append(row[0])
            radar_scores.append(float(row[1]))

    # Grade Distribution (Simplified for SQLite)
    grade_data = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT st.student_class,
                SUM(CASE WHEN m.obtained_marks >= 80 THEN 1 ELSE 0 END) as A,
                SUM(CASE WHEN m.obtained_marks BETWEEN 50 AND 79 THEN 1 ELSE 0 END) as B,
                SUM(CASE WHEN m.obtained_marks < 50 THEN 1 ELSE 0 END) as F
            FROM student_marks m
            JOIN apsokara_student st ON m.student_id = st.id
            WHERE m.exam_id = %s
            GROUP BY st.student_class
        """, [exam_id])
        grade_data = [dict(zip(['class_name', 'A', 'B', 'F'], r)) for r in cursor.fetchall()]
    # --- PRO ANALYTICS END ---

    context = {         'exam': exam, 'toppers': toppers, 'stats': stats, 'class_breakdown': class_breakdown,         'radar_labels': json.dumps(radar_labels), 'radar_scores': json.dumps(radar_scores),         'grade_data': json.dumps(grade_data)     }
    return render(request, 'hq_admin_custom/exam_analytics.html', context)









@login_required
def exam_class_detail_view(request, exam_id, class_name):
    import sqlite3
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Class-wise subjects stats
    c.execute("""
        SELECT s.name as subject_name, s.id as subject_id,
               AVG(m.obtained_marks) as avg_m, 
               MAX(m.obtained_marks) as max_m,
               COUNT(m.student_id) as total_s
        FROM student_marks m
        JOIN apsokara_subject s ON m.subject_id = s.id
        JOIN apsokara_student st ON m.student_id = st.id
        WHERE m.exam_id = ? AND st.student_class = ?
        GROUP BY s.id
    """, (exam_id, class_name))
    subject_stats = c.fetchall()
    
    # Student List for this class in this exam
    c.execute("""
        SELECT st.id, st.full_name, st.roll_number, 
               SUM(m.obtained_marks) as total_obtained,
               COUNT(m.subject_id) as subs_count
        FROM apsokara_student st
        LEFT JOIN student_marks m ON st.id = m.student_id AND m.exam_id = ?
        WHERE st.student_class = ?
        GROUP BY st.id
    """, (exam_id, class_name))
    students = c.fetchall()
    
    conn.close()
    return render(request, 'hq_admin_custom/exam_class_detail.html', {
        'exam_id': exam_id, 'class_name': class_name, 
        'subject_stats': subject_stats, 'students': students
    })
