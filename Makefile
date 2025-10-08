# Simple developer helper Makefile for PRISM-Files
PYTHON ?= python3
VENV_PY_FLAG = -m venv

.PHONY: help setup-all setup-launcher setup-tracker run-launcher run-tracker list-ports clean-venvs

help:
	@echo "Targets:"
	@echo "  make setup-all        # create venvs and install deps for Launcher and Tracker"
	@echo "  make setup-launcher   # create venv and install deps for Launcher"
	@echo "  make setup-tracker    # create venv and install deps for HandTracker"
	@echo "  make run-launcher     # run the launcher GUI"
	@echo "  make run-tracker      # run the hand tracker (camera window)"
	@echo "  make list-ports       # list likely serial devices (quick)"
	@echo "  make clean-venvs      # remove .venv directories (destructive)"

setup-launcher:
	cd Applications/Launcher && $(PYTHON) $(VENV_PY_FLAG) .venv && \
	. .venv/bin/activate && \
	python -m pip install -U pip setuptools wheel && \
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

setup-tracker:
	cd Applications/HandTracker && $(PYTHON) $(VENV_PY_FLAG) .venv && \
	. .venv/bin/activate && \
	python -m pip install -U pip setuptools wheel && \
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

setup-all: setup-launcher setup-tracker

run-launcher:
	Applications/Launcher/.venv/bin/python Applications/Launcher/launcher.py

run-tracker:
	Applications/HandTracker/.venv/bin/python Applications/HandTracker/hand_tracker.py

list-ports:
	@echo "macOS / Linux (try these):"
	@ls /dev/cu.* /dev/tty.* 2>/dev/null || true
	@echo ""
	@echo "On Linux also try: /dev/ttyACM0 or /dev/ttyUSB0"
	@echo "On Windows, open Device Manager and look under Ports (COMx)."

clean-venvs:
	rm -rf Applications/Launcher/.venv Applications/HandTracker/.venv
