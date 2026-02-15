from fastmcp import FastMCP
from tools import search_schemes

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


if __name__ == "__main__":
    # stdio transport allows this to be run as subprocess
    mcp.run(transport="stdio")
