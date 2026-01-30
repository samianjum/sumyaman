import sqlite3
import datetime
import streamlit as st

def get_active_news():
    try:
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        today = datetime.date.today().isoformat()
        query = "SELECT content FROM apsokara_schoolnews WHERE is_active=1 AND ? BETWEEN start_date AND end_date"
        cur.execute(query, (today,))
        results = cur.fetchall()
        conn.close()
        
        if results:
            return " | ".join([r[0] for r in results])
        return "📢 Welcome to APS OKARA Portal. System operational."
    except:
        return "📢 APS OKARA Updates: System Boundaries Active."

def render_news_ticker():
    news_text = get_active_news()
    # Classic Navy Blue with Gold border
    st.markdown(f'''
    <div style="background: #1e3a8a; padding: 10px; border-bottom: 3px solid #facc15; overflow: hidden; white-space: nowrap; margin-top: -50px; margin-bottom: 20px;">
        <marquee scrollamount="7" style="color: white; font-weight: bold; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px;">
            {news_text}
        </marquee>
    </div>
    ''', unsafe_allow_html=True)
