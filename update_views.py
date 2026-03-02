import sys

with open('apsokara/views.py', 'r') as f:
    lines = f.readlines()

new_view = """
@login_required
def view_student_result(request, student_id, exam_id=None, subject_id=None):
    from django.db import connection
    student = get_object_or_404(Student, id=student_id)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT e.id, e.name, e.start_date FROM exams e JOIN student_marks m ON e.id = m.exam_id WHERE m.student_id = %s ORDER BY e.id DESC", [student_id])
        exams_list = [{'id': r[0], 'name': r[1], 'start': r[2]} for r in cursor.fetchall()]

        cursor.execute(\"\"\"
            SELECT sub.name, e.name as exam_name, m.obtained_marks, m.total_marks, t.full_name as teacher
            FROM student_marks m
            JOIN apsokara_subject sub ON m.subject_id = sub.id
            JOIN exams e ON m.exam_id = e.id
            LEFT JOIN apsokara_teacher t ON m.teacher_id = t.id
            WHERE m.student_id = %s ORDER BY sub.name, e.id ASC
        \"\"\", [student_id])
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
            cursor.execute(\"\"\"
                SELECT sub.name, m.obtained_marks, m.total_marks, t.full_name
                FROM student_marks m
                JOIN apsokara_subject sub ON m.subject_id = sub.id
                LEFT JOIN apsokara_teacher t ON m.teacher_id = t.id
                WHERE m.student_id = %s AND m.exam_id = %s
            \"\"\", [student_id, ex['id']])
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
        'student': student, 'exams': exams_list, 'all_results': all_results, 'subject_depth': subject_depth
    })
"""

new_content = []
for line in lines:
    if "def view_student_result" in line: break
    new_content.append(line)
with open('apsokara/views.py', 'w') as f:
    f.writelines(new_content)
    f.write(new_view)
