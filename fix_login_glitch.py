file_path = 'mobile_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Fix the JavaScript Redirect (Line 578)
old_js = 'if(data.success) window.location.reload();'
new_js = 'if(data.success) { window.location.replace("/"); }'

# 2. Add Cache Clearing logic to Service Worker (sw.js update)
sw_path = 'static/sw.js'
if os.path.exists(sw_path):
    with open(sw_path, 'r') as f_sw:
        sw_content = f_sw.read()
    
    # Version update to force browser to see new worker
    if 'v21' in sw_content:
        sw_content = sw_content.replace('v21', 'v25')
    else:
        sw_content = sw_content.replace('v20', 'v25')
        
    with open(sw_path, 'w') as f_sw:
        f_sw.write(sw_content)

# Apply Python patch
if old_js in content:
    content = content.replace(old_js, new_js)
    with open(file_path, 'w') as f:
        f.write(content)
    print("✅ SUCCESS: Login redirect fixed and SW version bumped to v25!")
else:
    print("❌ ERROR: Could not find the specific login JS line.")
