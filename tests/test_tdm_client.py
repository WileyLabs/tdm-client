# Standard library imports
import os
from unittest.mock import Mock, patch
from http import HTTPStatus

# Third-party imports
import pytest
import requests
import urllib

# Local imports
from tdmclient import (
    TDMClient,
    DownloadResult,
    DownloadStatus,
)
from tdmclient.doi_utils import DOIUtils  # Updated from DOIValidator

# Test constants
INVALID_TOKEN = "not-a-uuid"
DOIS_FILE = "tests/dois.txt"  # Test DOIs file
DOIS_FILE_COUNT = 2  # Number of DOIs in test file
NOT_DOI = "not-a-doi;"
SEMICOLON_DOI = "10.1175/1520-0485(1986)016<1929:CTWOTE>2.0.CO;2"
OA_DOI = "10.1111/modl.12927"
OA_DOIS = ["10.1111/modl.12927", "10.1155/2023/9786090"]
PAYWALLED_DOI = "10.1112/mtk.70009"
NON_WILEY_DOI = "10.1007/978-3-540-49535-2_14"

# Test fixture for TDMClient instance
@pytest.fixture
def tdm_client():
    """Create a TDMClient instance for testing."""
    client = TDMClient(download_dir="tests/downloads") # Use default settings. Reads from TDM_API_TOKEN env var
    return client

def test_invalid_tdm_token():
    """Test that invalid UUID tokens are rejected."""
    with pytest.raises(ValueError, match="Invalid TDM API token format"):
        TDMClient(tdm_token=INVALID_TOKEN)

# Test TDM_API_TOKEN environment variable
def test_api_token_env_var():
    """Test reading TDM_API_TOKEN from environment variable."""
    token = os.environ.get("TDM_API_TOKEN")
    assert token is not None
    assert len(token) > 0  

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
    assert result.size > 0
    assert result.duration > 0

# Test single PDF download scenario
def test_single_download(tdm_client):
    """Test single PDF download."""
    result = tdm_client.download_pdf(OA_DOI)
    assert_successful_download(result, OA_DOI)

# Test multiple PDF downloads scenario
def test_multiple_downloads(tdm_client):
    """Test multiple PDF downloads."""
    results = tdm_client.download_pdfs(OA_DOIS)
    assert len(results) == len(OA_DOIS)  
    assert len(tdm_client.download_results) == len(results)

    for result in results:
        assert_successful_download(result, result.doi)

# Test multiple PDF downloads from file scenario
def test_multiple_downloads_from_file(tdm_client):
    """Test multiple PDF downloads from file."""

    results = tdm_client.download_pdfs_from_file(DOIS_FILE)
    assert len(results) == DOIS_FILE_COUNT
    assert len(tdm_client.download_results) == len(results)
    
    for result in results:
        assert_successful_download(result, result.doi)

#Test that callback is called for each download.
def test_download_callback(tdm_client):
    mock_callback = Mock()
    
    # Mock download_pdf to return success without actual downloads
    with patch.object(tdm_client, 'download_pdf') as mock_download:
        mock_download.side_effect = [
            DownloadResult(OA_DOIS[0], DownloadStatus.SUCCESS),
            DownloadResult(OA_DOIS[1], DownloadStatus.SUCCESS)
        ]
        
        # Execute
        results = tdm_client.download_pdfs(OA_DOIS, on_result=mock_callback)
        
        # Verify
        assert len(results) == len(OA_DOIS)
        assert mock_callback.call_count == len(OA_DOIS)

# Test pre URL encoded download scenario
def test_pre_url_encoded(tdm_client):
    """Test successful pre URL encoded download. To ensure not double encoding"""
    encoded_doi = urllib.parse.quote(OA_DOI)
    result = tdm_client.download_pdf(encoded_doi)
    assert_successful_download(result, OA_DOI)

# Test invalid DOI
def test_invalid_doi(tdm_client):
    """Test validation of incorrect DOI format."""
    result = tdm_client.download_pdf(NOT_DOI)
    
    assert result.status == DownloadStatus.INVALID_DOI
    assert result.path is None
    assert result.size is None

# Test non-Wiley DOI
def test_non_wiley_doi(tdm_client):
    """Test attempting to download non-Wiley DOI."""
    result = tdm_client.download_pdf(NON_WILEY_DOI)
    
    assert result.status == DownloadStatus.UNKNOWN_DOI
    assert result.path is None
    assert result.size is None

# Test semicolon issue still exists (WIP)
def test_semicolon_issue(tdm_client):
    """Test known limitation with semicolons in DOIs."""
    result = tdm_client.download_pdf(SEMICOLON_DOI)
    
    assert result.status == DownloadStatus.KNOWN_ISSUE
    assert result.path is None
    assert result.size is None
    assert result.api_status is HTTPStatus.NOT_FOUND

# Test unauthorized access
def test_unauthorized_access(tdm_client):
    """Test unauthorized IP address scenario."""

    result = tdm_client.download_pdf(PAYWALLED_DOI)
    assert result.status == DownloadStatus.FORBIDDEN
    assert result.path is None
    assert result.size is None

# Test skip functionality
def test_skip_existing_files(tdm_client):
    """Test handling of existing PDF files."""
    # First download
    result1 = tdm_client.download_pdf(OA_DOI)
    assert_successful_download(result1, OA_DOI)

    # Download same file again
    tdm_client.skip_existing_files = True
    result2 = tdm_client.download_pdf(OA_DOI)
    assert result2.status == DownloadStatus.EXISTING_FILE
    assert result2.path is not None
    assert result2.path == result1.path

# Test Wiley API error
@patch('requests.Session.get')
def test_network_error(mock_get, tdm_client):
    """Test handling of network errors."""
    mock_get.side_effect = requests.RequestException("Network error")
    result = tdm_client.download_pdf(OA_DOI)
    
    assert result.status == DownloadStatus.NETWORK_ERROR
    assert result.path is None
    assert result.size is None

@patch('builtins.open')
def test_storage_error(mock_open, tdm_client):
    """Test handling of file system errors."""
    mock_open.side_effect = IOError("Permission denied")   
    result = tdm_client.download_pdf(OA_DOI)
    
    assert result.status == DownloadStatus.STORAGE_ERROR
    assert result.path is not None
    assert result.size is None

def test_empty_doi_list(tdm_client):
    """Test handling of empty DOI list."""
    results = tdm_client.download_pdfs([])
    assert len(results) == 0

def test_duplicate_dois(tdm_client):
    """Test handling of duplicate DOIs in list."""
    dois = [OA_DOI, OA_DOI]  # Same DOI twice
    results = tdm_client.download_pdfs(dois)
    
    assert len(results) == 1  # Should deduplicate
    assert_successful_download(results[0], OA_DOI)

def test_invalid_dois_file(tdm_client):
    """Test handling of non-existent DOIs file."""
    with pytest.raises(FileNotFoundError):
        tdm_client.download_pdfs_from_file("nonexistent/file.txt")

# Clean up test files after each test
@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test files after each test."""
    yield
    import shutil
    if os.path.exists("tests/downloads"):
        shutil.rmtree("tests/downloads")