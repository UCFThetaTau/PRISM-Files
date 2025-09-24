# apps/launcher-desktop/launcher.py
import sys, os, platform
from pathlib import Path
from PySide6.QtCore import QProcess, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QSpinBox, QLineEdit, QFileDialog,
    QComboBox, QMessageBox
)
from PySide6.QtGui import QTextCursor



REPO_ROOT = Path(__file__).resolve().parents[2]
TRACKER_DIR = REPO_ROOT / "Applications" / "HandTracker"
DEFAULT_SCRIPT = TRACKER_DIR / "hand_tracker.py"      # adjust if different

def guess_python_for_tracker() -> str:
    """Prefer the hand-tracker's venv python; fall back to current python."""
    candidates = []
    venv = TRACKER_DIR / ".venv"
    if platform.system() == "Windows":
        candidates += [venv / "Scripts" / "python.exe"]
    else:
        candidates += [venv / "bin" / "python"]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable

class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Launcher")
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyReadStandardOutput.connect(self.on_stdout)
        self.proc.readyReadStandardError.connect(self.on_stdout)
        self.proc.finished.connect(self.on_finished)

        # --- UI ---
        central = QWidget(self); self.setCentralWidget(central)
        v = QVBoxLayout(central)

        # Status + controls row
        status_row = QHBoxLayout()
        self.status = QLabel("Idle")
        self.status.setStyleSheet("font-weight: 600;")
        status_row.addWidget(self.status)
        status_row.addStretch()
        v.addLayout(status_row)

        # Script path picker
        script_row = QHBoxLayout()
        self.script_edit = QLineEdit(str(DEFAULT_SCRIPT))
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_script)
        script_row.addWidget(QLabel("Tracker script:"))
        script_row.addWidget(self.script_edit, 1)
        script_row.addWidget(browse_btn)
        v.addLayout(script_row)

        # Python interpreter (auto-detected)
        py_row = QHBoxLayout()
        self.py_edit = QLineEdit(guess_python_for_tracker())
        py_row.addWidget(QLabel("Python:"))
        py_row.addWidget(self.py_edit, 1)
        v.addLayout(py_row)

        # Example args (customize to your tracker)
        args_row = QHBoxLayout()
        self.cam_spin = QSpinBox(); self.cam_spin.setRange(0, 10); self.cam_spin.setValue(0)
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["live", "video"])
        args_row.addWidget(QLabel("Camera:")); args_row.addWidget(self.cam_spin)
        args_row.addWidget(QLabel("Mode:")); args_row.addWidget(self.mode_combo)
        v.addLayout(args_row)

        # Start/Stop buttons
        btns = QHBoxLayout()
        self.start_btn = QPushButton("Start Hand Tracker")
        self.stop_btn  = QPushButton("Stop")
        self.start_btn.clicked.connect(self.start_tracker)
        self.stop_btn.clicked.connect(self.stop_tracker)
        btns.addWidget(self.start_btn); btns.addWidget(self.stop_btn)
        v.addLayout(btns)

        # Log output
        self.log = QTextEdit(); self.log.setReadOnly(True)
        v.addWidget(self.log, 1)

        # Size
        self.resize(900, 600)

    def browse_script(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select tracker script", str(TRACKER_DIR), "Python (*.py)")
        if path:
            self.script_edit.setText(path)

    def start_tracker(self):
        if self.proc.state() != QProcess.NotRunning:
            QMessageBox.information(self, "Already running", "Hand tracker is already running.")
            return

        python = self.py_edit.text().strip()
        script = self.script_edit.text().strip()
        if not Path(script).exists():
            QMessageBox.warning(self, "Script not found", f"Cannot find:\n{script}")
            return

        args = [script, "--camera", str(self.cam_spin.value()), "--mode", self.mode_combo.currentText()]
        # If your tracker expects different flags, adjust here.

        # Ensure working dir (so relative assets load)
        self.proc.setWorkingDirectory(str(TRACKER_DIR))

        self.append_log(f"$ {python} {' '.join(args)}\n")
        self.proc.start(python, args)
        if not self.proc.waitForStarted(3000):
            self.append_log("ERROR: Failed to start process.\n")
            return
        self.set_status("Running")

    def stop_tracker(self):
        if self.proc.state() != QProcess.NotRunning:
            self.proc.terminate()
            if not self.proc.waitForFinished(2000):
                self.proc.kill()

    def on_stdout(self):
        data = bytes(self.proc.readAllStandardOutput()).decode(errors="ignore")
        if data:
            self.append_log(data)
        data_err = bytes(self.proc.readAllStandardError()).decode(errors="ignore")
        if data_err:
            self.append_log(data_err)

    def on_finished(self):
        self.append_log("\n[process exited]\n")
        self.set_status("Idle")

    def append_log(self, text: str):
        self.log.moveCursor(QTextCursor.MoveOperation.End)
        self.log.insertPlainText(text)
        self.log.moveCursor(QTextCursor.MoveOperation.End)
        self.log.ensureCursorVisible()


    def set_status(self, s: str):
        self.status.setText(s)

def main():
    app = QApplication(sys.argv)
    w = Launcher(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
