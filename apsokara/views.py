from sumyaman_pro.router import set_current_db
from django.conf import settings
import sqlite3
import json
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import StudentForm, TeacherForm, SubjectAssignmentForm, SubjectAssignmentFormSet
from super_admin.models import SchoolClient
from .models import Student, Teacher, Attendance, SchoolNews
from django.db.models import Count, Q

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse

class TenantAdminLoginView(LoginView):
    template_name = 'hq_admin_custom/login.html'

    def get_success_url(self):
        # Get school slug from URL
        school_slug = self.request.resolver_match.kwargs.get('school_slug')
        if school_slug:
            return reverse('hq_dashboard', kwargs={'school_slug': school_slug})
        return reverse('hq_dashboard')  # fallback (shouldn't happen)


@login_required
def hq_dashboard(request, school_slug=None):
    current_school = get_object_or_404(SchoolClient, slug=school_slug) if school_slug else None
    if school_slug:
        set_current_db(school_slug)
    from .models import Attendance
    total = Student.objects.count()
    present = Attendance.objects.filter(date=timezone.now().date(), status__iexact='Present').count()
    perc = round((present / total * 100), 1) if total > 0 else 0
    return render(request, 'hq_admin_custom/dashboard.html', {
        'school_slug': school_slug,
        'total': total,
        'boys': Student.objects.filter(wing__iexact='Boys').count(),
        'girls': Student.objects.filter(wing__iexact='Girls').count(),
        'faculty_count': Teacher.objects.count(),
        'present': present,
        'perc': perc,
    })

@login_required
def attendance_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    try:
        target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        target_date = timezone.now().date()
    p = Attendance.objects.filter(date=target_date, status__iexact='Present').count()
    a = Attendance.objects.filter(date=target_date, status__iexact='Absent').count()
    l = Attendance.objects.filter(date=target_date, status__iexact='Leave').count()
    classes_data = Student.objects.values('student_class', 'student_section', 'wing').annotate(total=Count('id')).order_by('student_class', 'student_section')

    is_wing_based = Student.objects.filter(wing__in=['Boys', 'Girls']).exists()
    return render(request, 'hq_admin_custom/attendance.html', {
        'school_slug': school_slug,
        'classes': classes_data, 'today_date': target_date,
        'present': p, 'absent': a, 'leave': l,
        'total_students': Student.objects.count(),
        'is_wing_based': is_wing_based
    })

@login_required
def mark_attendance_view(request, class_name, section_name, wing_name, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    if not request.user.is_superuser:
        try:
            teacher = request.user.teacher
            if teacher.assigned_class != class_name or teacher.assigned_section != section_name:
                from django.core.exceptions import PermissionDenied; raise PermissionDenied()
        except:
            from django.core.exceptions import PermissionDenied; raise PermissionDenied()

    today = timezone.now().date()
    students = Student.objects.filter(student_class=class_name, student_section=section_name, wing__iexact=wing_name)

    if request.method == 'POST':
        for s in students:
            status = request.POST.get(f'status_{s.id}')
            if status:
                Attendance.objects.update_or_create(
                    student=s,
                    date=today,
                    defaults={'status': status}
                )
        return redirect('mark_attendance', class_name=class_name, section_name=section_name, wing_name=wing_name)

    attendance_records = {a.student_id: a for a in Attendance.objects.filter(student__in=students, date=today)}
    attendance_data = [
        attendance_records.get(s.id, {'student': s, 'status': 'Not Marked'})
        for s in students
    ]

    return render(request, 'hq_admin_custom/classroom_detail.html', {'school_slug': school_slug,
        'attendance_data': attendance_data, 'class_name': class_name, 'section_name': section_name, 'wing_name': wing_name,
        'present': Attendance.objects.filter(student__in=students, date=today, status__iexact='Present').count(),
        'absent': Attendance.objects.filter(student__in=students, date=today, status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(student__in=students, date=today, status__iexact='Leave').count(),
        'total_count': students.count(), 'today_date': today
    })


@login_required
def boys_wing_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact='Boys')
    return render(request, 'hq_admin_custom/wing_detail.html', {'school_slug': school_slug,
        'wing_title': 'BOYS WING HQ', 'wing_slug': 'Boys', 'theme_color': '#1e3a8a',
        'class_sections': students.values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class'),
        'present': Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, student__wing__iexact='Boys', status__iexact='Leave').count(),
        'total_students': students.count()
    })

@login_required
def girls_wing_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    today = timezone.now().date()
    students = Student.objects.filter(wing__iexact='Girls')
    return render(request, 'hq_admin_custom/wing_detail.html', {'school_slug': school_slug,
        'wing_title': 'GIRLS WING HQ', 'wing_slug': 'Girls', 'theme_color': '#701a75',
        'class_sections': students.values('student_class', 'student_section').annotate(total=Count('id')).order_by('student_class'),
        'present': Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Present').count(),
        'absent': Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Absent').count(),
        'leave': Attendance.objects.filter(date=today, student__wing__iexact='Girls', status__iexact='Leave').count(),
        'total_students': students.count()
    })

@login_required
def student_master_list(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)

    current_school = get_object_or_404(SchoolClient, slug=school_slug)

    if request.method == 'POST':
        form = StudentForm(request.POST, school_type=current_school.school_type)
        if form.is_valid():
            form.save()
            return redirect('student_master_list', school_slug=school_slug)
        else:
            # Re-render with errors
            students_list = Student.objects.all().order_by('student_class', 'full_name')
            paginator = Paginator(students_list, 50)
            page_obj = paginator.get_page(request.GET.get('page'))
            return render(request, 'hq_admin_custom/students_list.html', {'school_slug': school_slug, 'school_type': current_school.school_type,
                'form': form, 'page_obj': page_obj, 'show_modal': True,
                'wings_list': Student.objects.values_list('wing', flat=True).exclude(wing='None').distinct().order_by('wing'),
                'classes_list': Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class'),
            })

    query = request.GET.get('q', '')
    wing_filter = request.GET.get('wing', '')
    class_filter = request.GET.get('class', '')
    students_list = Student.objects.all().order_by('student_class', 'full_name')
    if query: students_list = students_list.filter(Q(full_name__icontains=query) | Q(roll_number__icontains=query))
    if wing_filter: students_list = students_list.filter(wing=wing_filter)
    if class_filter: students_list = students_list.filter(student_class=class_filter)

    paginator = Paginator(students_list, 50)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'hq_admin_custom/students_list.html', {'school_slug': school_slug, 'school_type': current_school.school_type,
        'form': StudentForm(school_type=current_school.school_type),
        'page_obj': page_obj,
        'wings_list': Student.objects.values_list('wing', flat=True).exclude(wing='None').distinct().order_by('wing'),
        'classes_list': Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class'),
        'selected_wing': wing_filter, 'selected_class': class_filter, 'query': query,
    })

@login_required
def student_profile_view(request,  student_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    s = get_object_or_404(Student, id=student_id)
    history = Attendance.objects.filter(student=s).order_by('-date')
    t_count = history.count()
    p_count = history.filter(status__iexact='Present').count()
    a_count = history.filter(status__iexact='Absent').count()
    l_count = history.filter(status__iexact='Leave').count()
    perc = (p_count / t_count * 100) if t_count > 0 else 0

    t_obt, t_tot = 0, 0  # Default values to prevent UnboundLocalError
    t_obt, t_tot = 0, 0  # Default values to prevent UnboundLocalError
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            # Marks table does not exist yet, setting defaults
            marks_data = (0, 0)
    except Exception:
        marks_data = (0, 0)
        t_obt = marks_data[0] if marks_data and marks_data[0] is not None else 0
        t_tot = marks_data[1] if marks_data and marks_data[1] is not None else 0

    return render(request, 'hq_admin_custom/student_profile.html', {'school_slug': school_slug,
        's': s, 'attendance_history': history, 'present_count': p_count,
        'absent_count': history.filter(status__iexact='Absent').count(),
        'leave_count': history.filter(status__iexact='Leave').count(),
        'total_days': t_count, 'percentage': round(perc, 1), 'total_obtained': t_obt, 'total_possible': t_tot,
    })

@login_required

def teacher_profile_view(request, teacher_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)

    current_school = get_object_or_404(SchoolClient, slug=school_slug)
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher, school_type=current_school.school_type)
        formset = SubjectAssignmentFormSet(request.POST, instance=teacher, prefix='assignments',
                                         form_kwargs={'school_type': current_school.school_type})
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('teacher_profile', school_slug=school_slug, teacher_id=teacher_id)
    else:
        form = TeacherForm(instance=teacher, school_type=current_school.school_type)
        formset = SubjectAssignmentFormSet(instance=teacher, prefix='assignments',
                                         form_kwargs={'school_type': current_school.school_type})

    context = {
        'school_slug': school_slug,
        'teacher': teacher,
        'current_school': current_school,
        'form': form,
        'formset': formset,
    }
    return render(request, 'hq_admin_custom/teacher_profile.html', context)



@login_required

@login_required

@login_required
def teacher_master_list(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)

    current_school = get_object_or_404(SchoolClient, slug=school_slug)
    show_modal = False

    if request.method == 'POST':
        form = TeacherForm(request.POST, school_type=current_school.school_type)
        formset = SubjectAssignmentFormSet(request.POST, prefix='assignments', form_kwargs={'school_type': current_school.school_type})

        if form.is_valid() and formset.is_valid():
            teacher = form.save()
            assignments = formset.save(commit=False)
            for assignment in assignments:
                assignment.teacher = teacher
                assignment.save()
            return redirect('teacher_master_list', school_slug=school_slug)
        else:
            # If validation fails, keep the modal open to show errors
            show_modal = True
    else:
        form = TeacherForm(school_type=current_school.school_type)
        formset = SubjectAssignmentFormSet(prefix='assignments', form_kwargs={'school_type': current_school.school_type})

    context = {
        'school_slug': school_slug,
        'teachers': Teacher.objects.all(),
        'form': form,
        'formset': formset,
        'total_count': Teacher.objects.count(),
        'current_school': current_school,
        'show_modal': show_modal  # Key fix for frontend
    }
    return render(request, 'hq_admin_custom/teachers_list.html', context)
def global_search(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    query = request.GET.get('q', '')
    students = Student.objects.filter(full_name__icontains=query) if query else []
    teachers = Teacher.objects.filter(full_name__icontains=query) if query else []
    return render(request, 'hq_admin_custom/search_results.html', {'school_slug': school_slug, 'students': students, 'teachers': teachers, 'query': query})

# --- NEWS MANAGER START ---

@login_required
def news_manager_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    today = timezone.now().date()
    if request.method == 'POST':
        n_id = request.POST.get('news_id')
        data = {
            'content': request.POST.get('content'),
            'target_role': request.POST.get('target_role'),
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date')
        }
        if n_id:
            SchoolNews.objects.filter(id=n_id).update(**data)
        else:
            SchoolNews.objects.create(**data)
        return redirect('news_manager')

    # Combined logic: Using ORM filters for efficiency
    active_news = SchoolNews.objects.filter(start_date__lte=today, end_date__gte=today).order_by('-created_at')
    upcoming_news = SchoolNews.objects.filter(start_date__gt=today).order_by('start_date')
    expired_news = SchoolNews.objects.filter(end_date__lt=today).order_by('-end_date')

    return render(request, 'hq_admin_custom/news_manager.html', {'school_slug': school_slug,
        'active_news': active_news,
        'upcoming_news': upcoming_news,
        'expired_news': expired_news,
        'today': today.strftime('%Y-%m-%d')
    })
def delete_news(request,  news_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    get_object_or_404(SchoolNews, id=news_id).delete()
    return redirect('news_manager')


from .models import Student


@login_required
def exam_window_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    conn = sqlite3.connect(connection.settings_dict['NAME'], timeout=20)
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

    return render(request, 'hq_admin_custom/exam_window.html', {'school_slug': school_slug,
        'running_exams': running_exams,
        'pending_exams': pending_exams,
        'expired_exams': expired_exams,
        'class_list': distinct_classes,
        'today': today
    })


@login_required
def create_exam_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    if request.method == 'POST':
        name = request.POST.get('exam_name')
        group = request.POST.get('class_group')
        s_date = request.POST.get('start_date')
        e_date = request.POST.get('end_date')
        if name and group and s_date and e_date:
            conn = sqlite3.connect(connection.settings_dict['NAME'], timeout=20)
            c = conn.cursor()
            c.execute("INSERT INTO exams (name, class_group, start_date, end_date) VALUES (?, ?, ?, ?)",
                      (name, group, s_date, e_date))
            conn.commit()
            conn.close()
    return redirect('exam_window')

@login_required
def delete_exam_view(request,  exam_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    conn = sqlite3.connect(connection.settings_dict['NAME'], timeout=20)
    c = conn.cursor()
    c.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    # Saath hi us exam ke saare marks bhi delete ho jayein (Cleanup)
    c.execute("DELETE FROM exam_marks WHERE exam_id = ?", (exam_id,))
    conn.commit()
    conn.close()
    return redirect('exam_window')



@login_required
def toggle_exam_status(request,  exam_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    from django.shortcuts import redirect

    db_path = connection.settings_dict['NAME']
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
    except Exception as e:
        pass
    finally:
        conn.close()
    return redirect('exam_window')



@login_required
def manage_subjects_view(request,  exam_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    conn = sqlite3.connect(connection.settings_dict['NAME'], timeout=20)
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
    return render(request, 'hq_admin_custom/manage_subjects.html', {'school_slug': school_slug, 'subjects': subjects, 'exam_id': exam_id, 'exam_name': exam_name})


@login_required
def delete_assignment_view(request, assignment_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    from .models import SubjectAssignment
    get_object_or_404(SubjectAssignment, id=assignment_id).delete()
    return redirect('subject_manager', school_slug=school_slug)

@login_required
def edit_student_view(request, student_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    student = get_object_or_404(Student, id=student_id)
    current_school = get_object_or_404(SchoolClient, slug=school_slug)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student, school_type=current_school.school_type)
        if form.is_valid():
            form.save()
            return redirect('student_profile', student_id=student.id)
    else:
        form = StudentForm(instance=student, school_type=current_school.school_type)
    return render(request, 'hq_admin_custom/edit_student.html', {'school_slug': school_slug, 'form': form, 'student': student})

@login_required
def delete_student_view(request, student_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    get_object_or_404(Student, id=student_id).delete()
    return redirect('student_master_list', school_slug=school_slug)




@login_required
def exam_analytics_view(request,  exam_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    from django.db import connection

    # 1. Fetch Exam Details
    conn = sqlite3.connect(connection.settings_dict['NAME'])
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
        return render(request, 'hq_admin_custom/includes/analytics_table.html', {'school_slug': school_slug, 'structure': structure, 'exam': {'school_slug': school_slug, 'id': exam_id}})



    return render(request, 'hq_admin_custom/exam_analytics.html', {'school_slug': school_slug,
        'exam': exam, 'stats': stats, 'toppers': toppers, 'structure': structure
    })











@login_required
def exam_class_detail_view(request,  exam_id, class_name, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    conn = sqlite3.connect(connection.settings_dict['NAME'])
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
    return render(request, 'hq_admin_custom/exam_class_detail.html', {'school_slug': school_slug,
        'exam_id': exam_id, 'class_name': class_name,
        'subject_stats': subject_stats, 'students': students
    })











@login_required
def exam_subject_analytics_view(request,  exam_id, subject_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
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

    return render(request, 'hq_admin_custom/exam_subject_analytics.html', {'school_slug': school_slug,
        'sub_name': sub_name, 'ex_name': ex_name, 'toppers': all_students[:3],
        'all_students': all_students, 'performance': performance, 'exam_id': exam_id, 'sub_id': subject_id
    })







@login_required

@login_required

@login_required

@login_required

@login_required
def view_student_result(request,  student_id, exam_id=None, subject_id=None, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
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

    return render(request, 'hq_admin_custom/student_result_view.html', {'school_slug': school_slug,
        'student': student, 'exams': exams_list, 'all_results': all_results, 'subject_depth': subject_depth,
        'exam_trend': [ {'exam': ex['name'], 'perc': all_results[ex['id']]['perc']} for ex in exams_list[::-1] ]
    })



@login_required

def subject_manager_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)

    from .models import Subject, SubjectAssignment, Teacher, Student
    from super_admin.models import SchoolClient
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, render, redirect

    # Get school type from main DB to handle wing logic
    current_school = get_object_or_404(SchoolClient.objects.using('default'), slug=school_slug)
    is_wing_based = current_school.school_type == 'wing-based'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_subject':
            name = request.POST.get('name')
            if name: Subject.objects.get_or_create(name=name.strip().title())

        elif action == 'assign_subject':
            t_id = request.POST.get('teacher_id')
            s_id = request.POST.get('subject_id')
            cl = request.POST.get('class')
            sec = request.POST.get('section')
            # If co-ed, force wing to 'None'
            wg = request.POST.get('wing') if is_wing_based else 'None'
            override = request.POST.get('override') == 'true'

            existing = SubjectAssignment.objects.filter(
                subject_id=s_id, student_class=cl, section=sec, wing=wg
            ).first()

            if existing and not override:
                messages.warning(request, f"Conflict: {existing.subject.name} already assigned to {existing.teacher.full_name} in {cl}-{sec}.")
                request.session['conflict_data'] = {'t_id': t_id, 's_id': s_id, 'cl': cl, 'sec': sec, 'wg': wg}
            else:
                SubjectAssignment.objects.update_or_create(
                    subject_id=s_id, student_class=cl, section=sec, wing=wg,
                    defaults={'teacher_id': t_id}
                )
                messages.success(request, "Assignment updated successfully.")
                if 'conflict_data' in request.session: del request.session['conflict_data']

        elif action == 'delete_assignment':
            a_id = request.POST.get('assignment_id')
            SubjectAssignment.objects.filter(id=a_id).delete()
            messages.info(request, "Assignment removed.")

        return redirect('subject_manager', school_slug=school_slug)

    context = {
        'subjects': Subject.objects.all(),
        'teachers': Teacher.objects.all(),
        'assignments': SubjectAssignment.objects.select_related('teacher', 'subject').all(),
        'conflict_data': request.session.get('conflict_data'),
        'school_slug': school_slug,
        'is_wing_based': is_wing_based,
    }
    return render(request, 'hq_admin_custom/subject_manager.html', context)



from datetime import date
from django.db.models import Count, Q


@login_required
def class_sections_view(request, school_slug, class_name):
    if school_slug:
        set_current_db(school_slug)
    selected_date_str = request.GET.get('date')
    from django.utils import timezone
    selected_date = timezone.now().date()
    if selected_date_str:
        try:
            from datetime import datetime
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    sections = Student.objects.filter(student_class=class_name).values('student_section', 'wing').annotate(total=Count('id')).order_by('student_section')
    total_students = Student.objects.filter(student_class=class_name).count()
    attendance_qs = Attendance.objects.filter(student__student_class=class_name, date=selected_date)

    context = {
        'school_slug': school_slug,
        'class_name': class_name,
        'sections': sections,
        'today_date': timezone.now().date().isoformat(),
        'selected_date': selected_date.isoformat(),
        'total_students': total_students,
        'total_present': attendance_qs.filter(status__iexact='Present').count(),
        'total_absent': attendance_qs.filter(status__iexact='Absent').count(),
        'total_leave': attendance_qs.filter(status__iexact='Leave').count(),
    }
    return render(request, 'hq_admin_custom/section_selection.html', context)

@login_required


@login_required
def school_settings_view(request, school_slug=None):
    from django.contrib.auth.models import User
    from django.contrib import messages
    from django.contrib.auth import authenticate, logout
    import re

    # Terminal Log
    print(f"[ACCESS] Settings page accessed by {request.user.username} for school: {school_slug}")

    school = get_object_or_404(SchoolClient.objects.using('default'), slug=school_slug)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_branding':
            school.name = request.POST.get('school_name')
            if 'logo' in request.FILES:
                school.logo = request.FILES['logo']
            school.save(using='default')
            print(f"[UPDATE] School Identity Changed: {school.name}")
            messages.success(request, "Branding updated successfully!")
            return redirect('school_settings', school_slug=school_slug)

        elif action == 'update_security':
            user = request.user
            current_pass = request.POST.get('current_password')
            new_pass = request.POST.get('new_password')
            confirm_pass = request.POST.get('confirm_password')
            new_username = request.POST.get('username')

            # 1. Verify Current Password
            if not user.check_password(current_pass):
                messages.error(request, "Incorrect current password!")
                print(f"[SECURITY ALERT] Failed credential update attempt by {user.username}")
                return redirect('school_settings', school_slug=school_slug)

            # 2. Server-side Validation (Double Check)
            if new_pass:
                if new_pass != confirm_pass:
                    messages.error(request, "Passwords do not match!")
                    return redirect('school_settings', school_slug=school_slug)

                # Regex Check
                is_valid = (
                    len(new_pass) >= 10 and
                    len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', new_pass)) >= 2 and
                    len(re.findall(r'\d', new_pass)) >= 3
                )

                if not is_valid:
                    messages.error(request, "Password does not meet complexity requirements!")
                    return redirect('school_settings', school_slug=school_slug)

                # 3. Apply Changes & Logout
                user.username = new_username
                user.set_password(new_pass)
                user.save()
                print(f"[SUCCESS] Admin {new_username} updated password and username.")
                logout(request)
                messages.info(request, "Credentials updated. Please login again.")
                return redirect(f'/s/{school_slug}/admin/login/')

            else:
                user.username = new_username
                user.save()
                messages.success(request, "Username updated successfully.")
                return redirect('school_settings', school_slug=school_slug)

    return render(request, 'hq_admin_custom/settings.html', {
        'school_slug': school_slug,
        'current_school': school
    })

from django.contrib.auth import logout
from django.shortcuts import redirect

def tenant_logout(request, school_slug=None):
    logout(request)
    if school_slug:
        return redirect(f'/s/{school_slug}/admin/login/')
    return redirect('/hq-admin/login/')


@login_required
def execute_promotion(request, school_slug=None):
    """Execute class promotion based on exam results."""
    if school_slug:
        set_current_db(school_slug)
    if request.method != 'POST':
        return redirect('promotion_center', school_slug=school_slug)
    exam_id = request.POST.get('exam_id')
    pass_perc = float(request.POST.get('pass_perc', 33))
    if not exam_id:
        messages.error(request, "No exam selected.")
        return redirect('promotion_center', school_slug=school_slug)
    from django.db import connection
    # Get all students who passed (overall percentage >= pass_perc)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT st.id, st.student_class, st.student_section, st.wing,
                   SUM(m.obtained_marks) as obt, SUM(m.total_marks) as tot
            FROM apsokara_student st
            JOIN student_marks m ON st.id = m.student_id
            WHERE m.exam_id = %s AND m.is_locked = 1
            GROUP BY st.id
        """, [exam_id])
        rows = cursor.fetchall()
    promoted = 0
    for row in rows:
        student_id, curr_class, section, wing, obt, tot = row
        obt = float(obt or 0)
        tot = float(tot or 1)
        perc = (obt / tot) * 100
        if perc >= pass_perc:
            # Promote to next class (simple increment)
            try:
                next_class = int(curr_class) + 1
            except:
                next_class = curr_class  # fallback
            Student.objects.filter(id=student_id).update(student_class=str(next_class))
            promoted += 1
    messages.success(request, f"Promoted {promoted} students to next class based on exam results.")
    return redirect('promotion_center', school_slug=school_slug)
