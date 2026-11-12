Create a new Python project called tripmate using uv with a src layout: run `uv init --package tripmate`. Then, inside it, add two dependencies: "mcp[cli]>=2.3" (the official MCP Python SDK, version 2) and tzdata. Do not write any server code yet. When done, show me the folder structure and the [project.scripts] section of pyproject.toml.



Create src/tripmate/tools/__init__.py (empty) and src/tripmate/tools/time_tools.py with two plain Python functions, with no MCP decorators:
1. local_time(timezone: str) -> str: the current local date and time in an IANA timezone such as "Asia/Tokyo".
2. trip_days(start_date: date, end_date: date) -> int: the number of days in a trip, counting the first and last day.
Write clear docstrings, because an AI model will read them to decide how to call these tools. Mention the input formats. For bad input (unknown timezone, end date before start date), raise ToolError from mcp.server.mcpserver.exceptions with a short, helpful message.



Now turn these functions into an MCP server. Use the MCP Python SDK version 2 API, not the old FastMCP one:
- Create src/tripmate/app.py. Import MCPServer with `from mcp.server import MCPServer`. Create `mcp = MCPServer("tripmate", instructions="...")` with a one-sentence instruction about what TripMate does. Register local_time and trip_days with mcp.add_tool().
- Replace main() in src/tripmate/__init__.py so it imports mcp from tripmate.app and calls mcp.run(), which uses the stdio transport.
- Never print to stdout anywhere, because stdout carries the MCP messages.
Then run `uv run tripmate` for 3 seconds with a timeout to check it starts without errors.


Create client.py in the project root: a small async MCP client using the MCP Python SDK v2 (`from mcp import Client, StdioServerParameters`). It should start our server with the command `uv run tripmate`, then:
1. print each tool name with the first line of its description,
2. call local_time for "Asia/Tokyo" and print the text result,
3. call trip_days with the end date before the start date, and print result.is_error and the error text.
Keep it short and add a comment above each step. Run it with `uv run client.py` and show me the output.



Create a CLAUDE.md file in the project root for this project. Keep it under 30 lines. Include:
- What TripMate is: a travel-assistant MCP server in Python.
- Stack: Python with uv, the official MCP Python SDK version 2 (`from mcp.server import MCPServer`). Never use the old v1 FastMCP API (`mcp.server.fastmcp`).
- Layout: tool logic as plain functions in src/tripmate/tools/, registered in src/tripmate/app.py with mcp.add_tool(); main() in src/tripmate/__init__.py.
- Rules: never print to stdout (it carries MCP messages over stdio), log to stderr; raise ToolError from mcp.server.mcpserver.exceptions for bad input; every tool needs a clear docstring with input formats, because the AI model reads it.
- Commands: `uv run tripmate` (run server), `uv run mcp dev src/tripmate/app.py` (MCP Inspector), `uv run client.py` (test client).



Add a tool that tells how many days are left until a trip starts. A date in the past is an error.


• MCP: Model Context Protocol, the standard that lets AI apps use your code.
• Host: the AI app (Claude Code, claude.ai, Claude Desktop).
• Client: the connector inside the host that talks to one server.
• Server: your program that offers tools, resources and prompts.
• Tool: a function the model can ask to call.
• Transport: how messages travel. stdio for local, Streamable HTTP for remote.
• Input schema: the description of a tool's inputs, built from your type hints.
• ToolError: the exception that sends a readable error back to the model.
• CLAUDE.md: a project file Claude Code reads at the start of every session.
• Scope: where claude mcp add saves the server (local, project, user).
