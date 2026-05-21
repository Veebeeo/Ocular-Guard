import os
import sys
import cv2
import mediapipe as mp
import numpy as np


def _patch_mediapipe_path():
    """
    In a PyInstaller frozen exe, mediapipe resolves model paths relative
    to its own __file__ which lives inside _MEIPASS. This works as long
    as the spec bundles modules/ at the right location.
    Setting MEDIAPIPE_RESOURCE_DIR as a fallback covers older versions.
    """
    if getattr(sys, 'frozen', False):
        mp_resource_dir = os.path.join(sys._MEIPASS, 'mediapipe')
        os.environ.setdefault('MEDIAPIPE_RESOURCE_DIR', mp_resource_dir)


_patch_mediapipe_path()


class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.LEFT_EYE  = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    def calculate_ear(self, landmarks, indices):
        points = [np.array([landmarks[i].x, landmarks[i].y]) for i in indices]
        A = np.linalg.norm(points[1] - points[5])
        B = np.linalg.norm(points[2] - points[4])
        C = np.linalg.norm(points[0] - points[3])
        return (A + B) / (2.0 * C)

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_ear  = self.calculate_ear(landmarks, self.LEFT_EYE)
            right_ear = self.calculate_ear(landmarks, self.RIGHT_EYE)
            return left_ear, right_ear, (left_ear + right_ear) / 2.0
        return None
