---
paths:
  - "src/tripmate/resources/**/*.py"
  - "src/tripmate/prompts/**/*.py"
---

# MCP resource and prompt rules

- Resources are read-only data the app can open, like a document. They never change anything. URIs use the `trip://` scheme, e.g. `trip://trips` and `trip://trips/{trip_id}` (template parameters must match the function's parameter names).
- Resources live in `src/tripmate/resources/`, prompts in `src/tripmate/prompts/`, as plain undecorated functions. Register them in `src/tripmate/app.py`: `mcp.resource(uri, name=..., description=..., mime_type=...)(fn)` and `mcp.prompt()(fn)`.
- Every resource has a `name`, a short `description` and a `mime_type`. For data, return JSON text (`json.dumps(...)` or Pydantic `model_dump_json()`) with `mime_type="application/json"`.
- A missing record raises `ResourceNotFoundError` from `mcp.server.mcpserver.exceptions` with a clear message naming the id (other expected failures: `ResourceError`).
- Prompts are templates the user picks. They take a few simple `str` arguments, have a docstring that becomes the description, and return messages (`UserMessage` from `mcp.server.mcpserver`) that name the TripMate tools to use, e.g. `list_trips`, `get_forecast`.
- Never print to stdout. It carries MCP messages; log to stderr instead.
