uv run mcp dev src/tripmate/app.py

# macOS / Linux / Git Bash
claude mcp add tripmate -- uv run --directory "$(pwd)" tripmate

# Windows PowerShell
claude mcp add tripmate --scope project -- uv run --directory "$PWD" tripmate

local

Project ==>.mcp.json

User ==> /.claude.json


claude mcp remove tripmate
claude mcp get tripmate     # show the saved command


# run and test
uv run tripmate                          # start the server (stdio, waits quietly)
uv run mcp dev src/tripmate/app.py       # open MCP Inspector
uv run client.py                         # run our test client

# Claude Code
claude mcp add tripmate -- uv run --directory "$(pwd)" tripmate
claude mcp list                          # status of all servers
claude mcp get tripmate                  # saved command for one server
claude mcp remove tripmate
/mcp                                     # inside claude: status, tools, reconnect

# git
git add -A && git commit -m "Session 1: TripMate with time tools"


