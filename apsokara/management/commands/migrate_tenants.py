#!/usr/bin/env python
from django.core.management import call_command
from django.conf import settings
from super_admin.models import SchoolClient

def run():
    for school in SchoolClient.objects.all():
        db_alias = school.slug
        if db_alias in settings.DATABASES:
            print(f"Migrating {school.name} ({db_alias})...")
            call_command('migrate', database=db_alias)

if __name__ == '__main__':
    run()
