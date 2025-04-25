from enum import Enum, auto

class DownloadStatus(Enum):
    """Status codes for download operations."""
    
    # TDM API
    SUCCESS = auto() 
    FORBIDDEN = auto()
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
        return self.name.replace('_', ' ').upper()