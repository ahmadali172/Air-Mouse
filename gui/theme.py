"""
Colors and fonts shared by all windows.
"""

import customtkinter as ctk

BG = "#0b0f19"
CARD = "#141b2d"
CARD_LIGHT = "#1c2540"
ACCENT = "#00d4ff"
ACCENT_DARK = "#0099bb"
GREEN = "#22c55e"
GREEN_DARK = "#16a34a"
RED = "#ef4444"
RED_DARK = "#dc2626"
AMBER = "#f59e0b"
TEXT = "#e6edf7"
MUTED = "#8a96b0"
OFF = "#3b4560"


def font(size, bold=False):
    return ctk.CTkFont(family="Segoe UI", size=size, weight="bold" if bold else "normal")
