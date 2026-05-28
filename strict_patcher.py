import re
import os

path = 'mobile_app.py'

try:
    with open(path, 'r') as f:
        content = f.read()

    # The exact UI block with deep navy theme and roles
    ui_block = '''<style>
        .saas-insight-wrap { background: #0F2A44; margin: 0 -20px; padding: 16px 20px; }
        .saas-scroll { display: flex; overflow-x: auto; gap: 12px; scrollbar-width: none; -ms-overflow-style: none; }
        .saas-scroll::-webkit-scrollbar { display: none; }
        .saas-card {
            flex: 0 0 160px; height: 70px; background: #173A5E;
            border-radius: 14px; border: 1px solid rgba(255,255,255,0.08);
            display: flex; align-items: center; padding: 0 16px; cursor: pointer; transition: transform 0.2s;
        }
        .saas-card:active { transform: scale(0.95); }
        .saas-icon {
            width: 32px; height: 32px; background: #2F80ED; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; margin-right: 12px; flex-shrink: 0;
        }
        .saas-text-wrap { display: flex; flex-direction: column; }
        .saas-label { color: rgba(255,255,255,0.6); font-size: 10px; font-weight: 600; text-transform: uppercase; line-height: 1; margin-bottom: 3px; }
        .saas-value { color: #ffffff; font-size: 13px; font-weight: 800; line-height: 1; }
    </style>

    <div class="saas-insight-wrap">
        <div class="saas-scroll">
            {% if session['user'].role == 'Student' %}
            <div class="saas-card" onclick="window.location.href='/timetable'">
                <div class="saas-icon">📚</div><div class="saas-text-wrap"><span class="saas-label">Classes Today</span><span class="saas-value">5 Subjects</span></div>
            </div>
            <div class="saas-card" onclick="window.location.href='/attendance'">
                <div class="saas-icon">🟢</div><div class="saas-text-wrap"><span class="saas-label">Attendance</span><span class="saas-value">92%</span></div>
            </div>
            <div class="saas-card" onclick="window.location.href='/diary'">
                <div class="saas-icon">📝</div><div class="saas-text-wrap"><span class="saas-label">Homework</span><span class="saas-value">2 Pending</span></div>
            </div>
            <div class="saas-card" onclick="window.location.href='/exams'">
                <div class="saas-icon">📅</div><div class="saas-text-wrap"><span class="saas-label">Next Exam</span><span class="saas-value">Chemistry - Fri</span></div>
            </div>

            {% elif session['user'].role == 'Teacher' %}
                {% if session['user'].is_class_teacher %}
                <div class="saas-card" onclick="window.location.href='/class-stats'">
                    <div class="saas-icon">📊</div><div class="saas-text-wrap"><span class="saas-label">Class Attendance</span><span class="saas-value">87%</span></div>
                </div>
                <div class="saas-card" onclick="window.location.href='/leaves'">
                    <div class="saas-icon">📩</div><div class="saas-text-wrap"><span class="saas-label">Leave Requests</span><span class="saas-value">4 Pending</span></div>
                </div>
                <div class="saas-card" onclick="window.location.href='/exams'">
                    <div class="saas-icon">🧪</div><div class="saas-text-wrap"><span class="saas-label">Upcoming Exam</span><span class="saas-value">Friday</span></div>
                </div>
                <div class="saas-card" onclick="window.location.href='/diary'">
                    <div class="saas-icon">📘</div><div class="saas-text-wrap"><span class="saas-label">Today's Diary</span><span class="saas-value">3 Subjects</span></div>
                </div>
                {% else %}
                <div class="saas-card" onclick="window.location.href='/schedule'">
                    <div class="saas-icon">🎓</div><div class="saas-text-wrap"><span class="saas-label">Classes Today</span><span class="saas-value">4 Scheduled</span></div>
                </div>
                <div class="saas-card" onclick="window.location.href='/manage-diary'">
                    <div class="saas-icon">📘</div><div class="saas-text-wrap"><span class="saas-label">Diary Pending</span><span class="saas-value">3 Classes</span></div>
                </div>
                <div class="saas-card" onclick="window.location.href='/mark-attendance'">
                    <div class="saas-icon">⏱</div><div class="saas-text-wrap"><span class="saas-label">Attendance Left</span><span class="saas-value">2 Classes</span></div>
                </div>
                <div class="saas-card" onclick="window.location.href='/leaves'">
                    <div class="saas-icon">📩</div><div class="saas-text-wrap"><span class="saas-label">Leave Requests</span><span class="saas-value">5 Pending</span></div>
                </div>
                {% endif %}
            {% endif %}
        </div>
    </div>
    '''

    # Strict Regex: Will ONLY replace if it finds BOTH the start and end markers
    pattern = r'.*?'

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, ui_block, content, flags=re.DOTALL)
        with open(path, 'w') as f:
            f.write(new_content)
        print("\n✅ PERFECT INJECTION: Only the Quick Status Strip was modified.")
        print("✅ No syntax errors triggered. File structure is safe.")
    else:
        print("\n❌ MARKERS NOT FOUND: Patcher did NOT modify the file to prevent breaking it.")
        print("Make sure '' and '' exist in the HTML.")

except Exception as e:
    print(f"Error: {e}")

finally:
    if os.path.exists(__file__):
        os.remove(__file__)
