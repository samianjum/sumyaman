# fix_admin_urls.py
import re
from pathlib import Path

urls_path = Path("/home/sami/sumyaman/sumyaman_pro/urls.py")

with open(urls_path, 'r') as f:
    content = f.read()

# Define a wrapper function to ignore school_slug
wrapper_code = """
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import logout
from django.shortcuts import redirect

def admin_wrapper(request, school_slug, **kwargs):
    \"\"\"Wrapper to remove school_slug from the URL and forward to admin site.\"\"\"
    # Preserve the original path without the school slug
    original_path = request.path
    new_path = original_path.replace(f'/s/{school_slug}/admin', '/admin', 1)
    request.path = new_path
    request.path_info = new_path
    # Call the admin site's URL resolver
    return admin.site.urls(request, **kwargs)

"""

# Check if wrapper already exists
if "admin_wrapper" in content:
    print("Wrapper already present, skipping...")
    exit(0)

# Insert wrapper after imports
import_pattern = re.compile(r'^(from django\.urls import .*)$', re.MULTILINE)
match = import_pattern.search(content)
if match:
    insert_pos = match.end()
    content = content[:insert_pos] + "\n" + wrapper_code + content[insert_pos:]
else:
    # Fallback: add at the top
    content = wrapper_code + content

# Replace the admin include line to use the wrapper
# Find the line: path('s/<slug:school_slug>/admin/', admin.site.urls),
pattern = re.compile(r"path\('s/<slug:school_slug>/admin/', admin\.site\.urls\),")
if pattern.search(content):
    content = pattern.sub("path('s/<slug:school_slug>/admin/', admin_wrapper),", content)
else:
    print("Could not find the admin include line, manual fix needed.")
    exit(1)

# Also ensure the login wrapper remains (it's already fine)
with open(urls_path, 'w') as f:
    f.write(content)

print("✅ Fixed admin URLs by adding wrapper that strips school_slug")
