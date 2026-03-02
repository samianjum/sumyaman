import re

path = 'templates/hq_admin_custom/student_result_view.html'
with open(path, 'r') as f:
    content = f.read()

# 1. Performance Analytics Section ko "Toggle Banner" se replace karna
new_analytics_html = """
    <div class="res-card mb-4" style="border: 1px solid #e2e8f0;">
        <div class="p-3 d-flex justify-content-between align-items-center bg-light" style="cursor: pointer;" data-bs-toggle="collapse" data-bs-target="#analyticsCollapse">
            <h6 class="m-0 fw-800 text-dark"><i class="fas fa-chart-line me-2 text-primary"></i>PERFORMANCE ANALYTICS</h6>
            <button class="btn btn-sm btn-outline-primary fw-bold">VIEW ANALYTICS <i class="fas fa-chevron-down ms-1"></i></button>
        </div>
        <div id="analyticsCollapse" class="collapse p-3 border-top">
            <div class="row mb-3">
                <div class="col-md-6">
                    <select id="chartFilter" class="form-select form-select-sm fw-bold">
                        <option value="overall">OVERALL PERFORMANCE TREND</option>
                        {% for sub in subject_depth %}
                        <option value="{{ sub }}">{{ sub|upper }} TREND</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div style="height: 300px; position: relative;">
                <canvas id="smartChart"></canvas>
            </div>
        </div>
    </div>
"""

# Purane charts aur "PERFORMANCE ANALYTICS" heading ko replace karna
pattern = r'<h5.*?PERFORMANCE ANALYTICS</h5>.*?<div class="res-card">| <div class="card shadow-sm mb-4">.*?<div class="res-card">'
content = re.sub(r'<h5.*?PERFORMANCE ANALYTICS</h5>.*?<div class="res-card">', new_analytics_html + '<div class="res-card">', content, flags=re.DOTALL)

# 2. Aik single Powerful Script end mein insert karna
smart_script = """
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('smartChart').getContext('2d');
    let currentChart;

    const chartData = {
        overall: {
            labels: [{% for sub, data in subject_depth.items %}"{{ sub }}",{% endfor %}],
            values: [{% for sub, data in subject_depth.items %}{{ data.avg }},{% endfor %}],
            label: 'Avg Score %'
        },
        {% for sub, data in subject_depth.items %}
        "{{ sub }}": {
            labels: [{% for h in data.history %}"{{ h.exam }}",{% endfor %}],
            values: [{% for h in data.history %}{{ h.perc }},{% endfor %}],
            label: 'Exam-wise Trend'
        },
        {% endfor %}
    };

    function renderChart(key) {
        if(currentChart) currentChart.destroy();
        const data = chartData[key];
        const isLine = key !== 'overall';

        currentChart = new Chart(ctx, {
            type: isLine ? 'line' : 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.label,
                    data: data.values,
                    backgroundColor: isLine ? 'rgba(79, 70, 229, 0.1)' : '#4f46e5',
                    borderColor: '#4f46e5',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
    }

    renderChart('overall');
    document.getElementById('chartFilter').addEventListener('change', (e) => renderChart(e.target.value));
});
</script>
"""

# Safai: Purane scripts aur endblock handle karna
content = content.split('{% endblock %}')[0] + smart_script + "\n{% endblock %}"

with open(path, 'w') as f:
    f.write(content)
print("✅ Smart Analytics System Installed!")
