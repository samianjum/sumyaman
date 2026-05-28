#!/usr/bin/env python3
# fix_fee_urls.py
import re
from pathlib import Path

urls_path = Path("/home/sami/sumyaman/apsokara/urls.py")

with open(urls_path, 'r') as f:
    content = f.read()

# Check if fee_views already imported
if "from .fee_views import" in content:
    print("✅ Fee views already imported. No changes needed.")
    exit(0)

# Find the last import line or the start of urlpatterns
import_pattern = re.compile(r'^from .* import .*$', re.MULTILINE)
matches = list(import_pattern.finditer(content))
if matches:
    last_import_end = matches[-1].end()
    # Insert after last import
    new_import = "\nfrom .fee_views import (\n    fee_structure_view,\n    delete_fee_structure,\n    fee_collection_view,\n    fee_collection_print,\n    family_payment_view,\n    defaulters_list,\n    fee_reports,\n    student_fee_view,\n)\n"
    new_content = content[:last_import_end] + new_import + content[last_import_end:]
else:
    # No imports? Insert after the shebang or at top
    new_content = "from .fee_views import (\n    fee_structure_view,\n    delete_fee_structure,\n    fee_collection_view,\n    fee_collection_print,\n    family_payment_view,\n    defaulters_list,\n    fee_reports,\n    student_fee_view,\n)\n\n" + content

with open(urls_path, 'w') as f:
    f.write(new_content)

print("✅ Added fee_views imports to apsokara/urls.py")
