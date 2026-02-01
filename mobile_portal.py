import streamlit as st

def render_mobile_view():
    u = st.session_state.user_info
    role = st.session_state.role
    
    # Session state for navigation
    if "curr_page" not in st.session_state:
        st.session_state.curr_page = "🏠 Dashboard"

    # --- UI STYLING ---
    st.markdown("""
        <style>
            /* Hide Sidebar & Streamlit Header */
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarCollapsedControl"] { display: none !important; }
            .stAppHeader { display: none !important; }
            
            /* Background and Container */
            .stApp { background-color: #f4f7f6; }
            
            /* Top Banner */
            .top-header {
                background: #1b4332;
                padding: 20px;
                text-align: center;
                border-bottom: 4px solid #d4af37;
                border-radius: 0 0 25px 25px;
                margin-bottom: 20px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            }
            .top-header h2 { color: #d4af37 !important; margin:0; font-size: 24px; }
            
            /* Welcome Card */
            .welcome-box {
                background: white;
                padding: 15px;
                border-radius: 15px;
                margin: 0 10px 20px 10px;
                border-left: 8px solid #1b4332;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            
            /* Button Styling (Making them look like Cards) */
            div.stButton > button {
                height: 100px;
                width: 100%;
                background-color: white !important;
                color: #1b4332 !important;
                border: 1px solid #e0e0e0 !important;
                border-radius: 15px !important;
                font-weight: bold !important;
                font-size: 16px !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
                transition: 0.3s !important;
            }
            div.stButton > button:active {
                transform: scale(0.95);
                background-color: #d4af37 !important;
                color: white !important;
            }
        </style>
        
        <div class="top-header">
            <h2>APS OKARA</h2>
        </div>
        
        <div class="welcome-box">
            <p style="margin:0; color:#666;">Assalam-o-Alaikum,</p>
            <h3 style="margin:0; color:#1b4332;">{u.get('full_name')}</h3>
            <span style="background:#d4af37; color:#1b4332; padding:2px 8px; border-radius:10px; font-size:12px; font-weight:bold;">{role}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- GRID SYSTEM ---
    if st.session_state.curr_page == "🏠 Dashboard":
        st.markdown("<p style='padding-left:15px; font-weight:bold; color:#555;'>Main Menu</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊\nAttendance"):
                st.session_state.curr_page = "Attendance"
                st.rerun()
            if st.button("🏆\nResults"):
                st.session_state.curr_page = "Results"
                st.rerun()
                
        with col2:
            if st.button("📝\nLeave App"):
                st.session_state.curr_page = "Leave"
                st.rerun()
            if st.button("🚪\nLogout"):
                st.session_state.clear()
                st.rerun()
                
    else:
        # Back Button for sub-pages
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.curr_page = "🏠 Dashboard"
            st.rerun()
            
        st.divider()
        
        # Rendering Content based on selection
        page = st.session_state.curr_page
        if page == "Attendance":
            st.subheader("Attendance Module")
            # Yahan apna render_attendance function call karlo
        elif page == "Results":
            st.subheader("Examination Results")
        elif page == "Leave":
            st.subheader("Apply for Leave")

