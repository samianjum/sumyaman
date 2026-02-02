import re

file_path = '/home/sami/sumyaman/mobile_portal.py'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Pehle saare triple ya double brackets ko single kar dete hain (Reset)
content = content.replace('{{{', '{').replace('}}}', '}')
content = content.replace('{{', '{').replace('}}', '}')

# 2. Ab sirf st.markdown wali f-strings ke andar brackets ko double karte hain
def double_brackets(match):
    inner_text = match.group(1)
    # Brackets ko double karo lekin variables (jo {u.get...} hain) unhein mat chhero
    # Variable pattern: {u.get...} ya {logo_base64} ya {name} ya {curr} ya {h_c} etc.
    fixed = re.sub(r'(?<!\{)\{ (?!u\.|logo_base64|name|curr|h_c|a_c|p_c)', '{{ ', inner_text)
    fixed = re.sub(r'(?<!u\.|logo_base64|name|curr|h_c|a_c|p_c)\}(?! \})', ' }}', fixed)
    # Simple brackets fix for CSS selectors
    fixed = fixed.replace('{', '{{').replace('}', '}}')
    # Restore variables (un-double them)
    for var in ['u.get', 'logo_base64', 'name', 'curr', 'h_c', 'a_c', 'p_c']:
        fixed = fixed.replace(f'{{{{{var}', f'{{{var}').replace(f'{var}}}}}', f'{var}}}')
    return f'f"""{fixed}"""'

content = re.sub(r'f"""(.*?)"""', double_brackets, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Brackets Normalized to Double {{ }}!")
