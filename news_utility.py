import pandas as pd
from datetime import date
import streamlit as st
import sqlite3

def get_filtered_news():
    user_role = st.session_state.get('role')
    if not user_role or user_role == 'None':
        return pd.DataFrame()
    user_info = st.session_state.get('user_info', {})
    if user_role == 'Teacher':
        role_to_check = 'Class Teacher' if user_info.get('is_class_teacher') == 1 else 'Subject Teacher'
    else:
        role_to_check = user_role
    roles_list = [role_to_check, 'All']
    today = date.today().strftime('%Y-%m-%d')
    try:
        with sqlite3.connect("db.sqlite3", timeout=30) as conn:
            placeholders = ', '.join(['?'] * len(roles_list))
            query = f"SELECT content FROM apsokara_schoolnews WHERE target_role IN ({placeholders}) AND start_date <= ? AND end_date >= ? ORDER BY created_at DESC"
            return pd.read_sql_query(query, conn, params=tuple(roles_list) + (today, today))
    except:
        return pd.DataFrame(columns=['content'])

def render_news_ticker():
    if not st.session_state.get('logged_in'):
        return
    df = get_filtered_news()
    if not df.empty:
        news_list = df['content'].tolist()
        display_text = " &nbsp;&nbsp;&nbsp;&nbsp; ★ &nbsp;&nbsp;&nbsp;&nbsp; ".join(news_list)
        
        st.markdown(f'''
            <style>
            @keyframes smooth-loop {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}

            .aps-ticker-container {{
                background: #1b4332; 
                border-top: 2px solid #d4af37; 
                border-bottom: 2px solid #d4af37;
                display: flex; 
                align-items: center; 
                margin: 0 !important; 
                margin-top: -20px !important;
                height: 45px; 
                overflow: hidden; 
                position: relative;
                z-index: 999;
            }}
            .aps-label {{
                background: #d4af37; color: #1b4332 !important; padding: 0 20px; height: 100%;
                display: flex; align-items: center; font-weight: 900; font-size: 0.9rem; z-index: 1000;
                position: absolute; left: 0; clip-path: polygon(0 0, 85% 0, 100% 100%, 0% 100%);
            }}
            .ticker-content-wrapper {{ display: inline-block; white-space: nowrap; animation: smooth-loop 40s linear infinite; padding-left: 100%; }}
            .moving-text {{ display: inline-flex; font-size: 1.2rem !important; font-weight: 700 !important; color: #FFFFFF !important; }}

            @media (max-width: 768px) {{
                .aps-ticker-container {{ height: 35px !important; margin-top: -25px !important; }}
                .aps-label {{ font-size: 0.6rem !important; padding: 0 10px !important; }}
                .moving-text {{ font-size: 0.85rem !important; }}
            }}
            </style>
            
            <div class="aps-ticker-container">
                <div class="aps-label">LATEST UPDATES</div>
                <div class="ticker-content-wrapper">
                    <div class="moving-text">{display_text} &nbsp;&nbsp;&nbsp;&nbsp; ★ &nbsp;&nbsp;&nbsp;&nbsp; {display_text}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
