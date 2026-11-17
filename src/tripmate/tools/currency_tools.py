"""Currency tools: conversions with today's rates via tripmate.clients.currency."""

import datetime as dt
import re
from typing import Any

from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field

from tripmate.clients import AppContext, get_http
from tripmate.clients.currency import Currency, get_currencies, get_rate

_ISO_CODE = re.compile(r"[A-Z]{3}")


class Conversion(BaseModel):
    """The result of converting an amount between two currencies."""

    amount: float = Field(description="The original amount, in from_currency.")
    from_currency: str = Field(description='The currency converted from, e.g. "USD".')
    to_currency: str = Field(description='The currency converted to, e.g. "INR".')
    converted_amount: float = Field(description="The amount in to_currency, rounded to 2 decimals.")
    rate: float = Field(description="How many units of to_currency one unit of from_currency buys.")
    rate_date: dt.date = Field(description="The day the rate was published, in YYYY-MM-DD format.")


def _check_code(code: str, arg: str) -> str:
    cleaned = code.strip().upper()
    if not _ISO_CODE.fullmatch(cleaned):
        raise ToolError(
            f'{arg} must be a 3-letter ISO 4217 currency code such as "USD", "EUR" or "INR", got "{code}".'
        )
    return cleaned


async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    ctx: Context[AppContext, Any],
) -> Conversion:
    """Convert an amount of money from one currency to another at the latest rate.

    Use this for travel budgets, e.g. "How much is 500 USD in Japanese yen?".
    Rates are European Central Bank reference rates, published once per
    working day, so on weekends and holidays the rate is from the last working
    day; rate_date in the result says which day. Only major currencies are
    covered (about 30, e.g. USD, EUR, GBP, INR, JPY, AUD, CAD, CHF, CNY, SGD, THB).

    Args:
        amount: The amount to convert, a number of 0 or more, e.g. 500 or 19.99.
        from_currency: The currency of the amount, a 3-letter ISO 4217 code, e.g. "USD".
        to_currency: The currency to convert to, a 3-letter ISO 4217 code, e.g. "JPY".

    Returns the original amount and codes, the converted amount (rounded to
    2 decimals), the exchange rate used and the date that rate was published.
    """
    if amount < 0:
        raise ToolError(f"amount must be 0 or more, got {amount}.")
    base = _check_code(from_currency, "from_currency")
    target = _check_code(to_currency, "to_currency")

    rate = await get_rate(get_http(ctx), base, target)
    return Conversion(
        amount=amount,
        from_currency=base,
        to_currency=target,
        converted_amount=round(amount * rate.rate, 2),
        rate=rate.rate,
        rate_date=rate.date,
    )


async def list_currencies(
    ctx: Context[AppContext, Any],
    search: str = "",
) -> list[Currency]:
    """List the currencies that convert_currency supports, with their codes and names.

    Use this to check whether a currency is supported, or to find the 3-letter
    code for a currency the user names in words (e.g. "Thai baht" -> "THB")
    before calling convert_currency.

    Args:
        search: Optional filter, matched case-insensitively against the code
            and the name, e.g. "yen", "dollar" or "INR". Leave empty to list all
            currencies (about 30).

    Returns a list of currencies sorted by code, each with its ISO 4217 code
    and English name, e.g. {"code": "JPY", "name": "Japanese Yen"}.
    """
    currencies = await get_currencies(get_http(ctx))
    term = search.strip().lower()
    if not term:
        return currencies
    matches = [c for c in currencies if term in c.code.lower() or term in c.name.lower()]
    if not matches:
        raise ToolError(
            f'No supported currency matches "{search}". Try a shorter word such as "peso" '
            "or a 3-letter code, or call list_currencies with no search to see them all."
        )
    return matches
