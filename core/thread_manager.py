"""
Runs a function in a background thread with start and stop control.
"""

from threading import Event, Thread


class ThreadManager:
    """
    Manages a background thread.
    The target function must accept a stop_event parameter.
    """

    def __init__(self, target):
        self.target = target
        self.stop_event = Event()
        self.thread = None

    def start(self):
        """Start the thread if it is not already running."""
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = Thread(
                target=lambda: self.target(self.stop_event), daemon=True
            )
            self.thread.start()

    def stop(self):
        """Ask the thread to stop and wait up to 2 seconds for it."""
        if self.thread and self.thread.is_alive():
            self.stop_event.set()
            self.thread.join(timeout=2.0)

    def is_alive(self):
        """Return True while the thread is running."""
        return self.thread is not None and self.thread.is_alive()