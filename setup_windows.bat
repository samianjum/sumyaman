@echo off
echo 🚀 Starting Sumyaman Setup for Windows...

:: 1. Create Virtual Environment
python -m venv venv
call venv\Scripts\activate

:: 2. Install Requirements
echo 📦 Installing libraries...
pip install -r requirements.txt

:: 3. Database Migration
echo 🛠 Applying Database Migrations...
python manage.py migrate

:: 4. Run Server
echo ✅ Everything is ready! Starting server...
start http://127.0.0.1:8000/hq-portal/
python manage.py runserver
pause
