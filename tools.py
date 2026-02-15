# mcp_server/tools.py

import requests
from typing import List, Dict

BASE_URL = "https://api.mfapi.in/mf"


class MFAPIError(Exception):
    pass


def search_schemes(scheme_name: str) -> List[Dict]:
    """
    Search mutual fund schemes by name.

    Args:
        scheme_name (str): Partial or full scheme name

    Returns:
        List[Dict]: List of matching schemes with schemeCode and schemeName
    """
    try:
        response = requests.get(
            f"{BASE_URL}/search",
            params={"q": scheme_name},
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise MFAPIError("Unexpected response format from MF API")

        return data

    except requests.RequestException as e:
        raise MFAPIError(f"MF API request failed: {str(e)}")
