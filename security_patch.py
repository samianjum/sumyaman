import re

file_path = 'mobile_app.py'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Add Cache-Control Headers to all responses
cache_logic = """
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
"""
content = content.replace("@app.route('/')", cache_logic)

# 2. JavaScript: Disable Back button after logout
js_security = """
        async function handleLogin() {
            // ... existing login logic ...
"""
# Logout script update
logout_script = """
@app.route('/logout')
def logout():
    session.clear()
    return \"\"\"
    <script>
        window.location.replace('/');
        setTimeout(function() {
            window.history.forward();
        }, 0);
    </script>
    \"\"\"
"""
content = re.sub(r"@app\.route\('/logout'\)[\s\S]*?\"\"\"", logout_script, content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Security Headers & Logout Logic Hardened!")
