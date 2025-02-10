import logging
from tdm_client import TDMClient

# Configuration
tdm_token = '1e1e7eb2-3c7c-4924-9146-49c374119629'
doi = '10.1002/1878-0261.13818'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

    tdm = TDMClient(tdm_token)
    tdm.download_pdf(doi)

if __name__ == "__main__":
    main()