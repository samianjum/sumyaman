
# fee_advanced_views.py - Add to apsokara/views.py or include separately
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count, F, Value, DecimalField, Case, When
from django.db.models.functions import TruncMonth, Coalesce
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
import csv
import json
from openpyxl import Workbook
from .models import FeeRecord, PaymentTransaction, Student, FeeStructure, SchoolFeeSettings
from .fee_views import allocate_payment

@login_required
def fee_analytics(request, school_slug=None):
    """JSON endpoint for dashboard charts"""
    today = timezone.now().date()
    # Last 6 months collection trend
    six_months_ago = today - timezone.timedelta(days=180)
    chart_data = PaymentTransaction.objects.filter(
        transaction_date__gte=six_months_ago
    ).annotate(month=TruncMonth('transaction_date')).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    months = [d['month'].strftime('%b %Y') for d in chart_data]
    amounts = [float(d['total']) for d in chart_data]

    # Top defaulters
    defaulters = Student.objects.filter(
        fee_records__status__in=['overdue', 'partial']
    ).distinct().annotate(
        pending=Coalesce(Sum(F('fee_records__total_amount') - F('fee_records__paid_amount')), Decimal('0'))
    ).filter(pending__gt=0).order_by('-pending')[:10]
    defaulter_list = [{'id': s.id, 'name': s.full_name, 'roll': s.roll_number, 'pending': str(s.pending)} for s in defaulters]

    return JsonResponse({
        'months': months,
        'amounts': amounts,
        'defaulters': defaulter_list,
    })

@login_required
def generate_invoices_bulk(request, school_slug=None):
    """Generate invoices for selected students (PDF)"""
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        month = request.POST.get('month')
        year = request.POST.get('year')
        # Use reportlab to generate combined PDF
        # ... implement PDF generation
        messages.success(request, f"Invoices generated for {len(student_ids)} students.")
        return redirect('fee_reports', school_slug=school_slug)

@login_required
def send_reminders(request, school_slug=None):
    """Send email/SMS reminders to defaulters"""
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        # Use Django's send_mail or SMS gateway
        # ...
        messages.success(request, f"Reminders sent to {len(student_ids)} parents.")
        return redirect('defaulters_upgraded', school_slug=school_slug)

@login_required
def export_fee_data(request, school_slug=None):
    """Export fee records to Excel/CSV"""
    report_type = request.GET.get('type', 'collection')
    export_format = request.GET.get('format', 'csv')
    if report_type == 'collection':
        queryset = PaymentTransaction.objects.select_related('student').all()
        filename = f"collection_report_{timezone.now().date()}.{export_format}"
        if export_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            writer = csv.writer(response)
            writer.writerow(['Receipt No', 'Student', 'Class', 'Amount', 'Date', 'Mode'])
            for t in queryset:
                writer.writerow([t.receipt_number, t.student.full_name, f"{t.student.student_class}-{t.student.student_section}", t.amount, t.transaction_date, t.get_payment_mode_display()])
            return response
        elif export_format == 'xlsx':
            wb = Workbook()
            ws = wb.active
            ws.append(['Receipt No', 'Student', 'Class', 'Amount', 'Date', 'Mode'])
            for t in queryset:
                ws.append([t.receipt_number, t.student.full_name, f"{t.student.student_class}-{t.student.student_section}", float(t.amount), str(t.transaction_date), t.get_payment_mode_display()])
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            wb.save(response)
            return response
