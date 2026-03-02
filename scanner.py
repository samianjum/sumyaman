import re

file_path = 'mobile_app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("--- [REPORT START] ---")

# 1. Check if Route Exists
route_match = re.search(r"@app\.route\('/api/get_diary'\)", content)
print(f"1. Route '@app.route('/api/get_diary')' Found: {'YES' if route_match else 'NO'}")

# 2. Extract Route Code (if exists)
if route_match:
    start_idx = route_match.start()
    # Extract next 30 lines to see implementation
    snippet = content[start_idx:start_idx+800]
    print("\n2. Route Implementation Snippet:")
    print("-" * 30)
    print(snippet)
    print("-" * 30)

# 3. Check for JavaScript Fetch
js_match = re.search(r"fetch\('/api/get_diary'\)", content)
print(f"\n3. JS 'fetch('/api/get_diary')' Found: {'YES' if js_match else 'NO'}")

# 4. Check for Session Variables
print(f"4. Session 'user' usage: {content.count('session[\\'user\\']') + content.count('session.get(\\'user\\')')}")

# 5. Check for Import Errors
print(f"5. sqlite3 Import: {'YES' if 'import sqlite3' in content else 'NO'}")
print(f"6. jsonify Import: {'YES' if 'jsonify' in content else 'NO'}")

print("\n--- [REPORT END] ---")
