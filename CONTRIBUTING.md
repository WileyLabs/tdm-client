# Contributing to tdm-client

[Wiley](http://wiley.com/) Open Source Software projects are managed under the
[WileyLabs](https://github.com/WileyLabs/) organization on GitHub.

## Table of Contents
- [Overview](#overview)
- [Development Setup](#development-setup)
  - [Requirements](#requirements)
  - [Manual Setup](#option-1-manual-setup)
  - [Script Setup](#option-2-install-script)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [License](#license)

## Overview
Thank you for your interest in contributing to this project! We use GitHub's
Pull Request (PR) system to review incoming changes.

Any changes sent via a PR will be reviewed by current project contributors for
provenance, code quality, and license concerns. Once approved, the PR will be
merged and become part of this "upstream" project. Any contributions should be
licensed under the same license as the project itself.

Please be sure any contributions are owned by you or are within your means to
contribute.

Thank you again for your interest!


## Development Setup

### Requirements:
- Python 3.9 or higher
- Git

### Option 1: Manual Setup

```bash
# Start in your projects directory
mkdir -p ~/projects && cd ~/projects

# Clone the repository
git clone https://github.com/WileyLabs/tdm-client.git

# Change to project directory
cd tdm-client

# Set your TDM API token
export TDM_API_TOKEN='your-tdm-api-token'

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package with test dependencies
(venv) $ pip install -e ".[test]"

# Run tests
(venv) $ pytest

# Deactivate virtual environment
(venv) $ deactivate
```

### Option 2: Script Setup

Alternatively, download and run ([install.sh](scripts/install.sh)).

```bash
# Start in your projects directory
mkdir -p ~/projects && cd ~/projects

# Download installation scripts
curl -O https://raw.githubusercontent.com/WileyLabs/tdm-client/main/scripts/{install,uninstall}.sh

# Make scripts executable
chmod +x *.sh

# Run installation
source ./install.sh your-tdm-api-token
```

## Running Tests

To run tests, use the following command:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
(venv) $ pytest
```

## Code Style

This project uses:
- black for code formatting
- pylint for linting
- isort for import sorting

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Add tests for any new functionality
4. Ensure all tests pass
5. Submit a pull request

## Questions or Issues?

Please open an issue in the GitHub repository.
