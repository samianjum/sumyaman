
#!/bin/bash

# 1. Bari files ko ignore list mein pakka kar dena

echo "*.zip" > .gitignore

echo "*.db" >> .gitignore

echo "*.sqlite3" >> .gitignore

echo "venv/" >> .gitignore



# 2. Files add karna (Bari files skip ho jayengi)

git add .



# 3. Commit message (Date ke sath)

msg="Update: $(date +'%d-%m-%Y %H:%M')"

git commit -m "$msg"



# 4. Final Push

git push origin main

