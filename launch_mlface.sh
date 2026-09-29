#!/bin/bash
# launch_mlface.sh - Start script for Homebrew service

# Navigate to the project directory
cd "/Volumes/Projects/iot/mlface"

# Ensure log directory/files are writable
touch mlface.log

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "No virtual environment found. Using system python."
fi

# Run the service
# Note: Ensure dependencies are installed: pip install -r requirements_mps.txt
exec python3 mlface_mps.py -d ./known_faces
