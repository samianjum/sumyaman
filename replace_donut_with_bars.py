import re

path = 'templates/hq_admin_custom/student_result_view.html'
try:
    with open(path, 'r') as f:
        content = f.read()

    # 1. Donut Chart ka kachra saaf karna (agar exist karta hai)
    content = re.sub(r'<div class="row mt-4">.*?donutChart.*?</div>\s+</div>\s+</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'// Donut Chart Logic.*?new Chart\(dCtx, \{.*?\}\);', '', content, flags=re.DOTALL)

    # 2. Naya "Subject Battery" Section (Progress Bars)
    battery_html = """
            <div class="mt-4 p-3 border rounded bg-white shadow-sm">
                <h6 class="small fw-800 text-muted mb-3 text-uppercase" style="letter-spacing:1px;">
                    <i class="fas fa-battery-half me-2 text-primary"></i>Subject Mastery Levels
                </h6>
                <div class="row g-3">
                    {% for sub, data in subject_depth.items %}
                    <div class="col-md-6">
                        <div class="d-flex justify-content-between mb-1">
                            <span class="small fw-bold text-dark">{{ sub|upper }}</span>
                            <span class="small fw-800 {% if data.avg < 40 %}text-danger{% elif data.avg < 70 %}text-warning{% else %}text-success{% endif %}">{{ data.avg }}%</span>
                        </div>
                        <div class="progress" style="height: 8px; background: #f1f5f9; border-radius: 10px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated {% if data.avg < 40 %}bg-danger{% elif data.avg < 70 %}bg-warning{% else %}bg-success{% endif %}" 
                                 role="progressbar" style="width: {{ data.avg }}%; border-radius: 10px;"></div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
    """

    # 3. Purani analytics row ke baad isko insert karna
    if 'Subject Mastery Levels' not in content:
        # Hum isay Smart Stats (row g-3 mt-3) ke foran baad laga rahe hain
        content = content.replace('<div class="row g-3 mt-3">', battery_html + '\n            <div class="row g-3 mt-3">')
        
        with open(path, 'w') as f:
            f.write(content)
        print("✅ Success: Donut removed and Battery Bars installed!")
    else:
        print("⚠️ Already installed.")

except Exception as e:
    print(f"❌ Error: {e}")
