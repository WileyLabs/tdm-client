import logging
import os
from tdm_client import TDMClient

# Configuration
tdm_api_token = os.getenv('TDM_API_TOKEN')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    tdm = TDMClient(tdm_api_token)

    # Download a single Article PDF to the 'downloads' folder
    doi = '10.1002/1878-0261.13818'
    tdm.download_pdf(doi)

    # Download multiple Article PDFs to the 'downloads' folder
    dois = ['10.1155/adme/9485656', '10.1155/2019/3692947']
    tdm.download_pdfs(dois)

    # Download multiple Article PDFs, listed in a file, to the 'downloads/oa-pdfs' folder
    tdm.set_download_dir('downloads/oa-pdfs')
    tdm.download_pdfs_from_file('oa-dois.txt')

if __name__ == "__main__":
    main()