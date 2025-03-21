import socket
import pytest
from unittest.mock import patch

import requests
from tdmclient.ip_utils import IPUtils

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