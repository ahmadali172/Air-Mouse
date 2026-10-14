"""
Hand tracker: reads the webcam, tracks one hand with MediaPipe,
moves the cursor with the index fingertip and clicks with pinch gestures.
"""

import time

import cv2
import mediapipe as mp
import pyautogui

from core.config_manager import ConfigManager
from tracking.gesture_engine import GestureEngine
from tracking.smoothing import Smoother

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01


class HandTracker:
    def __init__(self):
        cfg = ConfigManager()

        self.cam_index = cfg.get("camera", "index")
        self.frame_width = cfg.get("camera", "resolution_width")
        self.frame_height = cfg.get("camera", "resolution_height")
        self.cursor_speed = cfg.get("cursor", "speed")
        self.margin = cfg.get("cursor", "margin")
        self.click_cooldown = cfg.get("gestures", "click_cooldown")
        self.show_preview = cfg.get("ui", "show_preview")

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=cfg.get("tracking", "max_hands"),
            min_detection_confidence=cfg.get("tracking", "detection_confidence"),
            min_tracking_confidence=cfg.get("tracking", "tracking_confidence"),
        )

        self.gesture_engine = GestureEngine(
            pinch_threshold=cfg.get("gestures", "pinch_threshold")
        )
        self.smoother = Smoother(alpha=cfg.get("cursor", "smoothing"))

        self.last_left_click = 0
        self.last_right_click = 0

        self.cap = None
        self.running = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.preview_window = "Air Mouse - Camera Feed"

        self.fps = 0
        self.last_fps_time = time.time()
        self.frame_count = 0

    def start(self):
        if self.running:
            return

        self.cap = cv2.VideoCapture(self.cam_index)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open webcam")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.running = True

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.smoother.reset()
        cv2.destroyAllWindows()

    def _calculate_fps(self):
        self.frame_count += 1
        now = time.time()
        elapsed = now - self.last_fps_time
        if elapsed > 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_fps_time = now

    def _move_cursor(self, landmarks):
        """Move the cursor toward the index fingertip."""
        index_tip = landmarks[8]
        screen_x = int(index_tip[0] * self.screen_width)
        screen_y = int(index_tip[1] * self.screen_height)

        current_x, current_y = pyautogui.position()
        target_x = int(current_x + (screen_x - current_x) * self.cursor_speed)
        target_y = int(current_y + (screen_y - current_y) * self.cursor_speed)

        target_x = max(self.margin, min(self.screen_width - self.margin, target_x))
        target_y = max(self.margin, min(self.screen_height - self.margin, target_y))

        pyautogui.moveTo(target_x, target_y)

    def _handle_gestures(self, landmarks):
        """Click on pinch gestures. Returns a status text for the preview."""
        now = time.time()
        status = "TRACKING"

        if self.gesture_engine.detect_left_click(landmarks):
            if now - self.last_left_click > self.click_cooldown:
                pyautogui.click()
                self.last_left_click = now
                status = "LEFT CLICK"
        elif self.gesture_engine.detect_right_click(landmarks):
            if now - self.last_right_click > self.click_cooldown:
                pyautogui.rightClick()
                self.last_right_click = now
                status = "RIGHT CLICK"

        return status

    def get_frame(self):
        if not self.running or not self.cap:
            return None, None

        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        landmarks = []
        status = "NO HAND"

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2),
                )

                points = [(lm.x, lm.y, lm.z) for lm in hand.landmark]
                points = self.smoother.smooth(points)
                landmarks.append(points)

                self._move_cursor(points)
                status = self._handle_gestures(points)
        else:
            self.smoother.reset()

        if self.show_preview:
            self._display_preview(frame, status)

        self._calculate_fps()
        return frame, landmarks

    def _display_preview(self, frame, status):
        try:
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            color = (0, 0, 255) if "CLICK" in status else (0, 255, 0)
            cv2.putText(frame, f"Status: {status}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            instructions = [
                "Pinch Index + Thumb = Left Click",
                "Pinch Middle + Thumb = Right Click",
                "Press 'q' to close this window",
            ]
            y_pos = frame.shape[0] - 80
            for text in instructions:
                cv2.putText(frame, text, (10, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25

            cv2.imshow(self.preview_window, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.show_preview = False
                cv2.destroyWindow(self.preview_window)

        except Exception as e:
            print(f"Preview error: {e}")

    def toggle_preview(self):
        self.show_preview = not self.show_preview
        if not self.show_preview:
            cv2.destroyWindow(self.preview_window)

    def run_threaded(self, stop_event):
        try:
            self.start()
            print("Air Mouse started. Move the mouse to a screen corner to emergency stop.")
            while not stop_event.is_set():
                self.get_frame()
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()