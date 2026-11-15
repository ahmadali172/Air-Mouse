"""
Settings window: change cursor speed, smoothing and active area while the app runs.
"""

from tkinter import messagebox

import customtkinter as ctk

from core.config_manager import ConfigManager
from gui import theme


class SettingsPanel(ctk.CTkToplevel):
    def __init__(self, master, tracker):
        super().__init__(master)
        self.title("Settings")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG)
        self.transient(master.winfo_toplevel())
        self.after(200, self.bring_to_front)

        self.tracker = tracker
        self.settings = ConfigManager()
        self.protocol("WM_DELETE_WINDOW", self.save_and_close)

        ctk.CTkLabel(
            self, text="SETTINGS", font=theme.font(22, True), text_color=theme.ACCENT
        ).pack(pady=(16, 8))

        self.speed = self._slider_card(
            "Cursor Speed", "Slower  <->  Faster",
            0.5, 3.0, 25, self.tracker.cursor_speed, self.update_cursor_speed, "{:.1f}",
        )
        self.smooth = self._slider_card(
            "Smoothing", "Smoother  <->  More responsive",
            0.1, 0.9, 16, self.tracker.smoother.alpha, self.update_smoothing, "{:.2f}",
        )
        self.area = self._slider_card(
            "Active Area", "Smaller box  <->  Whole camera view",
            0.3, 1.0, 14, self.tracker.active_area, self.update_active_area, "{:.2f}",
        )

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=20, pady=14)

        ctk.CTkButton(
            buttons, text="Reset", height=40, corner_radius=12,
            fg_color=theme.CARD_LIGHT, hover_color=theme.OFF,
            command=self.reset_to_defaults,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="Save & Close", height=40, corner_radius=12,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_DARK, text_color="#021419",
            command=self.save_and_close,
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def bring_to_front(self):
        """Raise this window above the main window and give it focus."""
        self.lift()
        self.focus_force()

    def _slider_card(self, title, hint, low, high, steps, value, command, fmt):
        card = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=16)
        card.pack(fill="x", padx=20, pady=6)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 0))

        ctk.CTkLabel(top, text=title, font=theme.font(15, True), text_color=theme.TEXT).pack(side="left")
        value_label = ctk.CTkLabel(
            top, text=fmt.format(value), font=theme.font(15, True), text_color=theme.ACCENT
        )
        value_label.pack(side="right")

        ctk.CTkLabel(
            card, text=hint, font=theme.font(11), text_color=theme.MUTED
        ).pack(anchor="w", padx=16)

        def on_change(v):
            value_label.configure(text=fmt.format(v))
            command(v)

        slider = ctk.CTkSlider(
            card, from_=low, to=high, number_of_steps=steps,
            progress_color=theme.ACCENT, button_color=theme.ACCENT,
            button_hover_color=theme.ACCENT_DARK, command=on_change,
        )
        slider.set(value)
        slider.pack(fill="x", padx=16, pady=(8, 14))

        return slider, value_label, fmt

    def update_cursor_speed(self, value):
        speed = float(value)
        self.tracker.cursor_speed = speed
        self.settings.set("cursor", "speed", value=speed)

    def update_smoothing(self, value):
        alpha = float(value)
        self.tracker.smoother.alpha = alpha
        self.settings.set("cursor", "smoothing", value=alpha)

    def update_active_area(self, value):
        area = float(value)
        self.tracker.active_area = area
        self.settings.set("cursor", "active_area", value=area)

    def reset_to_defaults(self):
        if not messagebox.askyesno("Reset Settings", "Reset all settings to their defaults?"):
            return

        self.settings.reset_to_defaults()

        pairs = [
            (self.speed, "speed", self.update_cursor_speed),
            (self.smooth, "smoothing", self.update_smoothing),
            (self.area, "active_area", self.update_active_area),
        ]
        for (slider, label, fmt), key, update in pairs:
            value = self.settings.get("cursor", key)
            slider.set(value)
            label.configure(text=fmt.format(value))
            update(value)

    def save_and_close(self):
        self.settings.save()
        self.destroy()
