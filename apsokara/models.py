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
    profile_pic = models.ImageField(upload_to='teachers/', null=True, blank=True)

    is_class_teacher = models.BooleanField(default=False)
    assigned_class = models.CharField(max_length=10, blank=True, null=True)
    assigned_section = models.CharField(max_length=10, blank=True, null=True)
    assigned_wing = models.CharField(max_length=10, choices=WING_CHOICES, default='None')

    def __str__(self):
        return self.full_name

class Student(models.Model):
    RELIGION_CHOICES = [('Islam', 'Islam'), ('Christianity', 'Christianity'), ('Other', 'Other')]
    PROVINCE_CHOICES = [('Punjab', 'Punjab'), ('Sindh', 'Sindh'), ('KPK', 'KPK'), ('Balochistan', 'Balochistan'), ('Gilgit', 'Gilgit'), ('AJK', 'AJK')]
    WING_CHOICES = [('None', 'None'), ('Boys', 'Boys'), ('Girls', 'Girls')]

    full_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    

    b_form = models.CharField(max_length=20, unique=True, verbose_name="B-Form Number")
    father_cnic = models.CharField(max_length=15, verbose_name="Father CNIC", help_text="Father\'s CNIC for family payments")
    dob = models.DateField(verbose_name="Date of Birth")
    profile_pic = models.ImageField(upload_to='students/', null=True, blank=True)

    student_class = models.CharField(max_length=10)
    student_section = models.CharField(max_length=10)
    wing = models.CharField(max_length=10, choices=WING_CHOICES)
    custom_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Override monthly fee if set')
    roll_number = models.CharField(max_length=20, unique=True)

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
    wing = models.CharField(max_length=10, choices=Student.WING_CHOICES, blank=True, null=True, default='None')

    class Meta:
        unique_together = ('subject', 'student_class', 'section', 'wing')

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10)
    marked_by = models.TextField(default='Unknown')
    face_status = models.CharField(max_length=20, default='unknown')
    edit_count = models.IntegerField(default=0)

class StudentLeave(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    attachment = models.FileField(upload_to='leaves/', null=True, blank=True)

class DailyDiary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student_class = models.CharField(max_length=10)
    section = models.CharField(max_length=10)
    wing = models.CharField(max_length=10, choices=Student.WING_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateField(default=timezone.now)
    attachments = models.FileField(upload_to='diaries/', null=True, blank=True)

class SchoolNews(models.Model):
    content = models.TextField()
    target_role = models.CharField(max_length=50, default='All')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Exam(models.Model):
    name = models.CharField(max_length=100)
    term = models.CharField(max_length=50)
    session = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.session})"

class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)


# ---------- FEE MANAGEMENT MODELS ----------
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

class FeeStructure(models.Model):
    student_class = models.CharField(max_length=10, unique=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    grace_period_days = models.IntegerField(default=0, help_text="Days after due date before penalty applies")
    penalty_type = models.CharField(max_length=20, choices=[('percentage','Percentage'),('fixed','Fixed')], default='percentage')
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Penalty amount or percentage")
    max_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Maximum penalty (0 = no max)")
    pro_rata_type = models.CharField(max_length=20, choices=[('full','Full Month'),('half','Half Month'),('daily','Daily')], default='full')
    notify_email = models.BooleanField(default=False, help_text="Send email reminders to defaulters")


    def __str__(self):
        return f"Class {self.student_class} - ₹{self.monthly_fee}"

class FeeRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='fee_records')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    waived = models.BooleanField(default=False)
    waived_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    grace_period_days = models.IntegerField(default=0, help_text="Days after due date before penalty applies")
    penalty_type = models.CharField(max_length=20, choices=[('percentage','Percentage'),('fixed','Fixed')], default='percentage')
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Penalty amount or percentage")
    max_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Maximum penalty (0 = no max)")
    pro_rata_type = models.CharField(max_length=20, choices=[('full','Full Month'),('half','Half Month'),('daily','Daily')], default='full')
    notify_email = models.BooleanField(default=False, help_text="Send email reminders to defaulters")


    class Meta:
        unique_together = ('student', 'month', 'year')
        ordering = ['-year', '-month']

    @property
    def pending_amount(self):
        return self.total_amount - self.paid_amount

    def update_status(self):
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'overdue' if self.due_date < timezone.now().date() else 'pending'
        self.save(update_fields=['status'])

class PaymentTransaction(models.Model):
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('online', 'Online'),
    ]
    receipt_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    transaction_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True)
    fee_records = models.ManyToManyField('FeeRecord', related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt #{self.receipt_number} - ₹{self.amount}"

class SchoolFeeSettings(models.Model):
    generation_day = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(31)])
    due_date_offset = models.IntegerField(default=15, help_text="Days after generation when fee is due")
    late_fee_penalty = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentage added to overdue amount")
    updated_at = models.DateTimeField(auto_now=True)

    grace_period_days = models.IntegerField(default=0, help_text="Days after due date before penalty applies")
    penalty_type = models.CharField(max_length=20, choices=[('percentage','Percentage'),('fixed','Fixed')], default='percentage')
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Penalty amount or percentage")
    max_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Maximum penalty (0 = no max)")
    pro_rata_type = models.CharField(max_length=20, choices=[('full','Full Month'),('half','Half Month'),('daily','Daily')], default='full')
    notify_email = models.BooleanField(default=False, help_text="Send email reminders to defaulters")


    def __str__(self):
        return f"Settings (gen day: {self.generation_day})"


# ---------- NEW FEE MODELS (Upgrade) ----------
class FeeGenerationLog(models.Model):
    generated_on = models.DateTimeField(auto_now_add=True)
    trigger = models.CharField(max_length=20, choices=[('auto', 'Auto Cron'), ('manual', 'Manual')])
    month = models.IntegerField()
    year = models.IntegerField()
    students_processed = models.IntegerField()
    records_created = models.IntegerField()
    skipped_count = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)

    def __str__(self):
        return f"{self.trigger} - {self.month}/{self.year} on {self.generated_on}"

class AuditLog(models.Model):
    user = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=20, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

class LateFeeLog(models.Model):
    fee_record = models.ForeignKey('FeeRecord', on_delete=models.CASCADE, related_name='late_fee_logs')
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_on = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"Late fee ₹{self.penalty_amount} on {self.fee_record}"

