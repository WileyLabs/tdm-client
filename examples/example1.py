"""TDM Client Example 1 - Single PDF Download

This example demonstrates downloading a single Open Access Article PDF.
Files are saved to the 'downloads' directory relative to the current working directory.

Requirements:
    - Virtual environment activated
    - TDM_API_TOKEN environment variable set
    - wiley-tdm package installed

Output:
    - downloads/<doi>.pdf file(s)
"""

import logging

from wiley_tdm import TDMClient

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize client (uses TDM_API_TOKEN from environment)
tdm = TDMClient()

# Download a single Article PDF
tdm.download_pdf("10.1111/jtsb.12390")
