import cv2
import numpy as np
import torch
import mediapipe as mp

class ForensicFaceAnalyzer:
    def __init__(self):
        # Initialize MediaPipe Face Detection and Mesh components
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.detector = self.mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
        self.mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

    def extract_and_align_face(self, frame: np.ndarray):
        """
        Locates the primary face bounding box, cuts out the region-of-interest,
        and extracts topological structural landmark coordinates.
        """
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 1. Face Bounding Box Detection
        detection_results = self.detector.process(rgb_frame)
        if not detection_results.detections:
            return None, None # No tracking metrics found
            
        primary_detection = detection_results.detections[0]
        bbox = primary_detection.location_data.relative_bounding_box
        
        # Convert relative coordinates safely to pixel space integers
        x_min = max(0, int(bbox.xmin * w))
        y_min = max(0, int(bbox.ymin * h))
        box_w = int(bbox.width * w)
        box_h = int(bbox.height * h)
        
        x_max = min(w, x_min + box_w)
        y_max = min(h, y_min + box_h)
        
        face_crop = frame[y_min:y_max, x_min:x_max]
        
        # 2. Extract Structural Landmarks Mesh
        mesh_results = self.mesh.process(rgb_frame)
        landmarks_flat = []
        
        if mesh_results.multi_face_landmarks:
            face_landmarks = mesh_results.multi_face_landmarks[0]
            # Capture essential landmark metrics (e.g., coordinates for eyes, nose, mouth tracks)
            for lm in face_landmarks.landmark:
                landmarks_flat.extend([lm.x, lm.y, lm.z])
                
        return face_crop, landmarks_flat