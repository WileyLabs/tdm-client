from enum import Enum, auto

class DownloadStatus(Enum):
    """Status codes for download operations."""
    # Success states
    SUCCESS = auto()                  # Successfully downloaded and saved
    FILE_EXISTS = auto()              # File already exists locally
    
    # DOI validation errors
    INVALID_DOI_FORMAT = auto()       # DOI format validation failed
    UNKNOWN_WILEY_DOI_CROSSREF = auto()     # Wiley DOI not found in CrossRef
    UNKNOWN_WILEY_DOI = auto()        # DOI not found in Wiley
    SEMICOLON_ERROR = auto()          # Known API limitation with semicolons
    
    # Access errors
    FORBIDDEN = auto()                # IP not authorized for TDM access
    
    # Network/API errors
    NETWORK_ERROR = auto()            # Connection/timeout issues
    WILEY_API_ERROR = auto()          # Generic API error response
    CROSSREF_API_ERROR = auto()       # Generic API error response

    # Local storage errors
    STORAGE_ERROR = auto()            # File system issues (permissions, space)
    
    # Content errors
    INVALID_CONTENT = auto()          # Response not a PDF

    def __str__(self) -> str:
        """Return a human-readable string."""
        return self.name.replace('_', ' ').upper()