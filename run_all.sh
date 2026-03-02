#!/bin/bash

echo "🛑 Cleaning up old processes..."
pkill -f "manage.py runserver"
pkill -f "streamlit run"

source venv/bin/activate

echo "🚀 Starting All Systems (Press CTRL+C to stop everything)..."
echo "--------------------------------------------------------"

# Django aur Streamlit ko parallel chalao aur dono ka output terminal pe dikhao
# '&' hata kar 'wait' use karenge taake terminal busy rahe aur output dikhaye
(python3 manage.py runserver 0.0.0.0:8000) & (streamlit run main_app.py --server.port 8501) &

wait
