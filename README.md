# tdm-client

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Dependencies](https://img.shields.io/badge/dependencies-requests%20%3E%3D%202.32.0-orange)

## Table of Contents
- [Text and Data Mining (TDM)](#text-and-data-mining-tdm)
- [TDM Client](#tdm-client)
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
  - [Environment Variables](#environment-variables)
  - [Install](#install)
  - [Basic Usage](#basic-usage)
- [Development Setup](#development-setup)
  - [Requirements](#requirements-1)
  - [Option 1: Manual Setup](#option-1-manual-setup)
  - [Option 2: Install Script](#option-2-install-script)
  - [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
  - [Access denied](#access-denied)
  - [Installation Issues](#installation-issues)
- [Contributing](#contributing)
- [License](#license)

## Text and Data Mining (TDM)

To learn more about the TDM service and request a TDM Token visit our [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining)

## TDM Client

The TDM Client is a Python library (installable via pip) that aims to simplify interaction with Wiley's TDM API. 

## Features

The TDM Client has the following capabilities

* **PDF Downloads** - Download PDFs from Wiley's TDM API
  * Single or bulk DOI downloads (DOIs from file)
  * Configurable download directory
  * Automatic DOI-based file naming
* **DOI Validation**
  * Non-Wiley DOI detection (via CrossRef API)
  * Invalid DOIs
  * DOI encoding
* **API Handling**
  * Authentication (API Token & IP)
  * Rate limiting support 
  * Error handling (e.g. Access denied)
* **Reporting**
  * CSV export of download results
  * Download statistics (success/failure rates)
  * File sizes and download durations
* **Efficiency**
  * API Session handling
  * Low memory utilisation with PDF streaming
  * Graceful timeouts

## Requirements

You will require the following:

* A [Python 3.9+](https://www.python.org/downloads/) environment
* Python packages:
  * requests>=2.32.0
* A [Wiley Online Library](https://onlinelibrary.wiley.com/) (WOL) Account
* A TDM API Token, available from the WOL [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining) using your WOL Account
* Access to the content you wish to download
* Access will be determined via your IP address

## Quick Start

### Environment Variables

Set the environment variable `TDM_API_TOKEN` to be used by the TDMClient:

```bash
# Set your TDM API token (required)
export TDM_API_TOKEN='your-tdm-api-token'
echo $TDM_API_TOKEN
```

### Install

Install the TDMClient in a Virtual Environment using pip. We always recommend running in a Virtual Environment so as not to clash with existing System Python libraries:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install TDMClient directly from GitHub
pip install "git+https://github.com/WileyLabs/tdm-client.git"

# Verify installation
pip list | grep tdmclient

# Deactivate virtual environment (you can keep it open)
# deactivate
```

### Basic Usage

The following example will download a single Open Access Article PDF to a 'downloads' folder,
relative to your current working directory, and name the file `<doi>`.pdf.

Create example1.py (Copy or [download](examples/example1.py))

```python
import logging
from tdmclient import TDMClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize client (uses TDM_API_TOKEN from environment)
tdm = TDMClient()

# Download a single Article PDF
tdm.download_pdf('10.1111/jtsb.12390')
```

Execute in your Virtual Environment (important) and observe the downloaded PDF:

```bash
# Activate virtual environment
source venv/bin/activate

# Run example
(venv) $ python3 example1.py 

# List downloads
(venv) $ ls -la downloads/

# Deactivate when done
(venv) $ deactivate
```

See more [examples](examples/).

## Development Setup

### Requirements:
- Python 3.9 or higher
- Git

### Option 1: Manual Setup

```bash
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
pip install -e ".[test]"

# Run tests
pytest

# Deactivate virtual environment
deactivate
```

### Option 2: Install Script

Alternatively, download and run ([install.sh](scripts/install.sh)).

```bash
# Download installation scripts
mkdir -p tdm-scripts && cd tdm-scripts
curl -O https://raw.githubusercontent.com/WileyLabs/tdm-client/main/scripts/{install,uninstall}.sh
chmod +x *.sh

# Run installation
./install.sh your-tdm-api-token
```

### Running Tests

To run tests, use the following command:

```bash
pytest
```

## Troubleshooting

### Access denied

Check you can manually view the desired content directly on [Wiley Online Library](https://onlinelibrary.wiley.com/).

If you can, it is possible that the IP address you are accessing the website from is different to where you are running your TDM code. Observe your IP address in the TDM console log and compare to the IP address in your [browser](https://api.ipify.org?format=json).

Example console output:
```
2025-02-13 11:48:30,762 - INFO - Your IP address, used to check entitlements: XX.XX.XX.XX
```

Example Browser output:

```json
// https://api.ipify.org/?format=json

{
  "ip": "XX.XX.XX.XX"
}
```

### Installation Issues

If you encounter issues during installation, ensure you have the correct version of Python and the required packages. You can also try reinstalling the package:

```bash
pip uninstall tdmclient
pip install "git+https://github.com/WileyLabs/tdm-client.git"
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your PR includes:
- Clear description of changes
- Updated documentation
- Test cases if applicable

## License

Distributed under the MIT License. See `LICENSE` for more information.