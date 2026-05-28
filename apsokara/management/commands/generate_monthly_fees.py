# manage.py generate_monthly_fees
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
