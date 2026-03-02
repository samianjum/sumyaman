from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from datetime import date

@staff_member_required
def attendance_main(request):
    # Aapka asli logic yahan aayega
    return render(request, 'admin_intel/attendance/main.html', {})
