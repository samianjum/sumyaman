path = 'templates/hq_admin_custom/student_result_view.html'
with open(path, 'r') as f:
    content = f.read()

# Chart ke baad smart stats boxes insert karna
smart_stats_html = """
            <div class="row g-3 mt-3">
                <div class="col-6 col-md-3">
                    <div class="p-3 border rounded text-center" style="background: #f0fdf4;">
                        <div class="small fw-bold text-success">BEST SUBJECT</div>
                        <div class="h6 m-0 fw-800 text-dark" id="bestSub">---</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="p-3 border rounded text-center" style="background: #fef2f2;">
                        <div class="small fw-bold text-danger">WEAKEST</div>
                        <div class="h6 m-0 fw-800 text-dark" id="worstSub">---</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="p-3 border rounded text-center" style="background: #eff6ff;">
                        <div class="small fw-bold text-primary">CONSISTENCY</div>
                        <div class="h6 m-0 fw-800 text-dark" id="consistency">---</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="p-3 border rounded text-center" style="background: #fffbeb;">
                        <div class="small fw-bold text-warning">AVG GROWTH</div>
                        <div class="h6 m-0 fw-800 text-dark" id="growthRate">---</div>
                    </div>
                </div>
            </div>
"""

import re
# Insert after the chart canvas div
content = content.replace('</canvas>\n            </div>', '</canvas>\n            </div>' + smart_stats_html)

# Script mein calculation logic add karna
calc_logic = """
    // Smart Stats Calculation
    const subs = chartData;
    let best = {name: '', avg: 0}, worst = {name: '', avg: 101};
    
    Object.keys(subs).forEach(key => {
        if(key === 'overall') return;
        let sum = subs[key].values.reduce((a,b) => a+b, 0);
        let avg = sum / subs[key].values.length;
        if(avg > best.avg) best = {name: key, avg: avg};
        if(avg < worst.avg) worst = {name: key, avg: avg};
    });

    document.getElementById('bestSub').innerText = best.name.toUpperCase();
    document.getElementById('worstSub').innerText = worst.name.toUpperCase();
    
    const overallVals = chartData.overall.values;
    if(overallVals.length > 1) {
        let first = overallVals[0];
        let last = overallVals[overallVals.length - 1];
        let growth = last - first;
        document.getElementById('growthRate').innerText = (growth > 0 ? '+' : '') + growth.toFixed(1) + '%';
        document.getElementById('consistency').innerText = Math.abs(growth) < 10 ? 'STABLE' : 'VOLATILE';
    }
"""

content = content.replace("renderChart('overall');", calc_logic + "\n    renderChart('overall');")

with open(path, 'w') as f:
    f.write(content)
print("✅ Smart Insights added to Analytics!")
