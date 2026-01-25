#!/bin/bash

# 1. Activate Environment
source venv/bin/activate

# 2. Database Maintenance (Fixing 'wing' column data)
echo "🔧 Fixing Database..."
python3 -c "
import sqlite3
conn = sqlite3.connect('db.sqlite3')
try:
    # Match wings from student table to attendance table
    conn.execute(\"UPDATE apsokara_attendance SET wing=(SELECT wing FROM apsokara_student WHERE cnic=apsokara_attendance.student_id) WHERE wing IS NULL OR wing='' \")
    conn.commit()
    print('✅ Database Sync: OK')
except Exception as e:
    print(f'⚠️ DB Note: {e}')
conn.close()
"

# 3. Start Django Backend (in background)
echo "🚀 Starting Django Backend..."
python3 manage.py runserver 0.0.0.0:8000 & 

# 4. Start Streamlit Frontend
echo "🎨 Starting Streamlit Frontend..."
streamlit run main_app.py --server.port 8501

# Cleanup background processes on exit
trap 'kill $(jobs -p)' EXIT
