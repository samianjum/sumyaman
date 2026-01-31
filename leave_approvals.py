import streamlit as st
import pandas as pd
import sqlite3

def render_leave_approvals(u):
    t_class = u.get('class') or u.get('incharge_class')
    t_sec = u.get('sec', '') or u.get('incharge_section', '')
    t_wing = u.get('wing', '')
    
    with sqlite3.connect("db.sqlite3", timeout=30) as conn:
        p_count = pd.read_sql("SELECT COUNT(*) as count FROM apsokara_studentleave WHERE student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND wing=?) ", 
                             conn, params=(t_class, t_wing)).iloc[0]['count']

    st.markdown(f"""
        <style>
        .stTabs [data-baseweb="tab-list"] {{ gap: 15px; }}
        .stTabs [data-baseweb="tab"] {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 8px 20px;
            color: #475569;
        }}
        .stTabs [aria-selected="true"] {{
            background: #2563eb !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }}
        /* Modern Apple-Style Card */
        .req-card {{
            background: white;
            border-radius: 24px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #f1f5f9;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            transition: transform 0.2s ease;
        }}
        .req-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,0.06); }}
        .student-avatar {{
            background: #eff6ff;
            color: #2563eb;
            width: 45px; height: 45px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px; font-weight: bold;
            margin-right: 15px;
        }}
        .reason-bubble {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 16px;
            color: #334155;
            font-size: 0.95rem;
            line-height: 1.5;
            border: 1px inset #f1f5f9;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 99px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"📥 Pending ({p_count})", "🔍 History & Search"])

    with tab1:
        with sqlite3.connect("db.sqlite3", timeout=30) as conn:
            pending = pd.read_sql("""
                SELECT l.*, s.full_name as name 
                FROM apsokara_studentleave l 
                LEFT JOIN apsokara_student s ON l.student_id = s.id 
                WHERE s.student_class=? AND s.wing=?
            """, conn, params=(t_class, t_wing))
        
        if pending.empty:
            st.info("✨ Everything is clear! No pending requests.")
        else:
            for _, r in pending.iterrows():
                display_name = r['name'] if (isinstance(r['name'], str) and r['name'].strip()) else f"Student ID: {r['student_id']}"
                st.markdown(f"""
                <div class="req-card">
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <div class="student-avatar">{display_name[0]}</div>
                        <div>
                            <div style="font-weight: 800; color: #1e293b; font-size: 1.1rem;">{display_name}</div>
                            <div style="font-size: 0.8rem; color: #64748b;">Section {r['section']} • {r['from_date']} to {r['to_date']}</div>
                        </div>
                    </div>
                    <div class="reason-bubble">
                        <b>Message:</b><br>{r['reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, _ = st.columns([1,1,2])
                if c1.button("✅ Approve", key=f"a{r['id']}", width='stretch'):
                    with sqlite3.connect("db.sqlite3", timeout=30) as conn:
                        conn.execute("UPDATE apsokara_studentleave SET status='Approved', is_read=1 WHERE id=?", (r['id'],))
                    st.rerun()
                if c2.button("❌ Reject", key=f"r{r['id']}", width='stretch'):
                    with sqlite3.connect("db.sqlite3", timeout=30) as conn:
                        conn.execute("UPDATE apsokara_studentleave SET status='Rejected', is_read=1 WHERE id=?", (r['id'],))
                    st.rerun()

    with tab2:
        st.markdown("### 🕵️ Global History Search")
        c1, c2 = st.columns(2)
        s_name = c1.text_input("👤 Search Student Name", placeholder="Enter name...")
        s_date = c2.date_input("🗓️ Filter by Date", value=None)
        
        # Humne query loose rakhi hai taake filter sahi chalein
        query = """
            SELECT s.full_name as Name, l.from_date as Start, l.to_date as End, l.from_date as Date 
            FROM apsokara_studentleave l 
            LEFT JOIN apsokara_student s ON l.student_id = s.id 
            WHERE s.student_class=? AND s.wing=?
        """
        params = [t_class, t_wing]
        
        if s_name:
            query += " AND s.full_name LIKE ?"
            params.append(f"%{s_name}%")
        if s_date:
            query += " AND ? BETWEEN l.from_date AND l.to_date"
            params.append(str(s_date))
            
        with sqlite3.connect("db.sqlite3", timeout=30) as conn:
            hist = pd.read_sql(query + " ORDER BY l.id DESC", conn, params=params)
        
        if hist.empty:
            st.info("No records found for the selected filters.")
        else:
            st.dataframe(
                hist, 
                width='stretch', 
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", help="Approval Status")
                }
            )
