# wiley-tdm

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Dependencies](https://img.shields.io/badge/dependencies-1-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)

## Table of Contents
- [Text and Data Mining (TDM)](#text-and-data-mining-tdm)
- [Wiley TDM Client](#wiley-tdm-client)
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
  - [Environment Variables](#environment-variables)
  - [Install](#install)
  - [Basic Usage](#basic-usage)
- [Troubleshooting](#troubleshooting)
  - [Installation](#installation)
  - [Access denied](#access-denied)
- [Contributing](#contributing)
- [License](#license)

## Text and Data Mining (TDM)

To learn more about the TDM service and request a TDM Token visit our [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining)

## Wiley TDM Client

The Wiley TDM Client is a Python package (installable via pip) that aims to simplify interaction with Wiley's TDM API. 

## Features

The Wiley TDM Client has the following capabilities:

* **PDF Downloads** - Download PDFs from Wiley's TDM API
  * Single or bulk PDF downloads
  * Configurable download directory
  * Automatic DOI-based file naming
* **DOI Validation**
  * Wiley DOI verification
  * Invalid DOI detection
  * DOI URL encoding
* **API Handling**
  * Authentication (API token & IP based auth)
  * Rate limiting support 
  * Error handling (e.g. Access denied)
* **Reporting**
  * CSV export of download results
  * API status
  * File sizes and download durations
* **Efficiency**
  * API Session handling
  * Low memory utilization with PDF streaming
  * Graceful timeouts

## Requirements

You will require the following:

* A [Python 3.9+](https://www.python.org/downloads/) environment
* Python dependencies:
  * [requests](https://requests.readthedocs.io/) (≥2.32.0)
* A [Wiley Online Library](https://onlinelibrary.wiley.com/) (WOL) Account
* A TDM API Token, available from the WOL [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining) using your WOL Account
* Access to the content you wish to download
* Access will be determined via your [public IP address](https://api.ipify.org/?format=json)

## Quick Start

### Environment Variables

Set the environment variable `TDM_API_TOKEN` to your API token:

Linux example
```bash
# Set your TDM API token (required)
export TDM_API_TOKEN='your-api-token-here'
echo $TDM_API_TOKEN
```

### Install

Install the Wiley TDM package in a Virtual Environment using pip. We always recommend running in a Virtual Environment so as not to clash with existing System Python libraries:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
(venv) $ pip install wiley-tdm

# Verify installation
(venv) $ pip list | grep wiley-tdm
```

### Basic Usage

The following examples will download Article PDFs to a 'downloads' directory, and name the files `<doi>`.pdf. All file & directory paths are relative to your current working directory (pwd). Run all code in your [Virtual Environment](#install).

**Initialize client**
```python
from wiley_tdm import TDMClient

# Uses TDM_API_TOKEN from environment
tdm = TDMClient()
```

**Download Single PDF**
```python
tdm.download_pdf("10.1111/jtsb.12390")
```

**Download Multiple PDFs**
```python
tdm.download_pdfs(["10.1111/jtsb.12390", "10.1111/jlse.12141"])
```

**Download Multiple PDFs, DOIs listed in a file**
```python
tdm.download_pdfs("dois.txt")
```

**More examples**

See more [examples](examples/).

## Troubleshooting

In most troubleshooting scenarios it can be helpful to generate a report:

```python
# Save the download results to a CSV file: 'results.csv'
tdm.save_results()
```

### Installation

If you encounter installation issues:

```bash
# Ensure you're using Python 3.9+
python3 --version

# Update pip to latest version
python3 -m pip install --upgrade pip
```

Alternatively, try installing a fresh [Virtual Environment](#install).

If problems persist, please [open an issue](https://github.com/WileyLabs/tdm-client/issues) with:
- Your Python version
- The exact error message
- Your operating system details

### Access denied

Check access directly on [Wiley Online Library](https://onlinelibrary.wiley.com/).
- If access denied: contact your Institution/Wiley and check your subscription is active.
- If access granted: ensure you are accessing the TDM API from a known IP address (see below).

It is possible that the IP address you are accessing WOL from is different to where you are running your TDM code. Observe your IP address in the TDM console log and compare to the IP address in your [browser](https://api.ipify.org?format=json).

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

If problems persist, please contact: tdm@wiley.com

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for further details.

## License

Distributed under the MIT License. See `LICENSE` for more information.
