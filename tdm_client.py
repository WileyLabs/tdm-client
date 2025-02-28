# Standard library imports
import os
import csv
import logging
import time
import uuid
import urllib.parse
from http import HTTPStatus
from typing import List, Optional
from collections import OrderedDict
from dataclasses import dataclass

# Third-party imports
import requests

# Local imports
from doi_validator import DOIValidator

@dataclass(frozen=True)
class DownloadResult:
    """Class to store download attempt results.
    
    Attributes:
        doi: Digital Object Identifier of the article
        status: HTTP status code from the attempt
        comment: Additional context about the result
    """
    doi: str
    status: HTTPStatus
    comment: str

class TDMClient:
    """Client for downloading articles from Wiley's TDM API."""

    # API URLs and configuration
    TDM_API_URL: str = 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/'
    TDM_TOKEN_HEADER: str = 'Wiley-TDM-Client-Token'
    CROSSREF_API_URL: str = 'https://api.crossref.org/works'
    IPIFY_API_URL: str = 'https://api.ipify.org?format=json'
    DOI_URL_PREFIX: str = "https://doi.org/"

    # Default settings
    DEFAULT_RATE_LIMIT: float = 1.0 #seconds
    DEFAULT_IP_ADDRESS: str = "192.168.0.1"
    DEFAULT_DOWNLOAD_DIR: str = "downloads/"
    DEFAULT_RESULTS_FILE: str = "download_results.csv"
    DEFAULT_DOIS_FILE: str = "dois.txt"
    
    # HTTP configuration
    KB: int = 1024
    CHUNK_SIZE: int = 8 * KB  # 8KB chunks for PDF downloads
    
    # File handling
    DOI_SEPARATOR: str = "-"  # Used when converting DOI to filename
    CSV_HEADERS: List[str] = ['DOI', 'Status Code', 'Status', 'Comment']

    def __init__(self, tdm_token: str, download_dir: str = 'downloads/'):
        """Initialize the TDMClient with a TDM API token and download directory.

        Args:
            tdm_token: UUID token from Wiley's TDM service
            download_dir: Directory where PDFs will be saved. Defaults to 'downloads/'

        Raises:
            ValueError: If tdm_token is not a valid UUID
        """
        # Configure logging
        self.logger = logging.getLogger(__name__)

        # Public attributes
        self.download_results_errors_only: bool = False
        self.safe_mode: bool = True

        # Private instance attributes with type hints and defaults (use setters/constructors)
        self._download_dir: str = ""
        self._tdm_token: str = ""
        self._tdm_headers: dict = {}
        self._tdm_session: requests.Session = requests.Session()
        self._crossref_session: requests.Session = requests.Session()
        self._rate_limit: float = self.DEFAULT_RATE_LIMIT
        self._my_ip_address: str = self.DEFAULT_IP_ADDRESS
        self._download_results: List[DownloadResult] = []
        self._doi_validator:DOIValidator = DOIValidator()

        # Configure initial state
        _ = self.my_ip_address
        self.tdm_token = tdm_token
        self.download_dir = download_dir

    @property
    def rate_limit(self) -> float:
        """Get the current rate limit.

        Returns:
            float: Current rate limit in seconds
        """
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, value: float):
        """Set the rate limit.

        Args:
            value: Rate limit in seconds

        Raises:
            ValueError: If value is less than DEFAULT_RATE_LIMIT
        """
        if value < self.DEFAULT_RATE_LIMIT:
            raise ValueError(f"Rate limit cannot be below default value: {self.DEFAULT_RATE_LIMIT} seconds")
        self._rate_limit = value

    @property
    def tdm_token(self) -> str:
        """Get the current TDM API token."""
        return self._tdm_token

    @tdm_token.setter
    def tdm_token(self, value: str):
        """Set and validate the TDM API token.
        
        Args:
            value: UUID token from Wiley's TDM service

        Raises:
            ValueError: If token is not a valid UUID
        """
        try:
            uuid.UUID(value)
        except ValueError:
            self.logger.error(f"Invalid TDM API token: {value}")
            raise ValueError(f"The TDM API token must be a valid UUID: {value}")
            
        self._tdm_token = value
        self._tdm_headers = {self.TDM_TOKEN_HEADER: value}
        self._tdm_session.headers.update(self._tdm_headers)
        self.logger.debug(f"TDM API token updated")

    @property
    def download_dir(self) -> str:
        """Get the current download directory."""
        return self._download_dir

    @download_dir.setter
    def download_dir(self, value: str):
        """Set the download directory and ensure it exists.

        Args:
            value: The relative directory path where downloaded PDFs will be saved
        """
        if not os.path.exists(value):
            os.makedirs(value)
            self.logger.debug(f"Created download directory: {value}")
            
        self.logger.info(f"Downloading to: {value}")
        self._download_dir = value

    @property
    def my_ip_address(self) -> Optional[str]:
        """Get the public IP address, fetching it if not cached.

        Returns:
            str or None: The public IP address or None if unavailable
        """
        if self._my_ip_address is None:
            try:
                response = requests.get(self.IPIFY_API_URL)
                response.raise_for_status()
                ip_data = response.json()
                self._my_ip_address = ip_data.get('ip')
                if self._my_ip_address:
                    self.logger.info(f"Your IP address, used to check entitlements: {self._my_ip_address}")
            except requests.RequestException as e:
                self.logger.error(f"Failed to fetch public IP address: {e}")
                
        return self._my_ip_address

    def download_pdf(self, doi: str) -> Optional[str]:
        """Download an article PDF given its DOI.

        Args:
            doi: The DOI of the article to download

        Returns:
            str or None: Path to the downloaded PDF, or None if download failed
        """
        # Avoid double encoding or DOI validation issues later
        doi = urllib.parse.unquote(doi) 
        
        # Validate the DOI, pre-flight (adopt same HTTPStatus codes as TDM API)
        if self.safe_mode:
            if ';' in doi: # WIP!
                self._add_download_result(doi, HTTPStatus.UNPROCESSABLE_ENTITY, "Known Issue: DOI contains semi-colon")
                return None
            if not self._doi_validator.check_format(doi):
                self._add_download_result(doi, HTTPStatus.BAD_REQUEST, "Invalid DOI format")
                return None
            if not self._doi_validator.check_crossref(doi):
                self._add_download_result(doi, HTTPStatus.NOT_FOUND, "Crossref: Unknown DOI")
                return None
        
        # URL encode the DOI
        encoded_doi = urllib.parse.quote(doi, safe='')
        request_url = self.TDM_API_URL + encoded_doi
        self.logger.debug(f"API request URL: {request_url}")
        status = None

        # Download the PDF
        try:
            response = self._tdm_session.get(request_url, allow_redirects=True, stream=True)
            status = HTTPStatus(response.status_code)
            
            if status != HTTPStatus.OK:
                if status == HTTPStatus.FORBIDDEN:
                    self._add_download_result(doi, status, 
                        f"TDM access denied from IP {self.my_ip_address}. Try manually on WOL: https://doi.org/{doi}")
                elif status == HTTPStatus.NOT_FOUND:
                    self._add_download_result(doi, status, "Article not found")
                else:
                    self._add_download_result(doi, status, f"TDM API error: {response.text}")
                return None
                
            # Save the PDF
            return self._save_pdf(response, doi)
            
        except requests.RequestException as e:
            self._add_download_result(doi, HTTPStatus.INTERNAL_SERVER_ERROR, f"Network error: {str(e)}")
            return None

    def _save_pdf(self, response: requests.Response, doi: str) -> Optional[str]:
        """Save PDF content from response to file.

        Args:
            response: The HTTP response containing PDF content
            doi: The DOI of the article

        Returns:
            str or None: Path to the saved PDF, or None if saving failed
        """
        pdf_name = f"{doi.replace('/', self.DOI_SEPARATOR)}.pdf"
        pdf_path = os.path.join(self.download_dir, pdf_name)

        try:
            with open(pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:
                        pdf_file.write(chunk)
            self._add_download_result(doi, HTTPStatus.OK, f"Downloaded Article PDF to: {pdf_path}")
            return pdf_path
        except IOError as e:
            self._add_download_result(
                doi, 
                HTTPStatus.INTERNAL_SERVER_ERROR, #Yes, this is a bit of a stretch
                f"IO Error. Failed to save Article PDF to {pdf_path}: {e}"
            )
            return None

    def download_pdfs(self, dois: List[str]) -> List[Optional[str]]:
        """Download multiple articles given their DOIs.

        Args:
            dois: List of DOIs to download

        Returns:
            List[Optional[str]]: List of paths to downloaded PDFs, None for failed downloads
        """
        unique_dois = list(OrderedDict.fromkeys(dois))  # Remove duplicates while maintaining order
        
        downloaded_files = []
        for doi in unique_dois:
            pdf_path = self.download_pdf(doi)
            downloaded_files.append(pdf_path)
            if self.rate_limit > 0:
                self.logger.debug(f"Rate limiting: sleeping for {self.rate_limit} seconds")
                time.sleep(self.rate_limit)
        return downloaded_files

    def download_pdfs_from_file(self, dois_file_path: str = DEFAULT_DOIS_FILE) -> List[Optional[str]]:
        """Download articles listed in a file.

        Args:
            dois_file_path: Path to file containing DOIs, one per line. Defaults to 'dois.txt'

        Returns:
            List[Optional[str]]: List of paths to downloaded PDFs, None for failed downloads
        """
        try:
            with open(dois_file_path, 'r') as file:
                dois = []
                for line in file:
                    stripped_line = line.strip()
                    if (stripped_line and not stripped_line.startswith('#')):
                        dois.append(stripped_line)
        except IOError as e:
            self.logger.error(f"Failed to read DOIs from file: {dois_file_path}: {e}")
            return []

        return self.download_pdfs(dois)

    def _add_download_result(self, doi: str, status: HTTPStatus, comment: str = "") -> None:
        """Record download result.

        Args:
            doi: The DOI that failed
            status: The HTTP status code
            comment: Additional context about the result. Defaults to empty string
        """
        if status == HTTPStatus.OK and self.download_results_errors_only:
            return

        message = f"{status.phrase} ({status.value}): {comment}. DOI: {doi}"

        if status == HTTPStatus.OK:
            self.logger.info(message)
        else:
            self.logger.error(message)

        result = DownloadResult(doi, status, comment)
        self.download_results.append(result)

    @property
    def download_results(self) -> List[DownloadResult]:
        """Get the current download results.

        Returns:
            List[DownloadResult]: List of all download attempts and their results
        """
        return self._download_results.copy()  # Return copy to prevent external modification

    def save_download_results(self, csv_path: str = DEFAULT_RESULTS_FILE) -> None:
        """Save download results to CSV file.

        Args:
            csv_path: Path where CSV file will be saved. Defaults to 'download_results.csv'
        """
        if not self._download_results:
            self.logger.info("No results to save")
            return

        os.makedirs(os.path.dirname(csv_path), exist_ok=True)  # Create directory if needed
            
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.CSV_HEADERS)
            for result in self._download_results:
                writer.writerow([
                    result.doi,
                    result.status.value,
                    result.status.phrase,
                    result.comment
                ])
        
        self.logger.info(f"Download results saved to: {csv_path}")