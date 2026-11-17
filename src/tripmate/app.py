"""The TripMate MCP server.

Never print to stdout in this package: over the stdio transport, stdout
carries the MCP protocol messages. Log to stderr instead.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from tripmate.clients import AppContext
from tripmate.config import settings
from tripmate.tools.currency_tools import convert_currency, list_currencies
from tripmate.tools.time_tools import days_until_trip, local_time, trip_days
from tripmate.tools.trip_tools import create_trip, delete_trip, get_trip, list_trips
from tripmate.tools.weather_tools import get_forecast


@asynccontextmanager
async def lifespan(_server: MCPServer[AppContext]) -> AsyncIterator[AppContext]:
    """Create one shared HTTP client at startup and close it at shutdown."""
    async with httpx.AsyncClient(
        timeout=settings.http_timeout,
        headers={"User-Agent": "TripMate/0.1"},
    ) as http:
        yield AppContext(http=http)


mcp = MCPServer(
    "tripmate",
    instructions=(
        "TripMate helps plan trips. It can save trips (name, destination city, "
        "start and end dates, notes), list them, look one up by id, and delete "
        "one. It can also tell you the current local time at a destination, "
        "how many days a trip lasts, and how many days are left until a trip "
        "starts, and give the daily weather forecast for a city for the next "
        "1 to 7 days, and convert money between currencies at the latest "
        "exchange rate. Use list_currencies to see which currencies are "
        "supported and find their codes. Use list_trips to find a trip's id. Dates are YYYY-MM-DD."
    ),
    lifespan=lifespan,
)

mcp.add_tool(local_time)
mcp.add_tool(trip_days)
mcp.add_tool(days_until_trip)

mcp.add_tool(
    create_trip,
    title="Create trip",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
)
mcp.add_tool(
    list_trips,
    title="List trips",
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
mcp.add_tool(
    get_trip,
    title="Get trip",
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
mcp.add_tool(
    delete_trip,
    title="Delete trip",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=True,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
mcp.add_tool(
    get_forecast,
    title="Get weather forecast",
    annotations=ToolAnnotations(
        read_only_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    ),
)
mcp.add_tool(
    convert_currency,
    title="Convert currency",
    annotations=ToolAnnotations(
        read_only_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    ),
)
mcp.add_tool(
    list_currencies,
    title="List currencies",
    annotations=ToolAnnotations(
        read_only_hint=True,
        idempotent_hint=True,
        open_world_hint=True,
    ),
)
