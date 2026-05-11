import re
import os

def run_diagnostic():
    file_path = 'mobile_app.py'
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found!")
        return

    with open(file_path, 'r') as f:
        lines = f.readlines()

    print("🚀 --- STARTING PROFESSIONAL SCOPE SCAN --- 🚀")
    
    # Target Functions
    targets = ['showTab', 'openDiaryHub', 'openLeaveHub', 'doLogin', 'setRole']
    jinja_stack = []
    errors_found = 0

    for i, line in enumerate(lines):
        line_num = i + 1
        clean_line = line.strip()

        # Track Jinja Blocks
        if '{% if' in clean_line:
            jinja_stack.append({'line': line_num, 'condition': clean_line})
        elif '{% endif %}' in clean_line and jinja_stack:
            jinja_stack.pop()

        # Check for function definitions trapped in Jinja
        if 'function' in clean_line:
            for func in targets:
                if f"{func}(" in clean_line or f"{func} =" in clean_line:
                    if jinja_stack:
                        errors_found += 1
                        parent = jinja_stack[-1]
                        print(f"\n❗ CRITICAL: Function '{func}' is TRAPPED at Line {line_num}")
                        print(f"   └─ Inside Jinja Block: {parent['condition']} (Line {parent['line']})")
                        print(f"   └─ IMPACT: This function is GHOSTED unless the IF condition is met.")

        # Check for Syntax Errors mentioned in your logs
        if '%s' in clean_line and '.js' in clean_line:
            print(f"\n⚠️ SYNTAX ERROR: Possible '%s' found in JS logic at Line {line_num}")
            print(f"   └─ Content: {clean_line}")

    print("\n--- SCAN COMPLETE ---")
    if errors_found == 0:
        print("✅ No trapped functions found. Check if functions are missing entirely.")
    else:
        print(f"❌ Found {errors_found} scope issues. Move these functions OUTSIDE of Jinja tags.")

if __name__ == "__main__":
    run_diagnostic()
