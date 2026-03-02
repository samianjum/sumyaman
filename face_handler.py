import face_recognition
import sqlite3
import numpy as np
import io
from PIL import Image

def get_db_connection():
    return sqlite3.connect('db.sqlite3', timeout=20)

def register_face(user_id, role, image_file):
    try:
        img = Image.open(image_file)
        img_array = np.array(img.convert('RGB'))
        encodings = face_recognition.face_encodings(img_array)
        if not encodings: return False, "❌ Face detect nahi hua."
        
        encoding_bytes = encodings[0].tobytes()
        table = "apsokara_student" if role == "Student" else "apsokara_teacher"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table} SET face_status='ENROLLED', face_encoding=? WHERE id=?", (encoding_bytes, user_id))
        conn.commit()
        conn.close()
        return True, "✅ Face ID Registered!"
    except Exception as e: return False, str(e)

def verify_face(user_id, role, image_file):
    try:
        table = "apsokara_student" if role == "Student" else "apsokara_teacher"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT face_encoding FROM {table} WHERE id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row or not row[0]: return False, "❌ No Face ID found."

        saved_enc = np.frombuffer(row[0], dtype=np.float64)
        img = Image.open(image_file)
        curr_enc = face_recognition.face_encodings(np.array(img.convert('RGB')))

        if not curr_enc: return False, "❌ Camera mein face nahi dikha."
        
        matches = face_recognition.compare_faces([saved_enc], curr_enc[0], tolerance=0.5)
        if matches[0]: return True, "✅ Verified!"
        return False, "❌ Face match nahi hua!"
    except Exception as e: return False, str(e)
