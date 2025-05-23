"""Download status enumeration module.

Defines status codes for download operations with clear categories:
- TDM API
- File system operations
- DOI validation
- Network issues

"""

# Standard library imports
from enum import Enum, auto


class DownloadStatus(Enum):
    """Status codes for download operations."""

    # TDM API
    SUCCESS = auto()
    ACCESS_DENIED = auto()
    UNKNOWN_DOI = auto()
    KNOWN_ISSUE = auto()
    API_ERROR = auto()

    # File System
    EXISTING_FILE = auto()
    STORAGE_ERROR = auto()

    # Validation (via 3rd party)
    INVALID_DOI = auto()

    # Network/API errors
    NETWORK_ERROR = auto()

    def __str__(self) -> str:
        """Return a human-readable string."""
        return self.name.replace("_", " ").title()
