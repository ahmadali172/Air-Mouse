"""
Gesture detection from MediaPipe hand landmarks.
"""

import math

WRIST = 0
THUMB_TIP = 4
MIDDLE_MCP = 9
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
INDEX_PIP = 6
MIDDLE_PIP = 10
RING_PIP = 14
PINKY_PIP = 18


class GestureEngine:
    """Detects pinch gestures used for left and right click."""

    def __init__(self, pinch_threshold=0.12):
        self.pinch_threshold = pinch_threshold  # old setting, no longer used

        # A pinch counts when the fingertip-to-thumb gap is smaller than this
        # fraction of the hand size (so it works near or far from the camera)
        self.pinch_ratio_limit = 0.30

    @staticmethod
    def distance(p1, p2):
        """Flat (x, y) distance between two landmarks. Depth (z) is ignored
        because it is noisy and made pinches hard to detect."""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def pinch_ratio(self, hand_landmarks, finger_tip):
        """Gap between a fingertip and the thumb tip, relative to hand size."""
        hand_size = self.distance(hand_landmarks[WRIST], hand_landmarks[MIDDLE_MCP])
        gap = self.distance(hand_landmarks[finger_tip], hand_landmarks[THUMB_TIP])
        return gap / max(hand_size, 1e-6)

    def detect_left_click(self, hand_landmarks):
        """Left click: index fingertip and thumb tip close together."""
        return self.pinch_ratio(hand_landmarks, INDEX_TIP) < self.pinch_ratio_limit

    def detect_right_click(self, hand_landmarks):
        """Right click: middle fingertip and thumb tip close together."""
        return self.pinch_ratio(hand_landmarks, MIDDLE_TIP) < self.pinch_ratio_limit

    @staticmethod
    def _is_extended(landmarks, tip, pip):
        """A finger is straight (extended) if its tip is higher than its middle joint."""
        return landmarks[tip][1] < landmarks[pip][1]

    def detect_scroll_pose(self, hand_landmarks):
        """Scroll pose: index and middle fingers up, ring and pinky folded."""
        return (
            self._is_extended(hand_landmarks, INDEX_TIP, INDEX_PIP)
            and self._is_extended(hand_landmarks, MIDDLE_TIP, MIDDLE_PIP)
            and not self._is_extended(hand_landmarks, RING_TIP, RING_PIP)
            and not self._is_extended(hand_landmarks, PINKY_TIP, PINKY_PIP)
        )
