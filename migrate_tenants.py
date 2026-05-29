from django.core.management import call_command
from super_admin.models import SchoolClient

for school in SchoolClient.objects.all():
    print(f"Migrating {school.db_name}...")
    call_command('migrate', database=school.slug)
