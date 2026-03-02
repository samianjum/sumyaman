from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student, Teacher, Attendance
from django.utils import timezone

# ... (baaki views wahi rahengle, hum sirf profile view update kar rahe hain)
