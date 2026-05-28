#!/usr/bin/env python3
"""
APS OKARA FEE SYSTEM - COMPLETE AUTO FIX
Run this once, everything will be fixed automatically.
"""

import os
import re
from pathlib import Path

# ========== CONFIG ==========
BASE_DIR = Path.cwd()
APSOKARA_DIR = BASE_DIR / "apsokara"
TEMPLATES_DIR = BASE_DIR / "templates" / "hq_admin_custom"
FEE_TEMPLATES_DIR = TEMPLATES_DIR / "fee"

# ========== 1. FIX FEE_VIEWS.PY ==========
FEE_VIEWS_FIXED = '''import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator

from sumyaman_pro.router import set_current_db
from .models import Student, FeeStructure, FeeRecord, PaymentTransaction, SchoolFeeSettings
from .forms import FeeStructureForm, FeeCollectionForm, FamilyPaymentForm


def get_fee_settings():
    obj, _ = SchoolFeeSettings.objects.get_or_create(pk=1)
    return obj


def generate_fees_for_month(year, month):
    settings = get_fee_settings()
    students = Student.objects.all()
    created_count = 0
    for student in students:
        try:
            fee_struct = FeeStructure.objects.get(student_class=student.student_class)
            total = fee_struct.monthly_fee
        except FeeStructure.DoesNotExist:
            continue
        if FeeRecord.objects.filter(student=student, month=month, year=year).exists():
            continue
        if month == 2 and (year % 4 != 0 or (year % 100 == 0 and year % 400 != 0)):
            max_day = 28
        elif month in [4, 6, 9, 11]:
            max_day = 30
        else:
            max_day = 31
        due_day = min(settings.due_date_offset, max_day)
        due_date = date(year, month, due_day)
        FeeRecord.objects.create(
            student=student,
            month=month,
            year=year,
            total_amount=total,
            due_date=due_date,
            status='pending'
        )
        created_count += 1
    return created_count


@login_required
def generate_fees_view(request, year, month, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    if not request.user.is_superuser and not hasattr(request.user, 'teacher'):
        messages.error(request, "Permission denied.")
        return redirect('fee_reports', school_slug=school_slug)
    count = generate_fees_for_month(year, month)
    messages.success(request, f"Generated {count} fee records for {month}/{year}.")
    return redirect('fee_reports', school_slug=school_slug)


@login_required
def fee_structure_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fee structure added successfully.")
            return redirect('fee_structure', school_slug=school_slug)
    else:
        form = FeeStructureForm()
    structures = FeeStructure.objects.all().order_by('student_class')
    return render(request, 'hq_admin_custom/fee/fee_structure.html', {
        'structures': structures,
        'form': form,
        'school_slug': school_slug,
    })


@login_required
def delete_fee_structure(request, pk, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    if request.method == 'POST':
        get_object_or_404(FeeStructure, pk=pk).delete()
        messages.success(request, "Deleted.")
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
            payment_mode = form.cleaned_data['payment_mode']
            remarks = form.cleaned_data['remarks']

            student = get_object_or_404(Student, id=student_id)
            pending_records = FeeRecord.objects.filter(
                student=student,
                status__in=['pending', 'partial', 'overdue']
            ).order_by('year', 'month')
            if not pending_records:
                messages.warning(request, "No pending fee for this student.")
                return redirect('fee_collection', school_slug=school_slug)

            remaining = Decimal(str(amount))
            allocated_records = []
            with transaction.atomic():
                for record in pending_records:
                    if remaining <= 0:
                        break
                    pending = record.pending_amount
                    if pending > 0:
                        pay_this = min(remaining, pending)
                        record.paid_amount += pay_this
                        record.save()
                        record.update_status()
                        allocated_records.append(record)
                        remaining -= pay_this

                last_receipt = PaymentTransaction.objects.order_by('-id').first()
                if last_receipt and last_receipt.receipt_number.startswith('RCP-'):
                    try:
                        num = int(last_receipt.receipt_number.split('-')[1]) + 1
                    except:
                        num = 1
                else:
                    num = 1
                receipt_no = f"RCP-{num:06d}"

                payment = PaymentTransaction.objects.create(
                    receipt_number=receipt_no,
                    student=student,
                    amount=amount,
                    payment_mode=payment_mode,
                    remarks=remarks,
                )
                payment.fee_records.set(allocated_records)

            messages.success(request, f"Payment of ₹{amount} received. Receipt: {receipt_no}")
            return redirect('fee_collection_print', school_slug=school_slug, receipt_no=receipt_no)
    else:
        form = FeeCollectionForm()

    recent = PaymentTransaction.objects.select_related('student').order_by('-created_at')[:10]
    return render(request, 'hq_admin_custom/fee/fee_collection.html', {
        'form': form,
        'recent': recent,
        'school_slug': school_slug,
    })


@login_required
def fee_collection_print(request, receipt_no, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    payment = get_object_or_404(PaymentTransaction, receipt_number=receipt_no)
    return render(request, 'hq_admin_custom/fee/receipt_print.html', {
        'payment': payment,
        'school_slug': school_slug,
    })


@login_required
def family_payment_view(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    if request.method == 'POST':
        form = FamilyPaymentForm(request.POST)
        if form.is_valid():
            father_cnic = form.cleaned_data['father_cnic']
            amount = form.cleaned_data['amount']
            payment_mode = form.cleaned_data['payment_mode']

            students = Student.objects.filter(b_form=father_cnic)
            if not students.exists():
                messages.error(request, "No students found with this CNIC.")
                return redirect('family_payment', school_slug=school_slug)

            total_pending = 0
            pending_records_by_student = {}
            for student in students:
                records = FeeRecord.objects.filter(
                    student=student,
                    status__in=['pending', 'partial', 'overdue']
                ).order_by('year', 'month')
                pending_records_by_student[student] = records
                total_pending += sum(r.pending_amount for r in records)

            if amount is None or amount == "":
                amount = total_pending
            else:
                amount = Decimal(str(amount))

            if amount <= 0:
                messages.error(request, "Invalid amount.")
                return redirect('family_payment', school_slug=school_slug)

            allocated_all = []
            remaining = amount
            with transaction.atomic():
                for student, records in pending_records_by_student.items():
                    if remaining <= 0:
                        break
                    for record in records:
                        if remaining <= 0:
                            break
                        pend = record.pending_amount
                        if pend > 0:
                            pay_this = min(remaining, pend)
                            record.paid_amount += pay_this
                            record.save()
                            record.update_status()
                            allocated_all.append(record)
                            remaining -= pay_this

                last_receipt = PaymentTransaction.objects.order_by('-id').first()
                if last_receipt and last_receipt.receipt_number.startswith('RCP-'):
                    try:
                        num = int(last_receipt.receipt_number.split('-')[1]) + 1
                    except:
                        num = 1
                else:
                    num = 1
                receipt_no = f"RCP-{num:06d}"

                primary_student = students.first()
                payment = PaymentTransaction.objects.create(
                    receipt_number=receipt_no,
                    student=primary_student,
                    amount=amount,
                    payment_mode=payment_mode,
                    remarks=f"Family payment for CNIC {father_cnic} covering {len(allocated_all)} fee records",
                )
                payment.fee_records.set(allocated_all)

            messages.success(request, f"Paid ₹{amount} for family. Receipt: {receipt_no}")
            return redirect('fee_collection_print', school_slug=school_slug, receipt_no=receipt_no)
    else:
        form = FamilyPaymentForm()

    return render(request, 'hq_admin_custom/fee/family_payment.html', {
        'form': form,
        'school_slug': school_slug,
    })


@login_required
def defaulters_list(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    from django.db.models import OuterRef, Subquery
    pending_subquery = Subquery(
        FeeRecord.objects.filter(student=OuterRef('pk'))
        .values('student')
        .annotate(total_pending=Sum(F('total_amount') - F('paid_amount')))
        .values('total_pending')
    )
    students = Student.objects.annotate(
        pending_total=Coalesce(pending_subquery, Value(0, output_field=DecimalField()))
    ).filter(pending_total__gt=0).order_by('-pending_total')

    paginator = Paginator(students, 30)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'hq_admin_custom/fee/defaulters.html', {
        'page_obj': page_obj,
        'school_slug': school_slug,
    })


@login_required
def fee_reports(request, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    collections = PaymentTransaction.objects.values('transaction_date__year', 'transaction_date__month').annotate(
        total=Sum('amount')
    ).order_by('-transaction_date__year', '-transaction_date__month')

    pending_by_class = FeeRecord.objects.filter(status__in=['pending', 'partial', 'overdue']) \
        .values('student__student_class') \
        .annotate(pending_total=Sum(F('total_amount') - F('paid_amount'))) \
        .order_by('student__student_class')

    return render(request, 'hq_admin_custom/fee/fee_reports.html', {
        'collections': collections,
        'pending_by_class': pending_by_class,
        'school_slug': school_slug,
    })


@login_required
def student_fee_view(request, student_id, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    student = get_object_or_404(Student, id=student_id)
    fee_records = FeeRecord.objects.filter(student=student).order_by('-year', '-month')
    payments = PaymentTransaction.objects.filter(student=student).order_by('-created_at')
    total_pending = sum(record.pending_amount for record in fee_records if record.status != 'paid')
    return render(request, 'hq_admin_custom/fee/student_fee_view.html', {
        'student': student,
        'fee_records': fee_records,
        'payments': payments,
        'total_pending': total_pending,
        'school_slug': school_slug,
    })
'''

# ========== 2. CREATE MISSING PAGINATION.HTML ==========
PAGINATION_HTML = '''{% if page_obj.has_other_pages %}
<div class="d-flex justify-content-center mt-4">
    <nav>
        <ul class="pagination pagination-sm">
            {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.previous_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.wing %}&wing={{ request.GET.wing }}{% endif %}{% if request.GET.class %}&class={{ request.GET.class }}{% endif %}">Previous</a>
            </li>
            {% else %}
            <li class="page-item disabled"><span class="page-link">Previous</span></li>
            {% endif %}

            {% for num in page_obj.paginator.page_range %}
                {% if page_obj.number == num %}
                <li class="page-item active"><span class="page-link">{{ num }}</span></li>
                {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                <li class="page-item"><a class="page-link" href="?page={{ num }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.wing %}&wing={{ request.GET.wing }}{% endif %}{% if request.GET.class %}&class={{ request.GET.class }}{% endif %}">{{ num }}</a></li>
                {% endif %}
            {% endfor %}

            {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.next_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.wing %}&wing={{ request.GET.wing }}{% endif %}{% if request.GET.class %}&class={{ request.GET.class }}{% endif %}">Next</a>
            </li>
            {% else %}
            <li class="page-item disabled"><span class="page-link">Next</span></li>
            {% endif %}
        </ul>
    </nav>
</div>
{% endif %}'''

# ========== 3. PATCH ALL FEE TEMPLATES ==========
def patch_fee_templates():
    if not FEE_TEMPLATES_DIR.exists():
        print("⚠️ Fee templates folder not found, skipping.")
        return
    for template_file in FEE_TEMPLATES_DIR.glob("*.html"):
        content = template_file.read_text()
        original = content
        # Replace all url tags to include school_slug
        # Pattern: {% url 'name' args %} -> {% url 'name' school_slug=school_slug args %}
        # Handle delete_fee_structure with pk
        content = re.sub(
            r"{% url 'delete_fee_structure' (\w+\.pk) %}",
            r"{% url 'delete_fee_structure' school_slug=school_slug pk=\1 %}",
            content
        )
        content = re.sub(
            r"{% url 'fee_collection_print' (\w+\.receipt_number) %}",
            r"{% url 'fee_collection_print' school_slug=school_slug receipt_no=\1 %}",
            content
        )
        content = re.sub(
            r"{% url 'student_fee_view' (\w+\.id) %}",
            r"{% url 'student_fee_view' school_slug=school_slug student_id=\1 %}",
            content
        )
        # Simple ones with no args
        for url_name in ['fee_reports', 'fee_collection', 'family_payment', 'defaulters', 'fee_structure']:
            content = re.sub(
                r"{% url '" + url_name + r"' %}",
                r"{% url '" + url_name + r"' school_slug=school_slug %}",
                content
            )
        # generate_fees (has args)
        content = re.sub(
            r"{% url 'generate_fees' year=(\d+) month=(\d+) %}",
            r"{% url 'generate_fees' school_slug=school_slug year=\1 month=\2 %}",
            content
        )
        if content != original:
            template_file.write_text(content)
            print(f"✅ Patched {template_file}")

# ========== 4. ADD GENERATE_FEES URL TO apsokara/urls.py ==========
def add_generate_fees_url():
    urls_path = APSOKARA_DIR / "urls.py"
    if not urls_path.exists():
        print("❌ apsokara/urls.py not found")
        return
    content = urls_path.read_text()
    # Check if generate_fees already present
    if "generate_fees" in content:
        print("✅ generate_fees URL already exists")
        return
    # Insert after the last fee URL line
    insert_after = "path('fee/student/<int:student_id>/', student_fee_view, name='student_fee_view'),"
    new_line = "    path('fee/generate/<int:year>/<int:month>/', generate_fees_view, name='generate_fees'),"
    if insert_after in content:
        content = content.replace(insert_after, insert_after + "\n" + new_line)
        urls_path.write_text(content)
        print("✅ Added generate_fees URL pattern")
    else:
        # Fallback: add at end of urlpatterns
        content = content.replace("]", f"    {new_line}\n]")
        urls_path.write_text(content)
        print("✅ Added generate_fees URL pattern (fallback)")

# ========== 5. ENSURE generate_fees_view IS IMPORTED IN URLS.PY ==========
def fix_import_in_urls():
    urls_path = APSOKARA_DIR / "urls.py"
    if not urls_path.exists():
        return
    content = urls_path.read_text()
    if "generate_fees_view" in content:
        return
    # Add to import list
    import_line = "from .fee_views import ("
    if import_line in content:
        # Find the closing parenthesis and insert
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if line.strip() == import_line:
                # Insert generate_fees_view after existing imports
                new_lines.append("    generate_fees_view,")
        content = "\n".join(new_lines)
        urls_path.write_text(content)
        print("✅ Added generate_fees_view to imports")
    else:
        # Alternative: add a separate import line
        content = "from .fee_views import generate_fees_view\n" + content
        urls_path.write_text(content)
        print("✅ Added generate_fees_view import")

# ========== 6. CREATE PAGINATION.HTML ==========
def create_pagination():
    pagination_path = TEMPLATES_DIR / "pagination.html"
    pagination_path.write_text(PAGINATION_HTML)
    print("✅ Created pagination.html")

# ========== 7. UPDATE FEE_VIEWS.PY ==========
def update_fee_views():
    views_path = APSOKARA_DIR / "fee_views.py"
    if views_path.exists():
        import shutil
        shutil.copy(views_path, views_path.with_suffix(".py.bak_auto"))
        print("📁 Backed up fee_views.py")
    views_path.write_text(FEE_VIEWS_FIXED)
    print("✅ Updated fee_views.py")

# ========== MAIN ==========
def main():
    print("=" * 60)
    print("APS OKARA FEE SYSTEM - COMPLETE AUTO FIX")
    print("=" * 60)
    update_fee_views()
    create_pagination()
    patch_fee_templates()
    add_generate_fees_url()
    fix_import_in_urls()
    print("\n" + "=" * 60)
    print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
    print("\n📌 NEXT STEPS:")
    print("1. Restart your Django server:")
    print("   python3 manage.py runserver")
    print("\n2. Login and test fee pages.")
    print("=" * 60)

if __name__ == "__main__":
    main()
