import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
import django
django.setup()
from django.conf import settings
from django.core.management import call_command
from super_admin.models import SchoolClient

# Add all tenant DBs to settings dynamically
for school in SchoolClient.objects.all():
    db_name = school.db_name
    if db_name not in settings.DATABASES:
        db_config = settings.DATABASES['default'].copy()
        db_config['NAME'] = db_name
        settings.DATABASES[db_name] = db_config

# Migrate each
for school in SchoolClient.objects.all():
    db_name = school.db_name
    print(f"Migrating {db_name}...")
    try:
        call_command('migrate', database=db_name, interactive=False, verbosity=0)
        print(f"✅ Done {db_name}")
    except Exception as e:
        print(f"❌ Failed {db_name}: {e}")
