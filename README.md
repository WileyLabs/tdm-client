# tdm-client

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Dependencies](https://img.shields.io/badge/dependencies-requests-orange)

## Table of Contents
- [Text and Data Mining (TDM)](#text-and-data-mining-tdm)
- [TDM Client](#tdm-client-1)
- [Features](#features)
- [Requirements](#requirements)
- [Development Setup (Linux)](#development-setup-linux)
- [Basic Usage](#basic-usage)
- [Troubleshooting](#troubleshooting)
  - [Access Denied](#access-denied)
- [Contributing](#contributing)
- [License](#license)

## Text and Data Mining (TDM)

Wiley encourages innovative use of the content we publish, and supports customers who wish to perform text and data mining (TDM) on Wiley content. We are committed to developing tools and services that will enable subscribers to carry out TDM in the most efficient and effective manner, as well as to providing straightforward access to content for TDM purposes.

Academic subscribers can perform TDM under license (or in accordance with statutory rights under applicable legislation) on subscribed content for non-commercial purposes at no extra cost.

Corporate subscribers should contact their account manager to discuss options available for content access and delivery. [Learn more about our options for corporate customers.](https://www.wiley.com/corporations/content-licensing/xml-machine-learning)

In order to maximize platform stability and security for all users, access to content for TDM purposes takes place through our API service, rather than through crawling or scraping [Wiley Online Library](https://onlinelibrary.wiley.com/). Academic subscribers can access subscribed content once they have accepted the Wiley click-through TDM license and received an API token.

To learn more about the TDM service and request a TDM Token visit our [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining)

## TDM Client

The TDM Client greatly simplifies the use of the TDM API. All you need to get started is a TDM API Token. Currently, we only offer a Python implementation, others may follow in the future depending on demand. You are free to fork this codebase or make pull requests.

## Features

- Simple Python interface to Wiley's TDM API
- Download single or multiple PDFs
- Rate limiting to prevent API overload
- Comprehensive error handling
- Logging with configurable levels
- Support for both single DOIs and bulk downloads
- Automatic DOI validation via CrossRef

## Requirements

You will require the following:

* A [Python 3.7+](https://www.python.org/downloads/) environment
* Python packages:
  * requests>=2.31.0
* A [Wiley Online Library](https://onlinelibrary.wiley.com/) (WOL) Account
* A TDM API Token, available from the WOL [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining) using your WOL Account
* Access to the content you wish to download
* Access will be determined via your IP address

## Development Setup (Linux)

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

# Install requirements
pip install -r requirements.txt

# Deactivate virtual environment
deactivate
```

Alternatively, download and run ([install.sh](install.sh)). 

```bash
chmod +x install.sh
./install.sh your-tdm-api-token
```

## Basic Usage

The following example will download multiple Article PDFs to a 'downloads' folder, relative to the current working directory, and name the files `<doi>.pdf`.

```python
from tdm_client import TDMClient

# Configuration
tdm_api_token = os.getenv('TDM_API_TOKEN')

# Initialize client
tdm = TDMClient(tdm_api_token)

# Download multiple PDFs
dois = ['10.1155/2019/3692947', '10.1155/2019/3692948']
pdf_paths = tdm.download_pdfs(dois)

```

For more examples, see [tdm_example.py](tdm_example.py).

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