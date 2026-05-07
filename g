import os

# Path to your attendance template
template_path = 'templates/hq_admin_custom/attendance.html'

patch_code = """
{% extends 'hq_admin_custom/base.html' %}
{% block title %}Attendance HQ | APS OKARA{% endblock title %}

{% block content %}
<style>
    /* Base Styles */
    .hq-institutional-banner {
        background: linear-gradient(135deg, var(--hq-primary) 0%, #1a252b 100%);
        color: white; border-radius: 15px; padding: 40px; margin-bottom: 30px;
        position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-left: 8px solid var(--hq-accent);
    }
    .hq-institutional-banner::after {
        content: '\\f19c'; font-family: 'Font Awesome 6 Free'; font-weight: 900;
        position: absolute; right: -20px; bottom: -20px; font-size: 18rem;
        opacity: 0.05; transform: rotate(-15deg);
    }
    .hub-section { background: white; border: 1px solid var(--hq-border); border-radius: 15px; padding: 30px; margin-bottom: 30px; }
    .hub-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--hq-bg); padding-bottom: 20px; margin-bottom: 25px; }
    
    .ana-card-alt { text-align: center; padding: 20px; border-radius: 10px; background: #f8fafc; border: 1px solid #e2e8f0; }
    .ana-num { font-size: 2rem; font-weight: 800; display: block; color: var(--hq-primary); }
    .ana-label-alt { font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; }

    /* Wing-Based Styles (Old School Style) */
    .wing-card {
        background: white; border: 1px solid var(--hq-border);
        border-radius: 20px; padding: 40px; transition: 0.3s;
        text-decoration: none; color: inherit; display: block;
        position: relative; overflow: hidden;
    }
    .wing-card:hover { transform: translateY(-10px); border-color: var(--hq-accent); box-shadow: 0 15px 30px rgba(0,0,0,0.08); }
    .wing-card i { font-size: 3.5rem; color: var(--hq-accent); margin-bottom: 20px; }
    .wing-card h3 { font-weight: 800; color: var(--hq-primary); }
    .go-btn { position: absolute; bottom: 0; right: 0; background: var(--hq-primary); color: white; padding: 10px 25px; border-radius: 20px 0 0 0; font-size: 0.8rem; font-weight: bold; }

    /* Co-Ed Classroom Styles (New Grid) */
    .class-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
    .coed-class-card { 
        background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; 
        transition: 0.3s; text-decoration: none !important; color: inherit; text-align: center;
        border-top: 5px solid var(--hq-primary);
    }
    .coed-class-card:hover { transform: translateY(-5px); border-color: var(--hq-accent); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
</style>

<div class="hq-institutional-banner d-flex justify-content-between align-items-center">
    <div>
        <div class="d-flex align-items-center mb-2">
            <div style="width: 60px; height: 60px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 20px;">
                <i class="fas fa-shield-halved fa-2x text-white"></i>
            </div>
            <h1 class="fw-black text-uppercase mb-0">Intelligence & Attendance HQ</h1>
        </div>
        <p class="opacity-75">APS Okara Cantt — Central Monitoring System</p>
    </div>
</div>

<!-- Analytics Section -->
<div class="hub-section">
    <div class="hub-header">
        <h5 class="fw-bold mb-0 text-muted"><i class="fas fa-chart-pie me-2"></i>School-Wide Analytics</h5>
        <form method="GET" class="d-flex gap-2">
            <input type="date" name="date" class="form-control form-control-sm w-auto" value="{{ today_date|date:'Y-m-d' }}" onchange="this.form.submit()">
        </form>
    </div>
    <div class="row g-3">
        <div class="col-md-3"><div class="ana-card-alt"><span class="ana-num">{{ total_students }}</span><span class="ana-label-alt">Global Strength</span></div></div>
        <div class="col-md-3"><div class="ana-card-alt" style="border-bottom: 4px solid #10b981;"><span class="ana-num text-success">{{ present }}</span><span class="ana-label-alt">Present</span></div></div>
        <div class="col-md-3"><div class="ana-card-alt" style="border-bottom: 4px solid #ef4444;"><span class="ana-num text-danger">{{ absent }}</span><span class="ana-label-alt">Absent</span></div></div>
        <div class="col-md-3"><div class="ana-card-alt" style="border-bottom: 4px solid #f59e0b;"><span class="ana-num text-warning">{{ leave }}</span><span class="ana-label-alt">Leave</span></div></div>
    </div>
</div>

{% if is_wing_based %}
<!-- Case 1: Wing Based School (Show the 2 Big Boxes) -->
<div class="row g-4">
    <div class="col-md-6">
        <a href="{% url 'boys_wing' school_slug=school_slug %}" class="wing-card">
            <i class="fas fa-mars"></i>
            <h3>BOYS WING</h3>
            <p class="text-muted">Manage records for the Boys section from Junior to Senior levels.</p>
            <div class="go-btn">ENTER WING <i class="fas fa-arrow-right ms-1"></i></div>
        </a>
    </div>
    <div class="col-md-6">
        <a href="{% url 'girls_wing' school_slug=school_slug %}" class="wing-card">
            <i class="fas fa-venus"></i>
            <h3>GIRLS WING</h3>
            <p class="text-muted">Access girls' academic records and daily attendance trends.</p>
            <div class="go-btn" style="background: var(--hq-accent);">ENTER WING <i class="fas fa-arrow-right ms-1"></i></div>
        </a>
    </div>
</div>
{% else %}
<!-- Case 2: Co-Ed School (Show the Small Class Boxes) -->
<div class="hub-section">
    <div class="hub-header">
        <h5 class="fw-bold mb-0"><i class="fas fa-door-open me-2"></i>Active Classrooms</h5>
    </div>
    <div class="class-grid">
        {% for cls in classes %}
        <a href="{% url 'mark_attendance' school_slug=school_slug class_name=cls.student_class section_name=cls.student_section wing_name=cls.wing %}" 
           class="coed-class-card">
            <div class="h3 fw-black mb-0">{{ cls.student_class }}</div>
            <div class="fw-bold text-muted small">SECTION {{ cls.student_section }}</div>
            <div class="mt-3 pt-2 border-top small text-muted">
                <i class="fas fa-users me-1"></i> {{ cls.total }} Students
            </div>
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}
{% endblock content %}
"""

with open(template_path, 'w') as f:
    f.write(patch_code.strip())

print(f"FIX APPLIED: {template_path} now respects is_wing_based logic.")
