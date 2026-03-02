import re

path = 'templates/hq_admin_custom/student_result_view.html'
with open(path, 'r') as f:
    content = f.read()

# 1. Purana "Subject Mastery Levels" section hatana
pattern = r'<div class="mt-4 p-3 border rounded bg-white shadow-sm">.*?</div>\s+</div>'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# 2. Naya "Performance Insights" Table tayyar karna
insight_html = """
            <div class="mt-4 bg-white border rounded shadow-sm overflow-hidden">
                <div class="p-3 bg-light border-bottom">
                    <h6 class="m-0 fw-800 text-dark small text-uppercase"><i class="fas fa-chart-line me-2 text-primary"></i>Subject Performance Insights</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-sm table-hover mb-0 align-middle">
                        <thead class="bg-white">
                            <tr class="text-muted" style="font-size: 0.7rem;">
                                <th class="ps-3">SUBJECT</th>
                                <th class="text-center">AVG SCORE</th>
                                <th class="text-center">TREND</th>
                                <th class="text-center">REMARKS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sub, data in subject_depth.items %}
                            <tr>
                                <td class="ps-3 fw-bold">{{ sub|upper }}</td>
                                <td class="text-center"><span class="badge bg-light text-dark border">{{ data.avg }}%</span></td>
                                <td class="text-center">
                                    {% if data.change > 0 %}
                                        <span class="text-success small fw-bold"><i class="fas fa-arrow-up"></i> {{ data.change }}%</span>
                                    {% elif data.change < 0 %}
                                        <span class="text-danger small fw-bold"><i class="fas fa-arrow-down"></i> {{ data.change }}%</span>
                                    {% else %}
                                        <span class="text-muted small">--</span>
                                    {% endif %}
                                </td>
                                <td class="text-center">
                                    {% if data.avg >= 80 %}<span class="badge bg-success-subtle text-success small">EXCELLENT</span>
                                    {% elif data.avg >= 50 %}<span class="badge bg-primary-subtle text-primary small">STABLE</span>
                                    {% else %}<span class="badge bg-danger-subtle text-danger small">NEED FOCUS</span>{% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
"""

# Smart stats ke baad insert karna
content = content.replace('<div class="row g-3 mt-3">', insight_html + '\n            <div class="row g-3 mt-3">')

with open(path, 'w') as f:
    f.write(content)
print("✅ Insight Table installed!")
