#!/usr/bin/env python3
"""
Final APS Fix – Adds extra_head block to base.html and corrects reverse URL error.
Run once from /home/sami/sumyaman/
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "hq_admin_custom"

def fix_base_html():
    """Add {% block extra_head %} to base.html if missing."""
    base_path = TEMPLATES_DIR / "base.html"
    if not base_path.exists():
        print("❌ base.html not found!")
        return

    with open(base_path, 'r') as f:
        content = f.read()

    # Check if extra_head block already exists
    if "{% block extra_head %}" in content:
        print("✓ extra_head block already present in base.html")
        return

    # Insert the block just before the closing </head> tag
    new_block = """
    {% block extra_head %}{% endblock %}
</head>"""
    new_content = content.replace("</head>", new_block)
    if new_content != content:
        with open(base_path, 'w') as f:
            f.write(new_content)
        print("✅ Added {% block extra_head %} to base.html")
    else:
        print("⚠️ Could not modify base.html – check file structure")

def fix_student_fee_view():
    """Fix reverse URL error in student_fee_view.html."""
    template_path = TEMPLATES_DIR / "student_fee_view.html"
    if not template_path.exists():
        print("⚠️ student_fee_view.html not found, skipping.")
        return

    with open(template_path, 'r') as f:
        content = f.read()

    # Original: {% url 'student_fee_view' school_slug=school_slug student_id=s.id %}
    # Should be: {% url 'student_fee_view' student_id=s.id %}
    new_content = re.sub(
        r"{% url ['\"]student_fee_view['\"]\s+school_slug=\w+\s+student_id=([^}\s]+)%}",
        r"{% url 'student_fee_view' student_id=\1 %}",
        content
    )
    # Also fix any other occurrence where school_slug appears as an extra kwarg
    new_content = re.sub(
        r"url\('student_fee_view',\s*school_slug=\w+,\s*student_id=([^)]+)\)",
        r"url('student_fee_view', student_id=\1)",
        new_content
    )

    if new_content != content:
        with open(template_path, 'w') as f:
            f.write(new_content)
        print("✅ Fixed reverse URL error in student_fee_view.html")
    else:
        print("✓ student_fee_view.html already correct")

def main():
    print("🔧 Applying final fixes...")
    fix_base_html()
    fix_student_fee_view()
    print("\n✅ All fixes applied!")
    print("➡️ Restart your Django server and refresh the fee collection page.")
    print("➡️ The fee UI should now display correctly with all styles.")

if __name__ == "__main__":
    main()
