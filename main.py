"""
Air Mouse: control the mouse cursor with hand gestures.
"""

import traceback
from tkinter import TclError, messagebox

import customtkinter as ctk

from core.config_manager import ConfigManager
from core.state_manager import StateManager
from gui import theme


def run_app():
    """Create the main window and start the application."""
    config = ConfigManager()
    state_manager = StateManager()

    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.title("Air Mouse")
    root.configure(fg_color=theme.BG)

    window_width = 400
    window_height = 640

    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - window_width - 30  # right side, so the camera preview fits on the left
    y = max(0, (screen_height - window_height) // 2 - 20)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.minsize(380, 620)

    # Optional window icon
    try:
        root.iconbitmap("assets/icon.ico")
    except TclError:
        pass

    # Show the window right away, then load the heavy parts (camera + AI model)
    loading = ctk.CTkLabel(
        root, text="Loading Air Mouse...", font=theme.font(16), text_color=theme.MUTED
    )
    loading.pack(expand=True)
    root.update()

    from gui.control_panel import ControlPanel

    panel = ControlPanel(root, state_manager)
    loading.destroy()
    panel.pack(padx=18, pady=14, fill="both", expand=True)

    def on_closing():
        """Stop tracking, then close."""
        if panel.tracker_thread.is_alive():
            panel.stop_tracking()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        messagebox.showerror("Air Mouse", f"Fatal error:\n{e}")
