# 🚀 SUMYAMAN - ONE-CLICK SETUP (WINDOWS)

Teacher ke computer pe PowerShell kholiye aur niche wala poora block copy-paste karke Enter daba dein. Ye khud hi download, extract, install aur server run karega.

### ⚡ METHOD 1: FULL AUTOMATIC (No Git Required)
Copy and paste this in **PowerShell**:
\`\`\`powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; $url = "https://github.com/samianjum/sumyaman/archive/refs/heads/main.zip"; $zip = "sumyaman.zip"; Invoke-WebRequest -Uri $url -OutFile $zip; Expand-Archive -Path $zip -DestinationPath "."; cd "sumyaman-main"; .\setup_windows.bat
\`\`\`

---

### 🛠️ METHOD 2: IF GIT IS INSTALLED
Copy and paste this in **CMD**:
\`\`\`cmd
git clone https://github.com/samianjum/sumyaman.git && cd sumyaman && setup_windows.bat
\`\`\`

---

### 📂 METHOD 3: MANUAL SETUP (If everything fails)
1. Python install karein (Add to PATH lazmi karein).
2. Project folder mein CMD kholiye.
3. Ye commands chalaein:
   \`\`\`cmd
   python -m venv venv
   call venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   \`\`\`

---

### 🔑 ACCESS DETAILS
- **URL:** http://127.0.0.1:8000/hq-portal/
- **Admin:** (Yahan apna username/password likh dein)

