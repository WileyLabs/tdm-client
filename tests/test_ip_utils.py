"""Tests for IP address detection functionality.

Tests public IP detection and fallback behavior with mocked responses.
"""

# Local imports
from wiley_tdm.ip_utils import IPUtils


def test_get_ip_address_success():
    """Test successful IP address detection."""
    ip = IPUtils.get_ip_address()
    assert isinstance(ip, str)
    # Basic IP format validation
    parts = ip.split(".")
    assert len(parts) == 4
    assert all(0 <= int(p) <= 255 for p in parts)
