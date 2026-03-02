from django.db import models

class Teacher(models.Model):
    full_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200, null=True, blank=True)
    cnic = models.CharField(max_length=50, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    wing = models.CharField(max_length=10, choices=[('Boys', 'Boys'), ('Girls', 'Girls')], default='Boys')
    incharge_class = models.CharField(max_length=20, null=True, blank=True)
    incharge_section = models.CharField(max_length=20, null=True, blank=True)
    is_class_incharge = models.BooleanField(default=False)
    def __str__(self): return self.full_name

class Student(models.Model):
    full_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200, null=True, blank=True)
    cnic = models.CharField(max_length=50, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    wing = models.CharField(max_length=10, choices=[('Boys', 'Boys'), ('Girls', 'Girls')], default='Boys')
    student_class = models.CharField(max_length=20, null=True, blank=True)
    student_section = models.CharField(max_length=20, null=True, blank=True)
    session_year = models.CharField(max_length=10, default='2024-25')
    status = models.CharField(max_length=20, default='Active')
    roll_no = models.CharField(max_length=20, null=True, blank=True)
    parent_phone = models.CharField(max_length=15, default="03000000000")
    def __str__(self): return self.full_name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, default="N/A")
    def __str__(self): return self.name

class SubjectAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=20)
    section = models.CharField(max_length=20)
    wing = models.CharField(max_length=10, choices=[('Boys', 'Boys'), ('Girls', 'Girls')], default='Boys')
    def __str__(self): return f"{self.subject.name} - {self.class_name}{self.section}"

    is_active = models.BooleanField(default=True)

class Complain(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('P', 'Present'), ('A', 'Absent')])
    edit_count = models.IntegerField(default=0)
    wing = models.CharField(max_length=10, null=True, blank=True)
    student_class = models.CharField(max_length=20, null=True, blank=True)
    student_section = models.CharField(max_length=20, null=True, blank=True)
    session_year = models.CharField(max_length=10, default='2024-25')
    status = models.CharField(max_length=20, default='Active')

class SchoolNotice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

class StudentLeave(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=20)
    wing = models.CharField(max_length=10)
    section = models.CharField(max_length=20, null=True, blank=True)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return f"{self.student.full_name} - {self.status}"

class SchoolArchive(Student):
    class Meta:
        proxy = True
        verbose_name = "Digital Archive Vault"
        verbose_name_plural = "Digital Archive Vaults"

class StudentPromotion(Student):
    class Meta:
        proxy = True
        verbose_name = "🚀 Student Promotion Console"
        verbose_name_plural = "🚀 Student Promotion Console"

class ExamWindow(models.Model):
    title = models.CharField(max_length=100, help_text="e.g. Mid Term 2025")
    session_year = models.CharField(max_length=10, default='2024-25')
    is_active = models.BooleanField(default=True, help_text="Check to open mark entry for teachers")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.session_year})"

    class Meta:
        verbose_name = "Exam Window"
        verbose_name_plural = "Exam Windows"
