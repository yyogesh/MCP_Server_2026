"""Async client for the free Frankfurter exchange-rate API (no API key).

Rates are reference rates published by the European Central Bank, updated
once per working day. Functions take the shared httpx.AsyncClient from the
server lifespan and return Pydantic models, never raw JSON.
"""

import datetime as dt
import logging

import httpx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field, ValidationError

from tripmate.clients import get_json
from tripmate.config import settings

logger = logging.getLogger(__name__)


class ExchangeRate(BaseModel):
    """The exchange rate between two currencies on a given day."""

    base: str = Field(description='The currency converted from, as a 3-letter ISO code, e.g. "USD".')
    target: str = Field(description='The currency converted to, as a 3-letter ISO code, e.g. "INR".')
    rate: float = Field(description="How many units of target one unit of base buys, e.g. 93.93.")
    date: dt.date = Field(description="The day the rate was published, in YYYY-MM-DD format.")


async def get_rate(http: httpx.AsyncClient, base: str, target: str) -> ExchangeRate:
    """Get the latest exchange rate from `base` to `target` (3-letter ISO codes)."""
    if base == target:
        # Frankfurter rejects a same-currency pair with HTTP 422; the answer is trivially 1.
        return ExchangeRate(base=base, target=target, rate=1.0, date=dt.date.today())

    data = await get_json(
        http,
        f"{settings.currency_url}/latest",
        {"base": base, "symbols": target},
        "exchange rate",
        status_messages={
            404: (
                f"Unknown currency code: {base} or {target}. Use valid 3-letter ISO 4217 "
                "codes such as USD, EUR, GBP, INR or JPY."
            ),
        },
    )
    try:
        return ExchangeRate(base=data["base"], target=target, rate=data["rates"][target], date=data["date"])
    except (KeyError, TypeError, ValidationError):
        logger.warning("Unexpected exchange rate response: %r", data)
        raise ToolError("The exchange rate service sent unexpected data.") from None


class Currency(BaseModel):
    """A currency supported by the exchange-rate API."""

    code: str = Field(description='The 3-letter ISO 4217 code, e.g. "JPY".')
    name: str = Field(description='The English name, e.g. "Japanese Yen".')


async def get_currencies(http: httpx.AsyncClient) -> list[Currency]:
    """Get every currency the exchange-rate API supports, sorted by code."""
    data = await get_json(http, f"{settings.currency_url}/currencies", {}, "exchange rate")
    try:
        return [Currency(code=code, name=name) for code, name in sorted(data.items())]
    except (AttributeError, TypeError, ValidationError):
        logger.warning("Unexpected currencies response: %r", data)
        raise ToolError("The exchange rate service sent unexpected data.") from None
