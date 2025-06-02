"""Tests for download result reporting functionality.

Tests CSV report generation with sample download results,
including success and error cases.
"""

# Standard library imports
import csv
from http import HTTPStatus
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from wiley_tdm import DownloadResult, DownloadStatus, TDMReporting

# Test constants
TEST_DIR = Path("reports")
TEST_CSV = TEST_DIR / "results.csv"

TEST_DOI_1 = "10.1002/test1"
TEST_DOI_2 = "10.1002/test2"
TEST_PDF = Path("article.pdf")
TEST_SIZE = 12345


@pytest.fixture(name="results")
def results_fixture():
    """Create sample DownloadResult objects for testing."""
    return [
        DownloadResult(
            doi=TEST_DOI_1,
            status=DownloadStatus.SUCCESS,
            comment="Successfully downloaded",
            path=TEST_PDF,
            size=TEST_SIZE,
            duration=1.23,
            api_status=HTTPStatus.OK,
        ),
        DownloadResult(
            doi=TEST_DOI_2,
            status=DownloadStatus.ACCESS_DENIED,
            comment="Access denied",
            api_status=HTTPStatus.FORBIDDEN,
        ),
    ]


def test_save_results(tmp_path, results):
    """Test saving results to CSV with all fields."""

    csv_path = tmp_path / TEST_CSV

    TDMReporting.save_results(results, csv_path)

    assert csv_path.exists()

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

        assert len(rows) == 2

        # Check successful download row
        success_row = rows[0]
        assert success_row["DOI"] == TEST_DOI_1
        assert success_row["Status"] == str(DownloadStatus.SUCCESS)
        assert success_row["Comment"] == "Successfully downloaded"
        assert success_row["Path"] == str(TEST_PDF)
        assert success_row["Size (KB)"] == str(TEST_SIZE)
        assert success_row["Duration (s)"] == "1.2"
        assert success_row["HTTP Status"] == str(HTTPStatus.OK.value)

        # Check forbidden access row
        error_row = rows[1]
        assert error_row["DOI"] == TEST_DOI_2
        assert error_row["Status"] == str(DownloadStatus.ACCESS_DENIED)
        assert error_row["Comment"] == "Access denied"
        assert error_row["Path"] == ""
        assert error_row["Size (KB)"] == ""
        assert error_row["Duration (s)"] == ""
        assert error_row["HTTP Status"] == str(HTTPStatus.FORBIDDEN.value)


def test_save_empty_results(tmp_path):
    """Test handling of empty results list."""

    csv_path = tmp_path / TEST_CSV
    TDMReporting.save_results([], str(csv_path))

    assert not csv_path.exists()
