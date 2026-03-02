import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
django.setup()

from apsokara.models import StudentLeave, Student

print("\n" + "="*50)
print("1. TOTAL LEAVES COUNT IN DB:", StudentLeave.objects.count())

print("\n2. ALL LEAVES DETAILS:")
leaves = StudentLeave.objects.all()
if not leaves:
    print("   ❌ Database mein koi leave record nahi hai!")
else:
    for l in leaves:
        s = l.student
        print(f"   - ID: {l.id} | Student: {s.full_name} | Class: '{s.student_class}' | Section: '{s.student_section}' | Status: '{l.status}'")

print("\n3. CLASS 2-D SPECIFIC CHECK:")
class_2d_students = Student.objects.filter(student_class='2', student_section='D')
print(f"   - Students found in 2-D: {class_2d_students.count()}")
leaves_2d = StudentLeave.objects.filter(student__in=class_2d_students)
print(f"   - Leaves found for these students: {leaves_2d.count()}")
print("="*50 + "\n")
