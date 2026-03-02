import re

file_path = 'mobile_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Update Navigation Bar CSS & HTML
new_nav_css = """
        .app-nav { 
            position: absolute; bottom: 0; width: 100%; height: 65px; 
            background: rgba(255,255,255,0.9); backdrop-filter: blur(15px);
            display: flex; justify-content: space-around; align-items: center;
            border-top: 1px solid #f1f5f9; z-index: 30; padding-bottom: 5px;
        }
        .nav-btn { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s; }
        .nav-btn span:first-child { font-size: 24px; margin-bottom: -2px; }
        .nav-btn span:last-child { font-size: 9px; font-weight: 900; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        .active-nav span { color: #1B4332 !important; transform: scale(1.1); }
"""

new_nav_html = """
        <div class="app-nav">
            <div onclick="showTab('home')" id="n-home" class="nav-btn active-nav"><span>🏠</span><span>Home</span></div>
            <div onclick="showTab('mark')" id="n-mark" class="nav-btn"><span>📋</span><span>Attendance</span></div>
            <div onclick="showTab('profile')" id="n-profile" class="nav-btn"><span>👤</span><span>Profile</span></div>
            <div onclick="window.location.href='/logout'" class="nav-btn"><span>🚪</span><span>Exit</span></div>
        </div>
"""

# Profile Page HTML
profile_page = """
            <div id="page-profile" class="hidden space-y-6 p-6">
                <div class="text-center py-6">
                    <div class="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 border-4 border-white shadow-lg flex items-center justify-center text-4xl">👤</div>
                    <h3 class="font-black text-xl text-gray-800">{{ user.full_name }}</h3>
                    <p class="text-xs font-bold text-[#D4AF37] uppercase tracking-widest">{{ user.role }}</p>
                </div>
                <div class="space-y-3">
                    <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-50">
                        <p class="text-[10px] text-gray-400 font-bold uppercase">Personal ID</p>
                        <p class="font-bold text-gray-700">{{ user.id or user.b_form }}</p>
                    </div>
                    <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-50">
                        <p class="text-[10px] text-gray-400 font-bold uppercase">Date of Birth</p>
                        <p class="font-bold text-gray-700">{{ user.dob }}</p>
                    </div>
                </div>
            </div>
"""

# Apply Changes
content = re.sub(r"\.app-nav \{.*?\}", new_nav_css, content, flags=re.DOTALL)
content = content.replace('<div class="app-nav">', '').split('')[0] + new_nav_html + "        {% endif %}\n    </div>"
content = content.replace('<div id="page-mark" class="hidden space-y-4">', profile_page + '\n            <div id="page-mark" class="hidden space-y-4">')

# Update showTab JS function to handle active class
new_js_showtab = """
        function showTab(t) {
            document.querySelectorAll('#page-home, #page-mark, #page-profile').forEach(p => p.classList.add('hidden'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active-nav'));
            
            document.getElementById('page-'+t).classList.remove('hidden');
            document.getElementById('n-'+t).classList.add('active-nav');
            if(t === 'mark') loadStudents();
        }
"""
content = re.sub(r"function showTab\(t\) \{.*?\}", new_js_showtab, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Navbar Design & Profile Tab Updated!")
