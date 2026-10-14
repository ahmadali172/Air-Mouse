"""
Test if PyAutoGUI can control your mouse
"""

import pyautogui
import time

print("Testing PyAutoGUI...")
print(f"Screen size: {pyautogui.size()}")
print(f"Current mouse position: {pyautogui.position()}")

print("\n" + "="*60)
print("TEST 1: Move mouse to center of screen")
print("="*60)

screen_width, screen_height = pyautogui.size()
center_x = screen_width // 2
center_y = screen_height // 2

try:
    pyautogui.moveTo(center_x, center_y, duration=1)
    print(f"✓ Mouse moved to ({center_x}, {center_y})")
    time.sleep(1)
except Exception as e:
    print(f"❌ Failed to move mouse: {e}")

print("\n" + "="*60)
print("TEST 2: Perform a click")
print("="*60)

try:
    pyautogui.click()
    print("✓ Click performed!")
except Exception as e:
    print(f"❌ Failed to click: {e}")

print("\n" + "="*60)
print("TEST 3: Right click")
print("="*60)

try:
    pyautogui.rightClick()
    print("✓ Right click performed!")
except Exception as e:
    print(f"❌ Failed to right click: {e}")

print("\n" + "="*60)
print("Tests complete!")
print("="*60)
print("\nIf you saw ❌ errors, PyAutoGUI needs permissions.")

input("\nPress Enter to exit...")