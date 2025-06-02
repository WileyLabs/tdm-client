"""Module for TDM reporting functionality."""

# Standard library imports
import csv
import logging
from typing import Final, List

# Local imports
from .download_result import DownloadResult
from .file_utils import FileUtils
from .types import StrPath


class TDMReporting:
    """Handles reporting functionality for TDM downloads."""

    # CSV Configuration
    CSV_HEADERS: Final[List[str]] = [
        "DOI",
        "Status",
        "Comment",
        "Path",
        "Size (KB)",
        "Duration (s)",
        "HTTP Status",
    ]

    @staticmethod
    def save_results(results: List[DownloadResult], csv_path: StrPath) -> None:
        """Save download results to CSV file.

        Args:
            results: List of download results to save
            csv_path: Path to the CSV file. Can be either:
                - A PathLike object (recommend): Path("downloads") / "results.csv"
                - A string: "downloads/results.csv" Will be converted to Path internally
            Relative paths are resolved from the current working directory

        Note:
            Recommend using Path objects for platform-independent path handling.
        """
        logger = logging.getLogger(__name__)

        if not results or results == []:
            logger.info("No download results to save")
            return

        FileUtils.create_directory(csv_path)

        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(TDMReporting.CSV_HEADERS)
            for result in results:
                writer.writerow(
                    [
                        result.doi,
                        result.status,
                        result.comment or "",
                        result.path or "",
                        result.size or "",
                        f"{result.duration:.1f}" if result.duration else "",
                        result.api_status.value if result.api_status else "",
                    ]
                )

        logger.info("Download results saved to: %s", csv_path)
