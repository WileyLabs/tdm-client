import os
import logging
from typing import Final, List

class FileUtils:
    """Handles all file I/O operations for TDM Client."""

    # Class-level logger
    _logger = logging.getLogger(__name__)

    KB: Final[int] = 1024
    CHUNK_SIZE: Final[int] = 8 * KB  # 8KB chunks for downloads

    @staticmethod
    def ensure_directory(directory: str) -> None:
        """Create directory if it doesn't exist.

        Args:
            directory: Path to directory to create

        Raises:
            OSError: If directory cannot be created due to permissions or other OS issues
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
            FileUtils._logger.debug(f"Created directory: {directory}")

    @staticmethod
    def get_file_size_kb(file_path: str) -> int:
        """Get file size in kilobytes.

        Args:
            file_path: Path to file to check

        Returns:
            int: File size in kilobytes, rounded to nearest KB

        Raises:
            FileNotFoundError: If file does not exist
            OSError: If file size cannot be determined
        """
        return round(os.path.getsize(file_path) / FileUtils.KB)

    @staticmethod
    def save_file(response, file_path: str) -> int:
        """Save content from response to file.

        Downloads file content in chunks to minimize memory usage.
        Logs progress for files larger than 1MB.

        Args:
            response: requests.Response object with file content
            file_path: Path where to save the file

        Returns:
            int: Size of saved file in kilobytes

        Raises:
            IOError: If file cannot be written
            ValueError: If response content-length header is invalid
        """
        total_size = int(response.headers.get('content-length', 0))
        bytes_written = 0

        with open(file_path, 'wb') as output_file:
            for chunk in response.iter_content(chunk_size=FileUtils.CHUNK_SIZE):
                if chunk:
                    bytes_written += len(chunk)
                    output_file.write(chunk)
                    
                    if total_size > FileUtils.KB * 1024:  # Log progress for files > 1MB
                        progress = (bytes_written / total_size) * 100
                        FileUtils._logger.debug(f"Download progress: {progress:.1f}% ")

        file_size = FileUtils.get_file_size_kb(file_path)
        FileUtils._logger.info(f"Saved file: {file_path} ({file_size} KB)")
        return file_size

    @staticmethod
    def read_lines_from_file(file_path: str, skip_comments: bool = True, comment_char: str = '#') -> List[str]:
        """Read non-empty lines from a file.

        Args:
            file_path: Path to file to read
            skip_comments: Whether to ignore comment lines (default: True)
            comment_char: Character that indicates a comment line (default: '#')

        Returns:
            List[str]: List of non-empty, non-comment lines with whitespace stripped

        Raises:
            FileNotFoundError: If file does not exist
            OSError: If file cannot be read due to permissions
        """
        if not os.path.exists(file_path):
            message = f"File not found: {file_path}"
            FileUtils._logger.error(message)
            raise FileNotFoundError(message)

        lines = []
        with open(file_path, 'r') as file:
            for line in file:
                stripped = line.strip()
                if stripped and (not skip_comments or not stripped.startswith(comment_char)):
                    lines.append(stripped)

        FileUtils._logger.debug(f"Read {len(lines)} lines from {file_path}")
        return lines