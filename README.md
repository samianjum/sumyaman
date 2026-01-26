# 🚀 SUMYAMAN - One Click Setup

Agar teacher ke computer par Git install nahi hai, to **PowerShell** kholien aur ye poora block copy-paste kar dein:

\`\`\`powershell
$url = "https://github.com/samianjum/sumyaman/archive/refs/heads/main.zip"; $zip = "sumyaman.zip"; Invoke-WebRequest -Uri $url -OutFile $zip; Expand-Archive -Path $zip -DestinationPath "."; cd "sumyaman-main"; .\setup_windows.bat
\`\`\`

---

### 📝 Kya hoga is command se?
1. **Download:** Aapka poora project ZIP ban kar download hoga.
2. **Extract:** ZIP file khud hi khul kar folder ban jayegi.
3. **Setup:** Humara banaya hua \`setup_windows.bat\` khud hi Virtual Env banayenge aur server start kar dega.

### 🔑 Login Details:
- **Admin Portal:** http://127.0.0.1:8000/hq-portal/
- **Username:** (Yahan likhen)
- **Password:** (Yahan likhen)
