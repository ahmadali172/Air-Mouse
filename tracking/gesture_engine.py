"""
Gesture detection from MediaPipe hand landmarks.
"""

import math

THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12


class GestureEngine:
    """Detects pinch gestures used for left and right click."""

    def __init__(self, pinch_threshold=0.12):
        self.pinch_threshold = pinch_threshold

    @staticmethod
    def distance(p1, p2):
        """Euclidean distance between two 3D points."""
        return math.sqrt(
            (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2
        )

    def detect_left_click(self, hand_landmarks):
        """Left click: index fingertip and thumb tip close together."""
        return (
            self.distance(hand_landmarks[INDEX_TIP], hand_landmarks[THUMB_TIP])
            < self.pinch_threshold
        )

    def detect_right_click(self, hand_landmarks):
        """Right click: middle fingertip and thumb tip close together."""
        return (
            self.distance(hand_landmarks[MIDDLE_TIP], hand_landmarks[THUMB_TIP])
            < self.pinch_threshold
        )