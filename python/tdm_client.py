import os
import requests
import urllib.parse
import logging
import uuid
import re
from typing import List, Optional
from collections import OrderedDict

class TDMClient:
    """Class to download articles given their DOIs."""

    api_base_url = 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/'
    api_token_header = 'Wiley-TDM-Client-Token'
    DOI_REGEX = re.compile(r'^10.\d{4,9}/[-._;()/:<>\[\]A-Z0-9]+$', re.IGNORECASE)

    def __init__(self, api_token: str, download_dir: str = 'downloads/'):
        """
        Initialize the TDMClient with an API token and a download directory.

        :param api_token: The TDM API token.
        :param download_dir: The directory where downloaded PDFs will be saved.
        """
        self.logger = logging.getLogger(__name__)

        # Log the user's public IP address
        self.public_ip = self.get_public_ip()
        if self.public_ip:
            self.logger.info(f"User's public IP address: {self.public_ip}")

        # Validate the API token
        try:
            uuid.UUID(api_token)
        except ValueError:
            self.logger.error(f"Invalid API token: {api_token}")
            raise ValueError("Invalid API token. Must be a valid UUID.")

        # Ensure the download directory exists
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            self.logger.info(f"Created download directory: {download_dir}")
        else:
            self.logger.info(f"Download directory already exists: {download_dir}")

        self.api_token = api_token
        self.api_headers = {self.api_token_header: api_token}
        self.download_dir = download_dir

    def get_public_ip(self) -> Optional[str]:
        """Get the user's public IP address."""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            response.raise_for_status()
            ip_data = response.json()
            return ip_data.get('ip')
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch public IP address: {e}")
            return None

    @staticmethod
    def is_valid_doi(doi: str) -> bool:
        """
        Check if the given string is a valid DOI.

        :param doi: The DOI to validate.
        :return: True if the DOI is valid, False otherwise.
        """
        return bool(TDMClient.DOI_REGEX.match(doi))

    def download_pdf(self, doi: str) -> Optional[str]:
        """
        Download an article PDF given its DOI.

        :param doi: The DOI of the article to download.
        :return: The path to the downloaded PDF, or None if the download failed.
        """
        if not self.is_valid_doi(doi):
            self.logger.error(f"Invalid DOI: {doi}")
            return None
        
        encoded_doi = urllib.parse.quote(doi, safe='')
        self.logger.debug(f"URL encoded DOI: {encoded_doi}")
        request_url = self.api_base_url + encoded_doi

        try:
            response = requests.get(request_url, headers=self.api_headers, allow_redirects=True, stream=True)
            response.raise_for_status()
        except requests.RequestException as e:

            if response.status_code == 403:
                self.logger.error(f"Download failed. Access denied (403). Public IP: {self.public_ip}: DOI: {doi}" )
                self.logger.error(f">>Confirm access on WOL: https://onlinelibrary.wiley.com/doi/{doi}" )
            elif response.status_code == 404:
                self.logger.error(f"Download failed. Article not found (404). DOI: {doi}")
            else:
                self.logger.error(f"Download failed. API issue ({response.status_code}). DOI: {doi}: {e}")
   
            self.logger.debug(f"API Error: {e}")
            return None

        pdf_name = doi.replace('/', '-') + '.pdf'
        pdf_path = os.path.join(self.download_dir, pdf_name)

        try:
            with open(pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            self.logger.info(f"Downloaded article: {doi}")
            return pdf_path
        except IOError as e:
            self.logger.error(f"Failed to save article: DOI {doi} to {pdf_path}: {e}")
            return None

    def download_pdfs(self, dois: List[str]) -> List[Optional[str]]:
        """
        Download articles given a list of DOIs.

        :param dois: A list of DOIs to download.
        :return: A list of paths to the downloaded PDFs, or None for failed downloads.
        """
        unique_dois = list(OrderedDict.fromkeys(dois))  # Remove duplicates while maintaining order
        
        downloaded_files = []
        for doi in unique_dois:
            pdf_path = self.download_pdf(doi)
            downloaded_files.append(pdf_path)
        return downloaded_files

    def download_pdfs_from_file(self, dois_file_path: str = 'dois.txt') -> List[Optional[str]]:
        """
        Download articles listed in a file, named dois.txt by default.

        :param dois_file_path: The path to the file containing DOIs.
        :return: A list of paths to the downloaded PDFs, or None for failed downloads.
        """
        try:
            with open(dois_file_path, 'r') as file:
                dois = []
                for line in file:
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith('#'):
                        dois.append(stripped_line)
        except IOError as e:
            self.logger.error(f"Failed to read DOIs from file: {dois_file_path}: {e}")
            return []

        return self.download_pdfs(dois)