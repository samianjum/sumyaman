import streamlit as st
import pandas as pd
from db_bridge import fetch_df, execute, get_active_exam_for_class

def render_marks_entry(u):
    st.title("🎯 Mark Entry Portal")
    user_id = u.get('id', 1)
    
    # 1. Assignment Selection
    query = """
        SELECT sa.id, s.name, sa.class_name, sa.section, sa.wing, sa.total_marks, sa.submission_status 
        FROM apsokara_subjectassignment sa 
        JOIN apsokara_subject s ON sa.subject_id = s.id 
        WHERE sa.teacher_id = ?
    """
    assignments = fetch_df(query, (user_id,))
    
    if assignments.empty:
        st.warning("No assignments found.")
        return

    options = [f"{r['class_name']}-{r['section']} ({r['name']}) - {r['wing']}" for _, r in assignments.iterrows()]
    selected_label = st.selectbox("Select Class-Subject", options)
    
    # Finding matching assignment
    asg = assignments.iloc[options.index(selected_label)]

    exam = get_active_exam_for_class(asg['class_name'])
    if not exam: return st.error("No active exam found.")

    # Check Lock Status
    lock_check = fetch_df("SELECT is_locked FROM apsokara_classresultstatus WHERE class_name=? AND section=? AND wing=? AND exam_window_id=?", 
                          (asg['class_name'], asg['section'], asg['wing'], exam['id']))
    is_locked = not lock_check.empty and lock_check.iloc[0]['is_locked'] == 1

    # Header UI
    st.info(f"Exam: {exam['title']} | Status: {asg['submission_status']}")

    if is_locked:
        st.warning("🔒 This result has been published and locked. You can only view it.")
    
    # 2. Total Marks Setting
    t_marks = st.number_input("Set Total Marks", value=asg['total_marks'], disabled=is_locked)

    # 3. Marks Table
    students = fetch_df("""
        SELECT s.id, s.roll_no, s.full_name, IFNULL(m.obtained_marks, 0) as marks
        FROM apsokara_student s
        LEFT JOIN apsokara_mark m ON s.id = m.student_id AND m.subject_assignment_id = ?
        WHERE s.student_class=? AND s.student_section=? AND s.wing=?
    """, (asg['id'], asg['class_name'], asg['section'], asg['wing']))

    # --- FIX START ---
    # Agar is_locked True hai, to hum poore columns ki list ko 'disabled' parameter mein bhejenge
    disabled_cols = ["id", "roll_no", "full_name", "marks"] if is_locked else ["id", "roll_no", "full_name"]
    # --- FIX END ---

    edited_df = st.data_editor(
        students, 
        column_config={"id": None}, 
        disabled=disabled_cols, # Ab list ja rahi hai, error nahi aayega
        use_container_width=True, 
        hide_index=True
    )

    if not is_locked:
        c1, c2 = st.columns(2)
        if c1.button("💾 Save Progress"):
            for _, row in edited_df.iterrows():
                execute("""
                    INSERT INTO apsokara_mark (student_id, subject_assignment_id, obtained_marks, total_marks, exam_type, date_uploaded) 
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP) 
                    ON CONFLICT(student_id, subject_assignment_id) DO UPDATE SET obtained_marks=excluded.obtained_marks
                """, (row['id'], asg['id'], row['marks'], t_marks, exam['title']))
            st.toast("Saved!")

        if c2.button("🚀 SUBMIT SHEET", type="primary"):
            execute("UPDATE apsokara_subjectassignment SET submission_status='Submitted', total_marks=? WHERE id=?", (t_marks, asg['id']))
            st.success("Submitted to Class Teacher!")
            st.rerun()
