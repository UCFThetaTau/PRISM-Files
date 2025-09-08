# PRISM-Files
P.R.I.S.M. ( Prosthetic Recognition & Intelligent Sensing Mechanism )

Development Environment Setup

    after cloning the repo, you must set up a virtual environment, 
    this cannot be committed ./venv is ignored by .gitignore

    Commands for this are as follows
    
    macOS/Linux:

        python3.10 -m venv .venv
        source .venv/bin/activate
        python -m pip install -U pip setuptools wheel

    Windows(PowerShell):

        py -3.10 -m venv .venv
        .\.venv\Scripts\activate
        py -m pip install -U pip setuptools wheel

    After this, install necessary packages as follows
        pip install -r requirements.txt

    You'll have to select the interpreter and reload the window for it to take effect
        Press Cmd/Ctrl+Shift+P → “Python: Select Interpreter” → choose .venv
        Press Cmd/Ctrl+Shift+P → "Developer: Reload Window"

    Notes for Contributors:
        if you add packages, please update requirements.txt
        after git pull, ensure you have all necessary packages installed by running 
        pip install -r requirements.txt