import cv2
import mediapipe as mp

class ForensicFaceDetector:
    def __init__(self):
        # Initialize MediaPipe Face Mesh for high-fidelity landmarking
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=5, # Can detect multiple suspects in one frame
            refine_landmarks=True, # Critical for eye/lip deepfake detection
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def extract_evidence(self, frame):
        """
        Analyzes a single video frame and returns precise facial bounding boxes 
        and key landmark coordinates for forensic analysis.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        evidence_data = []
        h, w, _ = frame.shape
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 1. Calculate Bounding Box for ViT Cropping
                x_coords = [landmark.x * w for landmark in face_landmarks.landmark]
                y_coords = [landmark.y * h for landmark in face_landmarks.landmark]
                
                bbox = {
                    "x_min": int(min(x_coords)),
                    "y_min": int(min(y_coords)),
                    "x_max": int(max(x_coords)),
                    "y_max": int(max(y_coords))
                }
                
                # 2. Extract High-Risk Zones (Eyes & Mouth)
                high_risk_zones = {
                    "left_eye": (int(face_landmarks.landmark[159].x * w), int(face_landmarks.landmark[159].y * h)),
                    "right_eye": (int(face_landmarks.landmark[386].x * w), int(face_landmarks.landmark[386].y * h)),
                    "lips": (int(face_landmarks.landmark[13].x * w), int(face_landmarks.landmark[13].y * h))
                }
                
                evidence_data.append({"bounding_box": bbox, "risk_zones": high_risk_zones})
                
        return evidence_data

# Quick test logic
if __name__ == "__main__":
    detector = ForensicFaceDetector()
    print("✅ Forensic Face Detector Initialized Successfully.")