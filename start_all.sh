#!/bin/bash
echo "🚀 STARTING IN FAST-DEV MODE (NO BUILD NEEDED)..."

# Cleanup
fuser -k 8000/tcp 8501/tcp 8080/tcp 9000/tcp 2>/dev/null
sleep 1

# 1. API Bridge
python3 ~/sumyaman/api_bridge.py > api.log 2>&1 &

# 2. Streamlit
source venv/bin/activate
./run_all.sh > streamlit.log 2>&1 &

# 3. Flutter (Fast Mode)
cd ~/sumyaman/portal
flutter run -d web-server --web-port 9000 --web-hostname 0.0.0.0
