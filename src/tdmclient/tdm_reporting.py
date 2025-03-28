"""Module for TDM reporting functionality."""

# Standard library imports
import os
import csv
import logging
from typing import Final, List

# Local imports
from .download_result import DownloadResult
from .download_status import DownloadStatus

class TDMReporting:
    """Handles reporting functionality for TDM downloads."""

    # CSV Configuration
    CSV_HEADERS: Final[List[str]] = [
        'DOI', 
        'Status', 
        'Comment', 
        'Path', 
        'Size (KB)', 
        'Duration (s)', 
        'HTTP Status'
    ]

    @staticmethod
    def save_download_results(results: List[DownloadResult], csv_path: str) -> None:
        """Save download results to CSV file.

        Args:
            results: List of download results to save
            csv_path: Path where CSV file will be saved
        """
        logger = logging.getLogger(__name__)

        if not results or results == []:
            logger.info("No results to save")
            return

        # Create directory if needed
        directory = os.path.dirname(csv_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(TDMReporting.CSV_HEADERS)
            for result in results:
                writer.writerow([
                    result.doi,
                    result.status,
                    result.comment or "",
                    result.path or "",
                    result.size or "",
                    f"{result.duration:.1f}" if result.duration else "",
                    result.api_status.value if result.api_status else ""
                ])
        
        logger.info(f"Download results saved to: {csv_path}")