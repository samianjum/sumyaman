import re

file_path = 'main_app.py'

dashboard_ui_code = """
def render_mobile_dashboard():
    user = st.session_state.get('user_data', {})

    # CSS for Bottom Nav and Dashboard Cards
    st.markdown('''
        <style>
            [data-testid="stHeader"], [data-testid="stSidebar"] {display: none !important;}
            .main .block-container {padding: 0 !important; max-width: 100% !important;}

            .dash-header {
                background: #1B4332;
                padding: 40px 20px;
                color: white;
                border-radius: 0 0 30px 30px;
            }
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            }
            .nav-bar {
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background: white;
                display: flex;
                justify-content: space-around;
                padding: 15px 0;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
                z-index: 999;
            }
            .nav-item { text-align: center; color: #1B4332; font-size: 12px; }
        </style>

        <div class="dash-header">
            <p style="margin:0; opacity:0.8;">Welcome back,</p>
            <h2 style="margin:0;">''' + user.get('full_name', 'Student') + '''</h2>
        </div>

        <div style="padding: 20px; margin-bottom: 80px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="stat-card"><b>📚 Course</b><br>7th Class</div>
                <div class="stat-card"><b>🏆 Rank</b><br>#04</div>
            </div>

            <h3 style="margin-top:25px;">Quick Actions</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top:10px;">
                <button style="border:none; background:#E8F5E9; padding:20px; border-radius:15px; color:#1B4332;">View Results</button>
                <button style="border:none; background:#FFF3E0; padding:20px; border-radius:15px; color:#E65100;">Attendance</button>
                <button style="border:none; background:#E3F2FD; padding:20px; border-radius:15px; color:#1565C0;">Fees Info</button>
                <button style="border:none; background:#FCE4EC; padding:20px; border-radius:15px; color:#C2185B;">Schedule</button>
            </div>
        </div>

        <div class="nav-bar">
            <div class="nav-item">🏠<br>Home</div>
            <div class="nav-item">📝<br>Results</div>
            <div class="nav-item">👤<br>Profile</div>
        </div>
    ''', unsafe_allow_html=True)
"""

with open(file_path, 'r') as f:
    content = f.read()

# Inject the new dashboard function
if "def render_mobile_dashboard()" not in content:
    content = content.replace("def render_mobile_login():", dashboard_ui_code + "\ndef render_mobile_login():")

# Update the routing to handle dashboard
routing_replacement = """
if not st.session_state.get('logged_in'):
    render_mobile_login()
else:
    render_mobile_dashboard()
"""

# Replace old routing logic
content = re.sub(r"if not st\.session_state\.get\('logged_in'\):[\s\S]*", routing_replacement, content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Dashboard converted to Mobile UI!")
