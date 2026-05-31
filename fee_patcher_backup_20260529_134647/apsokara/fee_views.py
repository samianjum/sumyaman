import json
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
from .models import Student, FeeStructure, FeeRecord, PaymentTransaction, SchoolFeeSettings, AuditLog
from .forms import FeeStructureForm, FeeCollectionForm, FamilyPaymentForm

# ---------- UPGRADED FEE COLLECTION SYSTEM (AUTO-GENERATED) ----------
import json
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Student, FeeRecord, PaymentTransaction, FeeStructure

def allocate_payment(student, amount_paid, payment_mode, remarks=""):
    """
    Allocate payment to oldest pending fee records.
    Returns: (allocated_records_list, total_allocated, remaining_amount)
    """
    amount_left = Decimal(str(amount_paid))
    pending_records = FeeRecord.objects.filter(
        student=student,
        status__in=['pending', 'partial', 'overdue']
    ).order_by('year', 'month')  # oldest first

    allocated = []
    for record in pending_records:
        if amount_left <= 0:
            break
        due = record.pending_amount
        if due <= 0:
            continue
        if amount_left >= due:
            pay = due
        else:
            pay = amount_left
        record.paid_amount += pay
        record.update_status()
        record.save()
        allocated.append({
            'id': record.id,
            'month': record.month,
            'year': record.year,
            'original_fee': record.total_amount,
            'paid_from_this': pay,
            'remaining': record.pending_amount
        })
        amount_left -= pay
    return allocated, amount_paid - amount_left, amount_left

def student_search_api(request, school_slug=None):
    """AJAX endpoint to search student by roll number, name, father CNIC, or phone."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    students = Student.objects.filter(
        Q(roll_number__icontains=query) |
        Q(full_name__icontains=query) |
        Q(father_name__icontains=query) |
        Q(parents_phone__icontains=query) |
        Q(b_form__icontains=query)
    )[:10]

    results = []
    for s in students:
                    pending_data = FeeRecord.objects.filter(student=s, status__in=['pending','partial','overdue']).aggregate(

                        total=Sum('total_amount'), paid=Sum('paid_amount')

                    )

                    total = pending_data['total'] or Decimal('0.00')

                    paid = pending_data['paid'] or Decimal('0.00')

                    pending_total = total - paid
                    results.append({
            'id': s.id,
            'full_name': s.full_name,
            'roll_number': s.roll_number,
            'father_name': s.father_name,
            'student_class': s.student_class,
            'student_section': s.student_section,
            'wing': s.wing,
            'pending_total': str(pending_total),
        })
    return JsonResponse({'results': results})

def get_pending_details(request, school_slug=None):
    """AJAX endpoint to get detailed pending fee records for a student."""
    student_id = request.GET.get('student_id')
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

    records = FeeRecord.objects.filter(student=student).order_by('year', 'month')
    pending = []
    for r in records:
        if r.pending_amount > 0:
            pending.append({
                'id': r.id,
                'month': r.month,
                'year': r.year,
                'total_amount': str(r.total_amount),
                'paid_amount': str(r.paid_amount),
                'pending_amount': str(r.pending_amount),
                'due_date': r.due_date.isoformat(),
                'status': r.status,
            })
    return JsonResponse({'pending': pending, 'student_name': student.full_name})

def collect_payment_api(request, school_slug=None):
    """Process a payment transaction."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    student_id = data.get('student_id')
    amount = Decimal(str(data.get('amount')))
    payment_mode = data.get('payment_mode')
    remarks = data.get('remarks', '')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

    if amount <= 0:
        return JsonResponse({'error': 'Invalid amount'}, status=400)

    with transaction.atomic():
        # Allocate payment
        allocated_records, total_allocated, remaining = allocate_payment(student, amount, payment_mode, remarks)
        if total_allocated == 0:
            return JsonResponse({'error': 'No pending fee to allocate'}, status=400)

        # Generate receipt number
        today = timezone.now().date()
        last_receipt = PaymentTransaction.objects.filter(
            receipt_number__startswith=f"APS-{today.strftime("%Y%m")}-"
        ).order_by('-receipt_number').first()
        if last_receipt:
            last_num = int(last_receipt.receipt_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        receipt_no = f"APS-{today.strftime("%Y%m")}-{new_num:04d}"

        # Create payment transaction
        payment = PaymentTransaction.objects.create(
            receipt_number=receipt_no,
            student=student,
            amount=total_allocated,
            payment_mode=payment_mode,
            transaction_date=today,
            remarks=remarks,
        )
        # Associate fee records
        allocated_ids = [rec['id'] for rec in allocated_records]
        payment.fee_records.set(FeeRecord.objects.filter(id__in=allocated_ids))

        # Build receipt HTML
        receipt_context = {
            'school': request.current_school if hasattr(request, 'current_school') else None,
            'receipt': payment,
            'student': student,
            'allocated_months': allocated_records,
            'remaining_total': sum(Decimal(rec['remaining']) for rec in allocated_records),
            'date': today,
        }
        receipt_html = render_to_string('hq_admin_custom/fee/receipt_print.html', receipt_context)

    return JsonResponse({
        'success': True,
        'receipt_html': receipt_html,
        'receipt_no': receipt_no,
        'remaining_total': str(remaining),
        'allocated': allocated_records,
    })

def undo_payment(request, receipt_no, school_slug=None):
    """Admin only: revert a payment (marks as reversed)."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    try:
        payment = PaymentTransaction.objects.get(receipt_number=receipt_no)
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Receipt not found'}, status=404)
    # Mark as reversed without complex recalculation (admin can adjust manually)
    payment.reversed = True
    payment.save()
    return JsonResponse({'success': True, 'message': 'Payment marked as reversed. Please manually adjust fee records if needed.'})

def family_payment_api(request, school_slug=None):
    """Process payment for all children of a father (by CNIC)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    father_cnic = data.get('father_cnic')
    amount = Decimal(str(data.get('amount'))) if data.get('amount') else None
    payment_mode = data.get('payment_mode')
    remarks = data.get('remarks', '')

    students = Student.objects.filter(b_form=father_cnic)
    if not students.exists():
        return JsonResponse({'error': 'No student found with this CNIC'}, status=404)

    total_paid = Decimal('0.00')
    details = []
    with transaction.atomic():
        for student in students:
            if amount is None:
                            pending_data = FeeRecord.objects.filter(student=s, status__in=['pending','partial','overdue']).aggregate(

                                total=Sum('total_amount'), paid=Sum('paid_amount')

                            )

                            total = pending_data['total'] or Decimal('0.00')

                            paid = pending_data['paid'] or Decimal('0.00')

                            pending_total = total - paid
                            if pending_total > 0:
                                alloc, paid, rem = allocate_payment(student, pending_total, payment_mode, remarks)
                                if paid > 0:
                                    total_paid += paid
                                    details.append({'student': student.full_name, 'paid': str(paid), 'remaining': str(rem)})
        if total_paid == 0:
            return JsonResponse({'error': 'No pending fees for any student'}, status=400)
    return JsonResponse({'success': True, 'total_paid': str(total_paid), 'details': details})

def daily_collection_summary(request, school_slug=None):
    """Return today's collection total and count."""
    today = timezone.now().date()
    payments = PaymentTransaction.objects.filter(transaction_date=today)
    total = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    count = payments.count()
    return JsonResponse({'total': str(total), 'count': count})





def recent_payments_api(request, school_slug=None):
    """Return last 10 payment transactions for the dashboard."""
    if school_slug:
        set_current_db(school_slug)
    payments = PaymentTransaction.objects.select_related('student').order_by('-created_at')[:10]
    data = []
    for p in payments:
        data.append({
            'receipt': p.receipt_number,
            'student': p.student.full_name,
            'amount': str(p.amount),
            'mode': p.get_payment_mode_display(),
            'date': p.transaction_date.isoformat(),
        })
    return JsonResponse({'payments': data})

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
    return render(request, 'hq_admin_custom/fee_structure.html', {
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
    # Redirect to new upgraded collection counter
    return collection_counter(request, school_slug)
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
    return render(request, 'hq_admin_custom/fee_collection.html', {
        'form': form,
        'recent': recent,
        'school_slug': school_slug,
    })


@login_required
def fee_collection_print(request, receipt_no, school_slug=None):
    if school_slug:
        set_current_db(school_slug)
    payment = get_object_or_404(PaymentTransaction, receipt_number=receipt_no)
    return render(request, 'hq_admin_custom/receipt_print.html', {
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

    return render(request, 'hq_admin_custom/family_payment.html', {
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
    return render(request, 'hq_admin_custom/defaulters.html', {
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

    pending_by_class = FeeRecord.objects.filter(status__in=['pending', 'partial', 'overdue'])         .values('student__student_class')         .annotate(pending_total=Sum(F('total_amount') - F('paid_amount')))         .order_by('student__student_class')

    return render(request, 'hq_admin_custom/fee_reports.html', {
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
    return render(request, 'hq_admin_custom/student_fee_view.html', {
        'student': student,
        'fee_records': fee_records,
        'payments': payments,
        'total_pending': total_pending,
        'school_slug': school_slug,
    })



# ========== UPGRADED FEE MANAGEMENT VIEWS ==========

from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
from django.db.models import Sum, Count, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
import json, calendar
from django.utils.timezone import now, timedelta
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import csv
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

@login_required
def fee_dashboard(request, school_slug=None):
    """Main Fee Dashboard with KPIs, charts, alerts."""
    set_current_db(school_slug) if school_slug else None
    today = now().date()
    # KPIs
    today_collection = PaymentTransaction.objects.filter(transaction_date=today).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    month_start = today.replace(day=1)
    month_collection = PaymentTransaction.objects.filter(transaction_date__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    pending_total = FeeRecord.objects.filter(status__in=['pending','partial','overdue']).aggregate(total=Sum(F('total_amount')-F('paid_amount')))['total'] or Decimal('0')
    defaulter_count = FeeRecord.objects.filter(status='overdue').values('student').distinct().count()
    total_billed = FeeRecord.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
    if total_billed > 0:
        efficiency = (month_collection / total_billed) * 100
    else:
        efficiency = 0

    # Pending Alerts (top 5 defaulters)
    defaulters = FeeRecord.objects.filter(status='overdue').values('student').annotate(
        pending=Sum(F('total_amount')-F('paid_amount'))
    ).order_by('-pending')[:5]
    defaulter_list = []
    for d in defaulters:
        student = Student.objects.get(id=d['student'])
        days_overdue = (today - FeeRecord.objects.filter(student=student, status='overdue').first().due_date).days
        defaulter_list.append({
            'student': student, 'pending': d['pending'], 'days_overdue': days_overdue
        })

    # Recent Transactions
    recent = PaymentTransaction.objects.select_related('student').order_by('-created_at')[:5]

    # Monthly Collection Chart (last 6 months)
    six_months_ago = today - timedelta(days=180)
    chart_data = PaymentTransaction.objects.filter(transaction_date__gte=six_months_ago)        .annotate(month=TruncMonth('transaction_date'))        .values('month').annotate(total=Sum('amount')).order_by('month')
    months = [d['month'].strftime('%b %Y') for d in chart_data]
    amounts = [float(d['total']) for d in chart_data]

    # Upcoming Due Dates
    upcoming = FeeRecord.objects.filter(due_date__gte=today, status__in=['pending','partial']).order_by('due_date')[:5]
    upcoming_list = [{'student': r.student, 'due_date': r.due_date, 'amount': r.pending_amount} for r in upcoming]

    context = {
        'school_slug': school_slug,
        'today_collection': today_collection,
        'month_collection': month_collection,
        'pending_total': pending_total,
        'defaulter_count': defaulter_count,
        'efficiency': round(efficiency, 1),
        'defaulters': defaulter_list,
        'recent': recent,
        'chart_months': months,
        'chart_amounts': amounts,
        'upcoming': upcoming_list,
    }
    return render(request, 'hq_admin_custom/fee_dashboard.html', context)

@login_required
def collection_counter(request, school_slug=None):
    """Unified Collection Counter with sibling modal."""
    if school_slug:
        set_current_db(school_slug)
    return render(request, 'hq_admin_custom/collection_counter.html', {'school_slug': school_slug})

@login_required
def automation_settings(request, school_slug=None):
    """Manage auto-generation, late fee rules, pro-rata, etc."""
    if school_slug:
        set_current_db(school_slug)
    settings_obj, created = SchoolFeeSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        settings_obj.generation_day = int(request.POST.get('generation_day', 1))
        settings_obj.due_date_offset = int(request.POST.get('due_date_offset', 15))
        settings_obj.late_fee_penalty = Decimal(request.POST.get('late_fee_penalty', 0))
        # Additional fields (add to model if needed)
        settings_obj.grace_period_days = int(request.POST.get('grace_period_days', 0))
        settings_obj.penalty_type = request.POST.get('penalty_type', 'percentage')
        settings_obj.penalty_amount = Decimal(request.POST.get('penalty_amount', 0))
        settings_obj.max_penalty = Decimal(request.POST.get('max_penalty', 0))
        settings_obj.pro_rata_type = request.POST.get('pro_rata_type', 'full')
        settings_obj.notify_email = request.POST.get('notify_email') == 'on'
        settings_obj.save()
        messages.success(request, "Automation settings updated.")
        return redirect('automation_settings', school_slug=school_slug)
    return render(request, 'hq_admin_custom/automation_settings.html', {'settings': settings_obj, 'school_slug': school_slug})

@login_required
def reports_view(request, school_slug=None):
    """Comprehensive reports with filters and export."""
    if school_slug:
        set_current_db(school_slug)
    report_type = request.GET.get('type', 'collection')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    class_filter = request.GET.get('class')
    mode_filter = request.GET.get('mode')
    export = request.GET.get('export')

    if report_type == 'collection':
        qs = PaymentTransaction.objects.select_related('student')
        if from_date:
            qs = qs.filter(transaction_date__gte=from_date)
        if to_date:
            qs = qs.filter(transaction_date__lte=to_date)
        if class_filter:
            qs = qs.filter(student__student_class=class_filter)
        if mode_filter:
            qs = qs.filter(payment_mode=mode_filter)
        data = qs.order_by('-transaction_date')
        total = qs.aggregate(Sum('amount'))['amount__sum'] or 0
        if export == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="collection_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Receipt No', 'Student', 'Class', 'Amount', 'Date', 'Mode'])
            for p in data:
                writer.writerow([p.receipt_number, p.student.full_name, f"{p.student.student_class}-{p.student.student_section}", p.amount, p.transaction_date, p.get_payment_mode_display()])
            return response
    elif report_type == 'defaulters':
        data = Student.objects.filter(fee_records__status__in=['overdue','partial']).distinct().annotate(
            pending=Coalesce(Sum(F('fee_records__total_amount')-F('fee_records__paid_amount')), Decimal('0'))
        ).filter(pending__gt=0).order_by('-pending')
        total = data.count()
        if export == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="defaulters_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['Student Name', 'Roll No', 'Father Name', 'Class', 'Pending Amount'])
            for s in data:
                writer.writerow([s.full_name, s.roll_number, s.father_name, f"{s.student_class}-{s.student_section}", s.pending])
            return response
    elif report_type == 'receipt_book':
        data = PaymentTransaction.objects.select_related('student').order_by('-transaction_date')
        total = data.count()
        if export == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="receipt_book.csv"'
            writer = csv.writer(response)
            writer.writerow(['Receipt No', 'Student', 'Date', 'Amount', 'Mode'])
            for p in data:
                writer.writerow([p.receipt_number, p.student.full_name, p.transaction_date, p.amount, p.get_payment_mode_display()])
            return response
    else:
        data = None
        total = 0

    classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')
    modes = PaymentTransaction.MODE_CHOICES
    context = {
        'school_slug': school_slug,
        'report_type': report_type,
        'data': data,
        'total': total,
        'classes': classes,
        'modes': modes,
        'from_date': from_date,
        'to_date': to_date,
        'selected_class': class_filter,
        'selected_mode': mode_filter,
    }
    return render(request, 'hq_admin_custom/reports.html', context)

@login_required
def audit_log_view(request, school_slug=None):
    """Display audit logs."""
    if school_slug:
        set_current_db(school_slug)
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, 'hq_admin_custom/audit_log.html', {'logs': logs, 'school_slug': school_slug})

@login_required
def defaulters_list_upgraded(request, school_slug=None):
    """Improved defaulters page with bulk reminders."""
    if school_slug:
        set_current_db(school_slug)
    students = Student.objects.filter(fee_records__status__in=['overdue','partial']).distinct().annotate(
        pending=Coalesce(Sum(F('fee_records__total_amount')-F('fee_records__paid_amount')), Decimal('0'))
    ).filter(pending__gt=0).order_by('-pending')
    context = {'students': students, 'school_slug': school_slug}
    return render(request, 'hq_admin_custom/defaulters_upgraded.html', context)

# API endpoint for sibling search
@login_required
def sibling_search_api(request, school_slug=None):
    father_cnic = request.GET.get('father_cnic')
    if not father_cnic:
        return JsonResponse({'error': 'No CNIC provided'}, status=400)
    students = Student.objects.filter(b_form=father_cnic).values('id', 'full_name', 'roll_number', 'student_class', 'student_section')
    siblings = []
    for s in students:
        pending = FeeRecord.objects.filter(student_id=s['id'], status__in=['pending','partial','overdue']).aggregate(total=Sum(F('total_amount')-F('paid_amount')))['total'] or 0
        siblings.append({**s, 'pending_total': str(pending)})
    return JsonResponse({'siblings': siblings})

# Manual fee generation endpoint
@login_required
def manual_fee_generation(request, school_slug=None):
    if request.method == 'POST':
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        student_id = request.POST.get('student_id')
        class_name = request.POST.get('class')
        # Implement generation logic using existing generate_fees_for_month but with filters
        from apsokara.fee_views import generate_fees_for_month
        count = generate_fees_for_month(year, month)  # extend to accept filters
        messages.success(request, f"Generated {count} fee records for {month}/{year}.")
        return redirect('automation_settings', school_slug=school_slug)
