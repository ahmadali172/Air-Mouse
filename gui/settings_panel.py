"""
Settings window: change cursor speed and smoothing while the app runs.
"""

import tkinter as tk
from tkinter import messagebox

from core.config_manager import ConfigManager


class SettingsPanel(tk.Toplevel):
    def __init__(self, master, tracker):
        super().__init__(master)
        self.title("Air Mouse Settings")
        self.tracker = tracker
        self.settings = ConfigManager()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.save_and_close)

        cursor_speed = self.tracker.cursor_speed
        smoothing = self.tracker.smoother.alpha

        main_frame = tk.Frame(self, padx=20, pady=10)
        main_frame.pack()

        # Cursor speed
        speed_frame = tk.LabelFrame(main_frame, text="Cursor Speed", padx=10, pady=10)
        speed_frame.pack(fill="x", pady=10)

        tk.Label(speed_frame, text="Slower <-> Faster").pack()
        self.cursor_speed = tk.DoubleVar(value=cursor_speed)

        speed_scale = tk.Scale(
            speed_frame,
            variable=self.cursor_speed,
            from_=0.5,
            to=3.0,
            resolution=0.1,
            orient="horizontal",
            length=300,
            command=self.update_cursor_speed
        )
        speed_scale.pack(pady=5)

        self.speed_value_label = tk.Label(speed_frame, text=f"Current: {cursor_speed:.1f}")
        self.speed_value_label.pack()

        # Smoothing
        smooth_frame = tk.LabelFrame(main_frame, text="Smoothing Level", padx=10, pady=10)
        smooth_frame.pack(fill="x", pady=10)

        tk.Label(smooth_frame, text="Smoother <-> More Responsive").pack()
        self.smooth_level = tk.DoubleVar(value=smoothing)

        smooth_scale = tk.Scale(
            smooth_frame,
            variable=self.smooth_level,
            from_=0.1,
            to=0.9,
            resolution=0.05,
            orient="horizontal",
            length=300,
            command=self.update_smoothing
        )
        smooth_scale.pack(pady=5)

        self.smooth_value_label = tk.Label(smooth_frame, text=f"Current: {smoothing:.2f}")
        self.smooth_value_label.pack()

        # Tips
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill="x", pady=10)

        info_text = (
            "Tips:\n"
            "- Higher speed = faster cursor\n"
            "- Lower smoothing value = smoother movement\n"
            "- Settings are saved when you close this window"
        )
        tk.Label(
            info_frame,
            text=info_text,
            justify="left",
            bg="#e8f4f8",
            relief="sunken",
            padx=10,
            pady=10
        ).pack(fill="x")

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        tk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            bg="#ff9800",
            fg="white"
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Close",
            command=self.save_and_close,
            bg="#4CAF50",
            fg="white"
        ).pack(side="right", padx=5)

    def update_cursor_speed(self, value):
        """Apply a new cursor speed to the tracker right away."""
        speed = float(value)
        self.tracker.cursor_speed = speed
        self.speed_value_label.config(text=f"Current: {speed:.1f}")
        self.settings.set("cursor", "speed", value=speed)

    def update_smoothing(self, value):
        """Apply a new smoothing value to the tracker right away."""
        alpha = float(value)
        self.tracker.smoother.alpha = alpha
        self.smooth_value_label.config(text=f"Current: {alpha:.2f}")
        self.settings.set("cursor", "smoothing", value=alpha)

    def reset_to_defaults(self):
        """Reset the sliders, labels, tracker and saved file to the defaults."""
        if not messagebox.askyesno(
            "Reset Settings",
            "Reset all settings to their defaults?"
        ):
            return

        self.settings.reset_to_defaults()

        speed = self.settings.get("cursor", "speed")
        alpha = self.settings.get("cursor", "smoothing")

        self.cursor_speed.set(speed)
        self.smooth_level.set(alpha)
        self.update_cursor_speed(speed)
        self.update_smoothing(alpha)

    def save_and_close(self):
        """Save the settings to disk and close the window."""
        self.settings.save()
        self.destroy()