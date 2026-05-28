from django.urls import path
from . import views

urlpatterns = [
    path("", views.update_school_logo, name="update_school_logo"),
]
