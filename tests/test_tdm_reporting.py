import csv
import pytest
from http import HTTPStatus
from dataclasses import dataclass
from datetime import datetime

from tdmclient import (
    TDMClient,
    DownloadResult,
    DownloadStatus,
    TDMReporting
)

# Test constants
TEST_DOI_1 = "10.1002/test1"
TEST_DOI_2 = "10.1002/test2"
TEST_FILE = "article.pdf"
TEST_SIZE = 12345

@pytest.fixture
def sample_results():
    """Create sample DownloadResult objects for testing."""
    return [
        DownloadResult(
            doi=TEST_DOI_1,
            status=DownloadStatus.SUCCESS,
            comment="Successfully downloaded",
            path=TEST_FILE,
            size=TEST_SIZE,
            duration=1.23,
            api_status=HTTPStatus.OK
        ),
        DownloadResult(
            doi=TEST_DOI_2,
            status=DownloadStatus.FORBIDDEN,
            comment="Access denied",
            api_status=HTTPStatus.FORBIDDEN
        )
    ]

def test_save_download_results(tmp_path, sample_results):
    """Test saving results to CSV with all fields."""
    # Arrange
    csv_path = tmp_path / "results.csv"
    
    # Act
    TDMReporting.save_download_results(sample_results, str(csv_path))
    
    # Assert
    assert csv_path.exists()
    
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        
        assert len(rows) == 2
        
        # Check successful download row
        success_row = rows[0]
        assert success_row['DOI'] == TEST_DOI_1
        assert success_row['Status'] == 'SUCCESS'
        assert success_row['Comment'] == 'Successfully downloaded'
        assert success_row['Path'] == TEST_FILE
        assert success_row['Size (KB)'] == str(TEST_SIZE)
        assert success_row['Duration (s)'] == '1.2'
        assert success_row['HTTP Status'] == str(HTTPStatus.OK.value)
        
        # Check forbidden access row
        error_row = rows[1]
        assert error_row['DOI'] == TEST_DOI_2
        assert error_row['Status'] == 'FORBIDDEN'
        assert error_row['Comment'] == 'Access denied'
        assert error_row['Path'] == ''
        assert error_row['Size (KB)'] == ''
        assert error_row['Duration (s)'] == ''
        assert error_row['HTTP Status'] == str(HTTPStatus.FORBIDDEN.value)

def test_save_empty_results(tmp_path):
    """Test handling of empty results list."""
    # Arrange
    csv_path = tmp_path / "empty.csv"
    
    # Act
    TDMReporting.save_download_results([], str(csv_path))
    
    # Assert
    assert not csv_path.exists()

def test_save_results_creates_directories(tmp_path, sample_results):
    """Test creation of nested directories."""
    # Arrange
    nested_path = tmp_path / "reports" / "nested" / "results.csv"
    
    # Act
    TDMReporting.save_download_results(sample_results, str(nested_path))
    
    # Assert
    assert nested_path.exists()
    assert nested_path.parent.is_dir()

@pytest.fixture(autouse=True)
def cleanup(tmp_path):
    """Clean up test files after each test."""
    yield
    import shutil
    if tmp_path.exists():
        shutil.rmtree(tmp_path)