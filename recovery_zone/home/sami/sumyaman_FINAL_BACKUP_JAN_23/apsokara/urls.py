from django.urls import path

urlpatterns = [
    path('attendance/wing/', views.intel_wing_detail, name='intel_wing_detail'),
]
