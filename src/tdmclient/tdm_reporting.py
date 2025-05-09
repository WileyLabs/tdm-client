"""Module for TDM reporting functionality."""

# Standard library imports
import csv
import logging
import os
from typing import Final, List

# Local imports
from .download_result import DownloadResult

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
            logger.info("No download results to save")
            return

        # Create directory if needed
        directory = os.path.dirname(csv_path)
        os.makedirs(directory, exist_ok=True)

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
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

        logger.info("Download results saved to: %s", csv_path)
