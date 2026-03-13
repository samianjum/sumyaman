fname = 'mobile_app.py'
with open(fname, 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False

for i, line in enumerate(lines):
    # Line 25 ke baad jahan kachra shuru hota hai
    if '<script src="https://cdn.tailwindcss.com">' in line:
        new_lines.append(line)
        new_lines.append('    </script>\n')
        new_lines.append('</head>\n')
        new_lines.append('<body class="bg-gray-50 font-sans">\n')
        new_lines.append('    <div id="app-root"></div>\n')
        new_lines.append("    <script>\n")
        new_lines.append("        // Placeholder for JS\n")
        new_lines.append("    </script>\n")
        new_lines.append("</body>\n")
        new_lines.append("</html>\n")
        new_lines.append("'''\n") # Triple quote band kiya
        skip = True
        continue
    
    # Jab tak agla route '@app.route' nahi aata, skip karte raho (kachra saaf)
    if skip:
        if '@app.route' in line:
            skip = False
            new_lines.append('\n' + line)
        continue
        
    new_lines.append(line)

with open(fname, 'w') as f:
    f.writelines(new_lines)
print("✅ HTML Template Closed and Cleaned!")
