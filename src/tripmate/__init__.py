def main() -> None:
    """Run the TripMate MCP server over stdio."""
    from tripmate.app import mcp

    mcp.run()
