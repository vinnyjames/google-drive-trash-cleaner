#!/bin/bash
# Run Google Drive Trash Cleaner with virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/update dependencies if needed
if [ ! -f "$VENV_DIR/.installed" ] || [ "$SCRIPT_DIR/requirements.txt" -nt "$VENV_DIR/.installed" ]; then
    echo "Installing dependencies..."
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    touch "$VENV_DIR/.installed"
fi

# Run the cleaner with any passed arguments
python "$SCRIPT_DIR/cleaner.py" "$@"
