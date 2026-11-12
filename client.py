"""Small MCP client that exercises the TripMate server over stdio."""

import asyncio

from mcp import Client, StdioServerParameters

SERVER = StdioServerParameters(command="uv", args=["run", "tripmate"])


async def main() -> None:
    async with Client(SERVER) as client:
        # 1. List each tool with the first line of its description.
        tools = await client.list_tools()
        for tool in tools.tools:
            first_line = (tool.description or "").strip().splitlines()[0]
            print(f"{tool.name}: {first_line}")

        # 2. Ask for the current time in Tokyo and print the text result.
        result = await client.call_tool("local_time", {"timezone": "Asia/Tokyo"})
        print(result.content[0].text)

        # 3. Call trip_days with end before start; expect a tool error.
        result = await client.call_tool(
            "trip_days", {"start_date": "2026-12-10", "end_date": "2026-12-01"}
        )
        print(result.is_error, result.content[0].text)

        # 4. Days until a future trip, then a past date; expect a tool error.
        result = await client.call_tool("days_until_trip", {"start_date": "2099-01-01"})
        print(result.content[0].text)
        result = await client.call_tool("days_until_trip", {"start_date": "2000-01-01"})
        print(result.is_error, result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
