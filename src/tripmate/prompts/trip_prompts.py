"""Trip prompts: plan_trip and packing_list.

These functions are registered in tripmate.app. Each returns a user message
that tells the model which TripMate tools to call, by name.
"""

from typing import Annotated

from mcp.server.mcpserver import UserMessage
from mcp.shared.exceptions import MCPError
from mcp_types import INVALID_PARAMS
from pydantic import Field

from tripmate import storage


def plan_trip(
    destination: Annotated[str, Field(description='The destination city name, e.g. "Tokyo".')],
    start_date: Annotated[str, Field(description='The first day of the trip, YYYY-MM-DD, e.g. "2027-04-01".')],
    end_date: Annotated[str, Field(description='The last day of the trip, YYYY-MM-DD, e.g. "2027-04-10".')],
    home_currency: Annotated[
        str, Field(description='Your home currency as a 3-letter code, e.g. "INR" (default) or "USD".')
    ] = "INR",
) -> list[UserMessage]:
    """Plan a new trip step by step: save it, check weather, local time and budget, then a day-by-day plan."""
    text = f"""Help me plan a trip to {destination} from {start_date} to {end_date}. Work step by step with the TripMate tools:

1. Save the trip with create_trip. Give it a short name, destination "{destination}", start_date "{start_date}" and end_date "{end_date}". Note the id it returns.
2. Check the weather with get_forecast for "{destination}". If the trip starts more than 7 days from now, say the forecast is not available yet and describe typical weather for that season instead.
3. Tell me the current local time there with local_time, using the destination's IANA timezone (e.g. "Asia/Tokyo").
4. Pick a sample daily budget of 100 in the destination's local currency and convert it to {home_currency} with convert_currency. Use list_currencies if you are unsure of a currency code.
5. Finish with a short day-by-day plan, one or two lines per day, for every day from {start_date} to {end_date}."""
    return [UserMessage(text)]


def packing_list(
    trip_id: Annotated[
        str, Field(description='The id of a saved trip, a whole number such as "1". See list_trips or trip://trips.')
    ],
) -> list[UserMessage]:
    """Write a packing list for a saved trip, grouped by category and tuned to the weather and trip length."""
    trip = storage.get_trip(int(trip_id)) if trip_id.strip().isdigit() else None
    if trip is None:
        raise MCPError(
            code=INVALID_PARAMS,
            message=f"No trip with id {trip_id!r}. Use list_trips or read trip://trips to see the saved trip ids.",
        )
    days = (trip.end_date - trip.start_date).days + 1
    notes = f"\nTrip notes: {trip.notes}" if trip.notes else ""
    text = f"""Write a packing list for my trip "{trip.name}" to {trip.destination}, {trip.start_date} to {trip.end_date} ({days} days).{notes}

1. Check the weather with get_forecast for "{trip.destination}". If the trip starts more than 7 days from now, say the forecast is not available yet and use typical weather for that season instead.
2. Write the packing list grouped by category (Clothing, Toiletries, Electronics, Documents and money, Health, Other). Match clothing to the temperatures and rain you found, and scale quantities to {days} days."""
    return [UserMessage(text)]
