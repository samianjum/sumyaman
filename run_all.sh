#!/bin/bash
echo "🚀 Starting Django Backend on Port 8000..."
python manage.py runserver 0.0.0.0:8000 &

echo "🎨 Starting Main Streamlit App on Port 8501..."
streamlit run main_app.py --server.port 8501 --server.headless true &

echo "🛡️ Starting Secret HQ Admin on Port 8505..."
# Ab hum folder ke andar se run karenge
streamlit run hq_admin/dashboard.py --server.port 8505 --server.headless true &

wait
