import sqlite3
import pandas as pd
from datetime import date
import streamlit as st

def get_filtered_news():
    user_role = st.session_state.get('role', 'All')
    role_to_filter = 'All'
    if 'student' in (user_role or '').lower():
        role_to_filter = 'Student'
    elif 'teacher' in (user_role or '').lower():
        role_to_filter = user_role
    today = date.today().strftime('%Y-%m-%d')
    try:
        with sqlite3.connect("db.sqlite3", timeout=30) as conn:
            query = f"""
                SELECT content FROM apsokara_schoolnews 
                WHERE (target_role = '{role_to_filter}' OR target_role = 'All')
                AND start_date <= '{today}' AND end_date >= '{today}'
                ORDER BY id DESC
            """
            return pd.read_sql(query, conn)
    except:
        return pd.DataFrame()

def render_news_ticker():
    df = get_filtered_news()
    if not df.empty:
        news_list = df['content'].tolist()
        # High-end separator
        full_text = " &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#800000; opacity:0.5;'>◆</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join(news_list)
        
        st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');

            .ticker-container {{
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(128, 0, 0, 0.1);
                border-radius: 12px;
                display: flex;
                align-items: center;
                padding: 8px 0;
                margin: 15px 0;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.03);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}

            .ticker-badge {{
                background: #800000;
                color: white;
                padding: 5px 15px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-left: 10px;
                border-radius: 8px;
                z-index: 2;
                box-shadow: 2px 0 10px rgba(128, 0, 0, 0.2);
                animation: pulse-red 2s infinite;
            }}

            @keyframes pulse-red {{
                0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(128, 0, 0, 0.4); }}
                70% {{ transform: scale(1.02); box-shadow: 0 0 0 10px rgba(128, 0, 0, 0); }}
                100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(128, 0, 0, 0); }}
            }}

            .ticker-viewport {{
                flex-grow: 1;
                overflow: hidden;
                display: flex;
            }}

            .ticker-move {{
                display: inline-block;
                white-space: nowrap;
                padding-left: 100%;
                animation: ticker-swipe 40s linear infinite;
                font-size: 15px;
                color: #2D3748;
                font-weight: 500;
            }}

            @keyframes ticker-swipe {{
                0% {{ transform: translateX(0); }}
                100% {{ transform: translateX(-100%); }}
            }}

            .ticker-container:hover .ticker-move {{
                animation-play-state: paused;
            }}
            </style>
            
            <div class="ticker-container">
                <div class="ticker-badge">Live Update</div>
                <div class="ticker-viewport">
                    <div class="ticker-move">
                        {full_text} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ◆ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {full_text}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
