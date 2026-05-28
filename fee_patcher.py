#!/usr/bin/env python3
"""
Fee Management System Patcher for APS OKARA School Management App.
Run: python3 fee_patcher.py
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path("/home/sami/sumyaman")
APSOKARA_DIR = PROJECT_ROOT / "apsokara"
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "hq_admin_custom"
STUDENT_TEMPLATES_DIR = PROJECT_ROOT / "templates" / "hq_admin_custom"  # same folder

# ----------------------------------------------------------------------
# 1. Create new models.py content (append to existing models.py)
# ----------------------------------------------------------------------
MODELS_APPEND = """
# ---------- FEE MANAGEMENT MODELS ----------
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class FeeStructure(models.Model):
    student_class = models.CharField(max_length=10, unique=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Class {self.student_class} - ₹{self.monthly_fee}"

class FeeRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='fee_records')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'month', 'year')
        ordering = ['-year', '-month']

    @property
    def pending_amount(self):
        return self.total_amount - self.paid_amount

    def update_status(self):
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'overdue' if self.due_date < timezone.now().date() else 'pending'
        self.save(update_fields=['status'])

class PaymentTransaction(models.Model):
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('online', 'Online'),
    ]
    receipt_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    transaction_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True)
    fee_records = models.ManyToManyField('FeeRecord', related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt #{self.receipt_number} - ₹{self.amount}"

class SchoolFeeSettings(models.Model):
    generation_day = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(31)])
    due_date_offset = models.IntegerField(default=15, help_text="Days after generation when fee is due")
    late_fee_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentage added to overdue amount")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings (gen day: {self.generation_day})"
"""

def append_models():
    models_path = APSOKARA_DIR / "models.py"
    if not models_path.exists():
        print("❌ models.py not found! Aborting.")
        return False
    with open(models_path, 'a') as f:
        f.write("\n" + MODELS_APPEND)
    print("✅ Appended fee models to models.py")
    return True

# ----------------------------------------------------------------------
# 2. Create new views file: fee_views.py
# ----------------------------------------------------------------------
FEE_VIEWS_CONTENT = '''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal
from .models import Student, FeeStructure, FeeRecord, PaymentTransaction, SchoolFeeSettings
from .forms import FeeStructureForm, FeeCollectionForm, FamilyPaymentForm
import random
import string

def generate_receipt_number():
    return "RCPT-" + ''.join(random.choices(string.digits, k=10))

@login_required
def fee_structure_view(request, school_slug=None):
    structures = FeeStructure.objects.all().order_by('student_class')
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee structure added.")
            return redirect('fee_structure')
    else:
        form = FeeStructureForm()
    return render(request, 'hq_admin_custom/fee_structure.html', {
        'structures': structures,
        'form': form,
        'school_slug': school_slug
    })

@login_required
def delete_fee_structure(request, pk, school_slug=None):
    structure = get_object_or_404(FeeStructure, pk=pk)
    structure.delete()
    messages.success(request, "Deleted.")
    return redirect('fee_structure')

@login_required
def fee_collection_view(request, school_slug=None):
    student = None
    fee_records = []
    payment_form = None
    if request.method == 'POST':
        if 'search_student' in request.POST:
            student_id = request.POST.get('student_id')
            try:
                student = Student.objects.get(id=student_id)
                fee_records = student.fee_records.filter(status__in=['pending', 'partial', 'overdue']).order_by('due_date')
            except Student.DoesNotExist:
                messages.error(request, "Student not found.")
        elif 'make_payment' in request.POST:
            student_id = request.POST.get('student_id')
            amount = Decimal(request.POST.get('amount'))
            mode = request.POST.get('payment_mode')
            remarks = request.POST.get('remarks', '')
            student = get_object_or_404(Student, id=student_id)
            pending_records = student.fee_records.filter(status__in=['pending', 'partial', 'overdue']).order_by('due_date')
            if not pending_records:
                messages.warning(request, "No pending fees for this student.")
                return redirect('fee_collection')
            # Allocate payment to oldest pending records (FIFO)
            remaining = amount
            allocated_records = []
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
                allocated_records.append(rec)
            receipt_no = generate_receipt_number()
            payment = PaymentTransaction.objects.create(
                receipt_number=receipt_no,
                student=student,
                amount=amount,
                payment_mode=mode,
                remarks=remarks,
                transaction_date=timezone.now().date()
            )
            payment.fee_records.add(*allocated_records)
            messages.success(request, f"Payment of ₹{amount} received. Receipt #{receipt_no}")
            return redirect('fee_collection_print', receipt_no=receipt_no, school_slug=school_slug)
    else:
        payment_form = FeeCollectionForm()
    return render(request, 'hq_admin_custom/fee_collection.html', {
        'student': student,
        'fee_records': fee_records,
        'payment_form': payment_form,
        'school_slug': school_slug
    })

@login_required
def fee_collection_print(request, receipt_no, school_slug=None):
    payment = get_object_or_404(PaymentTransaction, receipt_number=receipt_no)
    return render(request, 'hq_admin_custom/receipt.html', {'payment': payment, 'school_slug': school_slug})

@login_required
def family_payment_view(request, school_slug=None):
    if request.method == 'POST':
        form = FamilyPaymentForm(request.POST)
        if form.is_valid():
            father_cnic = form.cleaned_data['father_cnic']
            amount = form.cleaned_data.get('amount')  # can be None for "pay all pending"
            students = Student.objects.filter(father_name__icontains=father_cnic)  # simplified; ideally use CNIC field
            if not students:
                messages.error(request, "No students found with that father name/CNIC.")
                return redirect('family_payment')
            total_pending = 0
            for s in students:
                pending = s.fee_records.aggregate(total=Sum('pending_amount'))['total'] or 0
                total_pending += pending
            if amount is None or amount >= total_pending:
                # Pay all
                for s in students:
                    pending_records = s.fee_records.filter(status__in=['pending', 'partial', 'overdue']).order_by('due_date')
                    for rec in pending_records:
                        rec.paid_amount = rec.total_amount
                        rec.update_status()
                # Create one receipt for the whole family (or separate)
                receipt_no = generate_receipt_number()
                payment = PaymentTransaction.objects.create(
                    receipt_number=receipt_no,
                    student=students.first(),  # representative
                    amount=total_pending,
                    payment_mode=form.cleaned_data['payment_mode'],
                    remarks=f"Family payment for {father_cnic}",
                    transaction_date=timezone.now().date()
                )
                # Attach all fee records (optional)
                all_records = FeeRecord.objects.filter(student__in=students, status__in=['pending','partial','overdue'])
                payment.fee_records.add(*all_records)
                messages.success(request, f"Family payment completed. Receipt #{receipt_no}")
            else:
                # Pay specific amount - allocate across students FIFO
                remaining = amount
                for s in students:
                    pending_records = s.fee_records.filter(status__in=['pending','partial','overdue']).order_by('due_date')
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
                receipt_no = generate_receipt_number()
                payment = PaymentTransaction.objects.create(
                    receipt_number=receipt_no,
                    student=students.first(),
                    amount=amount,
                    payment_mode=form.cleaned_data['payment_mode'],
                    remarks=f"Partial family payment for {father_cnic}",
                    transaction_date=timezone.now().date()
                )
                messages.success(request, f"Partial payment of ₹{amount} recorded. Receipt #{receipt_no}")
            return redirect('fee_collection_print', receipt_no=receipt_no, school_slug=school_slug)
    else:
        form = FamilyPaymentForm()
    return render(request, 'hq_admin_custom/family_payment.html', {'form': form, 'school_slug': school_slug})

@login_required
def defaulters_list(request, school_slug=None):
    overdue_records = FeeRecord.objects.filter(status='overdue').select_related('student')
    # Group by student
    defaulters = {}
    for rec in overdue_records:
        student = rec.student
        if student.id not in defaulters:
            defaulters[student.id] = {
                'student': student,
                'total_due': Decimal('0'),
                'records': []
            }
        defaulters[student.id]['total_due'] += rec.pending_amount
        defaulters[student.id]['records'].append(rec)
    defaulters_list = list(defaulters.values())
    # Sorting by total due descending
    defaulters_list.sort(key=lambda x: x['total_due'], reverse=True)
    return render(request, 'hq_admin_custom/defaulters.html', {'defaulters': defaulters_list, 'school_slug': school_slug})

@login_required
def fee_reports(request, school_slug=None):
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payments = PaymentTransaction.objects.all()
    if start_date:
        payments = payments.filter(transaction_date__gte=start_date)
    if end_date:
        payments = payments.filter(transaction_date__lte=end_date)
    total_collected = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    # Pending amount
    pending_total = FeeRecord.objects.aggregate(total=Sum('pending_amount'))['total'] or Decimal('0')
    # Defaulters count
    defaulter_count = FeeRecord.objects.filter(status='overdue').values('student').distinct().count()
    # Collection rate (collected / total expected)
    total_expected = FeeRecord.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0

    # Chart data: monthly collection
    monthly_collection = payments.extra(select={'month': "EXTRACT(MONTH FROM transaction_date)", 'year': "EXTRACT(YEAR FROM transaction_date)"}).values('year', 'month').annotate(total=Sum('amount')).order_by('year', 'month')
    # Payment mode pie chart
    mode_data = payments.values('payment_mode').annotate(total=Sum('amount'))
    # Class-wise pending
    class_pending = FeeRecord.objects.values('student__student_class').annotate(total_pending=Sum('pending_amount')).order_by('-total_pending')

    return render(request, 'hq_admin_custom/fee_reports.html', {
        'total_collected': total_collected,
        'pending_total': pending_total,
        'defaulter_count': defaulter_count,
        'collection_rate': round(collection_rate, 1),
        'monthly_collection': monthly_collection,
        'mode_data': mode_data,
        'class_pending': class_pending,
        'payments': payments.order_by('-transaction_date')[:50],
        'start_date': start_date,
        'end_date': end_date,
        'school_slug': school_slug
    })

@login_required
def student_fee_view(request, student_id, school_slug=None):
    student = get_object_or_404(Student, id=student_id)
    fee_records = student.fee_records.all().order_by('-year', '-month')
    total_pending = sum(rec.pending_amount for rec in fee_records)
    payments = student.payments.all().order_by('-transaction_date')
    return render(request, 'hq_admin_custom/student_fee_view.html', {
        'student': student,
        'fee_records': fee_records,
        'total_pending': total_pending,
        'payments': payments,
        'school_slug': school_slug
    })
'''

def create_fee_views():
    views_path = APSOKARA_DIR / "fee_views.py"
    with open(views_path, 'w') as f:
        f.write(FEE_VIEWS_CONTENT)
    print("✅ Created fee_views.py")
    return True

# ----------------------------------------------------------------------
# 3. Create new forms.py content (append)
# ----------------------------------------------------------------------
FORMS_APPEND = """
# ---------- FEE FORMS ----------
from django import forms
from .models import FeeStructure, FeeRecord, PaymentTransaction

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['student_class', 'monthly_fee']
        widgets = {
            'student_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class FeeCollectionForm(forms.Form):
    student_id = forms.IntegerField(label='Student ID', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    amount = forms.DecimalField(label='Amount', widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    payment_mode = forms.ChoiceField(choices=PaymentTransaction.MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

class FamilyPaymentForm(forms.Form):
    father_cnic = forms.CharField(label='Father CNIC / B-Form', widget=forms.TextInput(attrs={'class': 'form-control'}))
    amount = forms.DecimalField(required=False, label='Amount (leave blank to pay all pending)', widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    payment_mode = forms.ChoiceField(choices=PaymentTransaction.MODE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
"""

def append_forms():
    forms_path = APSOKARA_DIR / "forms.py"
    with open(forms_path, 'a') as f:
        f.write("\n" + FORMS_APPEND)
    print("✅ Appended fee forms to forms.py")
    return True

# ----------------------------------------------------------------------
# 4. Add URLs to apsokara/urls.py
# ----------------------------------------------------------------------
URL_ADDITIONS = """
    # Fee Management URLs
    path('fee/structure/', views.fee_structure_view, name='fee_structure'),
    path('fee/structure/delete/<int:pk>/', views.delete_fee_structure, name='delete_fee_structure'),
    path('fee/collection/', views.fee_collection_view, name='fee_collection'),
    path('fee/collection/print/<str:receipt_no>/', views.fee_collection_print, name='fee_collection_print'),
    path('fee/family/', views.family_payment_view, name='family_payment'),
    path('fee/defaulters/', views.defaulters_list, name='defaulters'),
    path('fee/reports/', views.fee_reports, name='fee_reports'),
    path('fee/student/<int:student_id>/', views.student_fee_view, name='student_fee_view'),
"""

def add_urls():
    urls_path = APSOKARA_DIR / "urls.py"
    with open(urls_path, 'r') as f:
        content = f.read()
    # Check if already added
    if "fee/structure/" in content:
        print("✅ URLs already present, skipping.")
        return True
    # Insert after the last path
    # Find the closing bracket of urlpatterns
    pattern = re.compile(r'urlpatterns\s*=\s*\[(.*?)\]', re.DOTALL)
    match = pattern.search(content)
    if not match:
        print("❌ Could not find urlpatterns list in urls.py")
        return False
    current_list = match.group(1)
    new_list = current_list.rstrip() + "\n" + URL_ADDITIONS + "\n"
    new_content = content[:match.start(1)] + new_list + content[match.end(1):]
    with open(urls_path, 'w') as f:
        f.write(new_content)
    print("✅ Added fee URLs to urls.py")
    return True

# ----------------------------------------------------------------------
# 5. Create templates
# ----------------------------------------------------------------------
TEMPLATES = {
    "fee_structure.html": """{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center">
        <h2>Fee Structure</h2>
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addModal">+ Add New</button>
    </div>
    <table class="table table-bordered mt-3">
        <thead><tr><th>Class</th><th>Monthly Fee (₹)</th><th>Actions</th></tr></thead>
        <tbody>
        {% for s in structures %}
        <tr>
            <td>{{ s.student_class }}</td>
            <td>{{ s.monthly_fee }}</td>
            <td><a href="{% url 'delete_fee_structure' s.id %}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</a></td>
        </tr>
        {% empty %}
        <tr><td colspan="3">No fee structures defined.</td></tr>
        {% endfor %}
        </tbody>
    </table>
</div>
<!-- Modal -->
<div class="modal fade" id="addModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><form method="post">{% csrf_token %}<div class="modal-header"><h5>Add Fee Structure</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body">{{ form.as_p }}</div><div class="modal-footer"><button type="submit" class="btn btn-primary">Save</button></div></form></div></div></div>
{% endblock %}
""",
    "fee_collection.html": """{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container">
    <h2>Fee Collection</h2>
    <form method="post" class="row g-3 mb-4">{% csrf_token %}
        <div class="col-auto"><input type="text" name="student_id" class="form-control" placeholder="Student ID"></div>
        <div class="col-auto"><button type="submit" name="search_student" class="btn btn-primary">Search</button></div>
    </form>
    {% if student %}
    <div class="card"><div class="card-body">
        <h4>{{ student.full_name }} (Roll: {{ student.roll_number }})</h4>
        <p>Class: {{ student.student_class }}-{{ student.student_section }}</p>
        {% if fee_records %}
        <table class="table"><thead><tr><th>Month/Year</th><th>Total</th><th>Paid</th><th>Pending</th><th>Due Date</th><th>Status</th></tr></thead>
        <tbody>{% for r in fee_records %}<tr><td>{{ r.month }}/{{ r.year }}</td><td>{{ r.total_amount }}</td><td>{{ r.paid_amount }}</td><td>{{ r.pending_amount }}</td><td>{{ r.due_date }}</td><td>{{ r.status }}</td></tr>{% endfor %}</tbody></table>
        <hr><h5>Make Payment</h5>
        <form method="post">{% csrf_token %}
            <input type="hidden" name="student_id" value="{{ student.id }}">
            <div class="row g-2">
                <div class="col-md-3">{{ payment_form.amount.label_tag }} {{ payment_form.amount }}</div>
                <div class="col-md-3">{{ payment_form.payment_mode.label_tag }} {{ payment_form.payment_mode }}</div>
                <div class="col-md-4">{{ payment_form.remarks.label_tag }} {{ payment_form.remarks }}</div>
                <div class="col-md-2"><button type="submit" name="make_payment" class="btn btn-success mt-4">Pay</button></div>
            </div>
        </form>
        {% else %}
        <div class="alert alert-success">No pending fees!</div>
        {% endif %}
    </div></div>
    {% endif %}
</div>
{% endblock %}
""",
    "receipt.html": """{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container" id="receipt">
    <div class="card shadow-lg p-4">
        <div class="text-center"><img src="/static/logo.png" height="60"><h3>Army Public School & College, Okara</h3><p>Fee Receipt</p></div>
        <hr>
        <p><strong>Receipt No:</strong> {{ payment.receipt_number }}</p>
        <p><strong>Student:</strong> {{ payment.student.full_name }} (Roll: {{ payment.student.roll_number }})</p>
        <p><strong>Amount:</strong> ₹{{ payment.amount }}</p>
        <p><strong>Mode:</strong> {{ payment.get_payment_mode_display }}</p>
        <p><strong>Date:</strong> {{ payment.transaction_date }}</p>
        <p><strong>Remarks:</strong> {{ payment.remarks }}</p>
        <hr>
        <div class="text-center"><button onclick="window.print()" class="btn btn-primary">Print Receipt</button></div>
    </div>
</div>
{% endblock %}
""",
    "family_payment.html": """{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container">
    <h2>Family Payment (by Father CNIC)</h2>
    <div class="card p-4"><form method="post">{% csrf_token %}{{ form.as_p }}<button type="submit" class="btn btn-success">Pay</button></form></div>
</div>
{% endblock %}
""",
    "defaulters.html": """{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container">
    <h2>Defaulters List</h2>
    <table class="table table-bordered">
        <thead><tr><th>Student</th><th>Class</th><th>Total Due</th><th>Overdue Since</th><th>Action</th></tr></thead>
        <tbody>
        {% for d in defaulters %}
        <tr>
            <td>{{ d.student.full_name }}</td>
            <td>{{ d.student.student_class }}-{{ d.student.student_section }}</td>
            <td>₹{{ d.total_due }}</td>
            <td>{{ d.records.0.due_date }}</td>
            <td><a href="{% url 'fee_collection' %}?student_id={{ d.student.id }}" class="btn btn-sm btn-warning">Collect</a></td>
        </tr>
        {% empty %}
        <tr><td colspan="5">No defaulters found.</td></tr>
        {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
""",
    "fee_reports.html": """{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container-fluid">
    <h2>Fee Reports</h2>
    <div class="row">
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h5>Total Collected</h5><h3>₹{{ total_collected }}</h3></div></div></div>
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h5>Pending Amount</h5><h3>₹{{ pending_total }}</h3></div></div></div>
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h5>Defaulters Count</h5><h3>{{ defaulter_count }}</h3></div></div></div>
        <div class="col-md-3"><div class="card text-center"><div class="card-body"><h5>Collection Rate</h5><h3>{{ collection_rate }}%</h3></div></div></div>
    </div>
    <div class="row mt-4">
        <div class="col-md-6"><canvas id="monthlyChart"></canvas></div>
        <div class="col-md-6"><canvas id="modeChart"></canvas></div>
    </div>
    <h4>Recent Payments</h4>
    <table class="table"><thead><tr><th>Receipt</th><th>Student</th><th>Amount</th><th>Mode</th><th>Date</th></tr></thead>
    <tbody>{% for p in payments %}<tr><td>{{ p.receipt_number }}</td><td>{{ p.student.full_name }}</td><td>{{ p.amount }}</td><td>{{ p.get_payment_mode_display }}</td><td>{{ p.transaction_date }}</td></tr>{% endfor %}</tbody></table>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    const monthly = {{ monthly_collection|safe }};
    const mode = {{ mode_data|safe }};
    new Chart(document.getElementById('monthlyChart'), { type: 'bar', data: { labels: monthly.map(m=>m.year+'-'+m.month), datasets: [{ label: 'Collection', data: monthly.map(m=>m.total) }] } });
    new Chart(document.getElementById('modeChart'), { type: 'pie', data: { labels: mode.map(m=>m.payment_mode), datasets: [{ data: mode.map(m=>m.total) }] } });
</script>
{% endblock %}
""",
    "student_fee_view.html": """{% extends 'hq_admin_custom/base.html' %}
{% block content %}
<div class="container">
    <h2>Fee Statement: {{ student.full_name }}</h2>
    <h5>Total Pending: ₹{{ total_pending }}</h5>
    <table class="table"><thead><tr><th>Month/Year</th><th>Total</th><th>Paid</th><th>Pending</th><th>Due Date</th><th>Status</th></tr></thead>
    <tbody>{% for r in fee_records %}<tr><td>{{ r.month }}/{{ r.year }}</td><td>{{ r.total_amount }}</td><td>{{ r.paid_amount }}</td><td>{{ r.pending_amount }}</td><td>{{ r.due_date }}</td><td>{{ r.status }}</td></tr>{% endfor %}</tbody></table>
    <h4>Payment History</h4>
    <table class="table"><thead><tr><th>Receipt</th><th>Amount</th><th>Mode</th><th>Date</th></tr></thead>
    <tbody>{% for p in payments %}<tr><td>{{ p.receipt_number }}</td><td>{{ p.amount }}</td><td>{{ p.get_payment_mode_display }}</td><td>{{ p.transaction_date }}</td></tr>{% endfor %}</tbody></table>
</div>
{% endblock %}
"""
}

def create_templates():
    for name, content in TEMPLATES.items():
        path = TEMPLATES_DIR / name
        with open(path, 'w') as f:
            f.write(content)
        print(f"✅ Created template: {name}")

# ----------------------------------------------------------------------
# 6. Modify student_profile.html to add fee tab (or link)
# ----------------------------------------------------------------------
STUDENT_PROFILE_ADDITION = """
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-info text-white">
                    <i class="fas fa-rupee-sign"></i> Fee Details
                </div>
                <div class="card-body">
                    <a href="{% url 'student_fee_view' student_id=s.id %}" class="btn btn-outline-info">View Full Fee Statement</a>
                </div>
            </div>
        </div>
    </div>
"""

def patch_student_profile():
    profile_path = TEMPLATES_DIR / "student_profile.html"
    if not profile_path.exists():
        print("⚠️ student_profile.html not found, skipping patch.")
        return
    with open(profile_path, 'r') as f:
        content = f.read()
    if "student_fee_view" in content:
        print("✅ student_profile.html already patched.")
        return
    # Insert before the closing container or after attendance history section
    # We'll look for a safe insertion point: after attendance table or before last div
    if "</div>" in content:
        # Insert before the last closing div of container
        content = content.replace('</div>', STUDENT_PROFILE_ADDITION + '\n</div>', 1)
    else:
        content += STUDENT_PROFILE_ADDITION
    with open(profile_path, 'w') as f:
        f.write(content)
    print("✅ Patched student_profile.html with fee link.")

# ----------------------------------------------------------------------
# 7. Create management command for auto generation
# ----------------------------------------------------------------------
MANAGE_COMMAND = """# manage.py generate_monthly_fees
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apsokara.models import Student, FeeStructure, FeeRecord, SchoolFeeSettings

class Command(BaseCommand):
    help = 'Generate monthly fee records for all active students'

    def handle(self, *args, **options):
        settings = SchoolFeeSettings.objects.first()
        if not settings:
            self.stdout.write(self.style.ERROR('No fee settings found. Please configure.'))
            return
        today = timezone.now().date()
        # Determine which month/year to generate (usually previous month or current month)
        # For simplicity, generate for current month if not already generated
        year = today.year
        month = today.month
        due_date = today.replace(day=settings.due_date_offset)
        if due_date < today:
            due_date = due_date.replace(month=month+1) if month < 12 else due_date.replace(year=year+1, month=1)

        students = Student.objects.all()
        generated = 0
        for student in students:
            # Get fee structure
            try:
                fee_struct = FeeStructure.objects.get(student_class=student.student_class)
                amount = fee_struct.monthly_fee
            except FeeStructure.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'No fee structure for class {student.student_class}, skipping {student.full_name}'))
                continue
            # Check if already exists
            existing = FeeRecord.objects.filter(student=student, month=month, year=year).first()
            if existing:
                continue
            FeeRecord.objects.create(
                student=student,
                month=month,
                year=year,
                total_amount=amount,
                due_date=due_date,
                status='pending'
            )
            generated += 1
        self.stdout.write(self.style.SUCCESS(f'Generated {generated} fee records for {month}/{year}'))
"""

def create_management_command():
    # Ensure directory exists
    mgmt_dir = APSOKARA_DIR / "management" / "commands"
    mgmt_dir.mkdir(parents=True, exist_ok=True)
    # Create __init__.py if missing
    init_file = mgmt_dir.parent / "__init__.py"
    if not init_file.exists():
        init_file.touch()
    cmd_file = mgmt_dir / "generate_monthly_fees.py"
    with open(cmd_file, 'w') as f:
        f.write(MANAGE_COMMAND)
    print("✅ Created management command: generate_monthly_fees")

# ----------------------------------------------------------------------
# 8. Run migrations note
# ----------------------------------------------------------------------
def final_message():
    print("\n" + "="*60)
    print("🎉 Fee Management System Patched Successfully!")
    print("Next steps:")
    print("1. Run migrations to create new tables:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print("2. Create SchoolFeeSettings via Django shell or admin:")
    print("   from apsokara.models import SchoolFeeSettings")
    print("   SchoolFeeSettings.objects.create(generation_day=1, due_date_offset=15)")
    print("3. Add fee structures using the admin interface under /s/<slug>/fee/structure/")
    print("4. Set up cron job for auto-generation (optional):")
    print("   0 0 1 * * cd /home/sami/sumyaman && python manage.py generate_monthly_fees")
    print("="*60)

# ----------------------------------------------------------------------
# Main execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Starting Fee System Patcher...")
    if not append_models():
        exit(1)
    create_fee_views()
    append_forms()
    add_urls()
    create_templates()
    patch_student_profile()
    create_management_command()
    final_message()
