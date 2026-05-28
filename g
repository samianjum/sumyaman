#!/usr/bin/env python3
"""
Fix fee collection reverse URL error – include school_slug in recent-payments URL.
Run once from /home/sami/sumyaman/
"""

import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.absolute() / "templates" / "hq_admin_custom"

def fix_recent_payments_url():
    template_path = TEMPLATES_DIR / "fee_collection.html"
    if not template_path.exists():
        print("❌ fee_collection.html not found!")
        return

    with open(template_path, 'r') as f:
        content = f.read()

    # Replace the meta tag to include school_slug in the URL
    # Current: <meta name="recent-payments-url" content="{% url "fee_recent_payments" %}">
    # Should be: <meta name="recent-payments-url" content="{% url 'fee_recent_payments' school_slug=school_slug %}">
    old_meta = r'<meta name="recent-payments-url" content="{% url ["\']fee_recent_payments["\'] %}"?>'
    new_meta = '<meta name="recent-payments-url" content="{% url \'fee_recent_payments\' school_slug=school_slug %}">'
    
    if re.search(old_meta, content):
        content = re.sub(old_meta, new_meta, content)
        print("✅ Fixed meta tag to include school_slug.")
    else:
        # Fallback: replace exact text
        content = content.replace(
            '<meta name="recent-payments-url" content="{% url "fee_recent_payments" %}">',
            '<meta name="recent-payments-url" content="{% url \'fee_recent_payments\' school_slug=school_slug %}">'
        )
        content = content.replace(
            "<meta name=\"recent-payments-url\" content=\"{% url 'fee_recent_payments' %}\">",
            "<meta name=\"recent-payments-url\" content=\"{% url 'fee_recent_payments' school_slug=school_slug %}\">"
        )
        print("✅ Replaced meta tag (alternative pattern).")

    with open(template_path, 'w') as f:
        f.write(content)
    print("✅ fee_collection.html updated.")

def main():
    print("🔧 Fixing reverse URL for recent payments...")
    fix_recent_payments_url()
    print("\n✅ Done! Restart Django and reload the fee collection page.")

if __name__ == "__main__":
    main()
