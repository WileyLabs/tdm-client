"""Wiley TDM Client package."""

from .download_result import DownloadResult
from .download_status import DownloadStatus
from .tdm_client import TDMClient
from .tdm_reporting import TDMReporting

__version__ = "0.1.0"

__all__ = ["TDMClient", "DownloadResult", "DownloadStatus", "TDMReporting"]
