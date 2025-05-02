"""TDM Client Example 3 - Multiple PDF Downloads from DOI List File

This example demonstrates downloading multiple Open Access Article PDFs using a text file
containing DOIs (one per line). Files are saved to the 'downloads/oa-pdfs' directory
relative to your current working directory.

Requirements:
    - Virtual environment activated
    - TDM_API_TOKEN environment variable set
    - tdmclient package installed
    - oa-dois.txt file containing DOIs (one per line)

Output:
    - downloads/oa-pdfs/<doi>.pdf: Downloaded PDF files
    - downloads/oa-pdfs/download_results.csv: Download status report
"""

import logging
from tdmclient import TDMClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize client (uses TDM_API_TOKEN from environment)
tdm = TDMClient(download_dir='downloads/oa-pdfs')

# Download multiple Article PDFs, listed in a file, to the 'downloads/oa-pdfs' folder
tdm.download_pdfs_from_file('oa-dois.txt')

# Save the download results to a CSV file: 'downloads/oa-pdfs/download_results.csv'
tdm.save_download_results()
