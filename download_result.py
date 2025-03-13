"""Module containing the DownloadResult dataclass."""

from dataclasses import dataclass
from typing import Optional
from http import HTTPStatus
from download_status import DownloadStatus

@dataclass
class DownloadResult:
    """Class to store download attempt results."""
    doi: str
    status: DownloadStatus
    comment: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None
    duration: Optional[float] = None
    api_status: Optional[HTTPStatus] = None

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self.status}"