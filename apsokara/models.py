from django.db import models
from django.utils import timezone

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Subject Name")
    def __str__(self):
        return self.name

class Teacher(models.Model):
    WING_CHOICES = [('None', 'None'), ('Boys', 'Boys'), ('Girls', 'Girls')]
    RELIGION_CHOICES = [('Islam', 'Islam'), ('Christianity', 'Christianity'), ('Other', 'Other')]

    full_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=15, unique=True)
    dob = models.DateField(verbose_name="Date of Birth")
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, default='Islam')
    contact = models.CharField(max_length=15)
    address = models.TextField()

    is_class_teacher = models.BooleanField(default=False)
    assigned_class = models.CharField(max_length=10, blank=True, null=True)
    assigned_section = models.CharField(max_length=10, blank=True, null=True)
    assigned_wing = models.CharField(max_length=10, choices=WING_CHOICES, default='None')

    def __str__(self):
        return self.full_name

class Student(models.Model):
    RELIGION_CHOICES = [('Islam', 'Islam'), ('Christianity', 'Christianity'), ('Other', 'Other')]
    PROVINCE_CHOICES = [('Punjab', 'Punjab'), ('Sindh', 'Sindh'), ('KPK', 'KPK'), ('Balochistan', 'Balochistan'), ('Gilgit', 'Gilgit'), ('AJK', 'AJK')]
    WING_CHOICES = [('Boys', 'Boys'), ('Girls', 'Girls')]

    # Basic Info
    full_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    b_form = models.CharField(max_length=20, unique=True, verbose_name="B-Form Number")
    dob = models.DateField(verbose_name="Date of Birth")
    
    # Academic Info
    student_class = models.CharField(max_length=10)
    student_section = models.CharField(max_length=10)
    wing = models.CharField(max_length=10, choices=WING_CHOICES)
    roll_number = models.CharField(max_length=20, unique=True)

    # Personal/Address Info
    nationality = models.CharField(max_length=50, default="Pakistani")
    province = models.CharField(max_length=20, choices=PROVINCE_CHOICES, default='Punjab')
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES, default='Islam')
    parents_phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"

class SubjectAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.CharField(max_length=10)
    section = models.CharField(max_length=10)
    wing = models.CharField(max_length=10, choices=[('Boys', 'Boys'), ('Girls', 'Girls')])

    class Meta:
        unique_together = ('subject', 'student_class', 'section', 'wing')

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10)

class StudentLeave(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
