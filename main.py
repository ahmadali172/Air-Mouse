"""
Air Mouse: control the mouse cursor with hand gestures.
"""

import tkinter as tk
import traceback
from tkinter import messagebox

from core.config_manager import ConfigManager
from core.state_manager import StateManager
from gui.control_panel import ControlPanel


def run_app():
    """Create the main window and start the application."""
    config = ConfigManager()
    state_manager = StateManager()

    root = tk.Tk()
    root.title("Air Mouse Control v2.0")

    window_width = config.get("ui", "window_width") or 300
    window_height = config.get("ui", "window_height") or 400

    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.minsize(300, 400)

    # Optional window icon
    try:
        root.iconbitmap("assets/icon.ico")
    except tk.TclError:
        pass

    panel = ControlPanel(root, state_manager)
    panel.pack(padx=10, pady=10, fill="both", expand=True)

    def on_closing():
        """Ask before closing while tracking is running."""
        if panel.tracker_thread.is_alive():
            if messagebox.askyesno(
                "Air Mouse Running",
                "Air Mouse is still running. Stop it before closing?"
            ):
                panel.stop_tracking()
                root.after(500, root.destroy)
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    messagebox.showinfo(
        "Welcome",
        "Welcome to Air Mouse v2.0\n\n"
        "Control your mouse with hand gestures.\n\n"
        "Click Help for instructions or START to begin."
    )

    root.mainloop()


if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()