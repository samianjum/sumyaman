import streamlit as st
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_news_db():
    conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3', check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def render_news_ticker():
    if 'user_info' not in st.session_state or st.session_state.user_info is None:
        return

    try:
        with get_news_db() as conn:
            res = conn.execute("SELECT content FROM apsokara_schoolnews ORDER BY id DESC LIMIT 5").fetchall()
        
        if res:
            ticker_text = " &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#800000;'>★</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join([item[0] for item in res])
            
            st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@600;800&display=swap');

            .aps-vibrant-ticker {{
                background: #f8fafc;
                border-top: 1px solid #e2e8f0;
                border-bottom: 3px solid #800000;
                padding: 14px 0;
                margin-bottom: 30px;
                display: flex;
                align-items: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.06);
                overflow: hidden;
                border-radius: 8px;
            }}

            .vibrant-alert {{
                background: #800000;
                color: #ffffff;
                padding: 6px 18px;
                margin-left: 12px;
                font-family: 'League Spartan', sans-serif;
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 1.5px;
                display: flex;
                align-items: center;
                gap: 10px;
                border-radius: 6px;
                z-index: 10;
                white-space: nowrap;
            }}

            .alert-blink {{
                height: 10px;
                width: 10px;
                background-color: #ffd700;
                border-radius: 50%;
                animation: pulse-gold 1.2s infinite;
            }}

            @keyframes pulse-gold {{
                0% {{ transform: scale(0.8); opacity: 0.5; }}
                50% {{ transform: scale(1.1); opacity: 1; }}
                100% {{ transform: scale(0.8); opacity: 0.5; }}
            }}

            .scroller-window {{
                flex: 1;
                overflow: hidden;
                white-space: nowrap;
                padding: 0 25px;
            }}

            .scroller-text {{
                display: inline-block;
                padding-left: 100%;
                /* Speed slowed down to 50s for better readability */
                animation: marquee-vibrant 50s linear infinite;
                color: #1e293b;
                font-family: 'League Spartan', sans-serif;
                font-size: 20px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            @keyframes marquee-vibrant {{
                0% {{ transform: translateX(0); }}
                100% {{ transform: translateX(-100%); }}
            }}

            .scroller-text:hover {{
                animation-play-state: paused;
                color: #800000;
            }}
            </style>

            <div class="aps-vibrant-ticker">
                <div class="vibrant-alert">
                    <div class="alert-blink"></div> LATEST UPDATES
                </div>
                <div class="scroller-window">
                    <div class="scroller-text">
                        {ticker_text} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ★ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {ticker_text}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        pass
