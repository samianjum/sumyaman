import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import os
import tempfile
import logging

# Disable TensorFlow logging to keep terminal clean
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class FaceEngine:
    def __init__(self, model_name='VGG-Face', distance_metric='cosine'):
        self.model_name = model_name
        self.distance_metric = distance_metric

    def verify(self, frame, reference_img_path):
        """
        Frame ko reference image se match karta hai.
        """
        try:
            # Step 1: Check if reference exists
            if not os.path.exists(reference_img_path):
                return False, f"Reference photo missing at {reference_img_path}"

            # Step 2: Convert Streamlit image to DeepFace compatible format
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                # Agar frame numpy array hai (OpenCV)
                if isinstance(frame, np.ndarray):
                    cv2.imwrite(tmp.name, frame)
                else:
                    # Agar frame PIL image ya uploaded file hai
                    img = Image.open(frame)
                    img.save(tmp.name)
                
                tmp_path = tmp.name

            # Step 3: DeepFace Verification
            # enforce_detection=True ka matlab hai agar face nahi dikha to error dega
            result = DeepFace.verify(
                img1_path=tmp_path, 
                img2_path=reference_img_path, 
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                enforce_detection=True,
                detector_backend='opencv' # Tez aur reliable
            )

            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

            return result['verified'], "Identity Verified" if result['verified'] else "Face Mismatch"

        except ValueError as v:
            return False, "Face not detected. Please look clearly at the camera."
        except Exception as e:
            return False, f"Engine Error: {str(e)}"

# Singleton Instance for global use
engine = FaceEngine()
