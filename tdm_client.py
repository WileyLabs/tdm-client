import os
import requests
import urllib.parse
import logging
import uuid
import re
import time
from typing import List, Optional
from collections import OrderedDict

class TDMClient:
    """Class to download articles given their DOIs."""

    # Public attributes
    safe_mode = True

    # Private attributes
    _download_dir = None
    _my_ip_address = None
    _tdm_base_url = 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/'
    _tdm_token = None
    _tdm_token_header = 'Wiley-TDM-Client-Token'
    _tdm_headers = None
    _tdm_session = None
    _xref_base_url = 'https://api.crossref.org/works'
    _xref_session = None
    _rate_limit = 1

    _DOI_REGEX = re.compile(r'^10.\d{4,9}/[-._;()/:<>\[\]A-Z0-9]+$', re.IGNORECASE)

    def __init__(self, tdm_token: str, download_dir: str = 'downloads/'):
        """
        Initialize the TDMClient with a TDM API token and a download directory.

        :param tdm_token: The TDM API token.
        :param download_dir: The relative directory path where downloaded PDFs will be saved.
        """
        self.logger = logging.getLogger(__name__)

        self._tdm_session = requests.Session()
        self._xref_session = requests.Session()

        self.set_my_ip_address()
        self.set_tdm_token(tdm_token)
        self.set_download_dir(download_dir)

    def set_tdm_token(self, tdm_token: str):
        """
        Set the TDM API token and validate it.

        :param api_token: The TDM API token (UUID)
        """
        try:
            uuid.UUID(tdm_token)
        except ValueError:
            self.logger.error(f"Invalid TDM API token: {tdm_token}")
            raise ValueError(f"The TDM API token must be a valid UUID: {tdm_token}")
        self._tdm_token = tdm_token
        self._tdm_headers = {self._tdm_token_header: tdm_token}
        self._tdm_session.headers.update(self._tdm_headers)

    def set_download_dir(self, download_dir: str):
        """
        Set the download directory and ensure it exists.

        :param download_dir: The relative directory path where downloaded PDFs will be saved.
        """
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            self.logger.debug(f"Created download directory: {download_dir}")
            
        self.logger.info(f"Downloading to: {download_dir}")
        self._download_dir = download_dir

    def set_my_ip_address(self) -> Optional[str]:
        """
        Get and set my public IP address.

        :return: The public IP address or None if the request fails.
        """
        try:
            response = requests.get('https://api.ipify.org?format=json')
            response.raise_for_status()
            ip_data = response.json()
            self._my_ip_address = ip_data.get('ip')
            if self._my_ip_address:
                self.logger.info(f"Your IP address, used to check entitlements: {self._my_ip_address}")

            return self._my_ip_address
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch public IP address: {e}")
            return None

    def download_pdf(self, doi: str) -> Optional[str]:
        """
        Download an article PDF given its DOI.

        :param doi: The DOI of the article to download.
        :return: The path to the downloaded PDF, or None if the download failed.
        """
        if self.safe_mode:
            # URL decode the DOI first to avoid double encoding
            decoded_doi = urllib.parse.unquote(doi)
            self.logger.debug(f"URL decoded DOI: {decoded_doi}")

            # Check for known issues
            if ';' in decoded_doi:
                self.logger.error(f"Known issue: DOI contains a semicolon: {decoded_doi}")
                return None

            # Use the decoded DOI for further processing
            doi = decoded_doi

            # Check if the DOI is valid using CrossRef API
            if not self.is_valid_doi_xref(doi):
                return None

        else:
            # Check if the DOI is valid
            if not self.is_valid_doi(doi):
                return None
        
        # URL encode the DOI
        encoded_doi = urllib.parse.quote(doi, safe='')
        self.logger.debug(f"URL encoded DOI: {encoded_doi}")
        request_url = self._tdm_base_url + encoded_doi
        self.logger.debug(f"API request URL: {request_url}")

        try:
            response = self._tdm_session.get(request_url, allow_redirects=True, stream=True)
            response.raise_for_status()
        except requests.RequestException as e:
            if response.status_code == 403:
                self.logger.error(f"Download failed. Access denied (403), from your IP address: {self._my_ip_address}: DOI: {doi}")
                self.logger.error(f">>Troubleshoot: Check access on WOL, from your IP address: {self._my_ip_address}. WOL: 'https://onlinelibrary.wiley.com/doi/{doi}'")
            elif response.status_code == 404:
                self.logger.error(f"Download failed. Article not found (404). DOI: {doi}")
            else:
                self.logger.error(f"Download failed. API issue ({response.status_code}). DOI: {doi}: {e}")
            self.logger.debug(f"API Error: {e}")
            return None

        pdf_name = doi.replace('/', '-') + '.pdf'
        pdf_path = os.path.join(self._download_dir, pdf_name)

        try:
            with open(pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            self.logger.info(f"Downloaded article: {doi} here: {pdf_path}" )
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
            if self._rate_limit > 0:
                self.logger.debug(f"Rate limiting: sleeping for {self._rate_limit} seconds")
                time.sleep(self._rate_limit)
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

    def is_valid_doi(self, doi: str) -> bool:
        """
        Check if the given string is a valid DOI.

        :param doi: The DOI to validate.
        :return: True if the DOI is valid, False otherwise.
        """
        is_valid = bool(self._DOI_REGEX.match(doi))
        if is_valid:
            self.logger.debug(f"Valid DOI: {doi}")
        else:
            self.logger.error(f"Invalid DOI: {doi}")
        return is_valid

    def is_valid_doi_xref(self, doi: str) -> bool:
        """
        Check if the given DOI is valid and published by Wiley using the CrossRef API.

        :param doi: The DOI to check.
        :return: True if the DOI is valid, False otherwise.
        """

        #xref_url = self._xref_base_url + "/" + doi
        xref_url = self._xref_base_url
        xref_params = {'select': 'title', 'query.publisher-name': 'Wiley', 'filter': f'doi:{doi}'}

        if not self.is_valid_doi(doi):
            return False

        try:
            response = self._xref_session.get(xref_url, params=xref_params)
            if response.status_code == 200:
                self.logger.debug(f"DOI known by CrossRef/Wiley: {xref_url}")
                self.logger.debug(f"CrossRef status: {response.json().get('status')}")
                return True
            elif response.status_code == 404:
                self.logger.error(f"DOI unknown by CrossRef/Wiley: {xref_url} / {doi}")
                return False
            else:
                response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Error checking DOI with CrossRef API: {e}")
            return False