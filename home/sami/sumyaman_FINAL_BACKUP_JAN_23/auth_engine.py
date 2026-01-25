import sqlite3
import pandas as pd
import streamlit as st

def get_teacher_permissions(u):
    t_id = st.session_state.get('username') or st.session_state.get('user', {}).get('username') or 'admin'
    conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
    
    query = """
        SELECT sa.class_name, sa.section, sub.name as subject_name 
        FROM apsokara_subjectassignment sa
        JOIN apsokara_subject sub ON sa.subject_id = sub.id
        WHERE sa.teacher_id = (SELECT id FROM auth_user WHERE username = ?)
           OR sa.teacher_id = ?
    """
    try:
        assign_df = pd.read_sql_query(query, conn, params=(str(t_id), str(t_id)))
    except:
        assign_df = pd.DataFrame()
    
    conn.close()
    return assign_df, t_id

def filter_permissions(assign_df, sel_cls=None, sel_sec=None):
    if assign_df is None or assign_df.empty:
        return [], [], []
    classes = sorted(assign_df['class_name'].unique())
    sections = sorted(assign_df[assign_df['class_name'] == sel_cls]['section'].unique()) if sel_cls else []
    subjects = sorted(assign_df[(assign_df['class_name'] == sel_cls) & (assign_df['section'] == sel_sec)]['subject_name'].unique()) if sel_cls and sel_sec else []
    return classes, sections, subjects
