#!/usr/bin/env python3
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

def write_file(path, content):
    path = BASE_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created/Updated: {path}")

# ------------------------------------------------------------
# 1. Create apsokara/fee_views.py
# ------------------------------------------------------------
fee_views_content = '''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
from .models import Student, FeeStructure, FeeRecord, PaymentTransaction
from .forms import FeeStructureForm, FeeCollectionForm, FamilyPaymentForm
from sumyaman_pro.router import set_current_db
import uuid

@login_required
def fee_structure_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    structures = FeeStructure.objects.all().order_by('student_class')
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee structure added.')
            return redirect('fee_structure', school_slug=school_slug)
    else:
        form = FeeStructureForm()
    return render(request, 'hq_admin_custom/fee_structure.html', {
        'structures': structures,
        'form': form,
        'school_slug': school_slug,
    })

@login_required
def delete_fee_structure(request, pk, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    fs = get_object_or_404(FeeStructure, pk=pk)
    fs.delete()
    messages.success(request, 'Fee structure deleted.')
    return redirect('fee_structure', school_slug=school_slug)

@login_required
def fee_collection_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    if request.method == 'POST':
        form = FeeCollectionForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            amount = form.cleaned_data['amount']
            mode = form.cleaned_data['payment_mode']
            remarks = form.cleaned_data.get('remarks', '')
            student = get_object_or_404(Student, id=student_id)
            # Find pending fee records (oldest first)
            pending_records = FeeRecord.objects.filter(
                student=student, status__in=['pending', 'partial']
            ).order_by('year', 'month')
            if not pending_records:
                messages.error(request, f'No pending fee for {student.full_name}.')
                return redirect('fee_collection', school_slug=school_slug)
            remaining = amount
            selected_records = []
            for rec in pending_records:
                if remaining <= 0:
                    break
                due = rec.pending_amount
                if remaining >= due:
                    rec.paid_amount = rec.total_amount
                    remaining -= due
                else:
                    rec.paid_amount += remaining
                    remaining = 0
                rec.update_status()
                rec.save()
                selected_records.append(rec)
            # Generate receipt number
            receipt_no = f"RCP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            trans = PaymentTransaction.objects.create(
                receipt_number=receipt_no,
                student=student,
                amount=amount,
                payment_mode=mode,
                remarks=remarks
            )
            trans.fee_records.set(selected_records)
            messages.success(request, f'Payment of ₹{amount} recorded. Receipt: {receipt_no}')
            return redirect('fee_collection_print', receipt_no=receipt_no, school_slug=school_slug)
    else:
        form = FeeCollectionForm()
    return render(request, 'hq_admin_custom/fee_collection.html', {
        'form': form,
        'school_slug': school_slug,
    })

@login_required
def fee_collection_print(request, receipt_no, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    transaction = get_object_or_404(PaymentTransaction, receipt_number=receipt_no)
    return render(request, 'hq_admin_custom/fee_receipt_print.html', {
        'transaction': transaction,
        'school_slug': school_slug,
    })

@login_required
def family_payment_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    students = []
    total_pending = Decimal('0')
    if request.method == 'POST':
        form = FamilyPaymentForm(request.POST)
        if form.is_valid():
            father_cnic = form.cleaned_data['father_cnic']
            amount = form.cleaned_data.get('amount')
            mode = form.cleaned_data['payment_mode']
            # Find all students with this father CNIC (B‑Form)
            students = Student.objects.filter(b_form=father_cnic)
            if not students:
                messages.error(request, 'No student found with this CNIC.')
                return redirect('family_payment', school_slug=school_slug)
            pending_total = Decimal('0')
            for s in students:
                pending = FeeRecord.objects.filter(
                    student=s, status__in=['pending', 'partial']
                ).aggregate(total=Sum('pending_amount'))['total'] or Decimal('0')
                pending_total += pending
            if amount is None or amount >= pending_total:
                # Pay all pending
                for s in students:
                    recs = FeeRecord.objects.filter(student=s, status__in=['pending', 'partial'])
                    for rec in recs:
                        rec.paid_amount = rec.total_amount
                        rec.update_status()
                        rec.save()
                paid_amount = pending_total
                # Create a single transaction for the family
                receipt_no = f"FAM-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                # To keep it simple, create one transaction per student or a single one? We'll create one for the first student with a remark.
                first_student = students.first()
                trans = PaymentTransaction.objects.create(
                    receipt_number=receipt_no,
                    student=first_student,
                    amount=paid_amount,
                    payment_mode=mode,
                    remarks=f'Family payment for CNIC {father_cnic} covering {students.count()} student(s).'
                )
                # Attach all affected fee records to the transaction
                all_records = FeeRecord.objects.filter(student__in=students, status='paid')
                trans.fee_records.set(all_records)
                messages.success(request, f'Full family payment of ₹{paid_amount} recorded. Receipt: {receipt_no}')
                return redirect('fee_collection_print', receipt_no=receipt_no, school_slug=school_slug)
            else:
                # Partial payment – not implemented in this simplified version
                messages.error(request, 'Partial family payment not supported. Please pay full pending amount or use individual collection.')
                return redirect('family_payment', school_slug=school_slug)
    else:
        form = FamilyPaymentForm()
    return render(request, 'hq_admin_custom/family_payment.html', {
        'form': form,
        'school_slug': school_slug,
    })

@login_required
def defaulters_list(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    # Students with any overdue or pending fee
    defaulters = Student.objects.filter(
        fee_records__status__in=['pending', 'partial', 'overdue']
    ).distinct().order_by('student_class', 'full_name')
    return render(request, 'hq_admin_custom/defaulters_list.html', {
        'defaulters': defaulters,
        'school_slug': school_slug,
    })

@login_required
def fee_reports(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    # Summary report: total collected, pending, etc.
    total_collected = PaymentTransaction.objects.aggregate(total=Sum('amount'))['total'] or 0
    pending_fees = FeeRecord.objects.filter(status__in=['pending', 'partial']).aggregate(total=Sum('pending_amount'))['total'] or 0
    overdue_fees = FeeRecord.objects.filter(status='overdue').aggregate(total=Sum('pending_amount'))['total'] or 0
    # Monthly collection chart data (last 6 months)
    from django.db.models.functions import TruncMonth
    monthly = PaymentTransaction.objects.annotate(month=TruncMonth('transaction_date')).values('month').annotate(total=Sum('amount')).order_by('-month')[:6]
    context = {
        'total_collected': total_collected,
        'pending_fees': pending_fees,
        'overdue_fees': overdue_fees,
        'monthly': monthly,
        'school_slug': school_slug,
    }
    return render(request, 'hq_admin_custom/fee_reports.html', context)

@login_required
def student_fee_view(request, student_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    student = get_object_or_404(Student, id=student_id)
    fee_records = FeeRecord.objects.filter(student=student).order_by('-year', '-month')
    payments = PaymentTransaction.objects.filter(student=student).order_by('-transaction_date')
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_due = fee_records.aggregate(total=Sum('pending_amount'))['total'] or 0
    return render(request, 'hq_admin_custom/student_fee_view.html', {
        'student': student,
        'fee_records': fee_records,
        'payments': payments,
        'total_paid': total_paid,
        'total_due': total_due,
        'school_slug': school_slug,
    })
'''

write_file('apsokara/fee_views.py', fee_views_content)

# ------------------------------------------------------------
# 2. Add fee links to sidebar base_nav.html
# ------------------------------------------------------------
sidebar_nav_path = BASE_DIR / 'templates/hq_admin_custom/base_nav.html'
if sidebar_nav_path.exists():
    with open(sidebar_nav_path, 'r', encoding='utf-8') as f:
        nav_content = f.read()
    
    # Check if fee links already present
    if 'fee/structure' not in nav_content:
        # Find the location after "Subject Assignment" and before "System Config"
        insert_before = '<div class="sidebar-label mt-4 mb-2">System Config</div>'
        new_links = '''
        <div class="sidebar-label mt-4 mb-2">Finance</div>
        <a href="{% url 'fee_structure' school_slug=school_slug %}" class="nav-btn">
            <i class="fas fa-coins"></i> <span>Fee Structure</span>
        </a>
        <a href="{% url 'fee_collection' school_slug=school_slug %}" class="nav-btn">
            <i class="fas fa-hand-holding-usd"></i> <span>Collect Fee</span>
        </a>
        <a href="{% url 'family_payment' school_slug=school_slug %}" class="nav-btn">
            <i class="fas fa-users"></i> <span>Family Payment</span>
        </a>
        <a href="{% url 'defaulters' school_slug=school_slug %}" class="nav-btn">
            <i class="fas fa-exclamation-triangle"></i> <span>Defaulters</span>
        </a>
        <a href="{% url 'fee_reports' school_slug=school_slug %}" class="nav-btn">
            <i class="fas fa-chart-line"></i> <span>Fee Reports</span>
        </a>
'''
        nav_content = nav_content.replace(insert_before, new_links + '\n        ' + insert_before)
        with open(sidebar_nav_path, 'w', encoding='utf-8') as f:
            f.write(nav_content)
        print("✅ Added fee management links to sidebar.")
    else:
        print("ℹ️ Fee links already exist in sidebar.")
else:
    print("⚠️ sidebar template not found; skipping sidebar update.")

# ------------------------------------------------------------
# 3. Create fee templates
# ------------------------------------------------------------
templates = {
    'fee_structure.html': '''{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold">Fee Structure</h2>
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">+ Add Class Fee</button>
    </div>
    <div class="card shadow-sm">
        <div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr><th>Class</th><th>Monthly Fee (₹)</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {% for fs in structures %}
                    <tr>
                        <td>{{ fs.student_class }}</td>
                        <td>₹{{ fs.monthly_fee }}</td>
                        <td>
                            <a href="{% url 'delete_fee_structure' fs.pk school_slug %}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Delete this structure?')">Delete</a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="3" class="text-center text-muted">No fee structures defined.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
<div class="modal fade" id="addModal" tabindex="-1">
    <div class="modal-dialog">
        <form method="post" class="modal-content">
            {% csrf_token %}
            <div class="modal-header"><h5 class="modal-title">Add Fee Structure</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
            <div class="modal-body">{{ form.as_p }}</div>
            <div class="modal-footer"><button type="submit" class="btn btn-primary">Save</button></div>
        </form>
    </div>
</div>
{% endblock %}''',
    'fee_collection.html': '''{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container">
    <h2>Collect Fee</h2>
    <div class="card mt-3">
        <div class="card-body">
            <form method="post">
                {% csrf_token %}
                {{ form.as_p }}
                <button type="submit" class="btn btn-success">Process Payment</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}''',
    'fee_receipt_print.html': '''{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container mt-5" id="receipt">
    <div class="card border-success">
        <div class="card-header bg-success text-white">
            <h3>Payment Receipt</h3>
        </div>
        <div class="card-body">
            <p><strong>Receipt No:</strong> {{ transaction.receipt_number }}</p>
            <p><strong>Student:</strong> {{ transaction.student.full_name }} ({{ transaction.student.roll_number }})</p>
            <p><strong>Amount:</strong> ₹{{ transaction.amount }}</p>
            <p><strong>Mode:</strong> {{ transaction.get_payment_mode_display }}</p>
            <p><strong>Date:</strong> {{ transaction.transaction_date }}</p>
            <p><strong>Remarks:</strong> {{ transaction.remarks|default:"-" }}</p>
        </div>
        <div class="card-footer">
            <button onclick="window.print()" class="btn btn-secondary">Print Receipt</button>
            <a href="{% url 'fee_collection' school_slug %}" class="btn btn-primary">New Payment</a>
        </div>
    </div>
</div>
{% endblock %}''',
    'family_payment.html': '''{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container">
    <h2>Family Payment (by Father CNIC)</h2>
    <div class="card mt-3">
        <div class="card-body">
            <form method="post">
                {% csrf_token %}
                {{ form.as_p }}
                <button type="submit" class="btn btn-primary">Pay All Pending</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}''',
    'defaulters_list.html': '''{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container-fluid">
    <h2>Defaulters List</h2>
    <div class="card mt-3">
        <div class="card-body p-0">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr><th>Student</th><th>Class</th><th>Actions</th></tr></thead>
                <tbody>
                    {% for s in defaulters %}
                    <tr>
                        <td>{{ s.full_name }} ({{ s.roll_number }})</td>
                        <td>{{ s.student_class }}-{{ s.student_section }}</td>
                        <td><a href="{% url 'student_fee_view' s.id school_slug %}" class="btn btn-sm btn-outline-primary">View Fee</a></td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="3" class="text-center">No defaulters</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',
    'fee_reports.html': '''{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container-fluid">
    <h2>Fee Reports</h2>
    <div class="row mt-4">
        <div class="col-md-4"><div class="card bg-info text-white"><div class="card-body">Total Collected<br><h2>₹{{ total_collected }}</h2></div></div></div>
        <div class="col-md-4"><div class="card bg-warning"><div class="card-body">Pending Fees<br><h2>₹{{ pending_fees }}</h2></div></div></div>
        <div class="col-md-4"><div class="card bg-danger text-white"><div class="card-body">Overdue<br><h2>₹{{ overdue_fees }}</h2></div></div></div>
    </div>
    <div class="card mt-4"><div class="card-header">Monthly Collection (Last 6 months)</div><div class="card-body"><ul>{% for m in monthly %}<li>{{ m.month|date:"M Y" }}: ₹{{ m.total }}</li>{% empty %}<li>No data</li>{% endfor %}</ul></div></div>
</div>
{% endblock %}''',
    'student_fee_view.html': '''{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container">
    <h2>Fee Statement: {{ student.full_name }} ({{ student.roll_number }})</h2>
    <div class="row mt-3">
        <div class="col-md-6"><div class="card bg-success text-white p-3">Total Paid: ₹{{ total_paid }}</div></div>
        <div class="col-md-6"><div class="card bg-danger text-white p-3">Total Due: ₹{{ total_due }}</div></div>
    </div>
    <h4 class="mt-4">Monthly Records</h4>
    <table class="table table-sm">
        <thead><tr><th>Month/Year</th><th>Total</th><th>Paid</th><th>Pending</th><th>Status</th></tr></thead>
        <tbody>
            {% for rec in fee_records %}
            <tr>
                <td>{{ rec.month }}/{{ rec.year }}</td>
                <td>₹{{ rec.total_amount }}</td>
                <td>₹{{ rec.paid_amount }}</td>
                <td>₹{{ rec.pending_amount }}</td>
                <td>{{ rec.get_status_display }}</td>
            </tr>
            {% empty %}<tr><td colspan="5">No records</td></tr>{% endfor %}
        </tbody>
    </table>
    <h4>Payment History</h4>
    <table class="table table-sm">
        <thead><tr><th>Date</th><th>Receipt</th><th>Amount</th><th>Mode</th></tr></thead>
        <tbody>
            {% for p in payments %}
            <tr><td>{{ p.transaction_date }}</td><td>{{ p.receipt_number }}</td><td>₹{{ p.amount }}</td><td>{{ p.get_payment_mode_display }}</td></tr>
            {% empty %}<tr><td colspan="4">No payments</td></tr>{% endfor %}
        </tbody>
    </table>
    <a href="{% url 'fee_collection' school_slug %}" class="btn btn-primary">Record Payment</a>
</div>
{% endblock %}'''
}

for tpl_name, content in templates.items():
    write_file(f'templates/hq_admin_custom/{tpl_name}', content)

print("\n🎉 Fee management system installed successfully!")
print("   Restart the Django server and refresh the tenant admin panel.")
print("   New 'Finance' section will appear in the sidebar.")
