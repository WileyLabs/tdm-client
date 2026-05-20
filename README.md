# wiley-tdm

![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Dependencies](https://img.shields.io/badge/dependencies-1-brightgreen)
![Version](https://img.shields.io/badge/version-1.1.0-blue)

## Table of Contents
- [wiley-tdm](#wiley-tdm)
  - [Table of Contents](#table-of-contents)
  - [Text and Data Mining (TDM)](#text-and-data-mining-tdm)
  - [Wiley TDM Client](#wiley-tdm-client)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Quick Start](#quick-start)
    - [Environment Variables](#environment-variables)
    - [Install](#install)
    - [Basic Usage](#basic-usage)
  - [Configuration](#configuration)
    - [API token](#api-token)
    - [Download directory](#download-directory)
    - [Rate limiting](#rate-limiting)
    - [Per-download callback](#per-download-callback)
    - [Skip existing files](#skip-existing-files)
    - [Download results](#download-results)
  - [Known Limitations](#known-limitations)
    - [Access is IP address based only](#access-is-ip-address-based-only)
    - [SICI DOIs are not supported](#sici-dois-are-not-supported)
  - [Troubleshooting](#troubleshooting)
    - [Installation](#installation)
    - [Access denied](#access-denied)
    - [Other issues](#other-issues)
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

* A [Python 3.10+](https://www.python.org/downloads/) environment
* Python dependencies:
  * [requests](https://requests.readthedocs.io/) (≥2.33.1)
* A [Wiley Online Library](https://onlinelibrary.wiley.com/) (WOL) Account
* Your TDM API Token (UUID format), available from the WOL [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining) using your WOL Account
* Access to the content you wish to download
* Access will be determined via your [public IP address](https://api.ipify.org/?format=json)

## Quick Start

### Environment Variables

Set the environment variable `TDM_API_TOKEN` to your API token:

```bash
# Windows (PowerShell)
$env:TDM_API_TOKEN = 'your-api-token-here'

# macOS / Linux
export TDM_API_TOKEN='your-api-token-here'
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

## Configuration

`TDMClient` exposes several options to control where files are saved, how requests are paced, and what gets recorded. All paths are relative to your current working directory unless you use an absolute path.

### API token

The TDM API token is a UUID issued via the [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining). Provide it via the `TDM_API_TOKEN` environment variable (recommended) or pass it directly:

```python
from wiley_tdm import TDMClient

tdm = TDMClient(api_token="your-uuid-token-here")
```

### Download directory

PDFs are saved to a `downloads` folder by default. Set a custom directory when creating the client, or change it later:

```python
from pathlib import Path
from wiley_tdm import TDMClient

# At initialization
tdm = TDMClient(download_dir=Path("downloads") / "oa-pdfs")

# Or after initialization
tdm.download_dir = "downloads/batch-2025"
```

Files are named `<doi>.pdf` in the download directory.

### Rate limiting

Wiley's [TDM resources](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining) document API limits of up to **3 articles per second** and **60 requests per 10 minutes** (about **10 seconds between requests** for sustained use).

Batch downloads (`download_pdfs`) sleep after each item (except existing local files). The default pause is **5 seconds**—a practical minimum given download time and typical batch sizes, not a substitute for the 10-second guideline on long, continuous runs. Increase it when needed; you cannot set it below the default:

```python
tdm = TDMClient()
tdm.api_rate_limit = 10.0  # Align with Wiley's 10-second recommendation
```

`download_pdf` is not delayed.

### Per-download callback

For batch downloads, pass an `on_result` callback to `download_pdfs`. It is called after each DOI finishes, so you can inject your own code into the loop without waiting for the whole batch to complete.

```python
from wiley_tdm import DownloadResult, TDMClient

def track_progress(result: DownloadResult) -> None:
    # Your integration: database, queue, metrics, UI, etc.
    record_in_my_system(doi=result.doi, status=result.status.name, path=result.path)

tdm = TDMClient()
tdm.download_pdfs("dois.txt", on_result=track_progress)
```

The callback receives the same `DownloadResult` returned by `download_pdf`. `download_pdfs` still returns the full list when the batch completes.

### Skip existing files

By default, `skip_existing_files` is `True`. When `<doi>.pdf` already exists in the download directory, the client skips the API call and records the file as already present. Set it to `False` to force a re-download:

```python
tdm = TDMClient()
tdm.skip_existing_files = False
tdm.download_pdf("10.1111/jtsb.12390")
```

### Download results

Each download returns a `DownloadResult` with status, file path, and timing. Access accumulated results via `tdm.results`, or save only failures:

```python
from wiley_tdm import DownloadStatus, TDMClient

tdm = TDMClient()
tdm.only_record_errors = True  # Default is False — only failures kept in tdm.results

result = tdm.download_pdf("10.1111/jtsb.12390")
if result.status == DownloadStatus.SUCCESS:
    print(f"Saved to {result.path}")

tdm.download_pdfs(["10.1111/jtsb.12390", "10.1111/jlse.12141"])
tdm.save_results("my-results.csv")  # Default is results.csv
```

## Known Limitations

There are two known limitations of the TDM Client (/TDM API):

### Access is IP address based only

The following scenarios are not supported:
* Your WOL customer account **doesn't** have IP based access configured. (e.g. SSO only)
* Your WOL customer account **does** have IP based access configured but you are outside the configured IP range. (e.g. Executing code off campus or in the Cloud)

Ask your WOL Account Admin to confirm your access model. See [Troubleshooting](#troubleshooting) for further assistance.

**Potential Workarounds:**

**IP access available:**
* Run code within configured IP range (e.g. Return to campus)
* Manually download entitled content on WOL, via https://onlinelibrary.wiley.com/doi/epdf/{doi}

**IP access not available:**
* Request IP based access via your WOL Account Admin.
* Request feed-based (non‑API‑based) content dissemination for TDM via your WOL Account Admin.

### SICI DOIs are not supported

The TDM APIs cannot support [SICI](https://en.wikipedia.org/wiki/Serial_Item_and_Contribution_Identifier) DOIs, containing semicolons. For example:
* 10.1002/1096-9861(20010212)430:3<283::AID-CNE1031>3.0.CO;2-V
* 10.1002/(SICI)1096-8644(1998)107:27+<1::AID-AJPA2>3.0.CO;2-H
  
**Potential Workarounds:**
* Manually download entitled content on WOL, via https://onlinelibrary.wiley.com/doi/epdf/{doi}

## Troubleshooting

In most troubleshooting scenarios it can be helpful to enable logging and generate a report:

```python
import logging
from wiley_tdm import TDMClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

tdm = TDMClient()
# ... run downloads ...
tdm.save_results()
```

Review the console logs and results.csv. For deeper analysis set `level=logging.DEBUG`

### Installation

If you encounter installation issues:

```bash
# Ensure you are in your Python Virtual Environment
source ./venv/bin/activate

# Ensure you are using Python 3.10+
python3 --version

# Update pip to latest version
python3 -m pip install --upgrade pip

# Ensure you are using the latest TDM Client
pip show wiley-tdm

# Update TDM Client to the latest version
pip install --upgrade wiley-tdm
```

Alternatively, try installing a fresh [Virtual Environment](#install).

If problems persist, please [open an issue](https://github.com/WileyLabs/tdm-client/issues) with:
- Your Python version
- The exact error message
- Your operating system details

### Access denied

The majority of reported issues relate to access problems. Please note that only IP based access is supported; see [Known Limitations](#known-limitations). If you do have IP based access and are still experiencing issues try the following:

Check access directly on [Wiley Online Library](https://onlinelibrary.wiley.com/).
- If access denied: contact your Institution or [Wiley](mailto:tdm@wiley.com) and check your subscription is active.
- If access granted: ensure you are accessing the TDM API from a known IP address (see below).

It is possible that the IP address you are accessing WOL from is different to where you are running your TDM code. Enable TDM logging (see [Troubleshooting](#troubleshooting)), observe your IP address in the TDM console log and compare to the IP address in your [browser](https://api.ipify.org?format=json).

Example console output:
```
2025-02-13 11:48:30,762 - INFO - Your IP address, used to check entitlements: XX.XX.XX.XX
```

Example Browser output:

https://api.ipify.org/?format=json

```json
{
  "ip": "XX.XX.XX.XX"
}
```
If the IP addresses are different then seek guidance from your network administrator.

### Other issues

For other issues please contact: tdm@wiley.com and provide the following information:

* TDM API Token (UUID)
* results.csv
* console log
* dois.txt (problematic DOIs)
* Summary of problem


## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for further details.

## License

Distributed under the MIT License. See `LICENSE` for more information.
