#!/bin/bash

# Wiley TDM Client Installation Script
# -----------------------------
# 
# Audience: Wiley Labs Developers/Contributors
#
# This script:
# 1. Sets up the Environment Variables (TDM_API_TOKEN & TDM_HOME)
# 2. Clones the tdm-client Git repository in the current directory
# 3. Creates a Python virtual environment, named 'venv'
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
#   source ./install.sh your-tdm-api-token

# Exit on error
set -e

# Check if TDM_API_TOKEN is provided as argument
if [ -z "$1" ]; then
    echo "Error: TDM_API_TOKEN not provided"
    echo "Usage: source ./install.sh your-tdm-api-token"
    return 1 
fi

# Set and export environment variables
export TDM_API_TOKEN="$1"
export TDM_HOME="$(pwd)/tdm-client"

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
pip list | grep wiley-tdm

# Run tests
pytest

# Deactivate virtual environment
deactivate

echo "Installation complete! wiley-tdm package installed and environment variables exported:"
echo "  TDM_API_TOKEN: $TDM_API_TOKEN"
echo "  TDM_HOME: $TDM_HOME"
echo
echo "To use wiley-tdm, activate the virtual environment:"
echo "  cd \$TDM_HOME"
echo "  source venv/bin/activate"

return 0
