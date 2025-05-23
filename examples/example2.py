"""TDM Client Example 2 - Multiple PDF Downloads

This example demonstrates downloading multiple Open Access Article PDFs.
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

# Download multiple Article PDFs
dois = ["10.1111/jtsb.12390", "10.1111/jlse.12141"]
tdm.download_pdfs(dois)
