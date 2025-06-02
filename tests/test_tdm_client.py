"""Tests for TDM client functionality.

Tests PDF downloads, error handling, and file management with mocked API responses.
Requires TDM_API_TOKEN environment variable for authentication tests.
"""

# Standard library imports
import os
import shutil
import time
from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import quote

# Third-party imports
import pytest
import requests

# Local imports
from wiley_tdm import DownloadResult, DownloadStatus, TDMClient

# Test constants
INVALID_TOKEN = "not-a-uuid"
DOIS_FILE = Path("tests") / "dois.txt"  # Test DOIs file
DOIS_FILE_COUNT = 2  # Number of DOIs in test file
NOT_DOI = "not-a-doi;"
SEMICOLON_DOI = "10.1175/1520-0485(1986)016<1929:CTWOTE>2.0.CO;2"
OA_DOI = "10.1111/modl.12927"
OA_DOIS = ["10.1111/modl.12927", "10.1155/2023/9786090"]
PAYWALLED_DOI = "10.1112/mtk.70009"
NON_WILEY_DOI = "10.1007/978-3-540-49535-2_14"
TEST_TOKEN = os.getenv("TDM_API_TOKEN")


# Test fixture for TDMClient instance
@pytest.fixture(name="tdm")
def tdm_fixture(tmp_path):
    """Create a TDMClient instance for testing.

    Uses temporary directory for downloads and reads token from TDM_API_TOKEN env var.
    """
    return TDMClient(download_dir=tmp_path / "downloads")


def test_env_tdm_token():
    """Test reading TDM_API_TOKEN from environment variable."""
    token = os.environ.get("TDM_API_TOKEN")
    assert token is not None
    assert len(token) > 0


def test_no_tdm_token(monkeypatch, tmp_path):
    """Test that ValueError is raised when token is not provided and not in environment."""
    # Clear the environment variable if it exists
    monkeypatch.delenv(TDMClient.API_TOKEN_ENV, raising=False)

    with pytest.raises(ValueError) as exc_info:
        TDMClient(download_dir=tmp_path / "downloads")  # No token provided either

    assert (
        str(exc_info.value) == f"{TDMClient.API_TOKEN_ENV} environment variable not set"
    )


def test_invalid_tdm_token(tmp_path):
    """Test that invalid UUID tokens are rejected."""
    with pytest.raises(ValueError, match="Invalid TDM API token format"):
        TDMClient(download_dir=tmp_path / "downloads", api_token=INVALID_TOKEN)


def test_rate_limit_minimum(tdm):
    """Test that the minimum rate limit is enforced."""
    message = f"Rate limit is below default: {TDMClient.API_RATE_LIMIT} seconds"
    with pytest.raises(ValueError, match=message):
        tdm.api_rate_limit = TDMClient.API_RATE_LIMIT - 1


def assert_successful_download(result: DownloadResult, doi: str):
    """Helper function to validate successful download results.

    Args:
        result: Download result to validate
        doi: Expected DOI
    """
    assert isinstance(result, DownloadResult)
    assert result.status == DownloadStatus.SUCCESS
    assert result.doi == doi
    assert result.path is not None
    assert result.size is not None and result.size > 0
    assert result.duration is not None and result.duration > 0


def test_single_download(tdm):
    """Test single PDF download."""
    result = tdm.download_pdf(OA_DOI)
    assert_successful_download(result, OA_DOI)


def test_multiple_downloads(tdm):
    """Test multiple PDF downloads."""
    results = tdm.download_pdfs(OA_DOIS)
    assert len(results) == len(OA_DOIS)
    assert len(tdm.results) == len(results)

    for result in results:
        assert_successful_download(result, result.doi)


def test_multiple_downloads_from_file(tdm):
    """Test multiple PDF downloads from file."""

    results = tdm.download_pdfs(DOIS_FILE)
    assert len(results) == DOIS_FILE_COUNT
    assert len(tdm.results) == len(results)

    for result in results:
        assert_successful_download(result, result.doi)


def test_save_results(tdm, tmp_path):
    """Test saving download results to CSV file."""
    # First generate some download results
    result = tdm.download_pdf(OA_DOI)
    assert_successful_download(result, OA_DOI)

    # Save results to temporary CSV file
    csv_path = tmp_path / "results.csv"
    tdm.save_results(str(csv_path))

    # Verify file exists and contains data
    assert csv_path.exists()
    content = csv_path.read_text()
    assert OA_DOI in content


def test_download_callback(tdm):
    """Test download callback functionality."""
    mock_callback = Mock()

    # Mock download_pdf to return success without actual downloads
    with patch.object(tdm, "download_pdf") as mock_download:
        mock_download.side_effect = [
            DownloadResult(OA_DOIS[0], DownloadStatus.SUCCESS),
            DownloadResult(OA_DOIS[1], DownloadStatus.SUCCESS),
        ]

        # Execute
        results = tdm.download_pdfs(OA_DOIS, on_result=mock_callback)

        # Verify
        assert len(results) == len(OA_DOIS)
        assert mock_callback.call_count == len(OA_DOIS)


def test_pre_url_encoded(tdm):
    """Test pre URL encoded download scenario, to ensure not double encoding"""
    encoded_doi = quote(OA_DOI)
    result = tdm.download_pdf(encoded_doi)
    assert_successful_download(result, OA_DOI)


@pytest.mark.parametrize("invalid_doi", ["", None, "   "])
def test_blank_doi(tdm, invalid_doi):
    """Test blank DOI scenario."""
    with pytest.raises(ValueError, match="DOI cannot be None or empty"):
        tdm.download_pdf(invalid_doi)


def test_invalid_doi(tdm):
    """Test invalid DOI format."""
    result = tdm.download_pdf(NOT_DOI)

    assert result.status == DownloadStatus.INVALID_DOI
    assert result.path is None
    assert result.size is None


def test_non_wiley_doi(tdm):
    """Test attempting to download a non-Wiley DOI."""
    result = tdm.download_pdf(NON_WILEY_DOI)

    assert result.status == DownloadStatus.UNKNOWN_DOI
    assert result.path is None
    assert result.size is None


def test_semicolon_issue(tdm):
    """Test known limitation with semicolons in DOIs."""
    result = tdm.download_pdf(SEMICOLON_DOI)

    assert result.status == DownloadStatus.KNOWN_ISSUE
    assert result.path is None
    assert result.size is None
    assert result.api_status is HTTPStatus.NOT_FOUND


def test_unauthorized_access(tdm):
    """Test unauthorized IP address scenario."""

    result = tdm.download_pdf(PAYWALLED_DOI)
    assert result.status == DownloadStatus.ACCESS_DENIED
    assert result.path is None
    assert result.size is None


def test_skip_existing_files(tdm):
    """Test skip existing files functionality."""
    # First download
    result1 = tdm.download_pdf(OA_DOI)
    assert_successful_download(result1, OA_DOI)

    # Download same file again
    tdm.skip_existing_files = True
    result2 = tdm.download_pdf(OA_DOI)
    assert result2.status == DownloadStatus.EXISTING_FILE
    assert result2.path is not None
    assert result2.path == result1.path


@patch("requests.Session.get")
def test_network_error(mock_get, tdm):
    """Test handling of network errors."""
    mock_get.side_effect = requests.RequestException("Network error")
    result = tdm.download_pdf(OA_DOI)

    assert result.status == DownloadStatus.NETWORK_ERROR
    assert result.path is None
    assert result.size is None


@patch("pathlib.Path.open")
def test_storage_error(mock_path_open, tdm):
    """Test handling of file system errors."""
    # Simulate permission error when trying to open file
    mock_path_open.side_effect = IOError("Permission denied")

    # Attempt download which should trigger storage error
    result = tdm.download_pdf(OA_DOI)

    # Verify error handling
    assert result.status == DownloadStatus.STORAGE_ERROR
    assert result.path is not None
    assert result.size is None
    assert "Permission denied" in result.comment


def test_api_error(tdm):
    """Test handling of API errors."""

    # Setup mock response
    mock_response = Mock()
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    mock_response.status_code = status_code
    result = tdm._handle_api_error(OA_DOI, status_code, mock_response)

    # Verify results
    assert result.status == DownloadStatus.API_ERROR
    assert result.doi == OA_DOI
    assert result.path is None
    assert result.size is None
    assert result.api_status == status_code


def test_empty_doi_list(tdm):
    """Test handling of empty DOI list."""
    with pytest.raises(ValueError, match="DOIs list cannot be empty"):
        tdm.download_pdfs([])


def test_empty_dois_file(tdm, tmp_path):
    """Test handling of empty DOIs file."""
    # Create an empty file
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")

    # Test empty file
    with pytest.raises(ValueError, match="DOIs list cannot be empty"):
        tdm.download_pdfs(empty_file)


def test_duplicate_dois(tdm):
    """Test handling of duplicate DOIs in list."""
    dois = [OA_DOI, OA_DOI]  # Same DOI twice
    results = tdm.download_pdfs(dois)

    assert len(results) == 1  # Should deduplicate
    assert_successful_download(results[0], OA_DOI)


def test_invalid_dois_file(tdm):
    """Test handling of non-existent DOIs file."""
    with pytest.raises(FileNotFoundError):
        tdm.download_pdfs("nonexistent/file.txt")


@pytest.fixture(autouse=True)
def pause_between_tests():
    """Pause between tests to avoid rate limiting issues."""
    time.sleep(TDMClient.API_RATE_LIMIT)


def cleanup():
    """Clean up test files after each test."""
    yield
    if os.path.exists("tests/downloads"):
        shutil.rmtree("tests/downloads")
