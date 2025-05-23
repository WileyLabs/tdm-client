"""File system utilities for TDM Client.

Handles file downloads, path management, and I/O operations with:
- Safe filename generation (handles special characters)
- Chunked downloads with progress tracking
- Directory and file management
- Line-based file reading with comment support

Path Arguments:
    All path parameters (type StrPath) accept either:
    - A PathLike object (recommend): Path("downloads") / "open-access" / "article.pdf"
    - A string: "downloads/open-access/article.pdf" Will be converted to Path internally

    For cross-platform compatibility, use Path objects and the / operator
"""

# Standard library imports
import logging
from pathlib import Path
from typing import Final, List

# Local imports
from .types import StrPath


class FileUtils:
    """Handles all file I/O operations for TDM Client."""

    # Class-level logger
    _logger = logging.getLogger(__name__)

    KB: Final[int] = 1024
    CHUNK_SIZE: Final[int] = 8 * KB  # 8KB chunks for downloads
    COMMENT_CHAR: Final[str] = "#"

    # File handling constants
    FILE_SEPARATOR: Final[str] = "-"
    UNSAFE_CHARS: Final[set] = {
        "/",
        "\\",  # Path separators
        ":",
        ";",  # Path/command delimiters
        "*",
        "?",  # Wildcards
        '"',
        "'",  # Quotes
        "<",
        ">",  # Redirections
        "|",  # Pipe
        " ",  # Space
        "\t",  # Tab
        "\n",
        "\r",  # Line endings
    }

    @staticmethod
    def to_path(path: StrPath) -> Path:
        """Convert any path input to a normalized Path object.

        Standardizes path handling by:
        - Converting String or PathLike input to Path object

        Args:
            path: Path to file or directory

        Note:
            Recommend using Path objects for platform-independent path handling.

        Returns:
            Path: Path object with normalized format

        """
        if isinstance(path, Path):
            return path
        return Path(str(path))

    @staticmethod
    def to_safe_filename(file_stem: str, file_suffix: str) -> str:
        """Create a safe filename by replacing unsafe characters.

        Args:
            file_stem: Name part of file without extension
            file_suffix: File extension without dot

        Returns:
            str: Safe filename with special chars replaced and extension added

        Example:
            >>> FileUtils.to_safe_filename("10.1002/smj:123", "pdf")
            '10.1002-smj-123.pdf'
        """

        for char in FileUtils.UNSAFE_CHARS:
            file_stem = file_stem.replace(char, FileUtils.FILE_SEPARATOR)

        # Then collapse multiple separators into one
        while "--" in file_stem:
            file_stem = file_stem.replace("--", "-")

        # Remove any leading or trailing separators
        file_stem = file_stem.strip("-")

        return f"{file_stem}.{file_suffix}"

    @staticmethod
    def create_directory(directory_path: StrPath) -> Path:
        """Create directory if it doesn't exist.

        Args:
            directory_path: Path to the directory
        Returns:
            Path: Path to the directory created or already existing
        Raises:
            OSError: If directory cannot be created due to permissions or other OS issues
        """
        path = FileUtils.to_path(directory_path)

        # If path looks like a file path, get its directory
        if path.suffix:  # Has extension
            path = path.parent

        path.mkdir(parents=True, exist_ok=True)
        FileUtils._logger.debug("Created directory: %s", path)
        return path

    @staticmethod
    def get_file_size_kb(file_path: StrPath) -> int:
        """Get file size in kilobytes (KB).

        Args:
            file_path: Path to file

        Returns:
            int: File size in kilobytes (KB)

        Raises:
            FileNotFoundError: If file does not exist
            OSError: If file size cannot be determined
        """
        path = FileUtils.to_path(file_path)
        return round(path.stat().st_size / FileUtils.KB)

    @staticmethod
    def save_file(response, file_path: StrPath) -> int:
        """Save content from response to file.

        Downloads file content in chunks to minimize memory usage.

        Args:
            response: requests.Response object with file content
            file_path: Path where the file will be saved

        Returns:
            int: Size of saved file in kilobytes (KBs)

        Raises:
            IOError: If file cannot be written
            ValueError: If response content-length header is invalid
        """
        path = FileUtils.to_path(file_path)
        FileUtils.create_directory(path.parent)

        bytes_written = 0
        with path.open("wb") as output_file:
            for chunk in response.iter_content(chunk_size=FileUtils.CHUNK_SIZE):
                bytes_written += len(chunk)
                output_file.write(chunk)

        file_size = FileUtils.get_file_size_kb(path)
        FileUtils._logger.debug("Saved file: %s (%d KB)", path, file_size)
        return file_size

    @staticmethod
    def read_lines_from_file(
        file_path: StrPath, skip_comments: bool = True
    ) -> List[str]:
        """Read non-empty lines from a file.

        Args:
            file_path: Path to file
            skip_comments: If True, skip lines starting with COMMENT_CHAR

        Returns:
            List[str]: List of non-empty, non-comment lines with whitespace stripped

        Raises:
            FileNotFoundError: If file does not exist
            OSError: If file cannot be read due to permissions
        """
        path = FileUtils.to_path(file_path)
        if not path.exists():
            message = f"File not found: {path}"
            FileUtils._logger.error(message)
            raise FileNotFoundError(message)

        lines = []
        with path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()
                if not stripped:
                    continue
                if skip_comments and stripped.startswith(FileUtils.COMMENT_CHAR):
                    continue
                lines.append(stripped)

        FileUtils._logger.debug("Read %d lines from %s", len(lines), path)
        return lines

    @staticmethod
    def to_file_path(directory_path: StrPath, file_stem: str, file_suffix: str) -> Path:
        """Get full file path with safe filename conversion.

        Args:
            directory_path: Path to directory
            file_stem: Name part of the file without extension (e.g. "document" from "document.pdf")
            file_suffix: File extension without dot (e.g. "pdf" not ".pdf")

        Returns:
            Path: Full normalized path with safe filename

        Example:
            >>> FileUtils.to_file_path("downloads", "10.1002/smj.123", "pdf")
            PosixPath('downloads/10.1002-smj-123.pdf')
        """
        directory = FileUtils.to_path(directory_path)
        file_name = FileUtils.to_safe_filename(file_stem, file_suffix)

        return directory / file_name
