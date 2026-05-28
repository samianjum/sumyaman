import sys

with open('apsokara/views.py', 'r') as f:
    lines = f.readlines()

new_view = """
@login_required
def view_student_result(request, student_id, exam_id=None, subject_id=None):
    from django.db import connection
    student = get_object_or_404(Student, id=student_id)

    with connection.cursor() as cursor:
        # 1. Exams List
        cursor.execute("SELECT DISTINCT e.id, e.name, e.start_date FROM exams e JOIN student_marks m ON e.id = m.exam_id WHERE m.student_id = %s ORDER BY e.id DESC", [student_id])
        exams_list = [{'id': r[0], 'name': r[1], 'start': r[2]} for r in cursor.fetchall()]

        # 2. Attendance Stats (Assuming you have an attendance table)
        # Main approximate kar raha hoon, agar table name different hai to batana
        cursor.execute("SELECT COUNT(*) FROM student_attendance WHERE student_id = %s AND status = 'P'", [student_id])
        presents = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM student_attendance WHERE student_id = %s", [student_id])
        total_days = cursor.fetchone()[0]
        att_perc = round((presents/total_days*100),1) if total_days > 0 else 0

        # 3. Subject-wise History with Class Average
        cursor.execute(\"\"\"
            SELECT sub.id, sub.name, m.obtained_marks, m.total_marks,
            (SELECT AVG(obtained_marks) FROM student_marks WHERE subject_id = sub.id AND exam_id = m.exam_id) as class_avg
            FROM student_marks m
            JOIN apsokara_subject sub ON m.subject_id = sub.id
            WHERE m.student_id = %s ORDER BY sub.name, m.exam_id ASC
        \"\"\", [student_id])
        raw_rows = cursor.fetchall()

        subject_depth = {}
        for row in raw_rows:
            sid, s_name, ob, tot, c_avg = row
            if s_name not in subject_depth:
                subject_depth[s_name] = {'history': [], 'total_ob': 0, 'total_tot': 0, 'total_c_avg': 0, 'count': 0}
            p = (ob/tot*100) if tot > 0 else 0
            ca_p = (c_avg/tot*100) if tot > 0 else 0
            subject_depth[s_name]['history'].append({'perc': round(p,1), 'class_avg': round(ca_p,1)})
            subject_depth[s_name]['total_ob'] += ob
            subject_depth[s_name]['total_tot'] += tot
            subject_depth[s_name]['total_c_avg'] += ca_p
            subject_depth[s_name]['count'] += 1

        # 4. AI Insights Logic
        insights = []
        for s, d in subject_depth.items():
            d['avg'] = round((d['total_ob']/d['total_tot']*100), 1) if d['total_tot'] > 0 else 0
            d['overall_class_avg'] = round(d['total_c_avg']/d['count'], 1) if d['count'] > 0 else 0

            if d['avg'] < d['overall_class_avg'] - 10:
                insights.append(f"{s} is weaker than class average. Teacher focus required.")
            elif d['avg'] > 85:
                insights.append(f"Outstanding performance in {s}.")

        # 5. Detailed Results
        all_results = {}
        for ex in exams_list:
            cursor.execute(\"\"\"
                SELECT sub.name, m.obtained_marks, m.total_marks, t.full_name,
                (SELECT AVG(obtained_marks) FROM student_marks WHERE subject_id = m.subject_id AND exam_id = %s) as c_avg
                FROM student_marks m
                JOIN apsokara_subject sub ON m.subject_id = sub.id
                LEFT JOIN apsokara_teacher t ON m.teacher_id = t.id
                WHERE m.student_id = %s AND m.exam_id = %s
            \"\"\", [ex['id'], student_id, ex['id']])
            sub_marks = []
            for r in cursor.fetchall():
                p_perc = (r[1]/r[2]*100) if r[2] > 0 else 0
                ca_perc = (r[4]/r[2]*100) if r[2] > 0 else 0
                sub_marks.append({
                    'name': r[0], 'ob': r[1], 'tot': r[2], 'teacher': r[3],
                    'perc': round(p_perc,1), 'c_avg': round(ca_perc,1)
                })

            t_ob = sum(s['ob'] for s in sub_marks)
            t_tot = sum(s['tot'] for s in sub_marks)
            all_results[ex['id']] = {
                'subjects': sub_marks, 'total_ob': t_ob, 'total_tot': t_tot,
                'perc': round((t_ob/t_tot*100),1) if t_tot > 0 else 0
            }

    return render(request, 'hq_admin_custom/student_result_view.html', {
        'student': student, 'exams': exams_list, 'all_results': all_results,
        'subject_depth': subject_depth, 'att_perc': att_perc, 'insights': insights
    })
"""

# Apply Patch
new_content = []
for line in lines:
    if "def view_student_result" in line: break
    new_content.append(line)
with open('apsokara/views.py', 'w') as f:
    f.writelines(new_content)
    f.write(new_view)
