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

            /* --- DESKTOP DEFAULT STYLE --- */
            .aps-ticker-container {{
                background: #1b4332; border-top: 3px solid #d4af37; border-bottom: 3px solid #d4af37;
                display: flex; align-items: center; margin: 20px 0; height: 55px; overflow: hidden; position: relative;
            }}
            .aps-label {{
                background: #d4af37; color: #1b4332 !important; padding: 0 25px; height: 100%;
                display: flex; align-items: center; font-weight: 900; font-size: 1.1rem; z-index: 100;
                position: absolute; left: 0; clip-path: polygon(0 0, 85% 0, 100% 100%, 0% 100%);
            }}
            .ticker-content-wrapper {{ display: inline-block; white-space: nowrap; animation: smooth-loop 60s linear infinite; padding-left: 100%; }}
            .moving-text {{ display: inline-flex; font-size: 1.6rem !important; font-weight: 800 !important; color: #FFFFFF !important; }}

            
            /* --- MOBILE OVERRIDE --- */
            @media (max-width: 768px) {
                .aps-ticker-container {
                    background: #1b4332 !important; /* Back to Green */
                    border-bottom: 2px solid #d4af37 !important;
                    margin: 0 !important; 
                    height: 35px !important; /* Slightly bigger */
                    position: relative !important; /* Fixed se hata kar normal kar diya */
                    top: 0 !important;
                    z-index: 1000;
                }
                .aps-label { 
                    display: flex !important; /* Mobile par bhi label dikhao */
                    font-size: 0.6rem !important;
                    padding: 0 10px !important;
                    clip-path: none !important;
                    border-right: 2px solid #1b4332;
                }
                .ticker-content-wrapper { 
                    animation: smooth-loop 30s linear infinite !important; 
                }
                .moving-text { 
                    font-size: 0.9rem !important; 
                    font-weight: 600 !important; 
                    color: #FFFFFF !important; 
                }
            }
}
            </style>
            
            <div class="aps-ticker-container">
                <div class="aps-label">APS UPDATES</div>
                <div class="ticker-content-wrapper">
                    <div class="moving-text">{display_text} &nbsp;&nbsp;&nbsp;&nbsp; ★ &nbsp;&nbsp;&nbsp;&nbsp; {display_text}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
