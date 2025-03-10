#!/bin/bash

# Exit on error
set -e

# Check if TDM_API_TOKEN is provided as argument
if [ -z "$1" ]; then
    echo "Error: TDM_API_TOKEN not provided"
    echo "Usage: ./install.sh your-tdm-api-token"
    exit 1
fi

# Export the TDM_API_TOKEN
export TDM_API_TOKEN="$1"

# Add the export to .bashrc for persistence
echo "export TDM_API_TOKEN='$1'" >> ~/.bashrc

# Clone repository if not already present
if [ ! -d "tdm-client" ]; then
    git clone https://github.com/WileyLabs/tdm-client.git
fi

# Change to project directory
cd tdm-client

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip list

# Deactivate virtual environment
deactivate

echo "Installation complete! TDM_API_TOKEN has been exported and added to .bashrc"