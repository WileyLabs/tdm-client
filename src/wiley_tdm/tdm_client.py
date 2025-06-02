"""Wiley TDM API client module for downloading academic articles.

This module provides a client interface for Wiley's Text and Data Mining (TDM) API.
It handles authentication, rate limiting, and manages the download of academic articles
through their DOIs.

For cross-platform compatibility, all path operations use PathLib:
    Path("downloads") / "open-access"

Typical usage:
    client = TDMClient(api_token)
    result = client.download_pdf("10.1002/example.doi")
"""

# Standard library imports
import logging
import os
import time
import urllib.parse
from http import HTTPStatus
from pathlib import Path
from typing import Callable, Final, List, Optional, Union
from uuid import UUID

# Third-party imports
import requests

# Local imports
from .doi_utils import DOIUtils
from .download_result import DownloadResult
from .download_status import DownloadStatus
from .file_utils import FileUtils
from .ip_utils import IPUtils
from .tdm_reporting import TDMReporting
from .types import StrPath


class TDMClient:
    """Client for downloading and managing Wiley TDM API article access.

    This class handles:
    - Single and batch article downloads via DOI
    - Rate-limited API requests
    - Download result tracking and reporting
    - Cross-platform file management
    - DOI validation and error handling

    Attributes:
        download_dir (Path): Directory where PDFs are saved
        api_rate_limit (float): Time in seconds between API requests
        download_results_errors_only (bool): Only track failed downloads
        skip_existing_files (bool): Skip downloading if file exists

    Return Types:
        All download methods return DownloadResult objects containing:
        - Download status
        - File path (if successful)
        - Error message (if failed)
        - API status code
        - Duration of download
    """

    # TDM API constants
    API_URL: Final[str] = "https://api.wiley.com/onlinelibrary/tdm/v1/articles/"
    API_TOKEN_ENV: Final[str] = "TDM_API_TOKEN"
    API_TOKEN_HEADER: Final[str] = "Wiley-TDM-Client-Token"
    API_USER_AGENT: Final[str] = "TDMClient/1.0.0"

    # TDM API connection constants
    API_RATE_LIMIT: Final[float] = 5.0  # seconds
    API_CONNECTION_TIMEOUT: Final[int] = 5  # seconds for initial connection
    API_READ_TIMEOUT: Final[int] = 30  # seconds for reading response

    # File handling constants. Relative to current working directory
    DOWNLOAD_DIR: Final[Path] = Path("downloads")
    RESULTS_FILE: Final[Path] = Path("results.csv")
    DOIS_FILE: Final[Path] = Path("dois.txt")

    # Other constants
    WOL_PDF_URL: Final[str] = "https://onlinelibrary.wiley.com/doi/epdf/"

    def __init__(
        self, api_token: Optional[str] = None, download_dir: StrPath = DOWNLOAD_DIR
    ):
        """Initialize the TDMClient with API token and download directory.

        The API token can be provided directly or read from environment.
        The download directory defaults to 'downloads' in current working directory.

        Args:
            api_token: TDM API token string (UUID) from Wiley's TDM service.
                If None, reads from TDM_API_TOKEN environment variable.

            download_dir: Directory path for saving PDFs.  Can be either:
                - A string path
                - A PathLike object (recommended)
                Relative paths are resolved from the current working directory.

        Raises:
            ValueError: If token is not provided, not in environment, or invalid UUID
            OSError: If download directory cannot be created
        """
        self.logger = logging.getLogger(__name__)

        # Public attributes (set via public properties)
        self.download_dir = download_dir
        self.api_rate_limit = TDMClient.API_RATE_LIMIT
        self.only_record_errors: bool = False
        self.skip_existing_files: bool = True

        # Private attributes
        self._download_dir: Path  # Set by property
        self._api_rate_limit: float  # Set by property
        self._api_token: str
        self._api_headers: dict[str, str] = {}
        self._api_session: requests.Session
        self._results: List[DownloadResult] = []

        self._validate_api_token(api_token)
        self._create_api_session()
        self._client_public_ip: Optional[str] = IPUtils.get_ip_address()

        if self._client_public_ip:
            self.logger.info(
                "Your public IP address, (only) used to check entitlements: %s",
                self._client_public_ip,
            )

    def _validate_api_token(self, api_token: Optional[str]) -> None:
        """Initialize the TDM API token.

        Private method to handle token initialization and validation.

        Args:
            api_token: UUID token from Wiley's TDM service or None to use environment

        Returns:
            None

        Raises:
            ValueError: If token is not provided, not in environment, or invalid UUID
        """
        # Get token from environment if not provided
        if api_token is None:
            api_token = os.getenv(TDMClient.API_TOKEN_ENV)
            if not api_token:
                raise ValueError(
                    f"{TDMClient.API_TOKEN_ENV} environment variable not set"
                )
            self.logger.debug("Using TDM API token from environment variable")

        # Validate UUID format
        try:
            uuid_obj = UUID(str(api_token))
            self._api_token = str(uuid_obj)
        except ValueError as exc:
            raise ValueError(
                "Invalid TDM API token format. Must be a valid UUID."
            ) from exc

    def _create_api_session(self):
        """Initialize the TDM API session."""
        self._api_session = requests.Session()
        self._api_session.headers.update(
            {
                TDMClient.API_TOKEN_HEADER: self._api_token,
                "User-Agent": TDMClient.API_USER_AGENT,
                "Connection": "keep-alive",
            }
        )

    @property
    def api_rate_limit(self) -> float:
        """Get the TDM API rate limit.

        Returns:
            float: Current rate limit in seconds
        """
        return self._api_rate_limit

    @api_rate_limit.setter
    def api_rate_limit(self, value: float):
        """Set the TDM API rate limit.

        Args:
            value: Rate limit in seconds

        Raises:
            ValueError: If value is less than default API_RATE_LIMIT
        """
        if value < TDMClient.API_RATE_LIMIT:
            raise ValueError(
                f"Rate limit is below default: {TDMClient.API_RATE_LIMIT} seconds"
            )
        self._api_rate_limit = value

    @property
    def download_dir(self) -> Path:
        """Directory where PDF files are saved.

        Returns:
            Path: Current download directory path
        """
        return self._download_dir

    @download_dir.setter
    def download_dir(self, download_dir: StrPath):
        """Set the download directory and ensure it exists.

        Args:
            download_dir: Directory path for saving PDFs. Can be either:
                - A string path
                - A PathLike object (recommended)
                Relative paths are resolved from the current working directory.

        Raises:
            OSError: If directory cannot be created due to permissions
        """
        path = FileUtils.create_directory(download_dir)
        self._download_dir = path
        self.logger.info("Downloading to: %s", path)

    def download_pdf(self, doi: str) -> DownloadResult:
        """Download a single article PDF given its DOI.

        Args:
            doi: The DOI of the article to download

        Returns:
            DownloadResult: Result of the download attempt

        Raises:
            ValueError: If DOI is None or empty string

        Examples:
            >>> client = TDMClient(api_token)
            >>> result = client.download_pdf("10.1002/example.doi")
            >>> if result.status == DownloadStatus.SUCCESS:
            ...     print(f"PDF saved to {result.file_path}")
        """
        result = None

        if doi is None or not doi.strip():
            raise ValueError("DOI cannot be None or empty")

        # Avoid double encoding or DOI validation issues later
        doi = urllib.parse.unquote(doi)

        if DOIUtils.is_valid(doi):
            if self.skip_existing_files:
                file_path = FileUtils.to_file_path(self.download_dir, doi, "pdf")
                if file_path.exists():
                    result = DownloadResult(
                        doi, DownloadStatus.EXISTING_FILE, "", file_path
                    )
        else:
            result = DownloadResult(doi, DownloadStatus.INVALID_DOI)

        if result is None:  # No issues, proceed with download
            start_time = time.perf_counter()
            result = self._download_pdf(doi)
            duration = time.perf_counter() - start_time
            result.duration = duration

        self._add_result(result)
        return result

    def download_pdfs(
        self,
        dois: Union[List[str], StrPath],
        on_result: Optional[Callable[[DownloadResult], None]] = None,
    ) -> List[DownloadResult]:
        """Download multiple PDFs from either a list of DOIs or a file containing DOIs.

        Args:
            dois: Either a list of DOI strings or a path to a file containing DOIs (one per line)
            on_result: Optional callback function called after each download
        Relative paths are resolved from the current working directory

        Returns:
            List[DownloadResult]: List of download results

        Raises:
            FileNotFoundError: If dois is a file path that doesn't exist
            ValueError: If dois list is empty
        """
        # Check if `dois` is a string or Path (matches StrPath type alias)
        if isinstance(dois, (str, Path)):
            dois_list: List[str] = FileUtils.read_lines_from_file(dois)
            self.logger.info("Found %d DOIs in %s", len(dois_list), dois)
        # Explicitly check that `dois` is a list of strings
        elif isinstance(dois, list):
            dois_list: List[str] = dois
        else:
            raise TypeError("Invalid type for `dois`. Expected List[str] or StrPath.")

        if not dois_list:
            raise ValueError("DOIs list cannot be empty")

        unique_dois: List[str] = DOIUtils.dedupe(dois_list)
        results: List[DownloadResult] = []

        for doi in unique_dois:
            result = self.download_pdf(doi)
            if result:
                results.append(result)
                if on_result:
                    on_result(result)
                if result.status != DownloadStatus.EXISTING_FILE:
                    self.logger.debug(
                        "Rate limiting: sleeping for %s seconds", self.api_rate_limit
                    )
                    time.sleep(self.api_rate_limit)
        return results

    def _download_pdf(self, doi: str) -> DownloadResult:
        """Download an article PDF given its DOI.

        Args:
            doi: The DOI of the article to download

        Returns:
            DownloadResult: DownloadResult for the requested Article DOI
        """

        # Prepare request
        encoded_doi = urllib.parse.quote(doi, safe="")
        request_url = f"{TDMClient.API_URL}{encoded_doi}"
        self.logger.debug("Requesting PDF from: %s", request_url)

        try:
            response = self._api_session.get(
                request_url,
                allow_redirects=True,
                stream=True,
                timeout=(TDMClient.API_CONNECTION_TIMEOUT, TDMClient.API_READ_TIMEOUT),
            )

            # Log response info for debugging
            self.logger.debug("Response headers: %s", dict(response.headers))

            status = HTTPStatus(response.status_code)

            if status != HTTPStatus.OK:
                return self._handle_api_error(doi, status, response)

            # Save PDF and include status code
            result = self._save_pdf(response, doi)
            result.api_status = status
            return result

        except requests.RequestException as e:
            return DownloadResult(doi, DownloadStatus.NETWORK_ERROR, str(e))

    def _handle_api_error(
        self, doi: str, status: HTTPStatus, response: requests.Response
    ) -> DownloadResult:
        """Handle non-200 HTTP status codes.

        Args:
            doi: The DOI being processed
            status: HTTP status code
            response: Full response object from the API request

        Returns:
            DownloadResult: Error result with appropriate status and message
        """
        if status == HTTPStatus.FORBIDDEN:
            pdf_url = f"{TDMClient.WOL_PDF_URL}{doi}"
            return DownloadResult(
                doi,
                DownloadStatus.ACCESS_DENIED,
                f"TDM access denied from IP {self._client_public_ip}. Try manually: {pdf_url}",
                api_status=status,
            )
        if status == HTTPStatus.NOT_FOUND:
            if ";" in doi:
                return DownloadResult(
                    doi,
                    DownloadStatus.KNOWN_ISSUE,
                    "DOI contains semicolon",
                    api_status=status,
                )
            return DownloadResult(
                doi, DownloadStatus.UNKNOWN_DOI, None, api_status=status
            )

        return DownloadResult(
            doi, DownloadStatus.API_ERROR, response.text, api_status=status
        )

    def _save_pdf(self, response: requests.Response, doi: str) -> DownloadResult:
        """Save PDF content from response to file.

        Args:
            response: The HTTP response containing PDF content
            doi: The DOI of the article

        Returns:
            DownloadResult: Result of the save operation
        """

        pdf_path = FileUtils.to_file_path(self.download_dir, doi, "pdf")

        try:
            file_size = FileUtils.save_file(response, pdf_path)
            return DownloadResult(doi, DownloadStatus.SUCCESS, "", pdf_path, file_size)
        except IOError as e:
            return DownloadResult(doi, DownloadStatus.STORAGE_ERROR, str(e), pdf_path)

    def _add_result(self, result: DownloadResult) -> None:
        """Record download result.

        Args:
            result: DownloadResult to add to the list
        """

        message = f"DOI: {result.doi} - {result.status}"

        if result.status in (DownloadStatus.SUCCESS, DownloadStatus.EXISTING_FILE):
            if self.only_record_errors:
                return
            self.logger.info(message)
        else:
            self.logger.error(message)

        self._results.append(result)

    @property
    def results(self) -> List[DownloadResult]:
        """Get the current download results.

        Returns:
            List[DownloadResult]: List of all download attempts and their results
        """
        return self._results.copy()  # Return copy to prevent external modification

    def save_results(self, csv_path: StrPath = RESULTS_FILE) -> None:
        """Save download results to CSV file. Defaults to 'results.csv'

        Args:
            csv_path: Path where CSV file will be saved. Can be either:
                - A string path
                - A PathLike object (recommended)
                Relative paths are resolved from the current working directory
        Returns:
            None

        Raises:
            OSError: If the file cannot be written due to permissions or other OS issues
        """
        TDMReporting.save_results(self._results, csv_path)
