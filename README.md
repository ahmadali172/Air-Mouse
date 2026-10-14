# Air Mouse

Control your computer's mouse cursor with hand gestures, using only a webcam.

Air Mouse tracks your hand in real time with MediaPipe, moves the cursor with your index finger, and turns pinch gestures into left and right clicks. It comes with a simple desktop control panel for starting, stopping and tuning the tracker.

![Air Mouse demo](assets/demo.gif)

---

## Features

- Real-time hand tracking from a standard webcam
- Cursor movement controlled by the index fingertip
- Left click and right click with pinch gestures
- Smoothing filter to reduce cursor jitter
- Live camera preview with FPS and gesture status
- Desktop control panel (Tkinter) with start, stop, preview toggle and help
- Settings window to adjust cursor speed and smoothing while running
- Settings saved to a JSON file and restored on the next launch
- Emergency stop: move the mouse to any screen corner

---

## Gestures

| Gesture | Action |
|---|---|
| Move your index finger | Cursor follows it |
| Index finger and thumb pinch | Left click |
| Middle finger and thumb pinch | Right click |

---

## How it works

```
Webcam frame
    -> MediaPipe Hands (21 hand landmarks)
    -> Smoothing (exponential moving average)
    -> Cursor movement (index fingertip mapped to the screen)
    -> Gesture detection (pinch distances between fingertips)
    -> PyAutoGUI (moves the cursor and sends clicks)
```

1. **Capture:** OpenCV reads frames from the webcam and flips them like a mirror
2. **Detect:** MediaPipe Hands finds 21 landmarks on the hand
3. **Smooth:** an exponential moving average reduces jitter. A lower smoothing value gives a steadier but slower cursor
4. **Move:** the index fingertip position is mapped to screen coordinates, and the cursor moves toward it, scaled by the cursor speed setting
5. **Click:** when the distance between the thumb tip and the index or middle fingertip drops below a threshold, a click is sent. A cooldown prevents repeated clicks
6. **Threading:** tracking runs in a background thread, so the control panel stays responsive

---

## Requirements

- Python 3.8 to 3.11 (the pinned MediaPipe and NumPy versions do not support newer Python versions)
- A webcam
- Tested on Windows

---

## Installation

```bash
git clone https://github.com/ahmadali172/air-mouse.git
cd air-mouse

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`. Cursor control and camera access may need extra permissions there, and the project has only been tested on Windows.

---

## Usage

```bash
python main.py
```

1. Click **START AIR MOUSE** and allow camera access
2. Hold your hand 1 to 2 feet from the camera, with your fingers visible
3. Move your index finger to move the cursor
4. Pinch to click
5. Click **STOP AIR MOUSE** when you are done

**Emergency stop:** move the mouse to any corner of the screen. PyAutoGUI's fail-safe stops all control.

**Preview window:** press `q` to close it, or use the Toggle Camera Preview button.

---

## Settings

Open **Settings** in the control panel to change these while the app is running:

| Setting | Effect |
|---|---|
| Cursor Speed | How far the cursor moves toward your fingertip each frame |
| Smoothing Level | Lower values give smoother but slower cursor movement |

Changes are saved when you close the settings window, and **Reset to Defaults** restores the original values.

Advanced options are stored in `config/settings.json`, which is created on first run. You can edit it while the app is closed:

| Key | Default | Meaning |
|---|---|---|
| `camera.index` | 0 | Which camera to use |
| `camera.resolution_width` / `resolution_height` | 640 / 480 | Capture resolution |
| `tracking.max_hands` | 1 | Number of hands tracked |
| `tracking.detection_confidence` | 0.5 | MediaPipe detection confidence |
| `tracking.tracking_confidence` | 0.5 | MediaPipe tracking confidence |
| `cursor.speed` | 1.5 | Cursor speed multiplier |
| `cursor.smoothing` | 0.3 | Smoothing factor |
| `cursor.margin` | 5 | Pixels kept free at the screen edges |
| `gestures.pinch_threshold` | 0.12 | How close the fingers must be to count as a pinch |
| `gestures.click_cooldown` | 0.5 | Seconds between clicks |
| `ui.show_preview` | true | Show the camera preview on start |

---

## Project structure

```
.
|-- main.py                  # entry point: creates the window and control panel
|-- requirements.txt
|-- core/
|   |-- config_manager.py    # load, save and reset JSON settings
|   |-- state_manager.py     # thread-safe tracking-active flag
|   `-- thread_manager.py    # start and stop the background tracking thread
|-- gui/
|   |-- control_panel.py     # main window: start, stop, preview, help
|   `-- settings_panel.py    # settings window with sliders
|-- tracking/
|   |-- hand_tracker.py      # webcam loop, MediaPipe, cursor movement, clicks
|   |-- gesture_engine.py    # pinch gesture detection
|   `-- smoothing.py         # exponential moving average smoother
`-- assets/
    `-- demo.gif
```

---

## Tech stack

| Part | Tool |
|---|---|
| Hand tracking | MediaPipe Hands |
| Video capture and preview | OpenCV |
| Mouse control | PyAutoGUI |
| Numerical work | NumPy |
| Interface | Tkinter |
| Settings | JSON |

---

## Troubleshooting

| Problem | Try this |
|---|---|
| The cursor jumps around | Move the Smoothing slider toward Smoother |
| The cursor feels slow | Increase Cursor Speed |
| Clicks do not register | Make sure your whole hand is visible and well lit. You can raise `gestures.pinch_threshold` in the config |
| Clicks trigger by accident | Lower `gestures.pinch_threshold` in the config |
| Camera does not open | Close other apps that use the camera, check camera permissions, or change `camera.index` |
| `pip install` fails | Check that you are using Python 3.8 to 3.11 |

---

## Limitations

- Supports one hand
- Only left click and right click. Drag and scroll are not implemented
- Needs good lighting, and accuracy drops when the hand is partly hidden
- Tested on Windows only

## Future improvements

- Drag and drop gesture
- Scroll gesture
- Cursor movement relative to a smaller active area of the camera frame
- Per-user gesture calibration
- Packaged executable for Windows

---

## Author

Ahmad Ali, CS graduate focused on AI and computer vision applications
GitHub: [@ahmadali172](https://github.com/ahmadali172)