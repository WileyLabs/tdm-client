import pytest
from tdmclient.doi_utils import DOIUtils

# Test constants
OA_DOI = "10.1111/modl.12927"
OA_DOIS = ["10.1111/modl.12927", "10.1155/2023/9786090"] 
PAYWALLED_DOI = "10.1112/mtk.70009" 
NOT_DOI = "not-a-doi"

@pytest.fixture
def doi_utils():
    """Create DOIUtils instance for testing."""
    return DOIUtils()

def test_is_valid_success(doi_utils):
    """Test successful DOI validation."""
    assert doi_utils.is_valid(OA_DOI) is True

def test_is_valid_failure():
    """Test validation with invalid DOI format."""
    assert DOIUtils.is_valid(NOT_DOI) is False

def test_dedupe(doi_utils):
    """Test DOI filtering and deduplication."""
    dois = [
        None,
        "",
        "   ",
        OA_DOI,
        OA_DOI,  # Duplicate
        f"  {OA_DOI}  ",  # Same DOI with whitespace
        PAYWALLED_DOI
    ]
    
    filtered_dois = doi_utils.dedupe(dois)
    
    assert len(filtered_dois) == 2
    assert filtered_dois[0] == OA_DOI
    assert filtered_dois[1] == PAYWALLED_DOI

def test_dedupe_empty_list(doi_utils):
    """Test filtering empty DOI list."""
    assert len(doi_utils.dedupe([])) == 0

def test_dedupe_all_invalid(doi_utils):
    """Test filtering list with only invalid DOIs."""
    dois = [None, "", "   "]
    assert len(doi_utils.dedupe(dois)) == 0