import logging
from typing import Final, List

import requests

class IPUtils:
    """Utility class for IP address detection using public IP APIs."""
    
    # IP Configuration
    DEFAULT_IP: Final[str] = "127.0.0.1"
    IP_APIS: Final[List[str]] = [
        "https://api.ipify.org",
        "https://api.my-ip.io/ip",
        "https://checkip.amazonaws.com"
    ]

    # Request Configuration
    REQUEST_TIMEOUT: Final[int] = 5  # seconds

    @staticmethod
    def get_ip_address() -> str:
        """Get the public IP address by trying multiple API endpoints.
        
        Returns:
            str: Public IP address or DEFAULT_IP if all attempts fail
        """
        logger = logging.getLogger(__name__)

        for api_url in IPUtils.IP_APIS:
            try:
                response = requests.get(api_url, timeout=IPUtils.REQUEST_TIMEOUT)
                if response.status_code == 200:
                    return response.text.strip()
            except requests.RequestException as e:
                logger.warning(f"IP detection failed for {api_url}: {e}")
                continue

        logger.error("All IP detection attempts failed")
        return IPUtils.DEFAULT_IP