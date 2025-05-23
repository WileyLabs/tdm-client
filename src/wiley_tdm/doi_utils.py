"""DOI validation and processing utilities.

This module provides functionality for validating and processing Digital Object
Identifiers (DOIs) through the doi.org API. It includes methods for format
validation, existence checking, and deduplication of DOI lists.

Features:
    - DOI format validation using regex
    - DOI existence validation via doi.org API
    - Deduplication of DOI lists while maintaining order
"""

# Standard library imports
import logging
import re
from collections import OrderedDict
from http import HTTPStatus
from typing import Final, List, Pattern

# Third-party imports
import requests


class DOIUtils:
    """Utility class for DOI operations and validation."""

    # Class-level logger and session
    _logger = logging.getLogger(__name__)
    _session: requests.Session = requests.Session()

    # DOI Configuration
    DOI_REGEX: Final[Pattern] = re.compile(
        r"^10.\d{4,9}/[-._;()/:<>\[\]A-Z0-9]+$", re.IGNORECASE
    )

    # DOI.org API Configuration
    API_URL: Final[str] = "https://doi.org/api/handles"
    API_TYPE: Final[str] = "URL"
    API_SUCCESS_CODE: Final[int] = 1
    API_CONNECTION_TIMEOUT: Final[int] = 2  # seconds - fail fast
    API_READ_TIMEOUT: Final[int] = 3  # seconds

    @staticmethod
    def is_valid(doi: str) -> bool:
        """Check if a DOI is valid via doi.org.

        Args:
            doi (str): The DOI to check.

        Returns:
            bool: True if either:
                - DOI format and API validation pass
                - Any error occurs (to avoid false negatives and fail gracefully)
            False only if DOI format check fails
        """
        try:
            if not DOIUtils.check_format(doi):
                return False
            url = f"{DOIUtils.API_URL}/{doi}?type={DOIUtils.API_TYPE}"
            response = DOIUtils._session.get(
                url,
                timeout=(DOIUtils.API_CONNECTION_TIMEOUT, DOIUtils.API_READ_TIMEOUT),
            )
            if response.status_code == HTTPStatus.OK:
                metadata = response.json()
                response_code = metadata.get("responseCode")
                return response_code == DOIUtils.API_SUCCESS_CODE
            return False
        except (requests.RequestException, ValueError, KeyError) as e:
            DOIUtils._logger.warning("Error validating DOI %s: %s", doi, str(e))
        return True  # Fail garcefully, as the TDM API will validate the DOI again

    @staticmethod
    def check_format(doi: str) -> bool:
        """Check if string matches DOI format.

        Args:
            doi: The DOI to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        is_valid = bool(DOIUtils.DOI_REGEX.match(doi))
        if is_valid:
            DOIUtils._logger.debug("Valid DOI format: %s", doi)
        return is_valid

    @staticmethod
    def dedupe(dois: List[str]) -> List[str]:
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
            DOIUtils._logger.debug(
                "Filtered out %d invalid or duplicate DOIs", filtered_count
            )
        return unique_dois
