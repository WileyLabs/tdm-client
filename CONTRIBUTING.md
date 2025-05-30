# Contributing to tdm-client

[Wiley](http://wiley.com/) Open Source Software projects are managed under the
[WileyLabs](https://github.com/WileyLabs/) organization on GitHub.

## Table of Contents
- [Overview](#overview)
- [Environment Setup](#environment-setup)
  - [Linux Users](#linux-users)
  - [Windows Users (using WSL)](#windows-users-using-wsl)
  - [VS Code Setup](#vs-code-setup)
- [Project Setup](#project-setup)
  - [Manual Installation](#manual-installation)
  - [Script Installation](#script-installation)
- [Development Workflow](#development-workflow)
  - [Code Style](#code-style)
  - [Running Tests](#running-tests)
  - [Building Package](#building-package)
  - [Local CI](#local-ci)
- [Contributing Changes](#contributing-changes)
  - [Pull Request Process](#pull-request-process)
  - [Questions and Issues](#questions-and-issues)

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


## Environment Setup

### Linux Users

Install the following:

- [Python](https://www.python.org/downloads/) 3.9 or higher
  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip
  ```
- [Git](https://git-scm.com/downloads) for version control
  ```bash
  sudo apt install git
  ```
- [Visual Studio Code](https://code.visualstudio.com/)
  ```bash
  sudo apt install code
  ```

Assuming Debian based envinemnt (e.g. Ubuntu)

### Windows Users
Follow VSC's [Developing in WSL](https://code.visualstudio.com/docs/remote/wsl). Then install inside WSL:

- [Python](https://www.python.org/downloads/) 3.9 or higher
  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip
  ```
- [Git](https://git-scm.com/downloads) for version control
  ```bash
  sudo apt install git
  ```

*Note: While Windows native development is possible, we recommend using WSL for the best experience.*

### VS Code Setup

This project uses VS Code with preconfigured [settings](.vscode/settings.json) and [recommended extensions](.vscode/extensions.json).

Opening the project in VS Code will automatically:
- Prompt to install recommended extensions
- Apply project-specific settings
- Configure Python tools (Black, isort, Pylint)


## Project Setup

### Manual Installation

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

# Locally installs dependencies, lints, tests with coverage, and builds project
(venv) $ make all

# Deactivate virtual environment (optional)
(venv) $ deactivate
```

### Script Installation

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

## Development Workflow

### Code Style

To check and enforce code style:

```bash
# Activate virtual environment
source venv/bin/activate

# Run style checks
(venv) $ make lint
```

This will:
- Run black to check code formatting
- Run isort to verify import sorting
- Run pylint for code quality checks (see [.pylintrc](.pylintrc))

Running style checks locally is highly recommended before pushing changes. They are also required to pass before merging pull requests.

### Running Tests

To run tests with coverage reporting:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests with clean environment
(venv) $ make clean test
```

This will:
- Clean build artifacts and cache
- Run tests with coverage reporting
- Generate HTML and XML coverage reports
- Confirms coverage is above minimum threshold set by project

Running tests locally is highly recommended before pushing changes. They are also required to pass before merging pull requests.

### Building Package

To build the package distribution:

```bash
# Activate virtual environment
source venv/bin/activate

# Build package with clean environment
(venv) $ make clean build
```

This will:
- Clean build artifacts and cache
- Build source distribution (sdist)
- Build wheel distribution
- Verify package metadata
- Store artifacts in `dist/` directory

Building locally is recommended before publishing to ensure package integrity. 
Package builds are also required to pass verification before merging pull requests.

### Local CI

To run the complete CI workflow locally:

```bash
# Activate virtual environment
source venv/bin/activate

# Run full CI pipeline
(venv) $ make all
```

This will:
- Clean all build artifacts and cache
- Run style checks (black, isort, pylint)
- Run tests with coverage reporting
- Build package distributions
- Verify package metadata

The `make all` command mirrors our GitHub Actions CI workflow and is useful for:
- Verifying changes before pushing
- Debugging CI failures locally
- Ensuring complete project validation

*Note: This is the same workflow that runs in GitHub Actions for pull requests.*

## Contributing Changes

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Add tests for any new functionality
4. Ensure all tests pass
5. Submit a pull request

### Questions and Issues
Please open an issue in the GitHub repository.
