path = 'templates/hq_admin_custom/student_result_view.html'
with open(path, 'r') as f:
    content = f.read()

# Donut chart ka container smart stats ke neeche add karna
donut_html = """
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="p-3 border rounded bg-white">
                        <h6 class="small fw-bold text-muted text-center mb-3">SUBJECT MASTERY DISTRIBUTION</h6>
                        <div style="height: 200px;"><canvas id="donutChart"></canvas></div>
                    </div>
                </div>
            </div>
"""

import re
# Smart stats row ke baad insert karna
content = content.replace('</div>\n            </div>', '</div>' + donut_html + '\n            </div>', 1)

# Script mein donut chart ka logic
donut_script = """
    // Donut Chart Logic
    const dCtx = document.getElementById('donutChart').getContext('2d');
    let zones = {safe: 0, average: 0, danger: 0};
    
    Object.keys(chartData).forEach(key => {
        if(key === 'overall') return;
        let avg = chartData[key].values.reduce((a,b) => a+b, 0) / chartData[key].values.length;
        if(avg >= 70) zones.safe++;
        else if(avg >= 40) zones.average++;
        else zones.danger++;
    });

    new Chart(dCtx, {
        type: 'doughnut',
        data: {
            labels: ['Safe (70%+)', 'Average (40-70%)', 'Danger (<40%)'],
            datasets: [{
                data: [zones.safe, zones.average, zones.danger],
                backgroundColor: ['#22c55e', '#eab308', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: { 
                legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } }
            },
            cutout: '70%'
        }
    });
"""

content = content.replace("renderChart('overall');", donut_script + "\n    renderChart('overall');")

with open(path, 'w') as f:
    f.write(content)
print("✅ Subject Mastery Donut added!")
