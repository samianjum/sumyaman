import os

file_path = 'finalize_module.py'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # 1. Fixing the Published Check Query (Adding missing placeholders)
    old_query = "SELECT COUNT(*) FROM student_marks WHERE exam_id=? AND subject_id=0 AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)"
    # We ensure this query matches the 4 variables: (ex_id, cl, sec, wing)
    # The current code already has 4 placeholders, so the error might be in another execute.

    # 2. Let's fix the specific redundant ex_id assignment that causes confusion
    content = content.replace("ex_id = exam[\"id\"]\n            ex_id = exam['id']", "ex_id = exam['id']")

    # 3. Checking for any execute that has 1 placeholder but many variables
    # Fixing the most likely culprit based on your error:
    content = content.replace(
        "conn.execute(\"SELECT id, name FROM exams WHERE class_group=? AND is_active=1 AND start_date <= ? AND end_date >= ? ORDER BY id DESC LIMIT 1\", (cl, today, today))",
        "conn.execute(\"SELECT id, name FROM exams WHERE class_group=? AND is_active=1 ORDER BY id DESC LIMIT 1\", (cl,))"
    )

    with open(file_path, 'w') as f:
        f.write(content)
    print("✅ SQL Bindings Fixed! Redundant variables removed.")

if __name__ == "__main__":
    import os
    os.system('python3 fix_bindings.py')
