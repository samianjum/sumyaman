#!/usr/bin/env python
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from apsokara.models import Student, FeeRecord, SchoolFeeSettings
from decimal import Decimal

class Command(BaseCommand):
    help = 'Send email reminders to defaulters'

    def handle(self, *args, **options):
        settings_obj = SchoolFeeSettings.objects.first()
        if not settings_obj or not settings_obj.notify_email:
            self.stdout.write("Email notifications disabled.")
            return
        defaulters = Student.objects.filter(fee_records__status__in=['overdue','partial']).distinct()
        sent = 0
        for student in defaulters:
            pending = sum(r.pending_amount for r in student.fee_records.filter(status__in=['overdue','partial']))
            if pending <= 0:
                continue
            subject = "Fee Payment Reminder"
            message = f"Dear Parent,\n\nReminder: Fee of ₹{pending:.2f} is overdue for {student.full_name} (Roll: {student.roll_number}). Please clear dues.\n\nRegards,\nAccounts"
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student.parents_phone + "@sms.example.com"], fail_silently=True)
                sent += 1
            except Exception as e:
                self.stdout.write(f"Failed: {e}")
        self.stdout.write(f"Sent reminders to {sent} defaulters.")
