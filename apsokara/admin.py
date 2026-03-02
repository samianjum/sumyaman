from django.contrib import admin
from .models import Teacher, Subject, SubjectAssignment, Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'roll_number', 'student_class', 'student_section', 'wing')
    search_fields = ('full_name', 'roll_number', 'b_form')
    list_filter = ('student_class', 'student_section', 'wing')

    fieldsets = (
        ("Personal Information", {
            'fields': ('full_name', 'father_name', 'b_form', 'dob', 'religion', 'nationality', 'province')
        }),
        ("Academic Details", {
            'fields': ('roll_number', 'student_class', 'student_section', 'wing')
        }),
        ("Contact & Address", {
            'fields': ('parents_phone', 'address')
        }),
    )

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'cnic', 'is_class_teacher')
    inlines = [
        type('SubjectAssignmentInline', (admin.TabularInline,), {'model': SubjectAssignment, 'extra': 1})
    ]
    fieldsets = (
        ("Personal Info", {'fields': ('full_name', 'father_name', 'cnic', 'dob', 'religion', 'contact', 'address')}),
        ("Class Teacher Status", {'fields': ('is_class_teacher', 'assigned_class', 'assigned_section', 'assigned_wing')}),
    )
    class Media:
        js = ('admin/js/teacher_toggle.js',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
