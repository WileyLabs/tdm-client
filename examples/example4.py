"""TDM Client Example 4 - Multiple PDF Downloads from SICI DOI List File

This example demonstrates downloading multiple SICI Article PDFs using a text file
containing DOIs (one per line). Files are saved to the 'downloads/sici-pdfs' directory
relative to your current working directory.

Requirements:
    - Virtual environment activated
    - TDM_API_TOKEN environment variable set
    - wiley-tdm package installed
    - sici-dois.txt file containing DOIs (one per line)

Output:
    - downloads/sici-pdfs/<doi>.pdf: Downloaded PDF files
    - results.csv: Download status report
"""

import logging
from pathlib import Path

from wiley_tdm import TDMClient

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize client (uses TDM_API_TOKEN from environment)
tdm = TDMClient(download_dir=Path("downloads") / "sici-pdfs")

# Download multiple Article PDFs, listed in a file, to the 'downloads/sici-pdfs' folder
tdm.download_pdfs("sici-dois.txt")

# Save the download results to a CSV file: 'results.csv'
tdm.save_results()
