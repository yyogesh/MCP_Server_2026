---
paths:
  - "src/tripmate/clients/**/*.py"
  - "src/tripmate/tools/**/*.py"
---

# API client rules

- All HTTP calls use `httpx.AsyncClient`. Never use `requests` (it blocks the server).
- Code for one external API lives in its own module in `src/tripmate/clients/` and returns Pydantic models, never raw JSON.
- Tools never create their own HTTP client. They use the shared client from the server lifespan, reached through the `Context` parameter.
- Base URLs and timeouts come from `src/tripmate/config.py`, never hard-coded in tools.
- Always set a timeout. Turn network errors, timeouts and bad status codes into `ToolError` with a short message for the model; never leak a stack trace.
- Tools that call the internet get the open-world annotation (`openWorldHint=True`).
