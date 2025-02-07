# tdm-client
## Text and Data Mining (TDM)

Wiley encourages innovative use of the content we publish, and supports customers who wish to perform text and data mining (TDM) on Wiley content. We are committed to developing tools and services that will enable subscribers to carry out TDM in the most efficient and effective manner, as well as to providing straightforward access to content for TDM purposes.

Academic subscribers can perform TDM under license (or in accordance with statutory rights under applicable legislation) on subscribed content for non-commercial purposes at no extra cost.

Corporate subscribers should contact their account manager to discuss options available for content access and delivery. [Learn more about our options for corporate customers.](https://www.wiley.com/corporations/content-licensing/xml-machine-learning)

In order to maximize platform stability and security for all users, access to content for TDM purposes takes place through our API service, rather than through crawling or scraping [Wiley Online Library](https://onlinelibrary.wiley.com/). Academic subscribers can access subscribed content once they have accepted the Wiley click-through TDM license and received an API token.

To learn more about the TDM service and request a TDM Token visit our [TDM resources page](https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining)

## TDM Client

The TDM Client greatly simplifies the use of the TDM API. All you need to get started is a TDM Token. Currently, we only offer a Python implementation, others may follow in the future depending on demand. You are free to fork this codebase or make pull requests.

## Prerequisites

* Python 3 environment.
* TDM Token.
* Access to the content already on [Wiley Online Library](https://onlinelibrary.wiley.com/).
* Access will be determined via your IP address.

## Quick Start

The following code will download an Article PDF. The Article is Open Access and will work regardless of your IP address and entitlements. The PDF will be placed in a /downloads folder, relative to the script execution, and be named `<doi>.pdf`

```python
import logging
from tdm_client import TDMClient

# Configuration
tdm_token = 'add-your-tdm-token-uuid-here'
doi = '10.1002/1878-0261.13818'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    tdm = TDMClient(tdm_token)
    tdm.downloadPDF(doi)

if __name__ == "__main__":
    main()
```

## Troubleshooting

TODO