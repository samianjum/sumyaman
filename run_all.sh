#!/bin/bash

echo "🛑 Cleaning up old processes..."
fuser -k 8000/tcp 8501/tcp 8505/tcp 2>/dev/null

echo "🚀 Starting Django Backend (HQ Portal) on Port 8000..."
nohup python3 manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &

echo "🎨 Starting Main Streamlit App on Port 8501..."
nohup streamlit run main_app.py --server.port 8501 > streamlit.log 2>&1 &

echo "✅ All systems are firing! Check logs if something fails."
echo "HQ Portal: http://127.0.0.1:8000/hq-portal/"
echo "Main App: http://127.0.0.1:8501"
