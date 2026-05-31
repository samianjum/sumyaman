# management/commands/auto_generate_monthly_fees.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apsokara.fee_views import generate_fees_for_month
from apsokara.models import SchoolFeeSettings

class Command(BaseCommand):
    help = 'Auto-generate fees for current month (to be run by cron)'

    def handle(self, *args, **options):
        settings = SchoolFeeSettings.objects.first()
        if not settings:
            self.stdout.write(self.style.ERROR('No fee settings found.'))
            return
        today = timezone.now().date()
        year = today.year
        month = today.month
        # Only generate if we are after generation day
        if today.day >= settings.generation_day:
            count = generate_fees_for_month(year, month)
            self.stdout.write(self.style.SUCCESS(f'Generated {count} fee records for {month}/{year}'))
        else:
            self.stdout.write('Not yet generation day.')
