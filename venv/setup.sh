#!/bin/bash

echo "Setting up Patient Viewer App..."

# Navigate to home directory first
cd ~

# Create virtual environment
# Create a virtual environment
python3 -m venv medical_app_env

# Activate the environment
source medical_app_env/bin/activate

# Install packages in the virtual environment
pip install flet requests

# Run your application
python main.py

echo "Setup complete!"
echo ""
echo "To run the app, first activate the virtual environment:"
echo "  source ~/patient_viewer_venv/bin/activate"
echo "Then navigate to your project:"
echo "  cd ~/GitHub/project-app-flet-for-oracle-apex/"
echo "And run:"
echo "  python3 main.py"