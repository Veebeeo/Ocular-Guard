import cv2
import mediapipe as mp
import numpy as np

class EyeTracker:
    def __init__(self):
     
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    def calculate_ear(self, landmarks, indices):
        
        # Helper to get numpy array of (x,y)
        points = []
        for idx in indices:
            points.append(np.array([landmarks[idx].x, landmarks[idx].y]))

        # Distance between p2 and p6
        A = np.linalg.norm(points[1] - points[5])
        # Distance between p3 and p5
        B = np.linalg.norm(points[2] - points[4])
        # Distance between p1 and p4
        C = np.linalg.norm(points[0] - points[3])

        # Compute EAR
        ear = (A + B) / (2.0 * C)
        return ear

    def process_frame(self, frame):
        # Convert BGR (OpenCV standard) to RGB (MediaPipe standard)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            left_ear = self.calculate_ear(landmarks, self.LEFT_EYE)
            right_ear = self.calculate_ear(landmarks, self.RIGHT_EYE)
            
            avg_ear = (left_ear + right_ear) / 2.0
            return left_ear, right_ear, avg_ear
        
        return None
