import logging
import re
from http import HTTPStatus
from typing import Final, Pattern, List
from collections import OrderedDict

# Third-party imports
import requests

class DOIUtils:
    """Utility class for DOI operations and validation."""

    # Class-level logger
    _logger = logging.getLogger(__name__)

    # DOI Configuration
    DOI_REGEX: Final[Pattern] = re.compile(r'^10.\d{4,9}/[-._;()/:<>\[\]A-Z0-9]+$', re.IGNORECASE)

    # CrossRef API Configuration
    CROSSREF_API_URL: Final[str] = 'https://api.crossref.org/works'
    CROSSREF_SELECT: Final[str] = 'title'
    CROSSREF_PUBLISHER: Final[str] = 'Wiley'
    
    # Class-level session for CrossRef API
    _crossref_session: requests.Session = requests.Session()

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
            DOIUtils._logger.debug(f"Valid DOI format: {doi}")
        return is_valid

    @staticmethod
    def check_crossref(doi: str) -> bool:
        """Check if DOI is valid using CrossRef API.
        
        Args:
            doi: The DOI to verify

        Returns:
            bool: True if verified by CrossRef, False otherwise

        Raises:
            requests.RequestException: If network error occurs during validation
        """
        crossref_params = {
            'select': DOIUtils.CROSSREF_SELECT,
            'query.publisher-name': DOIUtils.CROSSREF_PUBLISHER,
            'filter': f'doi:{doi}'
        }

        response = DOIUtils._crossref_session.get(
            DOIUtils.CROSSREF_API_URL, 
            params=crossref_params
        )
        
        if response.status_code != HTTPStatus.OK:
            return False

        crossref_data = response.json()
        return (crossref_data.get('status') == 'ok' and
                crossref_data.get('message') and
                crossref_data['message'].get('total-results') == 1)

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
            DOIUtils._logger.info(f"Filtered out {filtered_count} invalid or duplicate DOIs")
        
        return unique_dois