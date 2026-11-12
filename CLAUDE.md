# TripMate

TripMate is a travel-assistant MCP server written in Python.

## Stack
- Python, managed with `uv`.
- Official MCP Python SDK **v2**: `from mcp.server import MCPServer`.
- Never use the old v1 FastMCP API (`mcp.server.fastmcp`).

## Layout
- `src/tripmate/tools/`: tool logic as plain functions.
- `src/tripmate/app.py`: creates the server and registers tools with `mcp.add_tool()`.
- `src/tripmate/__init__.py`: `main()` entry point.

## Rules
- Never print to stdout. It carries MCP messages over stdio. Log to stderr instead.
- For bad input, raise `ToolError` from `mcp.server.mcpserver.exceptions`.
- Every tool needs a clear docstring that states its input formats, because the AI model reads it.

## Commands
- `uv run tripmate`: run the server
- `uv run mcp dev src/tripmate/app.py`: open the MCP Inspector
- `uv run client.py`: run the test client
