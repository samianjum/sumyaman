# 🚀 SUMYAMAN - School Management System

Sami bhai, teacher ke computer pe bas ye steps follow karein:

### 1. Clone the Project
Open CMD/Terminal and type:
\`\`\`bash
git clone https://github.com/samianjum/sumyaman.git
cd sumyaman
\`\`\`

### 2. Run Setup (Windows Only)
Double click on \`setup_windows.bat\` OR run:
\`\`\`bash
setup_windows.bat
\`\`\`

### 3. Login Details
- **Admin Portal:** http://127.0.0.1:8000/hq-portal/
- **Username:** (Apna admin username yahan likhein)
- **Password:** (Apna admin password yahan likhein)

---
### Manual Steps (In case script fails):
1. \`python -m venv venv\`
2. \`venv\Scripts\activate\`
3. \`pip install -r requirements.txt\`
4. \`python manage.py migrate\`
5. \`python manage.py runserver\`
