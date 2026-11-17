---
name: add-tool
description: Add a new MCP tool to TripMate
argument-hint: "<what the tool should do>"
disable-model-invocation: true
---

Add a new TripMate MCP tool that does: $ARGUMENTS

Do these steps in order:

1. **Name and place it.** Pick a clear snake_case tool name. Say which file it goes in: an existing module in `src/tripmate/tools/` if it fits (e.g. `trip_tools.py`, `time_tools.py`), otherwise a new one.
2. **Write the tool** as a plain function, following every file in `.claude/rules/`: a docstring for the model (what it does, when to use it, each argument's format with an example), type hints on every parameter, Pydantic models for structured data, and `ToolError` from `mcp.server.mcpserver.exceptions` for bad input. Never print to stdout.
3. **Register it** in `src/tripmate/app.py` with `mcp.add_tool()`, a `title`, and `ToolAnnotations` that fit: `read_only_hint`, `destructive_hint`, `idempotent_hint`, `open_world_hint` (True only if it calls the internet). Update the server `instructions` if the tool adds a new capability.
4. **Test it in memory** with `uv run python -c`. Set `TRIPMATE_DB` to a temp file *before* importing the app, then call the tool once with good input and once with bad input:
   ```python
   import asyncio, os, tempfile
   os.environ["TRIPMATE_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
   from mcp import Client
   from tripmate.app import mcp
   async def main():
       async with Client(mcp) as c:
           print(await c.call_tool("<tool_name>", {...good args...}))
           print(await c.call_tool("<tool_name>", {...bad args...}))
   asyncio.run(main())
   ```
   The bad-input call must return an error result with a helpful message, not crash. Fix and re-run until both behave.
5. **Summarize** briefly: tool name, file, annotations, and the good-input and bad-input test results.
