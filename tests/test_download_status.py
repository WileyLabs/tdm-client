"""Tests for DownloadStatus and related DownloadResult."""

# Local imports
from wiley_tdm import DownloadResult, DownloadStatus


def test_download_status_str():
    """Test string representation of DownloadStatus."""

    expected_str = "Network Error"
    status = DownloadStatus.NETWORK_ERROR
    result = DownloadResult(doi="10.1002/test", status=status)

    assert str(status) == expected_str
    assert str(result) == expected_str
