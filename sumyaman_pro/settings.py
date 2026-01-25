import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
with open('.env_key') as f: SECRET_KEY = f.read().strip()
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apsokara', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sumyaman_pro.urls'

# Maine yahan se double 'DIRS' ko remove kar ke clean kar diya hai
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = 'static/'
# Agar static files use karni hain to ye line bhi honi chahiye:
STATICFILES_DIRS = [BASE_DIR / "static"]
LOGOUT_REDIRECT_URL = '/admin/login/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# --- HQ ADMIN EXTRA SECURITY LAYER ---
# Sirf local machine se access allow karne ke liye
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# Browser Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session Security (Strict Mode)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
# Note: SECURE_COOKIEs tab enable karte hain jab HTTPS ho, 
# lekin local use ke liye HTTPONLY kafi hai.

# --- ADVANCED HACKER PROTECTION ---
# 1. Clickjacking se bachao (Koi aapki site ko frame nahi kar sakega)
X_FRAME_OPTIONS = 'DENY'

# 2. Browser ko majboor karna ke wo sirf hamari scripts chalaye (CSP)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# 3. Session Hijacking se bachne ke liye (Sirf browser read kar sakega)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# 4. Agar hacker SQL Injection try kare toh Django built-in protection active hai.
