# Standard library imports
import os
import csv
import logging
import time
import urllib.parse
from uuid import UUID
from http import HTTPStatus
from typing import List, Optional
from collections import OrderedDict
from dataclasses import dataclass

# Third-party imports
import requests

# Local imports
from doi_validator import DOIValidator
from status import DownloadStatus
from tdm_reporting import TDMReporting
from download_result import DownloadResult

@dataclass
class DownloadResult:
    """Class to store download attempt results."""
    doi: str
    status: DownloadStatus
    comment: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    duration: Optional[float] = None  # Duration in seconds
    api_status: Optional[HTTPStatus] = None  # HTTP status code from TDM API

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self.status}"

class TDMClient:
    """Client for downloading articles from Wiley's TDM API."""

    # API URLs and configuration
    ENV_TOKEN_KEY: str = 'TDM_API_TOKEN'
    TDM_API_URL: str = 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/'
    TDM_TOKEN_HEADER: str = 'Wiley-TDM-Client-Token'
    IPIFY_API_URL: str = 'https://api.ipify.org?format=json'
    WOL_PDF_URL: str = "https://onlinelibrary.wiley.com/doi/epdf/"

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
    CSV_HEADERS: List[str] = ['DOI', 'Status', 'Comment', 'Path']

    # Add timeout configuration
    CONNECT_TIMEOUT = 20  # seconds for initial connection
    READ_TIMEOUT = 30    # seconds for reading response

    def __init__(self, tdm_token: Optional[str] = None, download_dir: str = 'downloads/'):
        """Initialize the TDMClient with a TDM API token and download directory.

        Args:
            tdm_token: UUID token string from Wiley's TDM service. If None, reads from TDM_API_TOKEN env var
            download_dir: Directory where PDFs will be saved. Defaults to 'downloads/'

        Raises:
            ValueError: If tdm_token is not provided and not found in environment
        """
        self.logger = logging.getLogger(__name__)

        # Get token from environment if not provided
        if tdm_token is None:
            tdm_token = os.getenv(self.ENV_TOKEN_KEY)
            if not tdm_token:
                raise ValueError(f"TDM API token not provided and {self.ENV_TOKEN_KEY} environment variable not set")
            self.logger.debug("Using TDM API token from environment variable")

        # Public attributes
        self.download_results_errors_only: bool = False
        self.safe_mode: bool = True
        self.overwrite_existing_files: bool = True

        # Private instance attributes with type hints and defaults (use setters/constructors)
        self._download_dir: str = ""
        self._tdm_token: str = ""
        self._tdm_headers: dict[str, str] = {}
        self._tdm_session: requests.Session = requests.Session()
        self._rate_limit: float = self.DEFAULT_RATE_LIMIT
        self._my_ip_address: str = self.DEFAULT_IP_ADDRESS
        self._download_results: List[DownloadResult] = []
        self._doi_validator:DOIValidator = DOIValidator()

        # Configure initial state
        self._tdm_headers =  {
            self.TDM_TOKEN_HEADER: self._tdm_token,
            'User-Agent': 'TDMClient/1.0',
        }
        _ = self.my_ip_address  # Fetch IP address
        self.tdm_token = tdm_token  # Will validate UUID format
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
    def tdm_token(self, value: UUID):
        """Set and validate the TDM API token.
        
        Args:
            value: UUID token from Wiley's TDM service
        """    
        self._tdm_token = str(value)
        # Update only the token header
        self._tdm_headers[self.TDM_TOKEN_HEADER] = self._tdm_token
        self._tdm_session.headers.update({self.TDM_TOKEN_HEADER: self._tdm_token})
        self.logger.debug("TDM API token updated")

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
                self.logger.error(f"Failed to fetch public IP address: {str(e)}")
                
        return self._my_ip_address

    def download_pdf(self, doi: str) -> DownloadResult:
        """Download a single article PDF given its DOI.

        Args:
            doi: The DOI of the article to download

        Returns:
            DownloadResult: Result of the download attempt

        Raises:
            ValueError: If DOI is None or empty string
        """
        if doi is None or not doi.strip():
            raise ValueError("DOI cannot be None or empty")
            
        start_time = time.perf_counter()
        result = self._download_pdf(doi)
        duration = time.perf_counter() - start_time
        result.duration = duration
        self._add_download_result(result)
        return result

    def _download_pdf(self, doi: str) -> DownloadResult:
        """Download an article PDF given its DOI.

        Args:
            doi: The DOI of the article to download

        Returns:
            DownloadResult: DownloadResult for the requested Article DOI
        """
        # Avoid double encoding or DOI validation issues later
        doi = urllib.parse.unquote(doi)
        
        # Validate if in safe mode
        if self.safe_mode:
            validation_result = self._validate_doi(doi)
            if validation_result:
                return validation_result

        # Prepare request
        encoded_doi = urllib.parse.quote(doi, safe='')
        request_url = f"{self.TDM_API_URL}{encoded_doi}"
        self.logger.debug(f"Requesting PDF from: {request_url}")

        try:
            response = self._tdm_session.get(
                request_url, 
                allow_redirects=True, 
                stream=True,
                timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
            )

            # Log response info for debugging
            self.logger.debug(f"Response headers: {dict(response.headers)}")

            status = HTTPStatus(response.status_code)
            
            if status != HTTPStatus.OK:
                return self._handle_error_status(doi, status, response)
                    
            # Save PDF and include status code
            result = self._save_pdf(response, doi)
            result.api_status = status
            return result
                
        except requests.RequestException as e:
            return DownloadResult(
                doi,
                DownloadStatus.WILEY_API_ERROR,
                str(e)
            )

    def _validate_doi(self, doi: str) -> Optional[DownloadResult]:
        """Validate DOI format and existence.
        
        Args:
            doi: The DOI to validate
            
        Returns:
            Optional[DownloadResult]: Error result if validation fails, None if valid
        """
        try:
            if ';' in doi:
                return DownloadResult(
                    doi, 
                    DownloadStatus.SEMICOLON_ERROR,
                    "Known API limitation: DOI contains semicolon"
                )
            if not self._doi_validator.check_format(doi):
                return DownloadResult(
                    doi,
                    DownloadStatus.INVALID_DOI_FORMAT
                )
            if not self._doi_validator.check_crossref(doi):
                return DownloadResult(
                    doi,
                    DownloadStatus.UNKNOWN_WILEY_DOI_CROSSREF
                )
            return None
        except requests.RequestException as e:
            return DownloadResult(
                doi,
                DownloadStatus.CROSSREF_API_ERROR,
                str(e)
            )

    def _handle_error_status(self, doi: str, status: HTTPStatus, response: requests.Response) -> DownloadResult:
        """Handle non-200 HTTP status codes.
        
        Args:
            doi: The DOI being processed
            status: HTTP status code
            response: Full response object
            
        Returns:
            DownloadResult: Error result with appropriate status
        """
        
        if status == HTTPStatus.FORBIDDEN:
            return DownloadResult(
                doi,
                DownloadStatus.FORBIDDEN,
                f"TDM access denied from IP {self.my_ip_address}. Try manually: {self.WOL_PDF_URL}{doi}",
                api_status=status
            )
        elif status == HTTPStatus.NOT_FOUND:
            return DownloadResult(
                doi,
                DownloadStatus.UNKNOWN_WILEY_DOI,
                "Enable safe_mode to validate DOIs against CrossRef" if not self.safe_mode else None,
                api_status=status
            )
        else:
            return DownloadResult(
                doi,
                DownloadStatus.WILEY_API_ERROR,
                response.text,
                api_status=status
            )

    def _save_pdf(self, response: requests.Response, doi: str) -> DownloadResult:
        """Save PDF content from response to file.

        Args:
            response: The HTTP response containing PDF content
            doi: The DOI of the article

        Returns:
            DownloadResult: Result of the save operation
        """
        if not response.headers.get('content-type', '').startswith('application/pdf'):
            return DownloadResult(
                doi,
                DownloadStatus.INVALID_CONTENT
            )

        pdf_name = f"{doi.replace('/', self.DOI_SEPARATOR)}.pdf"
        pdf_path = os.path.join(self.download_dir, pdf_name)

        if not self.overwrite_existing_files and os.path.exists(pdf_path):
            self.logger.warning(f"PDF already exists: {pdf_path}")
            return DownloadResult(
                doi,
                DownloadStatus.FILE_EXISTS,
                "",
                pdf_path,
                os.path.getsize(pdf_path)
            )

        try:
            with open(pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:
                        pdf_file.write(chunk)
            file_size = round(os.path.getsize(pdf_path) / self.KB)
            self.logger.info(f"Downloaded PDF: {pdf_path} ({file_size} KB)")
            return DownloadResult(
                doi,
                DownloadStatus.SUCCESS,
                "",
                pdf_path,
                file_size
            )
        except IOError as e:
            return DownloadResult(
                doi,
                DownloadStatus.STORAGE_ERROR,
                str(e),
                pdf_path
            )

    def download_pdfs(self, dois: List[str]) -> List[DownloadResult]:
        """Download multiple articles given their DOIs.

        Args:
            dois: List of DOIs to download. None, empty strings, and duplicates will be filtered.

        Returns:
            List[DownloadResult]: List of download results
        """
        unique_dois = self._filter_and_dedupe_dois(dois)
        results: List[DownloadResult] = []

        for doi in unique_dois:
            result = self.download_pdf(doi)
            if result:
                results.append(result)
            if self.rate_limit > 0:
                self.logger.debug(f"Rate limiting: sleeping for {self.rate_limit} seconds")
                time.sleep(self.rate_limit)
        return results

    def download_pdfs_from_file(self, dois_file_path: str = DEFAULT_DOIS_FILE) -> List[DownloadResult]:
        """Download articles listed in a file.

        Args:
            dois_file_path: Path to file containing DOIs, one per line

        Returns:
            List[DownloadResult]: List of download results

        Raises:
            FileNotFoundError: If the DOIs file doesn't exist
            OSError: If there are permission or other OS-level errors
        """
        if not os.path.exists(dois_file_path):
            message = f"DOIs file not found: {dois_file_path}"
            self.logger.error(message)
            raise FileNotFoundError(message)

        dois = []
        with open(dois_file_path, 'r') as file:
            for line in file:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    dois.append(stripped_line)

        if not dois:
            self.logger.warning(f"No valid DOIs found in file: {dois_file_path}")
            return []

        self.logger.info(f"Found {len(dois)} DOIs in {dois_file_path}")
        return self.download_pdfs(dois)

    def _filter_and_dedupe_dois(self, dois: List[str]) -> List[str]:
        """Filter invalid DOIs and remove duplicates while maintaining order.
        
        Args:
            dois: List of DOIs to filter and deduplicate
            
        Returns:
            List[str]: Filtered and deduplicated DOIs
        """
        # Filter None/empty DOIs and clean whitespace
        valid_dois = [doi.strip() for doi in dois if doi is not None and doi.strip()]
        # Remove duplicates while maintaining order
        unique_dois = list(OrderedDict.fromkeys(valid_dois))
        
        filtered_count = len(dois) - len(unique_dois)
        if filtered_count > 0:
            self.logger.info(f"Filtered out {filtered_count} invalid or duplicate DOIs")
        
        return unique_dois

    def _add_download_result(self, result: DownloadResult) -> None:
        """Record download result.

        Args:
            result: DownloadResult to add to the list
        """
        if result.status == DownloadStatus.SUCCESS and self.download_results_errors_only:
            return

        message = f"{result.status} - DOI: {result.doi}"
        if result.comment:
            message += f" - {result.comment}"

        if result.status == DownloadStatus.SUCCESS:
            self.logger.info(message)
        else:
            self.logger.error(message)

        self._download_results.append(result) 

    @property
    def download_results(self) -> List[DownloadResult]:
        """Get the current download results.

        Returns:
            List[DownloadResult]: List of all download attempts and their results
        """
        return self._download_results.copy()  # Return copy to prevent external modifications.copy()  # Return copy to prevent external modification

    def save_download_results(self, csv_path: str = DEFAULT_RESULTS_FILE) -> None:
        """Save download results to CSV file.

        Args:
            csv_path: Path where CSV file will be saved. Defaults to 'download_results.csv'
        """
        TDMReporting.save_download_results(self._download_results, csv_path)