import face_recognition
import sqlite3
import numpy as np
import io
from PIL import Image

def get_db_connection():
    conn = sqlite3.connect('db.sqlite3', timeout=20)
    return conn

def register_face(user_id, role, image_file):
    """Face ko detect karke uski encoding database mein save karta hai."""
    try:
        # Image load karein
        img = Image.open(image_file)
        img_array = np.array(img.convert('RGB'))
        
        # Encodings dhoondein
        encodings = face_recognition.face_encodings(img_array)
        
        if len(encodings) == 0:
            return False, "No face detected. Please try again with better lighting."
        
        encoding_bytes = encodings[0].tobytes()
        table = "apsokara_student" if role == "Student" else "apsokara_teacher"
        
        conn = get_db_connection()
        conn.execute(f"UPDATE {table} SET face_status='ENROLLED', face_encoding=? WHERE id=?", (encoding_bytes, user_id))
        conn.commit()
        conn.close()
        return True, "Face registered successfully!"
    except Exception as e:
        return False, str(e)

def verify_face(user_id, role, captured_image):
    """Captured face ko database wali encoding se match karta hai."""
    try:
        table = "apsokara_student" if role == "Student" else "apsokara_teacher"
        conn = get_db_connection()
        res = conn.execute(f"SELECT face_encoding FROM {table} WHERE id=?", (user_id,)).fetchone()
        conn.close()

        if not res or not res[0]:
            return False, "No Face ID found for this user."

        stored_encoding = np.frombuffer(res[0], dtype=np.float64)
        
        img = Image.open(captured_image)
        img_array = np.array(img.convert('RGB'))
        current_encodings = face_recognition.face_encodings(img_array)

        if len(current_encodings) == 0:
            return False, "No face detected."

        # Compare faces
        results = face_recognition.compare_faces([stored_encoding], current_encodings[0], tolerance=0.5)
        
        if results[0]:
            return True, "Identity Verified!"
        else:
            return False, "Face did not match. Access Denied."
    except Exception as e:
        return False, str(e)
