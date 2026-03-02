import re

path = 'templates/hq_admin_custom/student_result_view.html'
with open(path, 'r') as f:
    content = f.read()

# 1. Purane kachre ki safai (Donut ya Mastery bars jo bhi reh gaya ho)
content = re.sub(r'<div class="mt-4.*?Subject Mastery Levels.*?</div>\s+</div>', '', content, flags=re.DOTALL)
content = re.sub(r'<div class="mt-4 bg-white border rounded shadow-sm overflow-hidden">.*?</table>.*?</div>\s+</div>', '', content, flags=re.DOTALL)

# 2. Naya Table UI
insight_table = """
            <div class="mt-4 bg-white border rounded shadow-sm overflow-hidden">
                <div class="p-3 bg-light border-bottom d-flex justify-content-between align-items-center">
                    <h6 class="m-0 fw-800 text-dark small"><i class="fas fa-microscope me-2 text-primary"></i>PERFORMANCE INSIGHTS</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-sm table-hover mb-0">
                        <thead class="bg-white">
                            <tr class="text-muted" style="font-size: 0.75rem;">
                                <th class="ps-3 border-0">SUBJECT</th>
                                <th class="text-center border-0">AVG SCORE</th>
                                <th class="text-center border-0">TREND</th>
                                <th class="text-center border-0">STATUS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sub, data in subject_depth.items %}
                            <tr>
                                <td class="ps-3 py-2 fw-bold text-dark">{{ sub|upper }}</td>
                                <td class="text-center">
                                    <div class="fw-800">{{ data.avg }}%</div>
                                </td>
                                <td class="text-center">
                                    {% if data.change > 0 %}
                                        <span class="badge bg-success-subtle text-success px-2 py-1"><i class="fas fa-caret-up me-1"></i>+{{ data.change }}%</span>
                                    {% elif data.change < 0 %}
                                        <span class="badge bg-danger-subtle text-danger px-2 py-1"><i class="fas fa-caret-down me-1"></i>{{ data.change }}%</span>
                                    {% else %}
                                        <span class="text-muted small">--</span>
                                    {% endif %}
                                </td>
                                <td class="text-center">
                                    {% if data.avg >= 75 %}<i class="fas fa-circle text-success me-1" style="font-size:8px;"></i> <span class="small fw-bold">Mastery</span>
                                    {% elif data.avg >= 40 %}<i class="fas fa-circle text-warning me-1" style="font-size:8px;"></i> <span class="small fw-bold">Average</span>
                                    {% else %}<i class="fas fa-circle text-danger me-1" style="font-size:8px;"></i> <span class="small fw-bold">Critical</span>{% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
"""

# Isay smart stats ke row ke foran baad insert karna
content = content.replace('<div class="row g-3 mt-3">', insight_table + '\n            <div class="row g-3 mt-3">')

with open(path, 'w') as f:
    f.write(content)
print("✅ Insight Table UI Installed!")
