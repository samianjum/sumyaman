from leave_utils import check_on_leave
import sys, os; sys.path.append(os.getcwd()); sys.path.append(os.path.join(os.getcwd(), "apsokara/logic"))
from apsokara.logic.teacher_modules import render_marks_entry
from apsokara.logic.student_modules import render_my_result
from apsokara.logic.class_teacher_modules import render_final_upload
from news_utility import render_news_ticker
import streamlit as st
import base64
import datetime
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from mobile_portal import render_mobile_view

# 1. Page Config
st.set_page_config(page_title="APS OKARA PORTAL", page_icon="/home/sami/Downloads/sami.png", layout="wide", initial_sidebar_state="expanded")

# Top Gap Fix
st.markdown('<style>.block-container {padding-top: 1rem !important;} header {visibility: hidden !important;}</style>', unsafe_allow_html=True)

# PWA Fix
st.markdown("""
    <link rel='manifest' href='./static/app_assets/manifest_v3.json'>
    <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('./static/app_assets/sw.js');
      });
    }
    </script>
""", unsafe_allow_html=True)

render_news_ticker()

# --- LEAVE SYSTEM HELPER FUNCTIONS ---
def check_on_leave(student_id):
    try:
        import sqlite3
        import datetime
        conn = sqlite3.connect('db.sqlite3')
        # ... rest of your code continues here ...

        today = datetime.date.today().isoformat()
        cur = conn.cursor()
        # Naye table 'apsokara_studentleave' se check karna
        query = "SELECT id FROM apsokara_studentleave WHERE student_id=? AND status='Approved' AND ? BETWEEN from_date AND to_date"
        cur.execute(query, (student_id, today))
        res = cur.fetchone()
        conn.close()
        return True if res else False
    except Exception as e:
        return False

def get_pending_count(u):
    try:
        