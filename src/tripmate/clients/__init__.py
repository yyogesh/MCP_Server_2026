"""Clients for external web APIs, plus access to the shared HTTP client."""

import logging
from dataclasses import dataclass
from typing import Any

import httpx
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError

logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Objects created once by the server lifespan and shared by all tools."""

    http: httpx.AsyncClient


def get_http(ctx: Context[AppContext, Any]) -> httpx.AsyncClient:
    """Return the shared httpx.AsyncClient created by the server lifespan.

    Tools get it through their Context parameter; they never create their own.
    """
    return ctx.request_context.lifespan_context.http


async def get_json(
    http: httpx.AsyncClient,
    url: str,
    params: dict[str, Any],
    what: str,
    status_messages: dict[int, str] | None = None,
) -> Any:
    """GET a URL and return the JSON body, turning network errors into ToolError.

    `what` names the service in error messages, e.g. "geocoding".
    `status_messages` maps HTTP status codes to a custom ToolError message,
    e.g. {404: "Unknown currency code."}; other non-200 codes get a generic one.
    """
    try:
        response = await http.get(url, params=params)
    except httpx.TimeoutException:
        logger.warning("%s request timed out: %s", what, url)
        raise ToolError(f"The {what} service timed out. Try again in a moment.") from None
    except httpx.HTTPError as exc:
        logger.warning("%s request failed: %r", what, exc)
        raise ToolError(f"Could not reach the {what} service. Try again later.") from None

    if response.status_code != 200:
        logger.warning("%s returned HTTP %s: %s", what, response.status_code, response.text[:200])
        if status_messages and response.status_code in status_messages:
            raise ToolError(status_messages[response.status_code])
        raise ToolError(f"The {what} service returned an error (HTTP {response.status_code}).")

    try:
        return response.json()
    except ValueError:
        raise ToolError(f"The {what} service sent an unreadable response.") from None
