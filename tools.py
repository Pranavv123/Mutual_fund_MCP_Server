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
    

def fetch_latest_nav(scheme_code: str) -> Dict:
    """
    Fetch the latest NAV of a mutual fund scheme.
    Args:
        scheme_code (str): Unique scheme code of the mutual fund

    Returns:
        Dict: Latest NAV details containing nav and date
    """
    try:
        response = requests.get(
            f"{BASE_URL}/{scheme_code}/latest",
            timeout=10,
        )
        

        response.raise_for_status()

        data = response.json()
        print(data)

        if not isinstance(data, dict):
            raise MFAPIError("Unexpected response format from MF API")

        # Basic validation
        #if "nav" not in data or "date" not in data:
            #raise MFAPIError("Missing expected NAV fields in MF API response")

        return data

    except requests.RequestException as e:
        raise MFAPIError(f"MF API request failed: {str(e)}")