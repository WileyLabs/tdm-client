import re
import logging
import requests
from http import HTTPStatus

class DOIValidator:
    """Utility class for DOI validation and formatting."""

    # DOI validation
    DOI_REGEX: re.Pattern = re.compile(r'^10.\d{4,9}/[-._;()/:<>\[\]A-Z0-9]+$', re.IGNORECASE)

    # CrossRef API configuration
    CROSSREF_API_URL: str = 'https://api.crossref.org/works'
    CROSSREF_SELECT: str = 'title'
    CROSSREF_PUBLISHER: str = 'Wiley'

    def __init__(self):
        """Initialize DOIUtils."""
        self.logger = logging.getLogger(__name__)
        self.crossref_session: requests.Session = requests.Session()

    def check_format(self, doi: str) -> bool:
        """Check if string matches DOI format.
        
        Args:
            doi: The DOI to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        is_valid = bool(self.DOI_REGEX.match(doi))
        if is_valid:
            self.logger.debug(f"Valid DOI format: {doi}")
        return is_valid

    def check_crossref(self, doi: str) -> bool:
        """Check if DOI is valid using CrossRef API.
        
        Args:
            doi: The DOI to verify

        Returns:
            bool: True if verified by CrossRef, False otherwise

        Raises:
            requests.RequestException: If network error occurs during validation
        """
        crossref_params = {
            'select': self.CROSSREF_SELECT,
            'query.publisher-name': self.CROSSREF_PUBLISHER,
            'filter': f'doi:{doi}'
        }

        response = self.crossref_session.get(self.CROSSREF_API_URL, params=crossref_params)
        if response.status_code != HTTPStatus.OK:
            return False

        crossref_data = response.json()
        return (crossref_data.get('status') == 'ok' and
                crossref_data.get('message') and
                crossref_data['message'].get('total-results') == 1)