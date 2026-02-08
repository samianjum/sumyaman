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
            # Fixed the tuple parameter error here
            params = tuple(roles_list) + (today, today)
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
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
                background: #1b4332 !important; 
                border-top: 2px solid #d4af37 !important; 
                border-bottom: 2px solid #d4af37 !important;
                display: flex !important; 
                align-items: center !important; 
                margin: 10px 0 !important; 
                height: 50px !important; 
                overflow: hidden !important; 
                position: relative !important;
                z-index: 99999 !important;
                visibility: visible !important;
            }}
            .aps-label {{
                background: #d4af37 !important; 
                color: #1b4332 !important; 
                padding: 0 15px !important; 
                height: 100% !important;
                display: flex !important; 
                align-items: center !important; 
                font-weight: 900 !important; 
                font-size: 0.9rem !important;
                position: absolute !important; 
                left: 0 !important; 
                z-index: 100000 !important;
                clip-path: polygon(0 0, 85% 0, 100% 100%, 0% 100%) !important;
            }}
            .ticker-content-wrapper {{ 
                display: inline-block !important; 
                white-space: nowrap !important; 
                animation: smooth-loop 40s linear infinite !important; 
                padding-left: 100% !important; 
            }}
            .moving-text {{ 
                display: inline-flex !important; 
                font-size: 1.1rem !important; 
                font-weight: 700 !important; 
                color: #FFFFFF !important; 
            }}

            @media (max-width: 768px) {{
                .aps-ticker-container {{ 
                    height: 38px !important; 
                    margin-top: 65px !important; /* Mobile view adjust */
                    margin-bottom: 0 !important;
                }}
                .aps-label {{ font-size: 0.65rem !important; padding: 0 8px !important; }}
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
