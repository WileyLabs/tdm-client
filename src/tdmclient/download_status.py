from enum import Enum, auto

class DownloadStatus(Enum):
    """Status codes for download operations."""
    
    # Success states
    SUCCESS = auto() 
    EXISTING_FILE = auto()
    
    # DOI validation errors
    INVALID_DOI = auto()
    UNKNOWN_DOI = auto()
    KNOWN_ISSUE = auto()
    
    # Access errors
    FORBIDDEN = auto()
    
    # Network/API errors
    NETWORK_ERROR = auto()
    WILEY_API_ERROR = auto()

    # File system issues 
    STORAGE_ERROR = auto()
    
    # Content errors (i.e. not PDF)
    INVALID_CONTENT = auto()

    def __str__(self) -> str:
        """Return a human-readable string."""
        return self.name.replace('_', ' ').upper()