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
            params={"q":scheme_name},
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

        if not isinstance(data, dict):
            raise MFAPIError("Unexpected response format from MF API")

        # Basic validation
        #if "nav" not in data or "date" not in data:
            #raise MFAPIError("Missing expected NAV fields in MF API response")

        return data

    except requests.RequestException as e:
        raise MFAPIError(f"MF API request failed: {str(e)}")
    

from typing import List, Dict
import requests


def fetch_nav_history(scheme_code: str) -> Dict:
    """
    Fetch full historical NAV data for a mutual fund scheme.

    Args:
        scheme_code (str): Mutual fund scheme code

    Returns:
        Dict: Full API response containing meta and data
    """
    try:
        response = requests.get(
            f"{BASE_URL}/{scheme_code}",
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict) or "data" not in data:
            raise MFAPIError("Unexpected response format from MF API")

        return data

    except requests.RequestException as e:
        raise MFAPIError(f"MF API request failed: {str(e)}")
    
from datetime import datetime


def normalize_nav_data(raw_data: List[Dict]) -> List[Dict]:
    """
    Normalize NAV data:
    - Convert NAV to float
    - Convert date to ISO format (YYYY-MM-DD)
    """

    normalized = []

    for entry in raw_data:
        normalized.append({
            "date": datetime.strptime(entry["date"], "%d-%m-%Y").strftime("%Y-%m-%d"),
            "nav": float(entry["nav"])
        })

    return normalized

def compress_nav_history(nav_data: List[Dict]) -> List[Dict]:
    """
    Compress NAV history dynamically to preserve trend
    while reducing token size.
    """

    total_points = len(nav_data)

    if total_points <= 365:
        return nav_data

    if total_points <= 5 * 365:
        step = 7      # Weekly
    elif total_points <= 10 * 365:
        step = 30     # Monthly
    else:
        step = 90     # Quarterly

    compressed = [nav_data[i] for i in range(0, total_points, step)]

    # Always include oldest point
    if compressed[-1] != nav_data[-1]:
        compressed.append(nav_data[-1])

    return compressed

def generate_nav_summary(nav_data: List[Dict]) -> Dict:
    latest = nav_data[0]
    oldest = nav_data[-1]

    latest_nav = latest["nav"]
    start_nav = oldest["nav"]

    absolute_return = ((latest_nav - start_nav) / start_nav) * 100

    return {
        "start_date": oldest["date"],
        "latest_date": latest["date"],
        "start_nav": round(start_nav, 2),
        "latest_nav": round(latest_nav, 2),
        "absolute_return_percent": round(absolute_return, 2),
        "total_days": len(nav_data),
    }
