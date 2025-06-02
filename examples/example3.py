"""TDM Client Example 3 - Multiple PDF Downloads from DOI List File

This example demonstrates downloading multiple Open Access Article PDFs using a text file
containing DOIs (one per line). Files are saved to the 'downloads/oa-pdfs' directory
relative to your current working directory.

Requirements:
    - Virtual environment activated
    - TDM_API_TOKEN environment variable set
    - wiley-tdm package installed
    - oa-dois.txt file containing DOIs (one per line)

Output:
    - downloads/oa-pdfs/<doi>.pdf: Downloaded PDF files
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
tdm = TDMClient(download_dir=Path("downloads") / "oa-pdfs")

# Download multiple Article PDFs, listed in a file, to the 'downloads/oa-pdfs' folder
tdm.download_pdfs("oa-dois.txt")

# Save the download results to a CSV file: 'results.csv'
tdm.save_results()
