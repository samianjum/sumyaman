import re
import os

path = 'mobile_app.py'

with open(path, 'r') as f:
    content = f.read()

# 1. CSS Styles update for the new theme
new_styles = """
        .insight-container { background: #0F2A44; padding: 16px 0; overflow: hidden; }
        .insight-scroll { display: flex; overflow-x: auto; gap: 12px; padding: 0 20px; scrollbar-width: none; -ms-overflow-style: none; }
        .insight-scroll::-webkit-scrollbar { display: none; }
        
        .insight-card { 
            flex: 0 0 170px; height: 70px; background: #173A5E; 
            border-radius: 14px; border: 1px solid rgba(255,255,255,0.08);
            display: flex; align-items: center; padding: 0 14px;
            transition: all 0.2s ease; cursor: pointer;
        }
        .insight-card:active { transform: scale(0.96); background: #1c4672; }
        
        .icon-circle { 
            width: 32px; height: 32px; background: #2F80ED; 
            border-radius: 10px; display: flex; align-items: center; 
            justify-content: center; margin-right: 12px; flex-shrink: 0;
        }
        .insight-label { color: rgba(255,255,255,0.6); font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.02em; line-height: 1; }
        .insight-value { color: #ffffff; font-size: 14px; font-weight: 800; margin-top: 2px; line-height: 1.2; }
"""

# Injecting new styles into the <style> tag
content = content.replace('.no-scrollbar::-webkit-scrollbar { display: none; }', '.no-scrollbar::-webkit-scrollbar { display: none; }' + new_styles)

# 2. Replacing the Status Strip with Role-Based Insight Bar
insight_html = '''
        <div class="insight-container">
            <div class="insight-scroll">
                
                {% if session['user'].role == 'Student' %}
                <div class="insight-card" onclick="window.location.href='/timetable'">
                    <div class="icon-circle">📚</div>
                    <div><p class="insight-label">Today's Classes</p><p class="insight-value">5 Subjects</p></div>
                </div>
                <div class="insight-card" onclick="window.location.href='/attendance'">
                    <div class="icon-circle">🟢</div>
                    <div><p class="insight-label">Attendance</p><p class="insight-value">92%</p></div>
                </div>
                <div class="insight-card" onclick="window.location.href='/diary'">
                    <div class="icon-circle">📝</div>
                    <div><p class="insight-label">Homework</p><p class="insight-value">2 Pending</p></div>
                </div>
                <div class="insight-card" onclick="window.location.href='/exams'">
                    <div class="icon-circle">📅</div>
                    <div><p class="insight-label">Next Exam</p><p class="insight-value">Chemistry - Fri</p></div>
                </div>

                {% elif session['user'].role == 'Teacher' %}
                    {% if session['user'].is_class_teacher %}
                    <div class="insight-card" onclick="window.location.href='/class-stats'">
                        <div class="icon-circle">📊</div>
                        <div><p class="insight-label">Class Attendance</p><p class="insight-value">87%</p></div>
                    </div>
                    <div class="insight-card" onclick="window.location.href='/leaves'">
                        <div class="icon-circle">📩</div>
                        <div><p class="insight-label">Leave Requests</p><p class="insight-value">4 Pending</p></div>
                    </div>
                    <div class="insight-card" onclick="window.location.href='/exams'">
                        <div class="icon-circle">🧪</div>
                        <div><p class="insight-label">Upcoming Exam</p><p class="insight-value">Friday</p></div>
                    </div>
                    <div class="insight-card" onclick="window.location.href='/diary'">
                        <div class="icon-circle">📘</div>
                        <div><p class="insight-label">Today's Diary</p><p class="insight-value">3 Subjects</p></div>
                    </div>
                    {% else %}
                    <div class="insight-card" onclick="window.location.href='/schedule'">
                        <div class="icon-circle">🎓</div>
                        <div><p class="insight-label">Classes</p><p class="insight-value">4 Scheduled</p></div>
                    </div>
                    <div class="insight-card" onclick="window.location.href='/manage-diary'">
                        <div class="icon-circle">📘</div>
                        <div><p class="insight-label">Diary Pending</p><p class="insight-value">3 Classes</p></div>
                    </div>
                    <div class="insight-card" onclick="window.location.href='/mark-attendance'">
                        <div class="icon-circle">⏱</div>
                        <div><p class="insight-label">Attendance Left</p><p class="insight-value">2 Classes</p></div>
                    </div>
                    <div class="insight-card" onclick="window.location.href='/leaves'">
                        <div class="icon-circle">📩</div>
                        <div><p class="insight-label">Leave Requests</p><p class="insight-value">5 Pending</p></div>
                    </div>
                    {% endif %}
                {% endif %}

            </div>
        </div>
'''

# Find the old section markers or the header end to inject
if "" in content:
    content = re.sub(r'.*?', insight_html, content, flags=re.DOTALL)
else:
    # Fallback: Inject after the app-header div if markers aren't there
    content = content.replace('</header>', '</header>' + insight_html)

with open(path, 'w') as f:
    f.write(content)

print("✅ Theme updated: Deep Navy UI injected.")
print("✅ Role-based logic (Student/Teacher/Class Teacher) active.")
os.remove(__file__)
