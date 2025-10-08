# PRISM-Files
Prosthetic Recognition & Intelligent Sensing Mechanism (PRISM)

Purpose
-------
This repo contains the hand-tracking + servo-control tools used by the PRISM project. The two main components live under `Applications/`:

- `Applications/Launcher` — desktop GUI to run the tracker, send manual angles, or forward Live Tracking angles to the hand.
- `Applications/HandTracker` — MediaPipe/OpenCV-based tracker that prints ANGLE lines: `ANGLE <hand_index> <degrees>`.
- `handSerial.py` — serial helper that sends ASCII commands to an Arduino (supports one-shot and `--serve` modes).
- `hand1.2.ino` — Arduino sketch for the PCA9685 servo driver (serial command protocol documented in the sketch).

Quick start overview
---------------------------
1) Pick your platform instructions below. 2) Use the included Makefile (`make setup-all`) on macOS/Linux, or run `dev-setup.ps1` on Windows to create the per-app `.venv` and install dependencies. 3) Start the Launcher GUI and choose User Input or Live Tracking.

Getting started (macOS / Linux)
------------------------------

Fast path (macOS/Linux):

```bash
# from repo root
make setup-all
make run-launcher
```

Fast path (Windows / PowerShell):

```powershell
# from repo root in PowerShell
.\dev-setup.ps1 -Target all
.\Applications\Launcher\.venv\Scripts\python.exe .\Applications\Launcher\launcher.py
```

Manual setup
-----------------------
Follow the platform-specific steps below if you prefer to set up environments by hand. These commands create an app-local virtualenv, install dependencies, and run the app.

macOS / Linux (zsh / bash)

1) Install Python 3.10+ if you don't have it (on macOS, Homebrew is convenient):

```bash
# macOS (Homebrew)
brew install python@3.11
# Linux: use your distro package manager, e.g. Ubuntu: sudo apt install python3 python3-venv python3-pip
```

2) Launcher (GUI)

```bash
cd Applications/Launcher
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python launcher.py
```

3) Hand tracker (optional standalone)

```bash
cd Applications/HandTracker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python hand_tracker.py
```

Windows (PowerShell)

1) Make sure you have Python 3.10+ installed (use the official installer from python.org).

2) Launcher (GUI)

```powershell
cd Applications\Launcher
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -U pip setuptools wheel
pip install -r requirements.txt
py launcher.py
```

3) Hand tracker (optional standalone)

```powershell
cd ..\HandTracker
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -U pip setuptools wheel
pip install -r requirements.txt
py hand_tracker.py
```


Finding serial ports
--------------------
- Python (cross-platform, requires pyserial):

```bash
python -m serial.tools.list_ports
```

- macOS: list candidates

```bash
ls /dev/cu.*
```

- Linux: check kernel messages after plugging the board

```bash
dmesg | tail -n 30
```

- Windows (PowerShell):

```powershell
Get-PnpDevice -Class Ports
```


Notes
-----
- Each application (Launcher / HandTracker) uses its own `.venv/` in the app folder. Activate the correct venv before running or selecting the interpreter in your editor.
- If you get serial permission errors on Linux, add your user to the `dialout` (or equivalent) group: `sudo usermod -a -G dialout $USER` and re-login.
- On macOS, if your terminal can't open the serial device, check System Settings → Privacy & Security and grant the Terminal or IDE access if required.

Launcher modes
--------------
- User Input: runs `handSerial.py` once to send a single `<channel> <angle>` command.
- Live Tracking: starts `handSerial.py --serve` and the tracker; ANGLE lines are forwarded to the server which writes to serial.

Serial port notes
-----------------
- macOS: device names are typically `/dev/cu.usbmodem*` or `/dev/cu.usbserial*` (`ls /dev/cu.*`).
- Linux: try `/dev/ttyACM0` or `/dev/ttyUSB0`.
- Windows: use COM ports (Device Manager).
- If the serial port is inaccessible, check OS permissions and drivers (macOS privacy, Windows CP210x/FTDI drivers).


Developer helpers
-----------------
- `Makefile` (repo root): `make setup-all`, `make run-launcher`, `make run-tracker`, `make list-ports`, `make clean-venvs`.
- `dev-setup.ps1`: PowerShell helper to create per-app venvs and install requirements on Windows.
- `handSerial.py`: supports `--serve` mode (persistent) and one-shot `--channel`/`--angle` calls.

Troubleshooting
---------------
- Wrong Python in VS Code: open the app folder and use "Python: Select Interpreter" to choose the app's `.venv`.
- Missing packages: activate the app venv and run `pip install -r requirements.txt`.
- Serial errors: close other serial apps, verify drivers, and check OS privacy/permissions.

Contributing / dependencies
---------------------------
When you add a dependency to an app:

```bash
# activate that app's venv
pip install <package>
python -m pip freeze > requirements.txt
git add requirements.txt
git commit -m "deps: add <package> to <App>"
```

