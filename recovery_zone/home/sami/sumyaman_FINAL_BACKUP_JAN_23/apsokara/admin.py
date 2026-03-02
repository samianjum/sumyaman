from .models import StudentPromotion
from django.contrib import admin
from django.shortcuts import render
from .models import *

# --- 1. NEW PROMOTION CONSOLE SECTION ---
class PromotionAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Abhi sirf ek khali page (Placeholder) rakhte hain
        # Yahan aap mujhe bataoge ke kaunse buttons aur filters chahiye
        context = {
            'title': '🚀 Student Promotion & Migration Console',
            'opts': self.model._meta,
        }
        return render(request, 'admin/apsokara/promotion_console.html', context)

# --- 2. ARCHIVE VAULT ---
class ArchiveAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        from django.db.models import Count
        sessions = Student.objects.values('session_year').annotate(total=Count('id')).order_by('-session_year')
        selected_year = request.GET.get('year')
        detailed_data = None
        if selected_year:
            detailed_data = {
                'students': Student.objects.filter(session_year=selected_year),
                'attendance': Attendance.objects.filter(student__session_year=selected_year).count(),
            }
        context = {'sessions': sessions, 'selected_year': selected_year, 'detailed_data': detailed_data, 'title': '🏛️ Archive Vault', 'opts': self.model._meta}
        return render(request, 'admin/apsokara/archive.html', context)

# --- 3. ORIGINAL MODULES (KEEPING THEM SAFE) ---
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'student_class', 'session_year', 'status')
    list_filter = ('student_class', 'session_year', 'status')

def safe_reg(model, admin_class=None):
    try:
        if admin.site.is_registered(model): admin.site.unregister(model)
        admin.site.register(model, admin_class) if admin_class else admin.site.register(model)
    except: pass

safe_reg(Student, StudentAdmin)
safe_reg(StudentPromotion, PromotionAdmin) # Naya Section
safe_reg(SchoolArchive, ArchiveAdmin)
safe_reg(Teacher)
safe_reg(Subject)
safe_reg(SubjectAssignment)
safe_reg(Attendance)
safe_reg(StudentLeave)

print("✅ All modules restored with new Promotion Console!")

admin.site.register(ExamWindow)
