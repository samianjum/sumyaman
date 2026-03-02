import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
django.setup()

from django.db import connection

exam_id = 5  # Aapke URL ke mutabiq
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT 
            sub.name as subject_name, 
            AVG(unique_marks.ob_m) as avg_m, 
            MAX(unique_marks.ob_m) as max_m,
            sub.id as s_id
        FROM (
            SELECT student_id, subject_id, MAX(obtained_marks) as ob_m
            FROM student_marks
            WHERE exam_id = %s AND subject_id NOT IN (0, '', '0')
            GROUP BY student_id, subject_id
        ) as unique_marks
        JOIN apsokara_subject sub ON CAST(unique_marks.subject_id AS TEXT) = CAST(sub.id AS TEXT)
        GROUP BY sub.id
    """, [exam_id])
    
    rows = cursor.fetchall()
    print("\n--- DEBUG DATA START ---")
    if not rows:
        print("❌ DATABASE SE KOI DATA NAHI MILA! Check if marks exist for exam 5.")
    for r in rows:
        print(f"Subject: {r[0]} | Avg: {r[1]} | Max: {r[2]} | ID: {r[3]}")
    print("--- DEBUG DATA END ---\n")
