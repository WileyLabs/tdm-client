"""Wiley TDM API client for downloading articles.

Manages article downloads, rate limiting, and result tracking.
Handles authentication, DOI validation, and file management.

"""

# Standard library imports
import os
import logging
import time
import urllib.parse
from http import HTTPStatus
from typing import Callable, Final, List, Optional
from uuid import UUID

# Third-party imports
import requests

# Local imports
from .tdm_reporting import TDMReporting
from .download_result import DownloadResult
from .download_status import DownloadStatus
from .ip_utils import IPUtils
from .file_utils import FileUtils
from .doi_utils import DOIUtils

class TDMClient:
    """Client for downloading articles from Wiley's TDM API."""

    # TDM API constants
    API_URL: Final[str] = 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/'
    API_TOKEN_ENV: Final[str] = 'TDM_API_TOKEN'
    API_TOKEN_HEADER: Final[str] = 'Wiley-TDM-Client-Token'
    API_USER_AGENT: Final[str] = 'TDMClient/0.1.0'

    # TDM API connection constants
    API_RATE_LIMIT: Final[float] = 5.0  # seconds
    API_CONNECTION_TIMEOUT: Final[int] = 5  # seconds for initial connection
    API_READ_TIMEOUT: Final[int] = 30    # seconds for reading response

    # File handling constants
    FILE_DOWNLOAD_DIR: Final[str] = "downloads/"
    FILE_RESULTS: Final[str] = "download_results.csv"
    FILE_DOIS: Final[str] = "dois.txt"
    FILE_DOI_SEPARATOR: Final[str] = "-"  # Used when converting DOI to filename

    # Other constants
    WOL_PDF_URL: Final[str] = "https://onlinelibrary.wiley.com/doi/epdf/"

    def __init__(self, tdm_token: Optional[str] = None, download_dir: str = FILE_DOWNLOAD_DIR):
        """Initialize the TDMClient with a TDM API token and download directory.
        If None, reads from TDM_API_TOKEN env variable.

        Args:
            tdm_token: UUID token string from Wiley's TDM service. 
            download_dir: Directory where PDFs will be saved. Defaults to 'downloads/'

        Raises:
            ValueError: If tdm_token is not provided and not found in environment
        """
        self.logger = logging.getLogger(__name__)

        # Get token from environment if not provided
        if tdm_token is None:
            tdm_token = os.getenv(TDMClient.API_TOKEN_ENV)
            if not tdm_token:
                raise ValueError(f"{TDMClient.API_TOKEN_ENV} environment variable not set")
            self.logger.debug("Using TDM API token from environment variable")

        # Public attributes
        self.download_results_errors_only: bool = False
        self.skip_existing_files: bool = True

        # Private instance attributes with type hints and defaults (use setters/constructors)
        self._download_dir: str  # Will be set by property
        self._tdm_token: str    # Will be set by property
        self._tdm_headers: dict[str, str] = {}
        self._tdm_session: requests.Session = requests.Session()
        self._rate_limit: float = TDMClient.API_RATE_LIMIT
        self._download_results: List[DownloadResult] = []
        self._my_ip_address: str = IPUtils.get_ip_address()
        self.logger.info("Your IP address, used to check entitlements: %s", self._my_ip_address)

        self.tdm_token = tdm_token  # Will validate UUID format
        self.download_dir = download_dir

        self._tdm_headers =  {
            TDMClient.API_TOKEN_HEADER: self._tdm_token,
            'User-Agent': TDMClient.API_USER_AGENT,
        }

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
        if value < TDMClient.API_RATE_LIMIT:
            raise ValueError(f"Rate limit is below default: {TDMClient.API_RATE_LIMIT} seconds")
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
            ValueError: If token is not a valid UUID string
        """
        try:
            # Validate UUID format
            uuid_obj = UUID(str(value))
            self._tdm_token = str(uuid_obj)
            # Update only the token header
            self._tdm_headers[TDMClient.API_TOKEN_HEADER] = self._tdm_token
            self._tdm_session.headers.update({TDMClient.API_TOKEN_HEADER: self._tdm_token})
            self.logger.debug("TDM API token updated")
        except ValueError as exc:
            raise ValueError("Invalid TDM API token format. Must be a valid UUID.") from exc

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
        FileUtils.ensure_directory(value)
        self.logger.info("Downloading to: %s", value)
        self._download_dir = value

    def download_pdf(self, doi: str) -> DownloadResult:
        """Download a single article PDF given its DOI.

        Args:
            doi: The DOI of the article to download

        Returns:
            DownloadResult: Result of the download attempt

        Raises:
            ValueError: If DOI is None or empty string
        """
        result:DownloadResult

        if doi is None or not doi.strip():
            raise ValueError("DOI cannot be None or empty")

        # Avoid double encoding or DOI validation issues later
        doi = urllib.parse.unquote(doi)

        if DOIUtils.is_valid(doi):

            if self.skip_existing_files and FileUtils.is_file(self.download_dir, doi, "pdf"):
                result = DownloadResult(
                    doi,
                    DownloadStatus.EXISTING_FILE,
                    "",
                    FileUtils.get_path(self.download_dir, doi, "pdf")
                )
            else:
                start_time = time.perf_counter()
                result = self._download_pdf(doi)
                duration = time.perf_counter() - start_time
                result.duration = duration
        else:
            result = DownloadResult(
                doi,
                DownloadStatus.INVALID_DOI
            )

        self._add_download_result(result)
        return result

    def _download_pdf(self, doi: str) -> DownloadResult:
        """Download an article PDF given its DOI.

        Args:
            doi: The DOI of the article to download

        Returns:
            DownloadResult: DownloadResult for the requested Article DOI
        """

        # Prepare request
        encoded_doi = urllib.parse.quote(doi, safe='')
        request_url = f"{TDMClient.API_URL}{encoded_doi}"
        self.logger.debug("Requesting PDF from: %s", request_url)

        try:
            response = self._tdm_session.get(
                request_url,
                allow_redirects=True,
                stream=True,
                timeout=(TDMClient.API_CONNECTION_TIMEOUT, TDMClient.API_READ_TIMEOUT),
            )

            # Log response info for debugging
            self.logger.debug("Response headers: %s", dict(response.headers))

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
                DownloadStatus.NETWORK_ERROR,
                str(e)
            )

    def _handle_error_status(
        self,
        doi: str,
        status: HTTPStatus,
        response: requests.Response
    ) -> DownloadResult:
        """Handle non-200 HTTP status codes.
        
        Args:
            doi: The DOI being processed
            status: HTTP status code
            response: Full response object
            
        Returns:
            DownloadResult: Error result with appropriate status
        """
        if status == HTTPStatus.FORBIDDEN:
            pdf_url = f"{TDMClient.WOL_PDF_URL}{doi}"
            return DownloadResult(
                doi,
                DownloadStatus.FORBIDDEN,
                f"TDM access denied from IP {self._my_ip_address}. Try manually: {pdf_url}",
                api_status=status
            )
        if status == HTTPStatus.NOT_FOUND:
            if ';' in doi:
                return DownloadResult(
                    doi,
                    DownloadStatus.KNOWN_ISSUE,
                    "DOI contains semicolon",
                    api_status=status
                )
            return DownloadResult(
                doi,
                DownloadStatus.UNKNOWN_DOI,
                None,
                api_status=status
            )

        return DownloadResult(
            doi,
            DownloadStatus.API_ERROR,
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
                DownloadStatus.API_ERROR,
                "Invalid content type. Expected application/pdf",
            )

        pdf_path = FileUtils.get_path(self.download_dir, doi, "pdf")

        try:
            file_size = FileUtils.save_file(response, pdf_path)
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

    def download_pdfs(
        self,
        dois: List[str],
        on_result: Optional[Callable[[DownloadResult], None]] = None
    ) -> List[DownloadResult]:
        """Download multiple articles given their DOIs.

        Args:
            dois: List of DOIs to download
            on_result: Optional callback function called after each download

        Returns:
            List[DownloadResult]: List of download results
        """
        unique_dois = DOIUtils.dedupe(dois)
        results: List[DownloadResult] = []

        for doi in unique_dois:
            result = self.download_pdf(doi)
            if result:
                results.append(result)
                if on_result:
                    on_result(result)
                if result.status != DownloadStatus.EXISTING_FILE:
                    self.logger.debug("Rate limiting: sleeping for %s seconds", self.rate_limit)
                    time.sleep(self.rate_limit)
        return results

    def download_pdfs_from_file(
        self,
        dois_file_path: str = FILE_DOIS,
        on_result: Optional[Callable[[DownloadResult], None]] = None
    ) -> List[DownloadResult]:
        """Download articles listed in a file.

        Args:
            dois_file_path: Path to file containing DOIs, one per line
            on_result: Optional callback function called after each download

        Returns:
            List[DownloadResult]: List of download results

        Raises:
            FileNotFoundError: If the DOIs file doesn't exist
            OSError: If there are permission or other OS-level errors
        """
        dois = FileUtils.read_lines_from_file(dois_file_path)

        if len(dois) == 0:
            self.logger.warning("Empty or invalid DOIs file: %s", dois_file_path)
            return []

        self.logger.info("Found %d DOIs in %s", len(dois), dois_file_path)
        return self.download_pdfs(dois, on_result=on_result)

    def _add_download_result(self, result: DownloadResult) -> None:
        """Record download result.

        Args:
            result: DownloadResult to add to the list
        """

        message = f"DOI: {result.doi} - {result.status}"

        if result.status in (DownloadStatus.SUCCESS, DownloadStatus.EXISTING_FILE):
            if self.download_results_errors_only:
                return
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
        return self._download_results.copy()  # Return copy to prevent external modification

    def save_download_results(self, csv_path: str = FILE_RESULTS) -> None:
        """Save download results to CSV file.

        Args:
            csv_path: Path where CSV file will be saved. Defaults to 'download_results.csv'
        """
        TDMReporting.save_download_results(self._download_results, csv_path)
