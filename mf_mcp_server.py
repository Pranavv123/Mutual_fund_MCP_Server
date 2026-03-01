from fastmcp import FastMCP
from tools import (
    search_schemes, 
    fetch_latest_nav,
    fetch_nav_history, 
    normalize_nav_data, 
    generate_nav_summary,
    compress_nav_history
)

mcp = FastMCP(
    name="mutual-fund-mcp",
    version="0.1.0",
    #description="MCP Server for Mutual Fund data using mfapi.in",
)


@mcp.tool()
def search_schemes_tool(scheme_name: str) -> dict:
    """
    Search mutual fund schemes by name.

    Args:
        scheme_name: Partial or full scheme name (e.g., HDFC)

    Returns:
        JSON object containing matching schemes.
    """
    results = search_schemes(scheme_name)

    return {
        "count": len(results),
        "schemes": results,
    }

@mcp.tool()
def get_latest_nav(scheme_code: str) -> dict:
    """
    Get the latest NAV of a mutual fund scheme.

    Args:
        scheme_code: Unique scheme code of the mutual fund (e.g., 120503)

    Returns:
        JSON object containing the latest NAV details.

    Example:
    Query: what is the latest nav of SBI Contra Fund - Direct Plan - Income Distribution cum Capital Withdrawal Option (IDCW) mutual fund scheme?
    Args: scheme_code : 119724
    """

    result = fetch_latest_nav(scheme_code)

    return result


@mcp.tool()
def get_nav_history(scheme_code: str) -> dict:
    """
    Get compressed historical NAV for a mutual fund scheme.

    Args:
        scheme_code: Mutual fund scheme code

    Returns:
        JSON object containing summary and compressed trend data.
    """

    api_response = fetch_nav_history(scheme_code)

    raw_nav_data = api_response["data"]
    meta = api_response["meta"]

    normalized = normalize_nav_data(raw_nav_data)

    summary = generate_nav_summary(normalized)

    compressed = compress_nav_history(normalized)

    return {
        "scheme_code": scheme_code,
        "scheme_name": meta.get("scheme_name"),
        "fund_house": meta.get("fund_house"),
        "summary": summary,
        "total_points_original": len(normalized),
        "total_points_returned": len(compressed),
        "trend_data": compressed
    }

if __name__ == "__main__":
    # stdio transport allows this to be run as subprocess
    mcp.run(transport="stdio")