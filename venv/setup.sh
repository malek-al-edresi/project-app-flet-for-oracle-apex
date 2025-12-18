#!/bin/bash

echo "Setting up Patient Viewer App..."

# Navigate to home directory first
cd ~

# Create virtual environment
python3 -m venv patient_viewer_venv

# Activate it
source patient_viewer_venv/bin/activate

# Install packages
pip install flet requests

echo "Setup complete!"
echo ""
echo "To run the app, first activate the virtual environment:"
echo "  source ~/patient_viewer_venv/bin/activate"
echo "Then navigate to your project:"
echo "  cd ~/GitHub/project-app-flet-for-oracle-apex/"
echo "And run:"
echo "  python3 main.py"