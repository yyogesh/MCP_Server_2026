"""The TripMate MCP server.

Never print to stdout in this package: over the stdio transport, stdout
carries the MCP protocol messages. Log to stderr instead.
"""

from mcp.server import MCPServer

from tripmate.tools.time_tools import local_time, trip_days

mcp = MCPServer(
    "tripmate",
    instructions=(
        "TripMate helps plan trips by telling you the current local time at a "
        "destination and how many days a trip lasts."
    ),
)

mcp.add_tool(local_time)
mcp.add_tool(trip_days)
