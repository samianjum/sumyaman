#!/bin/bash
echo "⚠️ Restoring project from MASTER_BACKUP.zip..."
unzip -o MASTER_BACKUP.zip
echo "✅ Project Overwritten with Backup Version!"
echo "🚀 Now run: streamlit run main_app.py"
