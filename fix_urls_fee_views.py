#!/usr/bin/env python3
# fix_urls_fee_views.py
import re
from pathlib import Path

urls_path = Path("/home/sami/sumyaman/apsokara/urls.py")

with open(urls_path, 'r') as f:
    content = f.read()

# Replace all occurrences of 'views.fee_' with just 'fee_'
# but careful not to break other things.
# Better: replace each pattern individually.

replacements = [
    ('views.fee_structure_view', 'fee_structure_view'),
    ('views.delete_fee_structure', 'delete_fee_structure'),
    ('views.fee_collection_view', 'fee_collection_view'),
    ('views.fee_collection_print', 'fee_collection_print'),
    ('views.family_payment_view', 'family_payment_view'),
    ('views.defaulters_list', 'defaulters_list'),
    ('views.fee_reports', 'fee_reports'),
    ('views.student_fee_view', 'student_fee_view'),
]

new_content = content
for old, new in replacements:
    new_content = new_content.replace(old, new)

with open(urls_path, 'w') as f:
    f.write(new_content)

print("✅ Fixed fee view references in urls.py")
