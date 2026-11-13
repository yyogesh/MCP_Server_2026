---
paths:
  - "src/tripmate/tools/**/*.py"
---

# MCP tool rules

- Each tool is a plain function in `src/tripmate/tools/`, registered in `src/tripmate/app.py` with `mcp.add_tool()`.
- Use type hints for every parameter. Use Pydantic models for structured input and output.
- The docstring is for the AI model: say what the tool does, when to use it, and the format of each argument with an example.
- For bad input or a missing record, raise `ToolError` from `mcp.server.mcpserver.exceptions` with a message that tells the model how to fix the call.
- Set tool annotations in `app.py`: `readOnlyHint` for tools that only read, `destructiveHint` for tools that delete.
- Never print to stdout. It carries MCP messages; log to stderr instead.
