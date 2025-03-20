#!/bin/bash

# TDM Client Installation Script
# -----------------------------
# This script:
# 1. Sets up the TDM API token for Wiley access
# 2. Clones the tdm-client repository
# 3. Creates a Python virtual environment
# 4. Installs the package with test dependencies
# 5. Runs the test suite to verify installation
#
# Requirements:
# - Python 3.9 or higher
# - Git
# - Bash shell
#
# Usage:
#   cd ~/projects/
#   curl -O https://raw.githubusercontent.com/WileyLabs/tdm-client/main/scripts/{install,uninstall}.sh
#   chmod +x *.sh
#   ./install.sh your-tdm-api-token
#
# Note: This script will:
# - Add TDM_API_TOKEN to your ~/.bashrc
# - Create a 'tdm-client' directory in current location (e.g. ~/projects/)
# - Create a Python virtual environment named 'venv'

# Exit on error
set -e

# Check if TDM_API_TOKEN is provided as argument
if [ -z "$1" ]; then
    echo "Error: TDM_API_TOKEN not provided"
    echo "Usage: ./install.sh your-tdm-api-token"
    exit 1
fi

# Set and export environment variables
export TDM_API_TOKEN="$1"

# Set parent directory for installation
INSTALL_DIR="$(pwd)"
export TDM_HOME="$INSTALL_DIR/tdm-client"

# Add exports to .bashrc for persistence
echo "export TDM_API_TOKEN='$1'" >> ~/.bashrc
echo "export TDM_HOME='$TDM_HOME'" >> ~/.bashrc

# Clone repository if not already present
if [ ! -d "$TDM_HOME" ]; then
    # Clone into the current directory - git will create tdm-client subdirectory
    git clone https://github.com/WileyLabs/tdm-client.git "$TDM_HOME"
fi

# Change to project directory
cd "$TDM_HOME"

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the package in editable mode (build not required)
pip install -e ".[test]"

# Show installed package
pip list | grep tdmclient

# Run tests
pytest

# Deactivate virtual environment
deactivate

echo "Installation complete! tdmclient package installed and environment variables exported:"
echo "  TDM_API_TOKEN: [configured]"
echo "  TDM_HOME: $TDM_HOME"
echo
echo "To use tdmclient, activate the virtual environment:"
echo "  cd \$TDM_HOME"
echo "  source venv/bin/activate"