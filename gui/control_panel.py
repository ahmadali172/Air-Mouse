"""
Main control panel: start and stop tracking, preview toggle, settings and help.
"""

import tkinter as tk
from tkinter import messagebox

from core.thread_manager import ThreadManager
from gui.settings_panel import SettingsPanel
from tracking.hand_tracker import HandTracker

HELP_TEXT = """AIR MOUSE HELP

GESTURES
- Move your index finger: the cursor follows it
- Index finger + thumb pinch: left click
- Middle finger + thumb pinch: right click

SETTINGS
- Cursor Speed: how fast the cursor moves
- Smoothing: how smooth the cursor movement is
  (lower value = smoother, slower to respond)

TIPS
- Keep your hand 1-2 feet from the camera
- Use good lighting
- Keep your fingers visible
- Practice in the preview window

EMERGENCY STOP
Move the mouse to any corner of the screen.

PREVIEW WINDOW
Press 'q' to close it, or use the Toggle Preview button.

TROUBLESHOOTING
- Cursor jumps: move the Smoothing slider toward Smoother
- Cursor is slow: increase Cursor Speed
- Clicks do not register: make sure your hand is clearly visible
- Camera does not work: check camera permissions
"""


class ControlPanel(tk.Frame):
    def __init__(self, master, state_manager):
        super().__init__(master)
        self.state_manager = state_manager

        self.tracker = HandTracker()
        self.tracker_thread = ThreadManager(target=self.tracker.run_threaded)

        # Status indicator
        self.status_frame = tk.Frame(self, bg="#f0f0f0", relief="sunken", bd=2)
        self.status_frame.pack(pady=5, fill="x")

        self.status_label = tk.Label(
            self.status_frame,
            text="READY",
            font=("Arial", 12, "bold"),
            fg="gray",
            bg="#f0f0f0"
        )
        self.status_label.pack(pady=5)

        # Start button
        self.start_btn = tk.Button(
            self,
            text="START AIR MOUSE",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 14, "bold"),
            command=self.start_tracking,
            cursor="hand2"
        )
        self.start_btn.pack(pady=10, fill="x", ipady=10)

        # Stop button
        self.stop_btn = tk.Button(
            self,
            text="STOP AIR MOUSE",
            bg="#f44336",
            fg="white",
            font=("Arial", 14, "bold"),
            command=self.stop_tracking,
            state="disabled",
            cursor="hand2"
        )
        self.stop_btn.pack(pady=10, fill="x", ipady=10)

        # Preview toggle button
        self.preview_btn = tk.Button(
            self,
            text="Toggle Camera Preview",
            font=("Arial", 12),
            command=self.toggle_preview,
            state="disabled",
            cursor="hand2"
        )
        self.preview_btn.pack(pady=5, fill="x", ipady=5)

        # Settings button
        self.settings_btn = tk.Button(
            self,
            text="Settings",
            font=("Arial", 12),
            command=self.open_settings,
            cursor="hand2"
        )
        self.settings_btn.pack(pady=5, fill="x", ipady=5)

        # Help button
        self.help_btn = tk.Button(
            self,
            text="Help",
            font=("Arial", 12),
            command=self.show_help,
            cursor="hand2"
        )
        self.help_btn.pack(pady=5, fill="x", ipady=5)

    def start_tracking(self):
        """Start the air mouse tracking."""
        try:
            if not self.tracker_thread.is_alive():
                self.tracker_thread.start()
            self.state_manager.set_tracking_active(True)

            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.preview_btn.config(state="normal")
            self.status_label.config(text="TRACKING", fg="green")

            messagebox.showinfo(
                "Air Mouse Started",
                "Air Mouse is now tracking.\n\n"
                "Gestures:\n"
                "- Index + Thumb pinch = Left Click\n"
                "- Middle + Thumb pinch = Right Click\n\n"
                "Move the mouse to any screen corner to emergency stop."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start tracking:\n{e}")
            self.status_label.config(text="ERROR", fg="red")

    def stop_tracking(self):
        """Stop the air mouse tracking."""
        try:
            self.tracker_thread.stop()
            self.state_manager.set_tracking_active(False)

            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.preview_btn.config(state="disabled")
            self.status_label.config(text="STOPPED", fg="orange")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop tracking:\n{e}")

    def toggle_preview(self):
        """Show or hide the camera preview window."""
        if self.tracker_thread.is_alive():
            self.tracker.toggle_preview()

    def open_settings(self):
        """Open the settings window."""
        SettingsPanel(self, self.tracker)

    def show_help(self):
        """Show the help window."""
        help_window = tk.Toplevel(self)
        help_window.title("Air Mouse Help")
        help_window.resizable(False, False)

        text_widget = tk.Text(help_window, wrap="word", width=50, height=30)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert("1.0", HELP_TEXT)
        text_widget.config(state="disabled")

        tk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=5)