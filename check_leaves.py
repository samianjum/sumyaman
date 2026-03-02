import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
django.setup()

from apsokara.models import Student, StudentLeave

print('\n--- DATABASE LEAVE CHECK ---')
leaves = StudentLeave.objects.all()
if not leaves.exists():
    print("❌ Database mein koi bhi leave record nahi mila!")
else:
    for l in leaves:
        print(f"ID: {l.id} | Student: {l.student.full_name}")
        print(f"Class: {l.student.student_class} | Section: {l.student.student_section}")
        print(f"Status: {l.status} | Dates: {l.from_date} to {l.to_date}")
        print("-" * 30)

print(f'\nTotal Leaves in DB: {leaves.count()}')
