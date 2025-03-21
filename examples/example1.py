# filepath: examples/example1.py
import logging
from tdmclient import TDMClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Initialize client (uses TDM_API_TOKEN from environment)
tdm = TDMClient()

# Download multiple PDFs
dois = [
    '10.1111/jtsb.12390',
    '10.1111/jlse.12141'
]
tdm.download_pdfs(dois)

# PDFs will be saved to: examples/downloads/<doi>.pdf