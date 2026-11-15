"""
Main control panel: big start/stop button, live status, gesture guide.
"""

from tkinter import messagebox

import customtkinter as ctk

from core.thread_manager import ThreadManager
from gui import theme
from gui.settings_panel import SettingsPanel
from tracking.hand_tracker import HandTracker

HELP_TEXT = """GESTURES
Move your index finger  ->  the cursor follows it
Pinch index + thumb  ->  left click
Hold that pinch for 0.4 seconds  ->  drag, release to drop
Pinch middle + thumb  ->  right click
Raise index + middle fingers, move hand up or down  ->  scroll

ACTIVE AREA
Only the cyan box in the camera preview controls the cursor.
Its edges match the screen edges, so small hand moves reach the whole screen.

TIPS
- Sit 1 to 2 feet from the camera
- Use good lighting and keep your whole hand visible
- If the cursor jumps, lower the Smoothing value
- If clicks happen by accident, hold your hand steadier

EMERGENCY STOP
Move the mouse to any corner of the screen.

PREVIEW WINDOW
Press q to close it, or use the Preview button.
"""

GESTURES = [
    ("Move", "Index finger", "Cursor"),
    ("Click", "Pinch index + thumb", "Left click"),
    ("Drag", "Hold the pinch", "Drag and drop"),
    ("Right", "Pinch middle + thumb", "Right click"),
    ("Scroll", "Index + middle up", "Move hand up/down"),
]

# Friendly text and color for each tracker status
STATUS_VIEW = {
    "NO HAND": ("No hand found", theme.AMBER),
    "TRACKING": ("Tracking", theme.GREEN),
    "PINCHING": ("Pinching", theme.ACCENT),
    "LEFT CLICK": ("Left click", theme.ACCENT),
    "RIGHT CLICK": ("Right click", theme.ACCENT),
    "DRAGGING": ("Dragging", theme.ACCENT),
    "DROPPED": ("Dropped", theme.ACCENT),
    "SCROLLING": ("Scrolling", theme.ACCENT),
}


class ControlPanel(ctk.CTkFrame):
    def __init__(self, master, state_manager):
        super().__init__(master, fg_color="transparent")
        self.state_manager = state_manager

        self.tracker = HandTracker()
        self.tracker_thread = ThreadManager(target=self.tracker.run_threaded)
        self.active = False
        self.settings_window = None
        self.help_window = None

        self._build_header()
        self._build_status_card()
        self._build_main_button()
        self._build_footer()
        self._build_guide()

        self._refresh()

    # ---------- layout ----------

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(
            header, text="AIR MOUSE", font=theme.font(30, True), text_color=theme.ACCENT
        ).pack()
        ctk.CTkLabel(
            header,
            text="Control your computer with your hand",
            font=theme.font(13),
            text_color=theme.MUTED,
        ).pack()

    def _build_status_card(self):
        card = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=16)
        card.pack(fill="x", pady=6)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 4))

        self.dot = ctk.CTkLabel(top, text="\u25CF", font=theme.font(22), text_color=theme.OFF)
        self.dot.pack(side="left")

        self.status_label = ctk.CTkLabel(
            top, text="Ready", font=theme.font(20, True), text_color=theme.TEXT
        )
        self.status_label.pack(side="left", padx=10)

        stats = ctk.CTkFrame(card, fg_color=theme.CARD_LIGHT, corner_radius=12)
        stats.pack(fill="x", padx=14, pady=(6, 14))

        self.fps_value = self._stat(stats, "FPS", "--")
        self.mode_value = self._stat(stats, "MODE", "Idle")

    def _stat(self, parent, name, value):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", expand=True, pady=8)
        ctk.CTkLabel(box, text=name, font=theme.font(11), text_color=theme.MUTED).pack()
        label = ctk.CTkLabel(box, text=value, font=theme.font(17, True), text_color=theme.TEXT)
        label.pack()
        return label

    def _build_main_button(self):
        self.main_btn = ctk.CTkButton(
            self,
            text="START",
            font=theme.font(20, True),
            height=58,
            corner_radius=29,
            fg_color=theme.GREEN,
            hover_color=theme.GREEN_DARK,
            text_color="#04210f",
            command=self.toggle_tracking,
        )
        self.main_btn.pack(fill="x", pady=12)

    def _build_guide(self):
        card = ctk.CTkFrame(self, fg_color=theme.CARD, corner_radius=16)
        card.pack(fill="both", expand=True, pady=4)

        ctk.CTkLabel(
            card, text="GESTURES", font=theme.font(12, True), text_color=theme.MUTED
        ).pack(anchor="w", padx=18, pady=(12, 4))

        for tag, how, result in GESTURES:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=4)

            ctk.CTkLabel(
                row,
                text=tag,
                width=56,
                height=28,
                corner_radius=8,
                fg_color=theme.CARD_LIGHT,
                text_color=theme.ACCENT,
                font=theme.font(12, True),
            ).pack(side="left")

            ctk.CTkLabel(
                row, text=how, font=theme.font(13), text_color=theme.TEXT, anchor="w"
            ).pack(side="left", padx=10)

            ctk.CTkLabel(
                row, text=result, font=theme.font(11), text_color=theme.MUTED, anchor="e"
            ).pack(side="right")

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=(8, 0))

        self.preview_btn = self._small_button(footer, "Preview", self.toggle_preview)
        self.preview_btn.configure(state="disabled")
        self._small_button(footer, "Settings", self.open_settings)
        self._small_button(footer, "Help", self.show_help)

    def _small_button(self, parent, text, command):
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=theme.font(13, True),
            width=100,
            height=38,
            corner_radius=12,
            fg_color=theme.CARD_LIGHT,
            hover_color=theme.OFF,
            text_color=theme.TEXT,
            command=command,
        )
        btn.pack(side="left", expand=True, fill="x", padx=4)
        return btn

    # ---------- actions ----------

    def toggle_tracking(self):
        if self.active:
            self.stop_tracking()
        else:
            self.start_tracking()

    def start_tracking(self):
        try:
            if not self.tracker_thread.is_alive():
                self.tracker_thread.start()
            self.state_manager.set_tracking_active(True)
            self.active = True

            self.main_btn.configure(
                text="STOP", fg_color=theme.RED, hover_color=theme.RED_DARK, text_color="white"
            )
            self.preview_btn.configure(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start tracking:\n{e}")
            self._show_stopped("Error")

    def stop_tracking(self):
        try:
            self.tracker_thread.stop()
            self.state_manager.set_tracking_active(False)
            self._show_stopped("Stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop tracking:\n{e}")

    def _show_stopped(self, text):
        """Put the window back into its not-running look."""
        self.active = False
        self.main_btn.configure(
            text="START", fg_color=theme.GREEN, hover_color=theme.GREEN_DARK, text_color="#04210f"
        )
        self.preview_btn.configure(state="disabled")
        self.dot.configure(text_color=theme.OFF)
        self.status_label.configure(text=text)
        self.fps_value.configure(text="--")
        self.mode_value.configure(text="Idle")

    def toggle_preview(self):
        if self.tracker_thread.is_alive():
            self.tracker.toggle_preview()

    def open_settings(self):
        # Only one settings window at a time
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.bring_to_front()
            return
        self.settings_window = SettingsPanel(self, self.tracker)

    def show_help(self):
        # Only one help window at a time
        if self.help_window is not None and self.help_window.winfo_exists():
            self._front(self.help_window)
            return

        window = ctk.CTkToplevel(self)
        self.help_window = window
        window.title("Help")
        window.geometry("520x520")
        window.configure(fg_color=theme.BG)
        window.transient(self.winfo_toplevel())
        window.after(200, lambda: self._front(window))

        ctk.CTkLabel(
            window, text="HELP", font=theme.font(22, True), text_color=theme.ACCENT
        ).pack(pady=(14, 6))

        box = ctk.CTkTextbox(
            window,
            fg_color=theme.CARD,
            text_color=theme.TEXT,
            font=theme.font(13),
            corner_radius=14,
            wrap="word",
        )
        box.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        box.insert("1.0", HELP_TEXT)
        box.configure(state="disabled")

        ctk.CTkButton(
            window, text="Close", height=38, corner_radius=12,
            fg_color=theme.CARD_LIGHT, hover_color=theme.OFF, command=window.destroy,
        ).pack(pady=(0, 14))

    @staticmethod
    def _front(window):
        """Raise a window above the main window and give it focus."""
        window.lift()
        window.focus_force()

    # ---------- live updates ----------

    def _refresh(self):
        """Update the status card ten times per second."""
        if self.active:
            if not self.tracker_thread.is_alive():
                # The tracking thread ended on its own (for example, no camera)
                self._show_stopped("Camera error")
            else:
                text, color = STATUS_VIEW.get(self.tracker.status, ("Tracking", theme.GREEN))
                self.dot.configure(text_color=color)
                self.status_label.configure(text=text)
                self.fps_value.configure(text=f"{self.tracker.fps:.0f}")
                self.mode_value.configure(text="Live")

        self.after(100, self._refresh)
