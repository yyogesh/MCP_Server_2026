"""The TripMate MCP server.

Never print to stdout in this package: over the stdio transport, stdout
carries the MCP protocol messages. Log to stderr instead.
"""

from mcp.server import MCPServer

from tripmate.tools.time_tools import days_until_trip, local_time, trip_days

mcp = MCPServer(
    "tripmate",
    instructions=(
        "TripMate helps plan trips by telling you the current local time at a "
        "destination, how many days a trip lasts, and how many days are left "
        "until a trip starts."
    ),
)

mcp.add_tool(local_time)
mcp.add_tool(trip_days)
mcp.add_tool(days_until_trip)
