
import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
import os
import sqlite3

def verify_face(frame, user_id, role):
    ref_path = f"assets/profiles/{role.lower()}_{user_id}.jpg"
    if not os.path.exists(ref_path):
        return False, "Reference image missing."
    try:
        # Save temp frame for DeepFace
        tmp_path = "temp_auth.jpg"
        cv2.imwrite(tmp_path, cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
        result = DeepFace.verify(img1_path=tmp_path, img2_path=ref_path, model_name='VGG-Face', enforce_detection=True)
        os.remove(tmp_path)
        return result['verified'], "Match Successful"
    except Exception as e:
        return False, f"Scan Error: {str(e)}"

def update_face_status(user_id, role, status):
    conn = sqlite3.connect('db.sqlite3')
    table = 'apsokara_student' if role == 'Student' else 'apsokara_teacher'
    conn.execute(f"UPDATE {table} SET face_status=? WHERE id=?", (status, user_id))
    conn.commit()
    conn.close()
