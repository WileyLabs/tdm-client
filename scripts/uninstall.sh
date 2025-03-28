#!/bin/bash

# TDM Client Uninstallation Script
# --------------------------------
# This script:
# 1. Removes the TDM API token and TDM_HOME environment variables from ~/.bashrc
# 2. Deletes the 'tdm-client' directory from the current location
# 3. Cleans up the Python virtual environment
#
# Requirements:
# - Bash shell
#
# Usage:
#   cd ~/projects/
#   source ./uninstall.sh

# Exit on error
set -e

echo "Uninstalling tdmclient..."

# Check if virtual environment is active and in TDM_HOME
if [ -n "$VIRTUAL_ENV" ]; then
    if [[ "$VIRTUAL_ENV" == "$TDM_HOME/venv" ]]; then
        echo "Deactivating tdmclient virtual environment: $VIRTUAL_ENV"
        VENV_PATH="$VIRTUAL_ENV"  # Store path before deactivating
        deactivate
        echo "Removing virtual environment at: $VENV_PATH"
        rm -rf "$VENV_PATH"
    else
        echo "Warning: Active virtual environment is not tdmclient's environment"
        echo "Current: $VIRTUAL_ENV"
        echo "Expected: $TDM_HOME/venv"
        return 1
    fi
else
    echo "No active virtual environment found"
fi

# Remove repository
echo "Removing tdmclient repository at: $TDM_HOME"
cd ~
rm -rf "$TDM_HOME"

# Clean up environment variables last
unset TDM_API_TOKEN
unset TDM_HOME
sed -i '/TDM_API_TOKEN/d' ~/.bashrc
sed -i '/TDM_HOME/d' ~/.bashrc

echo "Uninstallation complete! Package environment and variables removed"

return 0