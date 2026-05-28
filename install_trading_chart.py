path = 'templates/hq_admin_custom/student_result_view.html'
with open(path, 'r') as f:
    content = f.read()

# Chart configuration ko replace karna bilkul professional line graph se
trading_script = """
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('smartChart').getContext('2d');
    let currentChart;

    // Trading style gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(79, 70, 229, 0.4)');
    gradient.addColorStop(1, 'rgba(79, 70, 229, 0)');

    const chartData = {
        overall: {
            labels: [{% for t in exam_trend %}"{{ t.exam }}",{% endfor %}],
            values: [{% for t in exam_trend %}{{ t.perc }},{% endfor %}],
            label: 'Overall Progress %'
        },
        {% for sub, data in subject_depth.items %}
        "{{ sub }}": {
            labels: [{% for h in data.history %}"{{ h.exam }}",{% endfor %}],
            values: [{% for h in data.history %}{{ h.perc }},{% endfor %}],
            label: '{{ sub }} Trend'
        },
        {% endfor %}
    };

    function renderChart(key) {
        if(currentChart) currentChart.destroy();
        const data = chartData[key];

        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: data.label,
                    data: data.values,
                    borderColor: '#4f46e5',
                    borderWidth: 3,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#4f46e5',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.4, // Is se smooth curve aayega
                    fill: true,
                    backgroundColor: gradient
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: '#1e293b',
                        titleFont: { size: 14 },
                        bodyFont: { size: 13 },
                        callbacks: { label: (context) => ` Score: ${context.raw}%` }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: '#f1f5f9' },
                        ticks: { callback: (value) => value + '%' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    renderChart('overall');
    document.getElementById('chartFilter').addEventListener('change', (e) => renderChart(e.target.value));
});
</script>
"""

# Purane script block ko naye se replace karna
import re
content = re.sub(r'<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>.*?{% endblock %}', trading_script + "\n{% endblock %}", content, flags=re.DOTALL)

with open(path, 'w') as f:
    f.write(content)
print("✅ Trading-style Trend Chart installed!")
