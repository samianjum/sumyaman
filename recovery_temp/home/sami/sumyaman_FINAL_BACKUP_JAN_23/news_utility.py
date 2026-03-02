import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd

def render_news_ticker():
    try:
        conn = sqlite3.connect('db.sqlite3')
        news_df = pd.read_sql("SELECT content FROM apsokara_schoolnotice ORDER BY id DESC LIMIT 5", conn)
        conn.close()
        
        if not news_df.empty:
            news_text = " &nbsp;&nbsp;&nbsp;&nbsp; ⚡ &nbsp;&nbsp;&nbsp;&nbsp; ".join(news_df['content'].tolist())
            
            html_code = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@700&family=Montserrat:wght@500&display=swap');
                
                body {{ 
                    margin: 0; 
                    overflow: hidden; 
                    background: transparent;
                }}
                
                .main-container {{
                    background: #000000;
                    height: 45px;
                    display: flex;
                    align-items: center;
                    border-radius: 10px;
                    border: 1px solid #333;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    position: relative;
                    overflow: hidden;
                }}

                .live-tag {{
                    background: #ff0000;
                    color: white;
                    height: 100%;
                    padding: 0 20px;
                    display: flex;
                    align-items: center;
                    font-family: 'Syncopate', sans-serif;
                    font-size: 10px;
                    font-weight: bold;
                    letter-spacing: 2px;
                    z-index: 5;
                    position: relative;
                    box-shadow: 10px 0 20px rgba(255,0,0,0.4);
                    animation: glow-pulse 1.5s infinite;
                }}

                @keyframes glow-pulse {{
                    0% {{ background: #aa0000; }}
                    50% {{ background: #ff0000; }}
                    100% {{ background: #aa0000; }}
                }}

                .ticker-content {{
                    flex: 1;
                    overflow: hidden;
                    white-space: nowrap;
                    display: flex;
                    align-items: center;
                }}

                .moving-text {{
                    display: inline-block;
                    white-space: nowrap;
                    padding-left: 100%;
                    animation: slide-text 25s linear infinite;
                    color: #00ffcc; /* Neon Cyan color for maximum attraction */
                    font-family: 'Montserrat', sans-serif;
                    font-size: 16px;
                    font-weight: 600;
                    text-transform: uppercase;
                }}

                @keyframes slide-text {{
                    0% {{ transform: translateX(0); }}
                    100% {{ transform: translateX(-100%); }}
                }}

                .main-container::after {{
                    content: '';
                    position: absolute;
                    top: 0; left: 0; right: 0; bottom: 0;
                    pointer-events: none;
                    background: linear-gradient(90deg, #000 0%, transparent 10%, transparent 90%, #000 100%);
                    z-index: 2;
                }}
            </style>
            
            <div class="main-container">
                <div class="live-tag">LIVE UPDATE</div>
                <div class="ticker-content">
                    <div class="moving-text">
                        {news_text} &nbsp;&nbsp;&nbsp;&nbsp; ⚡ &nbsp;&nbsp;&nbsp;&nbsp;
                    </div>
                </div>
            </div>
            """
            components.html(html_code, height=60)
            
    except:
        pass
