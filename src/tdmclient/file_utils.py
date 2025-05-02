"""File system utilities for TDM Client.

Handles file downloads, path management, and I/O operations with:
- Safe filename generation (handles special characters)
- Chunked downloads with progress tracking
- Directory and file management
- Line-based file reading with comment support
"""

import os
import logging
from typing import Final, List

class FileUtils:
    """Handles all file I/O operations for TDM Client."""

    # Class-level logger
    _logger = logging.getLogger(__name__)

    KB: Final[int] = 1024
    CHUNK_SIZE: Final[int] = 8 * KB  # 8KB chunks for downloads
    COMMENT_CHAR: Final[str] = '#'

    # File handling constants
    FILE_SEPARATOR: Final[str] = "-"
    UNSAFE_CHARS: Final[set] = {
        '/', '\\',  # Path separators
        ':', ';',   # Path/command delimiters
        '*', '?',   # Wildcards
        '"', "'",   # Quotes
        '<', '>',   # Redirections
        '|',        # Pipe
        ' ',        # Space
        '\t',       # Tab
        '\n', '\r'  # Line endings
    }

    @staticmethod
    def make_safe_filename(name: str) -> str:
        """Convert string to safe filename by replacing unsafe characters.
        
        Args:
            name: Original filename or path component
            
        Returns:
            str: Safe filename with special chars replaced
            
        Example:
            >>> FileUtils.make_safe_filename("10.1002/smj:123")
            '10.1002-smj-123'
        """
        safe_name = name
        for char in FileUtils.UNSAFE_CHARS:
            safe_name = safe_name.replace(char, FileUtils.FILE_SEPARATOR)

        # Then collapse multiple separators into one
        while '--' in safe_name:
            safe_name = safe_name.replace('--', '-')

        # Remove any leading or trailing separators
        safe_name = safe_name.strip('-')

        return safe_name

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
            FileUtils._logger.debug("Created directory: %s", directory)

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
                        FileUtils._logger.debug("Download progress: %.1f%%", progress)

        file_size = FileUtils.get_file_size_kb(file_path)
        FileUtils._logger.debug("Saved file: %s (%d KB)", file_path, file_size)
        return file_size

    @staticmethod
    def read_lines_from_file(file_path: str, skip_comments: bool = True) -> List[str]:
        """Read non-empty lines from a file.

        Args:
            file_path: Path to file to read
            skip_comments: Whether to ignore comment lines (default: True)

        Returns:
            List[str]: List of non-empty, non-comment lines with whitespace stripped

        Raises:
            FileNotFoundError: If file does not exist
            OSError: If file cannot be read due to permissions
        """
        if not os.path.exists(file_path):
            message = f"File not found: {file_path}"
            FileUtils._logger.error("File not found: %s", file_path)
            raise FileNotFoundError(message)

        lines = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                stripped = line.strip()
                if not stripped:
                    continue
                if skip_comments:
                    if stripped.startswith(FileUtils.COMMENT_CHAR):
                        continue
                lines.append(stripped)

        FileUtils._logger.debug("Read %d lines from %s", len(lines), file_path)
        return lines

    @staticmethod
    def get_path(directory: str, name: str, extension: str) -> str:
        """Get full file path with safe filename conversion.
        
        Args:
            directory: Directory path
            name: Base name (e.g., DOI)
            extension: File extension without dot
            
        Returns:
            str: Full path with safe filename
            
        Example:
            >>> FileUtils.get_path("downloads", "10.1002/smj.123", "pdf")
            'downloads/10.1002-smj.123.pdf'
        """
        safe_name = FileUtils.make_safe_filename(name)
        return os.path.join(directory, f"{safe_name}.{extension.lstrip('.')}")

    @staticmethod
    def is_file(directory: str, name: str, extension: str) -> bool:
        """Check if a file exists in the specified directory."""
        file_path = FileUtils.get_path(directory, name, extension)
        exists = os.path.exists(file_path)

        if exists:
            FileUtils._logger.debug("File exists: %s", file_path)

        return exists
