import re

with open('mobile_app.py', 'r') as f:
    lines = f.readlines()

content = "".join(lines)

# 1. Sabse pehle wo extra endifs hatao jo file ke bilkul niche chale gaye hain
content = re.sub(r'(% endif %}\s*)+$', '', content.strip())

# 2. HTML_TEMPLATE ke andar ka hissa nikaalein
start_marker = "HTML_TEMPLATE = '''"
end_marker = "'''"

if start_marker in content:
    parts = content.split(start_marker)
    template_and_rest = parts[1].split(end_marker, 1)
    template_body = template_and_rest[0]
    rest_of_file = template_and_rest[1]

    # Count actual tags inside template only
    ifs = len(re.findall(r'{% if', template_body))
    endifs = len(re.findall(r'{% endif %}', template_body))

    print(f"Inside Template -> Ifs: {ifs}, Endifs: {endifs}")

    if ifs > endifs:
        missing = ifs - endifs
        # Template khatam hone se pehle zaroori endifs add karein
        template_body += "\n" + ("{% endif %}\n" * missing)
        print(f"Added {missing} missing endifs to template body.")

    # Reconstruct the file
    new_content = parts[0] + start_marker + template_body + end_marker + rest_of_file

    with open('mobile_app.py', 'w') as f:
        f.write(new_content)
    print("✅ mobile_app.py recovered and balanced!")
else:
    print("❌ Could not find HTML_TEMPLATE marker!")
