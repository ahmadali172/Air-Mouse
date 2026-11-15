"""
Hand tracker: reads the webcam, tracks one hand with MediaPipe,
moves the cursor with the index fingertip and clicks with pinch gestures.
"""

from collections import deque
import time

import cv2
import mediapipe as mp
import pyautogui

from core.config_manager import ConfigManager
from tracking.gesture_engine import GestureEngine
from tracking.smoothing import Smoother

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


class HandTracker:
    def __init__(self):
        cfg = ConfigManager()

        self.cam_index = cfg.get("camera", "index")
        self.frame_width = cfg.get("camera", "resolution_width")
        self.frame_height = cfg.get("camera", "resolution_height")
        self.cursor_speed = cfg.get("cursor", "speed")
        self.margin = cfg.get("cursor", "margin")
        self.active_area = cfg.get("cursor", "active_area") or 0.6
        self.click_cooldown = cfg.get("gestures", "click_cooldown")
        self.show_preview = cfg.get("ui", "show_preview")

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=cfg.get("tracking", "max_hands"),
            model_complexity=0,
            min_detection_confidence=cfg.get("tracking", "detection_confidence"),
            min_tracking_confidence=cfg.get("tracking", "tracking_confidence"),
        )

        self.gesture_engine = GestureEngine(
            pinch_threshold=cfg.get("gestures", "pinch_threshold")
        )
        self.smoother = Smoother(alpha=cfg.get("cursor", "smoothing"))

        self.last_left_click = 0
        self.last_right_click = 0

        # Cursor positions of the last moments, used to undo drift while pinching
        self.pos_history = deque(maxlen=30)
        self.was_pinching = False

        # Drag support: hold a left pinch this long to start dragging
        self.drag_hold_time = 0.4
        self.pinch_start = None
        self.dragging = False

        # Scroll support: two fingers up, move the hand up or down
        self.scroll_speed = 6000
        self.scroll_deadzone = 0.004
        self.scroll_last_y = None

        self.cap = None
        self.running = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.preview_window = "Air Mouse - Camera Feed"
        self.preview_placed = False

        self.fps = 0
        self.status = "STOPPED"
        self.pinch_info = (0.0, 0.0)
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
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True

    def stop(self):
        self.running = False
        self.status = "STOPPED"
        self._release_drag()
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

    def _box_origin(self):
        """Top-left corner of the active area, as fractions of the frame.
        The box sits a bit above center, because the palm hangs below the
        fingertip and must stay inside the camera view."""
        x_low = (1 - self.active_area) / 2
        y_low = (1 - self.active_area) * 0.25
        return x_low, y_low

    def _move_cursor(self, landmarks):
        """Move the cursor straight to where the index fingertip points."""
        index_tip = landmarks[8]

        # Only the middle part of the camera frame (the active area) is used.
        # Its edges map to the screen edges, so small hand moves cover the screen.
        x_low, y_low = self._box_origin()
        norm_x = (index_tip[0] - x_low) / self.active_area
        norm_y = (index_tip[1] - y_low) / self.active_area

        # Cursor speed = how much the movement is stretched around the center
        gain = self.cursor_speed / 1.5
        norm_x = 0.5 + (norm_x - 0.5) * gain
        norm_y = 0.5 + (norm_y - 0.5) * gain

        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        target_x = int(norm_x * self.screen_width)
        target_y = int(norm_y * self.screen_height)

        target_x = max(self.margin, min(self.screen_width - self.margin, target_x))
        target_y = max(self.margin, min(self.screen_height - self.margin, target_y))

        self.pos_history.append((time.time(), target_x, target_y))
        pyautogui.moveTo(target_x, target_y)

    def _rewind_cursor(self):
        """Put the cursor back to where it was just before the pinch began."""
        now = time.time()
        for t, x, y in self.pos_history:
            if now - t <= 0.25:
                pyautogui.moveTo(x, y)
                break

    def _release_drag(self):
        """Let go of the mouse button if a drag is in progress."""
        if self.dragging:
            pyautogui.mouseUp()
        self.dragging = False
        self.pinch_start = None

    def _handle_scroll(self, landmarks):
        """Scroll the page by how far the two raised fingers moved up or down."""
        y = (landmarks[8][1] + landmarks[12][1]) / 2

        if self.scroll_last_y is not None:
            dy = y - self.scroll_last_y
            if abs(dy) > self.scroll_deadzone:
                pyautogui.scroll(int(-dy * self.scroll_speed))

        self.scroll_last_y = y
        return "SCROLLING"

    def _handle_gestures(self, landmarks):
        """Click, drag and right click. Returns a status text for the preview."""
        now = time.time()
        status = "TRACKING"

        if self.gesture_engine.detect_left_click(landmarks):
            # Pinch is held: remember when it started
            if self.pinch_start is None:
                self.pinch_start = now

            held = now - self.pinch_start
            if held >= self.drag_hold_time and not self.dragging:
                pyautogui.mouseDown()
                self.dragging = True

            if self.dragging:
                status = "DRAGGING"
            else:
                status = "PINCHING"
        else:
            # Pinch was released
            if self.dragging:
                pyautogui.mouseUp()
                self.dragging = False
                status = "DROPPED"
            elif self.pinch_start is not None:
                # Short pinch = normal left click
                if now - self.last_left_click > self.click_cooldown:
                    pyautogui.click()
                    self.last_left_click = now
                    status = "LEFT CLICK"
            self.pinch_start = None

            if self.gesture_engine.detect_right_click(landmarks):
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

                if not self.dragging and self.gesture_engine.detect_scroll_pose(points):
                    status = self._handle_scroll(points)
                else:
                    self.scroll_last_y = None

                    self.pinch_info = (
                        self.gesture_engine.pinch_ratio(points, 8),
                        self.gesture_engine.pinch_ratio(points, 12),
                    )
                    pinching = (
                        self.gesture_engine.detect_left_click(points)
                        or self.gesture_engine.detect_right_click(points)
                    )
                    if pinching and not self.dragging:
                        # Pinching moves the fingertip, so freeze the cursor
                        if not self.was_pinching:
                            self._rewind_cursor()
                    else:
                        self._move_cursor(points)
                    self.was_pinching = pinching

                    status = self._handle_gestures(points)
        else:
            self.smoother.reset()
            self.scroll_last_y = None
            self._release_drag()

        self.status = status

        if self.show_preview:
            self._display_preview(frame, status)

        self._calculate_fps()
        return frame, landmarks

    def _display_preview(self, frame, status):
        try:
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Draw the active area box
            h, w = frame.shape[:2]
            x_low, y_low = self._box_origin()
            top_left = (int(w * x_low), int(h * y_low))
            bottom_right = (int(w * (x_low + self.active_area)),
                            int(h * (y_low + self.active_area)))
            cv2.rectangle(frame, top_left, bottom_right, (255, 255, 0), 2)

            color = (0, 0, 255) if ("CLICK" in status or status == "DRAGGING") else (0, 255, 0)
            cv2.putText(frame, f"Status: {status}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            idx_ratio, mid_ratio = self.pinch_info
            limit = self.gesture_engine.pinch_ratio_limit
            cv2.putText(frame, f"Pinch  index {idx_ratio:.2f}  middle {mid_ratio:.2f}  (click below {limit:.2f})",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            instructions = [
                "Pinch Index + Thumb = Left Click",
                "Hold that pinch 0.4s = Drag",
                "Index + Middle up, move hand = Scroll",
                "Pinch Middle + Thumb = Right Click",
                "Press 'q' to close this window",
            ]
            y_pos = frame.shape[0] - 130
            for text in instructions:
                cv2.putText(frame, text, (10, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25

            if not self.preview_placed:
                # Open the camera view at the top-left, away from the control window
                cv2.namedWindow(self.preview_window)
                cv2.moveWindow(self.preview_window, 0, 40)
                self.preview_placed = True

            cv2.imshow(self.preview_window, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.show_preview = False
                self.preview_placed = False
                cv2.destroyWindow(self.preview_window)

        except Exception as e:
            print(f"Preview error: {e}")

    def toggle_preview(self):
        self.show_preview = not self.show_preview
        if not self.show_preview:
            self.preview_placed = False
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