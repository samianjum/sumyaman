import os

file_path = 'mobile_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Inject Authentication Guard at the very top of <head>
auth_guard = \"\"\"
    <script>
        (function() {
            const isLocal = localStorage.getItem('isLoggedIn') === 'true';
            const isServer = {{ 'true' if logged_in else 'false' }};
            
            // Offline bypass: If offline and was logged in, show dashboard
            if (!navigator.onLine && isLocal) {
                document.documentElement.classList.add('is-offline-auth');
            }
            // Online Sync: If online and server says no session, but local says yes -> force logout
            if (navigator.onLine && !isServer && isLocal) {
                localStorage.clear();
                window.location.href = '/?logged_out_sync';
            }
        })();
    </script>
    <style>
        .is-offline-auth #login-screen { display: none !important; }
        .is-offline-auth #dashboard-view, .is-offline-auth #nav-bar { display: block !important; }
    </style>
\"\"\"

if '<head>' in content:
    content = content.replace('<head>', '<head>' + auth_guard)

# 2. Fix the Logout Route to be absolute
old_logout = \"\"\"@app.route('/logout')
def logout():
    session.clear()
    return '<script>window.location.href="/";</script>'\"\"\"

new_logout = \"\"\"@app.route('/logout')
def logout():
    session.clear()
    return '<script>localStorage.clear(); sessionStorage.clear(); window.location.href="/?logout=" + Date.now();</script>'\"\"\"

content = content.replace(old_logout, new_logout)

with open(file_path, 'w') as f:
    f.write(content)
print("✅ App Logic: Auth Guard & Logout Sync Fixed.")
