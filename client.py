"""Small MCP client that exercises the TripMate server over stdio."""

import asyncio
import os

from mcp import Client, StdioServerParameters

# The server process only inherits a few safe env vars, so pass TRIPMATE_DB
# through explicitly when it is set (e.g. to use a temporary database).
_ENV = {"TRIPMATE_DB": os.environ["TRIPMATE_DB"]} if "TRIPMATE_DB" in os.environ else None
SERVER = StdioServerParameters(command="uv", args=["run", "tripmate"], env=_ENV)


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

        # 5. List the resources and resource templates (URI and name).
        resources = await client.list_resources()
        for res in resources.resources:
            print(f"resource: {res.uri} ({res.name})")
        templates = await client.list_resource_templates()
        for tmpl in templates.resource_templates:
            print(f"template: {tmpl.uri_template} ({tmpl.name})")

        # 6. Read trip://trips and print its JSON text.
        contents = await client.read_resource("trip://trips")
        print(contents.contents[0].text)

        # 7. List the prompts with their argument names.
        prompts = await client.list_prompts()
        for prompt in prompts.prompts:
            arg_names = ", ".join(arg.name for arg in prompt.arguments or [])
            print(f"prompt: {prompt.name}({arg_names})")

        # 8. Get the plan_trip prompt for Tokyo and print the message text.
        plan = await client.get_prompt(
            "plan_trip",
            {"destination": "Tokyo", "start_date": "2026-12-20", "end_date": "2026-12-24"},
        )
        print(plan.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
