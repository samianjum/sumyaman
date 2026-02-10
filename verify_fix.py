import face_recognition
import sqlite3
import numpy as np
from PIL import Image

def verify_face(user_id, role, image_file):
    try:
        table = "apsokara_student" if role == "Student" else "apsokara_teacher"
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute(f"SELECT face_encoding FROM {table} WHERE id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row or not row[0]:
            return False, "❌ Face ID data nahi mila."

        # Saved encoding load karein
        saved_encoding = np.frombuffer(row[0], dtype=np.float64)
        
        # Current photo process karein
        img = Image.open(image_file)
        current_encoding = face_recognition.face_encodings(np.array(img.convert('RGB')))

        if not current_encoding:
            return False, "❌ Face detect nahi hua."

        # Compare karein
        matches = face_recognition.compare_faces([saved_encoding], current_encoding[0], tolerance=0.5)
        
        if matches[0]:
            return True, "✅ Biometric Verified!"
        else:
            return False, "❌ Face match nahi hua! Dobara koshish karein."
    except Exception as e:
        return False, f"⚠️ Error: {str(e)}"

# Append to face_handler.py
with open('face_handler.py', 'a') as f:
    f.write("\n\n" + open('verify_fix.py').read())
