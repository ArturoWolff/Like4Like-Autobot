#!/bin/bash

# Navigate to the script's directory (ensures it can be run from anywhere)
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment 'venv' not found. Please create it and install requirements first."
    exit 1
fi

# Run the bot using the Python executable inside the venv
echo "[*] Starting Like4Like Autobot..."
./venv/bin/python main.py
