"""Module containing the DownloadResult dataclass."""

# Standard library imports
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Optional

# Local imports
from .download_status import DownloadStatus


@dataclass
class DownloadResult:
    """Class to store download attempt results."""

    doi: str
    status: DownloadStatus
    comment: Optional[str] = None
    path: Optional[Path] = None
    size: Optional[int] = None
    duration: Optional[float] = None
    api_status: Optional[HTTPStatus] = None

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"{self.status}"
