import re

with open('mobile_app.py', 'r') as f:
    content = f.read()

# HTML_TEMPLATE ki body nikaalna
template_match = re.search(r"(HTML_TEMPLATE\s*=\s*'''|HTML_TEMPLATE\s*=\s*\"\"\")(.*?)('''|\"\"\")", content, re.DOTALL)

if template_match:
    prefix = template_match.group(1)
    body = template_match.group(2)
    suffix = template_match.group(3)

    ifs = len(re.findall(r'{% if', body))
    endifs = len(re.findall(r'{% endif %}', body))

    if ifs > endifs:
        diff = ifs - endifs
        # Body ke end mein missing endifs add karna
        fixed_body = body + "\n" + ("{% endif %}\n" * diff)
        new_content = content.replace(body, fixed_body)

        with open('mobile_app.py', 'w') as f:
            f.write(new_content)
        print(f"✅ Success! Added {diff} missing endif(s).")
    else:
        print("✅ Counts are already balanced!")
else:
    print("❌ Could not find HTML_TEMPLATE")
