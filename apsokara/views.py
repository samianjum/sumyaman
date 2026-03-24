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
    conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3', timeout=20)
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
            conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3', timeout=20)
            c = conn.cursor()
            c.execute("INSERT INTO exams (name, class_group, start_date, end_date) VALUES (?, ?, ?, ?)", 
                      (name, group, s_date, e_date))
            conn.commit()
            conn.close()
    return redirect('exam_window')

@login_required
def delete_exam_view(request, exam_id):
    import sqlite3
    conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3', timeout=20)
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
    conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3', timeout=20)
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



@login_required
def exam_analytics_view(request, exam_id):
    from django.db import connection
    import sqlite3

    # 1. Fetch Exam Details
    conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
    exam = c.fetchone()
    conn.close()

    if not exam:
        return redirect('exam_window')

    # 2. Subject Performance Ranking
    with connection.cursor() as cursor:
        cursor.execute("""            SELECT 
                sub.name as subject_name, 
                AVG(unique_marks.ob_m) as avg_m, 
                MAX(unique_marks.ob_m) as max_m,
                sub.id as subject_id
            FROM (
                SELECT student_id, subject_id, MAX(obtained_marks) as ob_m
                FROM student_marks
                WHERE exam_id = %s AND subject_id NOT IN (0, '', '0')
                GROUP BY student_id, subject_id
            ) as unique_marks
            JOIN apsokara_subject sub ON CAST(unique_marks.subject_id AS TEXT) = CAST(sub.id AS TEXT)
            GROUP BY sub.id
            ORDER BY avg_m DESC""", [exam_id])
        stats = [dict(zip(['subject_name', 'avg_m', 'max_m', 'subject_id'], r)) for r in cursor.fetchall()]

    
    # 3. TOP 3 Students (Deep Data Validation)
    with connection.cursor() as cursor:
        cursor.execute("""            SELECT 
                st.id, st.full_name, st.father_name, st.b_form,
                SUM(m.obtained_marks) as grand_total,
                SUM(m.total_marks) as total_possible,
                (SUM(m.obtained_marks) * 100.0 / NULLIF(SUM(m.total_marks), 0)) as percentage
            FROM apsokara_student st
            JOIN student_marks m ON st.id = m.student_id
            WHERE m.exam_id = %s 
              AND st.student_class = (SELECT class_group FROM exams WHERE id = %s)
            GROUP BY st.id 
            ORDER BY grand_total DESC, percentage DESC
            LIMIT 3""", [exam_id, exam_id])
        toppers = []
        for r in cursor.fetchall():
            toppers.append({
                'student_id': r[0],
                'full_name': r[1],
                'father_name': r[2],
                'b_form': r[3],
                'grand_total': r[4],
                'total_possible': r[5],
                'percentage': round(r[6], 1) if r[6] else 0
            })


    
    
    # 4. Class-Section-Wing Structure with Enhanced Search
    q = request.GET.get('table_q', '').strip()
    wing_f = request.GET.get('table_wing', '')
    
    query = """
        SELECT DISTINCT st.wing, st.student_class, st.student_section
        FROM apsokara_student st
        JOIN student_marks m ON st.id = m.student_id
        WHERE m.exam_id = %s
    """
    params = [exam_id]
    
    if q:
        query += " AND (st.student_class LIKE %s OR st.student_section LIKE %s OR st.wing LIKE %s)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
    if wing_f:
        query += " AND st.wing = %s"
        params.append(wing_f)
        
    query += " ORDER BY st.wing, st.student_class, st.student_section"
    
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        structure = [dict(zip(['wing', 'class', 'section'], r)) for r in cursor.fetchall()]

    # Agar AJAX request hai to sirf table return karein
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'hq_admin_custom/includes/analytics_table.html', {'structure': structure, 'exam': {'id': exam_id}})



    return render(request, 'hq_admin_custom/exam_analytics.html', {
        'exam': exam, 'stats': stats, 'toppers': toppers, 'structure': structure
    })











@login_required
def exam_class_detail_view(request, exam_id, class_name):
    import sqlite3
    conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
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
        SELECT st.id, st.id as student_id, st.full_name, st.roll_number, 
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











@login_required
def exam_subject_analytics_view(request, exam_id, subject_id):
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM apsokara_subject WHERE id = %s", [subject_id])
        res_sub = cursor.fetchone()
        sub_name = res_sub[0] if res_sub else "Subject"
        
        cursor.execute("SELECT name FROM exams WHERE id = %s", [exam_id])
        res_ex = cursor.fetchone()
        ex_name = res_ex[0] if res_ex else "Exam"

    all_students = []
    performance_map = {}
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                st.id, st.id, st.roll_number, st.full_name, st.father_name, st.b_form,
                st.student_class, st.student_section, st.wing,
                m.obtained_marks, m.total_marks,
                t.full_name as teacher_name
            FROM student_marks m
            JOIN apsokara_student st ON m.student_id = st.id
            LEFT JOIN apsokara_teacher t ON m.teacher_id = t.id
            WHERE m.exam_id = %s AND m.subject_id = %s
            ORDER BY m.obtained_marks DESC
        """, [exam_id, subject_id])
        rows = cursor.fetchall()
    
    for r in rows:
        m_obt = float(r[9]) if r[9] is not None else 0
        m_tot = float(r[10]) if r[10] else 100
        perc = (m_obt * 100.0 / m_tot) if m_tot > 0 else 0
        sec_key = f"{r[6]}-{r[7]} ({r[8]})"
        
        s_data = {
            'student_id': r[0], 'roll': r[2], 'name': r[3], 'father': r[4], 'b_form': r[5],
            'class': r[6], 'section': r[7], 'wing': r[8],
            'marks': m_obt, 'total': m_tot, 'perc': perc,
            'teacher': r[11] if r[9] else "Not Assigned",
            'unit': sec_key
        }
        all_students.append(s_data)
        
        if sec_key not in performance_map:
            performance_map[sec_key] = {'percs': [], 'pass': 0, 'total': 0, 'teacher': r[11] if r[10] else 'Not Assigned'}
            performance_map[sec_key] = {'percs': [], 'pass': 0, 'total': 0, 'teacher': r[11] if r[9] else "Not Assigned"}
        
        performance_map[sec_key]['percs'].append(perc)
        performance_map[sec_key]['total'] += 1
        if perc >= 33: performance_map[sec_key]['pass'] += 1

    performance = []
    for sec, data in performance_map.items():
        t_father, t_cnic = "---", "---"
        if data['teacher'] != "Not Assigned":
            with connection.cursor() as cursor:
                cursor.execute("SELECT father_name, cnic FROM apsokara_teacher WHERE full_name = %s", [data['teacher']])
                t_row = cursor.fetchone()
                if t_row: t_father, t_cnic = t_row[0], t_row[1]

        avg_val = sum(data['percs']) / len(data['percs']) if data['percs'] else 0
        performance.append({
            'class_name': sec, 'teacher': data['teacher'], 'father': t_father, 'cnic': t_cnic,
            'avg': round(avg_val, 1),
            'pass_count': data['pass'], 'fail_count': data['total'] - data['pass'],
            'total_count': data['total'],
            'status': "EXCELLENT" if avg_val >= 80 else "GOOD" if avg_val >= 60 else "AVERAGE" if avg_val >= 33 else "POOR",
            'color': "success" if avg_val >= 70 else "warning" if avg_val >= 40 else "danger"
        })

    return render(request, 'hq_admin_custom/exam_subject_analytics.html', {
        'sub_name': sub_name, 'ex_name': ex_name, 'toppers': all_students[:3],
        'all_students': all_students, 'performance': performance, 'exam_id': exam_id, 'sub_id': subject_id
    })







@login_required

@login_required

@login_required

@login_required

@login_required
def view_student_result(request, student_id, exam_id=None, subject_id=None):
    from django.db import connection
    student = get_object_or_404(Student, id=student_id)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT e.id, e.name, e.start_date FROM exams e JOIN student_marks m ON e.id = m.exam_id WHERE m.student_id = %s ORDER BY e.id DESC", [student_id])
        exams_list = [{'id': r[0], 'name': r[1], 'start': r[2]} for r in cursor.fetchall()]

        cursor.execute("""
            SELECT sub.name, e.name as exam_name, m.obtained_marks, m.total_marks, t.full_name as teacher
            FROM student_marks m
            JOIN apsokara_subject sub ON m.subject_id = sub.id
            JOIN exams e ON m.exam_id = e.id
            LEFT JOIN apsokara_teacher t ON m.teacher_id = t.id
            WHERE m.student_id = %s ORDER BY sub.name, e.id ASC
        """, [student_id])
        raw_rows = cursor.fetchall()
        
        subject_depth = {}
        for row in raw_rows:
            s_name, e_name, ob, tot, teacher = row
            if s_name not in subject_depth:
                subject_depth[s_name] = {'history': [], 'teacher': teacher, 'total_ob': 0, 'total_tot': 0}
            p = (ob/tot*100) if tot > 0 else 0
            subject_depth[s_name]['history'].append({'exam': e_name, 'perc': round(p,1)})
            subject_depth[s_name]['total_ob'] += ob
            subject_depth[s_name]['total_tot'] += tot
        
        for s in subject_depth:
            sd = subject_depth[s]
            sd['avg'] = round((sd['total_ob']/sd['total_tot']*100), 1) if sd['total_tot'] > 0 else 0

        all_results = {}
        for ex in exams_list:
            cursor.execute("""
                SELECT sub.name, m.obtained_marks, m.total_marks, t.full_name
                FROM student_marks m
                JOIN apsokara_subject sub ON m.subject_id = sub.id
                LEFT JOIN apsokara_teacher t ON m.teacher_id = t.id
                WHERE m.student_id = %s AND m.exam_id = %s
            """, [student_id, ex['id']])
            sub_marks = []
            pass_count = 0
            fail_count = 0
            for r in cursor.fetchall():
                p_perc = (r[1]/r[2]*100) if r[2] > 0 else 0
                is_pass = p_perc >= 50
                if is_pass: pass_count += 1
                else: fail_count += 1
                sub_marks.append({'name': r[0], 'ob': r[1], 'tot': r[2], 'teacher': r[3], 'perc': round(p_perc,1), 'pass': is_pass})
            
            t_ob = sum(s['ob'] for s in sub_marks)
            t_tot = sum(s['tot'] for s in sub_marks)
            all_results[ex['id']] = {
                'subjects': sub_marks, 'total_ob': t_ob, 'total_tot': t_tot,
                'pass_count': pass_count, 'fail_count': fail_count,
                'perc': round((t_ob/t_tot*100),1) if t_tot > 0 else 0
            }

    return render(request, 'hq_admin_custom/student_result_view.html', {
        'student': student, 'exams': exams_list, 'all_results': all_results, 'subject_depth': subject_depth,
        'exam_trend': [ {'exam': ex['name'], 'perc': all_results[ex['id']]['perc']} for ex in exams_list[::-1] ]
    })
