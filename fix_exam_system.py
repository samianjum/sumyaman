import os

file_path = 'templates/hq_admin_custom/exam_window.html'

# We keep your exact Modal IDs and Form Actions from the backup
new_html = """{% extends 'hq_admin_custom/dashboard.html' %}
{% block hq_content %}
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<style>
    .hq-banner {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 15px; color: white; padding: 30px; margin-bottom: 25px;
    }
    .exam-card { border-radius: 15px; transition: 0.3s; border: none; }
    .exam-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important; }
    .view-btn { border-radius: 8px; width: 45px; }
    .search-box { border-radius: 10px; border: 1px solid #ddd; padding: 10px 15px; }
</style>

<div class="p-4">
    <div class="hq-banner shadow-sm d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
            <h2 class="fw-bold mb-1">Exam Control Center</h2>
            <p class="mb-0 opacity-75">Manage cycles, track performance, and deploy new papers.</p>
        </div>
        <div class="d-flex gap-2">
            <button class="btn btn-light fw-bold shadow-sm" style="border-radius: 10px;" data-bs-toggle="modal" data-bs-target="#createExamModalFix">
                <i class="fas fa-plus-circle me-1"></i> Launch New Exam
            </button>
        </div>
    </div>

    <div class="row mb-4 g-3 align-items-center">
        <div class="col-md-5">
            <input type="text" id="examSearch" class="form-control search-box" placeholder="Search exams or classes...">
        </div>
        <div class="col-md-4">
            <div class="d-flex gap-2 text-center">
                <div class="bg-white p-2 flex-fill shadow-sm rounded-3">
                    <small class="text-muted d-block">Active</small>
                    <span class="fw-bold text-success">{{ exams|length }}</span>
                </div>
                <div class="bg-white p-2 flex-fill shadow-sm rounded-3">
                    <small class="text-muted d-block">Date</small>
                    <span class="fw-bold">{{ today }}</span>
                </div>
            </div>
        </div>
        <div class="col-md-3 text-end">
            <button class="btn btn-outline-dark view-btn" onclick="toggleView('grid')"><i class="fas fa-th-large"></i></button>
            <button class="btn btn-outline-dark view-btn" onclick="toggleView('list')"><i class="fas fa-list"></i></button>
        </div>
    </div>

    <div id="examGridView" class="row">
        {% for exam in exams %}
        <div class="col-md-4 mb-4 exam-item" data-name="{{ exam.name|lower }}" data-class="{{ exam.class_group|lower }}">
            <div class="card shadow-sm exam-card h-100">
                <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center pt-3">
                    <span class="badge bg-{{ exam.status_class }} px-3 py-2">{{ exam.status_label }}</span>
                    <div class="dropdown">
                        <i class="fas fa-ellipsis-v text-muted cursor-pointer" data-bs-toggle="dropdown"></i>
                        <ul class="dropdown-menu shadow border-0">
                            <li><a class="dropdown-item" href="{% url 'manage_subjects' exam.id %}"><i class="fas fa-book me-2"></i>Edit Subjects</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="javascript:void(0)" onclick="confirmDelete('{% url 'delete_exam' exam.id %}')"><i class="fas fa-trash me-2"></i>Delete Exam</a></li>
                        </ul>
                    </div>
                </div>
                <div class="card-body">
                    <h5 class="fw-bold mb-1">{{ exam.name }}</h5>
                    <p class="text-muted small mb-3">Target: <span class="badge bg-light text-dark">{{ exam.class_group }}</span></p>
                    <div class="d-flex justify-content-between small text-muted mb-3">
                        <span><i class="far fa-calendar-alt me-1"></i> {{ exam.start_date }}</span>
                        <span><i class="far fa-calendar-check me-1"></i> {{ exam.end_date }}</span>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <a href="javascript:void(0)" 
                           onclick="confirmToggle('{% url 'toggle_exam' exam.id %}', '{{ exam.is_active }}')" 
                           class="btn btn-sm btn-{{ exam.is_active|yesno:'outline-danger,success' }} fw-bold">
                           <i class="fas fa-power-off me-1"></i> {{ exam.is_active|yesno:'Deactivate,Activate' }}
                        </a>
                        <button class="btn btn-sm btn-dark"><i class="fas fa-chart-bar me-1"></i> Analytics</button>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="examListView" class="d-none">
        <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
            <table class="table table-hover align-middle mb-0">
                <thead class="bg-light">
                    <tr>
                        <th class="ps-4">Exam Name</th>
                        <th>Class</th>
                        <th>Status</th>
                        <th>Timeline</th>
                        <th class="text-end pe-4">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for exam in exams %}
                    <tr>
                        <td class="ps-4 fw-bold">{{ exam.name }}</td>
                        <td>{{ exam.class_group }}</td>
                        <td><span class="badge bg-{{ exam.status_class }}">{{ exam.status_label }}</span></td>
                        <td class="small">{{ exam.start_date }} - {{ exam.end_date }}</td>
                        <td class="text-end pe-4">
                            <a href="{% url 'toggle_exam' exam.id %}" class="btn btn-sm btn-light"><i class="fas fa-sync"></i></a>
                            <a href="{% url 'manage_subjects' exam.id %}" class="btn btn-sm btn-light"><i class="fas fa-cog"></i></a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="modal fade" id="createExamModalFix" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <form method="POST" action="{% url 'create_exam' %}" class="modal-content shadow-lg border-0" style="border-radius:20px;">
            {% csrf_token %}
            <div class="modal-header border-0 pt-4 px-4">
                <h5 class="fw-bold">New Exam Configuration</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body px-4">
                <label class="small fw-bold text-muted mb-2">EXAM TITLE</label>
                <input type="text" name="exam_name" class="form-control mb-3 p-3 bg-light border-0" placeholder="e.g. Annual Exam 2026" required style="border-radius:12px;">
                
                <label class="small fw-bold text-muted mb-2">TARGET CLASS</label>
                <select name="class_group" class="form-select mb-3 p-3 bg-light border-0" style="border-radius:12px;">
                    <option value="All">All Classes</option>
                    {% for c in class_list %}<option value="{{ c }}">{{ c }}</option>{% endfor %}
                </select>
                
                <div class="row">
                    <div class="col">
                        <label class="small fw-bold text-muted mb-2">START DATE</label>
                        <input type="date" name="start_date" class="form-control p-3 bg-light border-0" value="{{ today }}" required style="border-radius:12px;">
                    </div>
                    <div class="col">
                        <label class="small fw-bold text-muted mb-2">END DATE</label>
                        <input type="date" name="end_date" class="form-control p-3 bg-light border-0" required style="border-radius:12px;">
                    </div>
                </div>
            </div>
            <div class="modal-footer border-0 p-4">
                <button type="submit" class="btn btn-success w-100 py-3 fw-bold shadow-sm" style="border-radius:15px;">Deploy Exam to System</button>
            </div>
        </form>
    </div>
</div>

<script>
    function toggleView(view) {
        if(view === 'grid') {
            document.getElementById('examGridView').classList.remove('d-none');
            document.getElementById('examListView').classList.add('d-none');
        } else {
            document.getElementById('examGridView').classList.add('d-none');
            document.getElementById('examListView').classList.remove('d-none');
        }
    }

    function confirmToggle(url, isActive) {
        let action = (isActive === 'True') ? 'Deactivate' : 'Activate';
        Swal.fire({
            title: action + ' Exam?',
            text: "This will affect mark entry and attendance access!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: (isActive === 'True') ? '#d33' : '#28a745',
            confirmButtonText: 'Yes, ' + action + ' it!'
        }).then((result) => {
            if (result.isConfirmed) { window.location.href = url; }
        });
    }

    function confirmDelete(url) {
        Swal.fire({
            title: 'Pakka delete karna hai?',
            text: "Sara record (Marks/Subjects) khatam ho jaye ga!",
            icon: 'error',
            showCancelButton: true,
            confirmButtonText: 'Delete Forever'
        }).then((result) => {
            if (result.isConfirmed) { window.location.href = url; }
        });
    }

    document.getElementById('examSearch').addEventListener('keyup', function() {
        let filter = this.value.toLowerCase();
        document.querySelectorAll('.exam-item').forEach(item => {
            let text = item.innerText.toLowerCase();
            item.style.display = text.includes(filter) ? '' : 'none';
        });
    });
</script>
{% endblock %}
"""

with open(file_path, 'w') as f:
    f.write(new_html)
print("SUCCESS: Design updated with original system preserved.")
