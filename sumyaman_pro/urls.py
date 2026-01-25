from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

# Secret Redirect Function
def secret_admin_redirect(request):
    if request.user.is_authenticated and request.user.is_superuser:
        # Ye apko Streamlit wale port par bhej dega
        return redirect("http://127.0.0.1:8505")
    else:
        return redirect("/admin/login/?next=/secret-hq/")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('secret-hq-portal-2026/', secret_admin_redirect), # Aapka secret URL
]
