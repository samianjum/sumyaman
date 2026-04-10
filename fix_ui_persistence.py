file_path = 'mobile_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# 1. CSS to ensure classes work
css_patch = "<style>.offline-auth #login-screen { display: none !important; } .offline-auth #dashboard-view, .offline-auth #nav-bar { display: block !important; }</style>"

# 2. JS to detect offline and force session
js_patch = \"\"\"
<script>
    (function() {
        if (!navigator.onLine && localStorage.getItem('isLoggedIn') === 'true') {
            document.documentElement.classList.add('offline-auth');
        }
    })();
</script>
\"\"\"

if '</head>' in content:
    content = content.replace('</head>', css_patch + js_patch + '</head>')

with open(file_path, 'w') as f:
    f.write(content)
print("✅ UI Persistence script added to mobile_app.py!")
