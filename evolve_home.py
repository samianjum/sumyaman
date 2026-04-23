import os

file_path = 'mobile_app.py'

# Modern SVG Icons
icons = {
    'leave': '<svg class="w-7 h-7 mb-2 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>',
    'diary': '<svg class="w-7 h-7 mb-2 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>',
    'attendance': '<svg class="w-7 h-7 mb-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>',
    'reports': '<svg class="w-7 h-7 mb-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>',
    'results': '<svg class="w-7 h-7 mb-2 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>',
    'marks': '<svg class="w-7 h-7 mb-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>',
    'finalize': '<svg class="w-7 h-7 mb-2 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>'
}

new_home_html = f"""
            <div id="page-home" class="grid grid-cols-2 gap-4 animate-zoom-in">
                
                {{# --- LEAVE HUB (Student & Class Teacher) --- #}}
                {% if user.role == 'Student' or (user.role == 'Teacher' and user.is_class_teacher) %}
                <div onclick="openLeaveHub()" class="relative glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-rose-500 active:scale-95 transition-all cursor-pointer group">
                    <span id="leave-badge" class="hidden absolute top-3 right-3 bg-red-600 text-white text-[10px] font-black h-5 w-5 flex items-center justify-center rounded-full shadow-lg border-2 border-white animate-bounce">0</span>
                    {icons['leave']}
                    <h4 class="font-black text-[11px] uppercase tracking-tighter text-gray-800 group-hover:text-rose-600 transition-colors">Leave Hub</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">STATUS & APPLY</p>
                </div>
                {% endif %}

                {{# --- DAILY DIARY (Student & Subject Teacher) --- #}}
                {% if (user.role == 'Teacher' and user.assignments) or user.role == 'Student' %}
                <div onclick="openDiaryHub()" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-amber-500 active:scale-95 transition-all cursor-pointer group relative">
                    <div id="diary-badge" class="hidden absolute -top-2 -right-2 bg-red-600 text-white text-[10px] font-bold px-2 py-1 rounded-full animate-bounce">0</div>
                    {icons['diary']}
                    <h4 class="font-black text-[11px] uppercase tracking-tighter text-gray-800 group-hover:text-amber-600 transition-colors">Daily Diary</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">{{ 'POST HOMEWORK' if user.role == 'Teacher' else 'CHECK DIARY' }}</p>
                </div>
                {% endif %}

                {{# --- ATTENDANCE (Class Teacher Only) --- #}}
                {% if user.role == 'Teacher' and user.is_class_teacher %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-green-600 active:scale-95 transition-all cursor-pointer group">
                    {icons['attendance']}
                    <h4 class="font-black text-[11px] uppercase tracking-tighter text-gray-800 group-hover:text-green-600 transition-colors">Attendance</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">MARK DAILY PRESENCE</p>
                </div>
                {% endif %}

                {{# --- REPORTS (Student Only) --- #}}
                {% if user.role == 'Student' %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-blue-600 active:scale-95 transition-all cursor-pointer group">
                    {icons['reports']}
                    <h4 class="font-black text-[11px] uppercase tracking-tighter text-gray-800 group-hover:text-blue-600 transition-colors">Attendance</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">VIEW PROGRESS</p>
                </div>
                {% endif %}

                {{# --- RESULTS (Student Only) --- #}}
                {% if user.role == 'Student' %}
                <div onclick="showTab('results'); loadStudentResults();" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-emerald-500 active:scale-95 transition-all cursor-pointer group">
                    {icons['results']}
                    <h4 class="font-black text-[11px] uppercase tracking-tighter text-gray-800 group-hover:text-emerald-600 transition-colors">My Result</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">OFFICIAL RECORD</p>
                </div>
                {% endif %}

                {{# --- MARKS ENTRY (All Teachers) --- #}}
                {% if user.role == 'Teacher' %}
                <div onclick="navToMarks()" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-indigo-600 active:scale-95 transition-all cursor-pointer group">
                    {icons['marks']}
                    <h4 class="font-black text-[11px] uppercase tracking-tighter text-gray-800 group-hover:text-indigo-600 transition-colors">Marks Entry</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">GRADING PORTAL</p>
                </div>
                {% endif %}

                {{# --- FINALIZE (Class Teacher Only) --- #}}
                {% if user.role == 'Teacher' and user.is_class_teacher %}
                <div onclick="showTab('final-upload'); loadFinalizeStatus();" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-orange-500 active:scale-95 transition-all cursor-pointer group">
                    {icons['finalize']}
                    <h4 class="font-black text-[11px] uppercase tracking-tighter text-gray-800 group-hover:text-orange-600 transition-colors">Finalize</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">SUBMIT CLASS DATA</p>
                </div>
                {% endif %}
            </div>
"""

if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    start_line = -1
    end_line = -1
    
    for i, line in enumerate(lines):
        if 'id="page-home"' in line:
            start_line = i
        if start_line != -1 and '</div>' in line and i > start_line + 5:
            # Finding the closing div of the page-home grid
            # Based on your sed output, the grid ends around line 560
            if i > 550 and i < 570:
                end_line = i
                break

    if start_line != -1 and end_line != -1:
        # Construct new content
        final_lines = lines[:start_line] + [new_home_html] + lines[end_line+1:]
        
        with open(file_path, 'w') as f:
            f.writelines(final_lines)
        print("🚀 Home Page Design Upgraded to SaaS Standard!")
    else:
        print("❌ Could not precisely locate the Home Page grid block.")
    
    os.remove(__file__)
