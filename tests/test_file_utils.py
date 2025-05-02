"""Tests for file system operations.

"""

# Standard library imports
import os
from unittest.mock import Mock, patch

# Third-party imports
import pytest

# Local imports
from tdmclient.file_utils import FileUtils

# Test constants
TEST_DIR = "test_dir"
TEST_FILE = "test_file.txt"
TEST_CONTENT = "line1\n#comment\nline2\n\n  line3  \n"

@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test files after each test."""
    yield
    if os.path.exists(TEST_DIR):
        os.rmdir(TEST_DIR)
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_ensure_directory():
    """Test directory creation."""
    FileUtils.ensure_directory(TEST_DIR)
    assert os.path.exists(TEST_DIR)
    assert os.path.isdir(TEST_DIR)

def test_get_file_size_kb():
    """Test file size calculation."""
    content = "x" * FileUtils.KB
    with open(TEST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    size = FileUtils.get_file_size_kb(TEST_FILE)
    assert size == 1

def test_save_file():
    """Test saving file from response."""
    mock_response = Mock()
    mock_response.headers = {'content-length': '1024'}
    mock_response.iter_content.return_value = [b"x" * 512, b"x" * 512]

    size = FileUtils.save_file(mock_response, TEST_FILE)

    assert os.path.exists(TEST_FILE)
    assert size == 1  # 1KB
    mock_response.iter_content.assert_called_once_with(chunk_size=FileUtils.CHUNK_SIZE)

def test_save_file_no_content_length():
    """Test saving file without content-length header."""
    mock_response = Mock()
    mock_response.headers = {}
    mock_response.iter_content.return_value = [b"data"]

    FileUtils.save_file(mock_response, TEST_FILE)

    assert os.path.exists(TEST_FILE)

def test_read_lines_from_file():
    """Test reading lines from file."""
    with open(TEST_FILE, 'w', encoding='utf-8') as f:
        f.write(TEST_CONTENT)

    lines = FileUtils.read_lines_from_file(TEST_FILE)

    assert len(lines) == 3
    assert lines == ["line1", "line2", "line3"]

def test_read_lines_with_comments():
    """Test reading lines including comments."""
    with open(TEST_FILE, 'w', encoding='utf-8') as f:
        f.write(TEST_CONTENT)

    lines = FileUtils.read_lines_from_file(TEST_FILE, skip_comments=False)

    assert len(lines) == 4
    assert "#comment" in lines

def test_read_lines_nonexistent():
    """Test reading from non-existent file."""
    with pytest.raises(FileNotFoundError):
        FileUtils.read_lines_from_file("nonexistent.txt")

@patch('builtins.open')
def test_read_lines_permission_error(mock_open):
    """Test file read permission error."""
    mock_open.side_effect = OSError("Permission denied")
    with pytest.raises(OSError):
        FileUtils.read_lines_from_file(TEST_FILE)

def test_make_safe_filename():
    """Test conversion of unsafe filenames."""
    unsafe_names = [
        ("10.1002/smj:123", "10.1002-smj-123"),
        ("file*with?wildcards", "file-with-wildcards"),
        ("name with spaces", "name-with-spaces"),
        ('quotes"and\'chars', "quotes-and-chars"),
        ("line\nbreaks\r\there", "line-breaks-here"),
    ]

    for unsafe, expected in unsafe_names:
        assert FileUtils.make_safe_filename(unsafe) == expected
