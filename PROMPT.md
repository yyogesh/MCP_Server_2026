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





Create a Claude Code rules file at
.claude/rules/mcp-tools.md.

It should only apply to files matching
src/tripmate/tools/**/*.py
(use a paths: list in YAML frontmatter).

Rules, as a short bullet list:

- Each tool is a plain function in src/tripmate/tools/,
  registered in src/tripmate/app.py with mcp.add_tool().
- Use type hints for every parameter.
  Use Pydantic models for structured input and output.
- The docstring is for the AI model: say what the tool
  does, when to use it, and the format of each argument
  with an example.
- For bad input or a missing record, raise ToolError
  from mcp.server.mcpserver.exceptions with a message
  that tells the model how to fix the call.
- Set tool annotations in app.py: readOnlyHint for
  tools that only read, destructiveHint for tools
  that delete.
- Never print to stdout.

Keep it under 20 lines.



Add a Claude Code hook to this project that protects the MCP server after every file edit.
- Write the hook as a Python script at .claude/hooks/check_server.py (standard library only). It reads the hook JSON from stdin and gets tool_input.file_path.
- Only check .py files under src/.
- Check 1: if the file has a print( call that does not write to sys.stderr, block with exit code 2 and a message on stderr explaining that stdout carries MCP messages over stdio.
- Check 2: run `uv run python -c "import tripmate.app"` in the project folder; if it fails, exit 2 and show the error on stderr.
- Otherwise exit 0.
- Register it in .claude/settings.json as a PostToolUse hook with matcher "Edit|Write", running: uv run --no-project python "$CLAUDE_PROJECT_DIR/.claude/hooks/check_server.py"
Keep the script short and commented.


Add trip storage to TripMate. Do not add any MCP tools yet.
1. Create src/tripmate/models.py with Pydantic v2 models:
   - TripIn: name (str, 1-100 chars), destination (str, a city name like "Tokyo"), start_date (date), end_date (date), notes (str, optional, default ""). Validate that end_date is not before start_date.
   - Trip: everything in TripIn plus id (int). Give every field a Field(description=...) because the AI model reads them.
2. Create src/tripmate/storage.py using only the standard library sqlite3:
   - The database file path comes from the TRIPMATE_DB environment variable, default ~/.tripmate/trips.db. Create the folder if needed.
   - Create the trips table on first use.
   - Functions: add_trip(trip: TripIn) -> Trip, list_trips() -> list[Trip], get_trip(trip_id: int) -> Trip | None, delete_trip(trip_id: int) -> bool.
   - Open a new connection per call with a context manager. Keep it simple, no ORM.
Then run a quick check with uv run python -c that adds and lists a trip using a temporary TRIPMATE_DB, and show me the output.



Add MCP tools for trips in src/tripmate/tools/trip_tools.py, using storage.py and models.py:
- create_trip: takes the trip details and returns the saved Trip.
- list_trips: returns all saved trips.
- get_trip: takes a trip id and returns that Trip.
- delete_trip: takes a trip id and deletes it.
Register them in app.py with the right tool annotations, and update the server instructions. Follow the project rules.