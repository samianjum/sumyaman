from django.shortcuts import render, redirect, get_object_or_404
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
