import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
django.setup()

from apsokara.models import Student

print("\n--- DATABASE STATUS ---")
students = Student.objects.all()
if not students:
    print("Database is currently empty.")
else:
    print(f"Total Students: {students.count()}")
    for s in students:
        print(f"Name: {s.full_name} | Roll: {s.roll_number} | B-Form: {s.b_form}")
print("-----------------------\n")
