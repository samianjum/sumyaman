import os

# Path to your attendance template
template_path = 'templates/hq_admin_custom/attendance.html'

patch_code = """
{% extends 'hq_admin_custom/base.html' %}
{% block title %}Attendance HQ | {{ current_school.name|default:"Institution" }}{% endblock title %}

{% block content %}
<style>
    /* Premium Institutional Banner */
    .hq-institutional-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
        color: white; border-radius: 15px; padding: 50px 40px; margin-bottom: 30px;
        position: relative; overflow: hidden; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border-bottom: 4px solid var(--hq-accent);
    }

    /* Abstract UI Decorations (The "Google" Look) */
    .hq-institutional-banner::before {
        content: ''; position: absolute; top: -50px; right: -50px;
        width: 250px; height: 250px; background: rgba(255,255,255,0.03);
        border-radius: 50%;
    }
    .hq-institutional-banner::after {
        content: '\\f19c'; font-family: 'Font Awesome 6 Free'; font-weight: 900;
        position: absolute; right: 30px; bottom: -10px; font-size: 12rem;
        opacity: 0.07; transform: rotate(-10deg);
    }

    .banner-badge {
        background: var(--hq-accent); color: var(--hq-primary);
        padding: 4px 12px; border-radius: 50px; font-size: 0.7rem;
        font-weight: 800; text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 15px; display: inline-block;
    }

    .hub-section { background: white; border: 1px solid var(--hq-border); border-radius: 15px; padding: 30px; margin-bottom: 30px; }
    .hub-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--hq-bg); padding-bottom: 20px; margin-bottom: 25px; }
    
    .ana-card-alt { text-align: center; padding: 20px; border-radius: 10px; background: #f8fafc; border: 1px solid #e2e8f0; }
    .ana-num { font-size: 2rem; font-weight: 800; display: block; color: var(--hq-primary); }
    .ana-label-alt { font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; }

    /* Wing/Co-Ed Cards */
    .wing-card, .coed-class-card {
        background: white; border: 1px solid var(--hq-border);
        border-radius: 15px; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none !important; color: inherit; display: block;
    }
    .wing-card:hover, .coed-class-card:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0,0,0,0.1); border-color: var(--hq-accent); }
    .wing-card { padding: 40px; position: relative; overflow: hidden; }
    .wing-card i { font-size: 3.5rem; color: var(--hq-accent); margin-bottom: 20px; }
    .go-btn { position: absolute; bottom: 0; right: 0; background: var(--hq-primary); color: white; padding: 10px 25px; border-radius: 15px 0 0 0; font-size: 0.8rem; font-weight: bold; }

    .class-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
    .coed-class-card { padding: 25px; text-align: center; border-top: 5px solid var(--hq-primary); }
</style>

<div class="hq-institutional-banner">
    <div class="position-relative" style="z-index: 2;">
        <span class="banner-badge"><i class="fas fa-bolt me-1"></i> Live Monitoring</span>
        <h1 class="fw-black text-uppercase mb-1" style="font-size: 2.8rem; letter-spacing: -1px;">
            {{ current_school.name|default:"Central Intelligence" }}
        </h1>
        <p class="opacity-75 fs-5 fw-light">
            Integrated Attendance & Analytics <span class="mx-2">|</span> HQ Control Panel
        </p>
    </div>
</div>

<!-- Analytics Section -->
<div class="hub-section">
    <div class="hub-header">
        <h5 class="fw-bold mb-0 text-muted"><i class="fas fa-chart-line me-2"></i>Daily Statistics</h5>
        <form method="GET" class="d-flex gap-2">
            <input type="date" name="date" class="form-control form-control-sm w-auto" value="{{ today_date|date:'Y-m-d' }}" onchange="this.form.submit()">
        </form>
    </div>
    <div class="row g-3">
        <div class="col-md-3"><div class="ana-card-alt"><span class="ana-num">{{ total_students }}</span><span class="ana-label-alt">Total Strength</span></div></div>
        <div class="col-md-3"><div class="ana-card-alt" style="border-bottom: 4px solid #10b981;"><span class="ana-num text-success">{{ present }}</span><span class="ana-label-alt">Present Today</span></div></div>
        <div class="col-md-3"><div class="ana-card-alt" style="border-bottom: 4px solid #ef4444;"><span class="ana-num text-danger">{{ absent }}</span><span class="ana-label-alt">Absent</span></div></div>
        <div class="col-md-3"><div class="ana-card-alt" style="border-bottom: 4px solid #f59e0b;"><span class="ana-num text-warning">{{ leave }}</span><span class="ana-label-alt">On Leave</span></div></div>
    </div>
</div>

{% if is_wing_based %}
<!-- Case 1: Wing Based -->
<div class="row g-4">
    <div class="col-md-6">
        <a href="{% url 'boys_wing' school_slug=school_slug %}" class="wing-card">
            <i class="fas fa-person-arrow-up-from-line"></i>
            <h3 class="fw-black">BOYS WING</h3>
            <p class="text-muted">Manage academic presence and records for the Boys section.</p>
            <div class="go-btn">ACCESS SECTOR <i class="fas fa-chevron-right ms-1"></i></div>
        </a>
    </div>
    <div class="col-md-6">
        <a href="{% url 'girls_wing' school_slug=school_slug %}" class="wing-card">
            <i class="fas fa-person-dress"></i>
            <h3 class="fw-black">GIRLS WING</h3>
            <p class="text-muted">Access girls' wing monitoring and attendance trends.</p>
            <div class="go-btn" style="background: var(--hq-accent); color: var(--hq-primary);">ACCESS SECTOR <i class="fas fa-chevron-right ms-1"></i></div>
        </a>
    </div>
</div>
{% else %}
<!-- Case 2: Co-Ed -->
<div class="hub-section">
    <div class="hub-header">
        <h5 class="fw-bold mb-0"><i class="fas fa- chalkboard me-2"></i>Classroom Directory</h5>
    </div>
    <div class="class-grid">
        {% for cls in classes %}
        <a href="{% url 'mark_attendance' school_slug=school_slug class_name=cls.student_class section_name=cls.student_section wing_name=cls.wing %}" 
           class="coed-class-card">
            <div class="h3 fw-black mb-0">{{ cls.student_class }}</div>
            <div class="fw-bold text-muted small text-uppercase">Section {{ cls.student_section }}</div>
            <div class="mt-3 pt-2 border-top small text-muted">
                <i class="fas fa-fingerprint me-1"></i> {{ cls.total }} Enrolled
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

print("SUCCESS: Dynamic Banner & Branding applied. Hardcoded names removed.")
