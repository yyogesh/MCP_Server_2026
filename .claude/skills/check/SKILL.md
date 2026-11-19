---
name: check
description: Health check for the TripMate MCP server
disable-model-invocation: true
allowed-tools: Bash(uv run:*), Bash(git status:*)
---

Run a health check on TripMate. Do not change any files. Run every step even if an earlier one fails, and note each result.

1. **Import**: `uv run python -c "import tripmate.app"`. OK if it exits 0.
2. **Inventory**: run this in-memory client with a temporary database, then report the counts and names:
   ```
   uv run python -c "import os,tempfile,asyncio; os.environ['TRIPMATE_DB']=os.path.join(tempfile.mkdtemp(),'check.db'); from mcp import Client; from tripmate.app import mcp
   async def m():
       async with Client(mcp) as c:
           for k,x in [('tools',(await c.list_tools()).tools),('resources',(await c.list_resources()).resources),('resource templates',(await c.list_resource_templates()).resource_templates),('prompts',(await c.list_prompts()).prompts)]: print(f'{k}: {len(x)} -',', '.join(i.name for i in x))
   asyncio.run(m())"
   ```
3. **Client run**: `uv run python -c "import os,tempfile,runpy; os.environ['TRIPMATE_DB']=os.path.join(tempfile.mkdtemp(),'check.db'); runpy.run_path('client.py', run_name='__main__')"`. OK if it exits 0 with no traceback. The tool errors from `trip_days` and `days_until_trip` are expected; they are not failures.
4. **Git**: `git status --short`. Report the changed files, or "clean".

End with a short table:

| Check | Result | Detail |
|---|---|---|

One row per step. Result is OK or FAIL. Detail is one short line, such as counts, the error, or the changed files.
