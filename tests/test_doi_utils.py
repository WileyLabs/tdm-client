"""Tests for DOI validation and processing utilities."""

# Standard library imports
from unittest.mock import patch

# Third-party imports
import requests

# Local imports
from wiley_tdm.doi_utils import DOIUtils

# Test constants
OA_DOI = "10.1111/modl.12927"
OA_DOIS = ["10.1111/modl.12927", "10.1155/2023/9786090"]
PAYWALLED_DOI = "10.1112/mtk.70009"
NOT_DOI = "not-a-doi"


def test_valid():
    """Test successful DOI validation."""
    assert DOIUtils.is_valid(OA_DOI) is True


def test_invalid():
    """Test validation with invalid DOI format."""
    assert DOIUtils.is_valid(NOT_DOI) is False


def test_valid_on_fail():
    """Test successful DOI validation on error."""
    # Simulate a failed request by mocking the requests library

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Connection error")
        assert DOIUtils.is_valid(OA_DOI) is True


def test_dedupe():
    """Test DOI filtering and deduplication."""
    dois = [
        None,
        "",
        "   ",
        OA_DOI,
        OA_DOI,  # Duplicate
        f"  {OA_DOI}  ",  # Same DOI with whitespace
        PAYWALLED_DOI,
    ]

    filtered_dois = DOIUtils.dedupe(dois)

    assert len(filtered_dois) == 2
    assert filtered_dois[0] == OA_DOI
    assert filtered_dois[1] == PAYWALLED_DOI


def test_dedupe_empty_list():
    """Test filtering empty DOI list."""
    assert len(DOIUtils.dedupe([])) == 0


def test_dedupe_all_invalid():
    """Test filtering list with only invalid DOIs."""
    dois = [None, "", "   "]
    assert len(DOIUtils.dedupe(dois)) == 0
