"""Tests for IP address detection functionality.

Tests public IP detection and fallback behavior with mocked responses.
"""

# Standard library imports
import socket
from unittest.mock import patch

# Third-party imports
import requests

# Local imports
from wiley_tdm.ip_utils import IPUtils

def test_get_ip_address_success():
    """Test successful IP address detection."""
    ip = IPUtils.get_ip_address()
    assert isinstance(ip, str)
    # Basic IP format validation
    parts = ip.split('.')
    assert len(parts) == 4
    assert all(0 <= int(p) <= 255 for p in parts)

def test_get_ip_address_fallback():
    """Test fallback to DEFAULT_IP when detection fails."""
    with patch('requests.get', side_effect=requests.RequestException):
        with patch('socket.gethostbyname', side_effect=socket.error):
            ip = IPUtils.get_ip_address()
            assert ip == IPUtils.DEFAULT_IP
