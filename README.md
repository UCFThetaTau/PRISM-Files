# PRISM-Files
P.R.I.S.M. ( Prosthetic Recognition & Intelligent Sensing Mechanism )

PRISM — Dev Environment Setup (per app)

This repo has two Python apps under Applications/, each with its own virtual environment in .venv/ (which must not be committed).

Prereqs :

Python 3.10+ installed (python3 --version on macOS/Linux, py --version on Windows).

VS Code with the Python extension (recommended).

HAND TRACKER :

    Commands for this are as follows
    
    macOS/Linux:

        cd Applications/HandTracker
        python3.10 -m venv .venv
        source .venv/bin/activate
        python -m pip install -U pip setuptools wheel

    Windows(PowerShell):

        cd Applications\HandTracker
        py -3.10 -m venv .venv
        .\.venv\Scripts\Activate.ps1
        py -m pip install -U pip setuptools wheel


LAUNCHER :

    macOS/Linux:

        cd Applications/Launcher
        python3 -m venv .venv
        source .venv/bin/activate
        python -m pip install -U pip setuptools wheel
        pip install -r requirements.txt   # contains PySide6 and any other UI deps
        python launcher.py

    Windows (PowerShell): 

        cd Applications\Launcher
        py -3 -m venv .venv
        .\.venv\Scripts\Activate.ps1
        py -m pip install -U pip setuptools wheel
        pip install -r requirements.txt
        py launcher.py

VS CODE: select the right interpreter (per app)

    Open the folder for the app (Applications/HandTracker or Applications/Launcher).

    Cmd/Ctrl+Shift+P → Python: Select Interpreter → choose the one in that app’s .venv/.

    Cmd/Ctrl+Shift+P → Developer: Reload Window.

KEEPING DEPENDENCIES IN SYNC :

    Installing packages per app:

        cd Applications/HandTracker OR cd Applications/Launcher
        git pull

    When YOU add a new package:
        - please replace anything within <> with the actual name
        
        pip install <package>
        python -m pip freeze > requirements.txt
        git add requirements.txt
        git commit -m "deps: add <package> to <App>"

COMMON ISSUES :

    If VS Code runs the wrong Python...

        re-run "Python: Select Interpreter" inside the app folder

    Careful...
    
        Don’t share one venv across apps—each app should activate its own .venv/