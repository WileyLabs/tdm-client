"""Tests for file system operations."""

# Standard library imports
from pathlib import Path
from unittest.mock import Mock

# Third-party imports
import pytest

# Local imports
from wiley_tdm.file_utils import FileUtils

# Test constants
TEST_DIR = Path("test") / "dir"
TEST_FILE = Path("test.txt")
TEST_CONTENT = "line1\n#comment\nline2\n\n  line3  \n"


def test_create_directory_with_path(tmp_path):
    """Test directory creation with Path object."""
    path = tmp_path / TEST_DIR
    FileUtils.create_directory(path)
    assert path.exists()
    assert path.is_dir()


def test_create_directory_with_string(tmp_path):
    """Test directory creation with string path."""
    path = str(tmp_path / TEST_DIR)
    FileUtils.create_directory(path)
    assert Path(path).exists()
    assert Path(path).is_dir()


def test_get_file_size_kb(tmp_path):
    """Test file size calculation."""
    content = "x" * FileUtils.KB
    file_path = tmp_path / TEST_FILE
    FileUtils.create_directory(file_path)
    file_path.write_text(content, encoding="utf-8")
    size = FileUtils.get_file_size_kb(file_path)
    assert size == 1


def test_save_file(tmp_path):
    """Test saving file from response."""
    mock_response = Mock()
    mock_response.headers = {"content-length": "1024"}
    mock_response.iter_content.return_value = [b"x" * 512, b"x" * 512]

    file_path = tmp_path / TEST_FILE

    size = FileUtils.save_file(mock_response, file_path)

    assert file_path.exists()
    assert size == 1  # 1KB
    mock_response.iter_content.assert_called_once_with(chunk_size=FileUtils.CHUNK_SIZE)


def test_read_lines_from_file(tmp_path):
    """Test reading lines from file."""
    file_path = tmp_path / TEST_FILE
    file_path.write_text(TEST_CONTENT, encoding="utf-8")

    lines = FileUtils.read_lines_from_file(file_path)

    assert len(lines) == 3
    assert lines == ["line1", "line2", "line3"]


def test_read_lines_with_comments(tmp_path):
    """Test reading lines including comments."""
    file_path = tmp_path / TEST_FILE
    file_path.write_text(TEST_CONTENT, encoding="utf-8")

    lines = FileUtils.read_lines_from_file(file_path, skip_comments=False)

    assert len(lines) == 4
    assert "#comment" in lines


def test_read_lines_nonexistent():
    """Test reading from non-existent file."""
    nonexistent = Path("nonexistent.txt")
    with pytest.raises(FileNotFoundError):
        FileUtils.read_lines_from_file(nonexistent)


def test_to_file_path_with_string(tmp_path):
    """Test file path generation with string input."""
    path = FileUtils.to_file_path(str(tmp_path), "10.1002/smj.123", "pdf")
    assert isinstance(path, Path)
    assert path == tmp_path / "10.1002-smj.123.pdf"


def test_to_file_path_with_path(tmp_path):
    """Test file path generation with Path input."""
    path = FileUtils.to_file_path(tmp_path, "10.1002/smj.123", "pdf")
    assert isinstance(path, Path)
    assert path == tmp_path / "10.1002-smj.123.pdf"


def test_to_safe_filename():
    """Test conversion of unsafe filenames."""
    unsafe_names = [
        ("10.1002/smj:123", "10.1002-smj-123.pdf"),
        ("file*with?wildcards", "file-with-wildcards.pdf"),
        ("name with spaces", "name-with-spaces.pdf"),
        ("quotes\"and'chars", "quotes-and-chars.pdf"),
        ("line\nbreaks\nhere", "line-breaks-here.pdf"),
    ]

    for unsafe, expected in unsafe_names:
        assert FileUtils.to_safe_filename(unsafe, "pdf") == expected
