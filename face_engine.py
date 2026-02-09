import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import os
import tempfile
import sqlite3

class FaceEngine:
    def verify(self, frame, reference_img_path):
        try:
            if not os.path.exists(reference_img_path):
                return False, "Reference photo missing"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                if isinstance(frame, np.ndarray):
                    cv2.imwrite(tmp.name, frame)
                else:
                    img = Image.open(frame)
                    img.save(tmp.name)
                tmp_path = tmp.name

            result = DeepFace.verify(img1_path=tmp_path, img2_path=reference_img_path, 
                                   model_name='VGG-Face', enforce_detection=True)
            os.remove(tmp_path)
            return result['verified'], "Match Successful"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def update_db_status(self, user_id, role, status):
        conn = sqlite3.connect('db.sqlite3')
        table = 'apsokara_student' if role == 'Student' else 'apsokara_teacher'
        conn.execute(f"UPDATE {table} SET face_status=? WHERE id=?", (status, user_id))
        conn.commit()
        conn.close()

engine = FaceEngine()
