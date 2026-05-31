#!/usr/bin/env python
from django.core.management.base import BaseCommand
from django.utils import timezone
from apsokara.models import FeeRecord, SchoolFeeSettings, LateFeeLog
from decimal import Decimal

class Command(BaseCommand):
    help = 'Apply late fees to overdue fee records'

    def handle(self, *args, **options):
        settings = SchoolFeeSettings.objects.first()
        if not settings or settings.late_fee_penalty == 0:
            self.stdout.write("No late fee settings or penalty is zero. Exiting.")
            return
        today = timezone.now().date()
        # Overdue records where due date + grace period < today
        overdue_records = FeeRecord.objects.filter(
            status__in=['pending', 'partial'],
            due_date__lt=today - timezone.timedelta(days=settings.grace_period_days)
        )
        count = 0
        for record in overdue_records:
            pending = record.pending_amount
            penalty = pending * (settings.late_fee_penalty / Decimal(100))
            # Cap at maximum if needed (default 100% of pending)
            max_penalty = pending  # or use settings.max_late_fee if added
            penalty = min(penalty, max_penalty)
            if penalty > 0:
                # Apply penalty by increasing total_amount? Or add a separate field?
                # We'll add to total_amount for simplicity, but you can store separately.
                record.total_amount += penalty
                record.save()
                LateFeeLog.objects.create(fee_record=record, penalty_amount=penalty)
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Applied late fees to {count} records.'))
