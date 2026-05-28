import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
django.setup()
from super_admin.models import SchoolClient

for school in SchoolClient.objects.all():
    old = school.db_name
    new = old.replace('.sqlite3', '_db').replace('.', '_')
    if old != new:
        school.db_name = new
        school.save(using='default')
        print(f"Renamed: {old} -> {new}")
