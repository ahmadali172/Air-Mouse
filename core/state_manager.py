"""
Thread-safe flag that records whether tracking is active.
"""

from threading import Lock


class StateManager:
    def __init__(self):
        self._lock = Lock()
        self._tracking_active = False

    def set_tracking_active(self, active: bool):
        """Turn the tracking state on or off."""
        with self._lock:
            self._tracking_active = active

    def is_tracking_active(self) -> bool:
        """Return True while tracking is active."""
        with self._lock:
            return self._tracking_active