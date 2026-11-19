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



Create a Claude Code rules file at .claude/rules/api-clients.md that only applies to files matching src/tripmate/clients/**/*.py and src/tripmate/tools/**/*.py (use a `paths:` list in YAML frontmatter). Rules, as a short bullet list:
- All HTTP calls use httpx.AsyncClient. Never use requests (it blocks the server).
- Code for one external API lives in its own module in src/tripmate/clients/ and returns Pydantic models, never raw JSON.
- Tools never create their own HTTP client. They use the shared client from the server lifespan, reached through the Context parameter.
- Base URLs and timeouts come from src/tripmate/config.py, never hard-coded in tools.
- Always set a timeout. Turn network errors, timeouts and bad status codes into ToolError with a short message for the model; never leak a stack trace.
- Tools that call the internet get the open-world annotation.
Keep it under 20 lines.




Create a Claude Code skill for this project called add-tool, so I can type `/add-tool <what the tool should do>`. Save it as .claude/skills/add-tool/SKILL.md.
Frontmatter: name add-tool, a one-line description ("Add a new MCP tool to TripMate"), argument-hint "<what the tool should do>", and disable-model-invocation: true so it only runs when I type it.
The body tells Claude to do these steps for $ARGUMENTS, in order:
1. Pick a clear snake_case tool name and say which file it goes in (an existing file in src/tripmate/tools/ if it fits, otherwise a new one).
2. Write the tool as a plain function following .claude/rules/ (docstring for the model, type hints, ToolError for bad input).
3. Register it in src/tripmate/app.py with the right annotations.
4. Test it with an in-memory client: `uv run python -c` using `from mcp import Client` and `Client(mcp)`, calling the tool once with good input and once with bad input. Use a temporary TRIPMATE_DB.
5. Finish with a short summary: tool name, file, annotations, and both test results.
Keep the skill under 30 lines.



Prepare TripMate to call free public web APIs. No new tools yet.
1. Run `uv add httpx pydantic-settings`.
2. Create src/tripmate/config.py with a pydantic-settings Settings class (env prefix TRIPMATE_): geocoding_url = "https://geocoding-api.open-meteo.com/v1/search", forecast_url = "https://api.open-meteo.com/v1/forecast", currency_url = "https://api.frankfurter.dev/v1", http_timeout = 10.0 seconds. Export one `settings` object.
3. Add a lifespan to the server in app.py: create ONE shared httpx.AsyncClient (with the timeout from settings and a User-Agent "TripMate/0.1") when the server starts, close it when it stops, and expose it as an AppContext dataclass with an `http` field. Pass it with MCPServer(..., lifespan=...). Check the installed MCP SDK v2 source to see how a tool reaches the lifespan object through its Context parameter, and write a small helper get_http(ctx) in src/tripmate/clients/__init__.py that returns the shared client.
4. Do not change the existing tools.
Then run the in-memory client to check that all existing tools still work.



Create src/tripmate/clients/weather.py, an async client for the free Open-Meteo APIs (no API key). Follow the project rules. Use the URLs from config.
- find_city(http, name) -> City: calls the geocoding API with name=<name>&count=1&language=en&format=json. The response looks like {"results": [{"name": "Tokyo", "latitude": 35.6895, "longitude": 139.69171, "country": "Japan", "timezone": "Asia/Tokyo", ...}]}. If "results" is missing or empty, raise ToolError saying the city was not found and to try the English city name.
- get_daily_forecast(http, city, days) -> list[DayForecast]: calls the forecast API with latitude, longitude, timezone=auto, forecast_days=days and daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code. The response has "daily": {"time": [...], "temperature_2m_max": [...], "temperature_2m_min": [...], "precipitation_probability_max": [...], "weather_code": [...]}.
- DayForecast has date, temp_max_c, temp_min_c, rain_chance_percent and conditions: a short English text from the WMO weather code (e.g. 0 "Clear sky", 61 "Light rain"); use a small dict, "Unknown" for others.
- Pydantic models City and DayForecast with Field descriptions.
- Turn httpx timeouts, connection errors and non-200 responses into ToolError with a short message.
Test it with a real call for Tokyo, and with one unknown city.



/add-tool convert_currency: convert an amount from one currency to another with today's rate, using the free Frankfurter API (no key). Put the API code in a new src/tripmate/clients/currency.py. The call is GET {currency_url}/latest?base=USD&symbols=INR and returns {"amount": 1.0, "base": "USD", "date": "2026-11-12", "rates": {"INR": 94.49}}. Currency codes are 3-letter ISO codes like USD, EUR, INR, JPY; an unknown code gives HTTP 404, which should become a ToolError that asks for a valid ISO code. Return the converted amount, the rate and the rate date.


/add-tool list_currencies: list the currency codes Frankfurter supports (GET {currency_url}/currencies returns {"USD": "United States Dollar", ...}).



Create a Claude Code rules file at .claude/rules/mcp-resources-prompts.md. It should only apply to files matching src/tripmate/resources/**/*.py and src/tripmate/prompts/**/*.py (use a `paths:` list in YAML frontmatter). Check the installed MCP SDK v2 source first so the rules match the real API. Rules, as a short bullet list:
- Resources are read-only data the app can open, like a document. They never change anything. URIs use the trip:// scheme, e.g. trip://trips and trip://trips/{trip_id}.
- Resources live in src/tripmate/resources/, prompts in src/tripmate/prompts/, as plain functions registered in src/tripmate/app.py (not decorated where they are defined).
- Every resource has a name, a short description and a mime_type. Return JSON text for data (mime_type application/json).
- A missing record in a resource raises the SDK resource error with a clear message.
- Prompts are templates the user picks. They take a few simple string arguments, have a docstring that becomes the description, and return messages that tell the model which TripMate tools to use by name.
- Never print to stdout.
Keep it under 20 lines.



Add MCP resources for saved trips, following the project rules. Put them in src/tripmate/resources/trip_resources.py, using storage.py:
- trip://trips: all saved trips as a JSON list (id, name, destination, start_date, end_date).
- trip://trips/{trip_id}: one trip as JSON, with all its fields plus "days" (the trip length, counting first and last day).
Register both in app.py with a name, description and mime_type. Then test with the in-memory client (Client(mcp)) using a temporary TRIPMATE_DB: create a trip with the create_trip tool, list the resources and resource templates, read both URIs, and read trip://trips/999 to show the error.



Add two MCP prompts in src/tripmate/prompts/trip_prompts.py, following the project rules, and register them in app.py:
1. plan_trip(destination, start_date, end_date, home_currency="INR"): asks the model to plan the trip step by step using TripMate tools: save it with create_trip, check the weather with get_forecast, give the local time with local_time, convert a sample daily budget with convert_currency into the home currency, and finish with a short day-by-day plan.
2. packing_list(trip_id): reads the saved trip from storage (raise a clear error if it does not exist) and asks the model to check the forecast for that destination with get_forecast and write a packing list grouped by category, tuned to the weather and the trip length.
Then test with the in-memory client using a temporary TRIPMATE_DB: list the prompts with their arguments, get plan_trip with sample arguments, create a trip and get packing_list for it, and get packing_list for id 999 to show the error.



Extend client.py so that, after the existing steps, it also:
4. lists the resources and resource templates (URI and name),
5. reads trip://trips and prints the text,
6. lists the prompts with their argument names,
7. gets the plan_trip prompt for Tokyo, 2026-12-20 to 2026-12-24, and prints the message text.
Keep a comment above each step. Run it with a temporary TRIPMATE_DB and show me the output.


Create a Claude Code skill called check, so I can type `/check` to get a quick health report for TripMate. Save it as .claude/skills/check/SKILL.md.
Frontmatter: name check, description "Health check for the TripMate MCP server", disable-model-invocation: true, and allowed-tools limited to running uv and git commands (Bash(uv run:*), Bash(git status:*)).
The body tells Claude to run these steps and keep going even if one fails:
1. Import check: uv run python -c "import tripmate.app".
2. Inventory: use an in-memory Client(mcp) with a temporary TRIPMATE_DB and print how many tools, resources, resource templates and prompts the server has, with their names.
3. Client run: run client.py with a temporary TRIPMATE_DB and say whether it finished without errors.
4. git status --short.
5. Finish with a short table: Check, Result (OK or FAIL), Detail.
Do not change any files. Keep it under 30 lines.


Create explore.py in the project root: a small, generic MCP explorer that works with ANY stdio MCP server, not just TripMate. Usage:
  uv run explore.py -- <server command> [args...]
  uv run explore.py --call TOOL '<json args>' -- <server command>
  uv run explore.py --read URI -- <server command>
  uv run explore.py --prompt NAME '<json args>' -- <server command>
With no action, print sections: server name and instructions, tools (name, first line of description, required arguments, and annotation hints that are set), resources, resource templates, prompts (with arguments). Skip a section cleanly if the server does not support that feature. --call prints is_error, the text content and the structured content if any. --read prints the text of each content item. --prompt prints each message with its role.
Keep it under 120 lines with short comments. Then run it against TripMate (-- uv run tripmate) with a temporary TRIPMATE_DB: the overview, one --call of local_time, one --read of trip://trips, and one --prompt of packing_list with a missing id.


Give me the JSON to add TripMate to Claude Desktop on this machine. Use the full absolute path to uv (find it with `which uv`, or `where uv` on Windows) and `uv run --directory <absolute project path> tripmate`, so it works no matter which folder Claude Desktop starts in. Show only the "tripmate" entry that goes inside "mcpServers", tell me where the config file is on my operating system, and say if I need to escape anything. Do not change any files.