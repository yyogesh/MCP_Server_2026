"""Tools for saving, listing, viewing and deleting trips.

These are plain functions; the server module registers them as MCP tools.
"""

from mcp.server.mcpserver.exceptions import ToolError

from tripmate import storage
from tripmate.models import Trip, TripIn


def _not_found(trip_id: int) -> ToolError:
    return ToolError(
        f"No trip with id {trip_id}. Call list_trips to see the saved trips and their ids."
    )


def create_trip(trip: TripIn) -> Trip:
    """Save a new trip. Use this when the user wants to record a planned trip.

    Each call saves a separate trip, even if the details match an existing
    one, so call list_trips first if you are not sure the trip is already saved.

    Args:
        trip: The trip details, as an object with these fields:
            name: a short name, 1-100 characters, such as "Spring in Japan".
            destination: the destination city name, such as "Tokyo".
            start_date: the first day, in ISO format "YYYY-MM-DD".
            end_date: the last day, in ISO format "YYYY-MM-DD", on or after
                start_date.
            notes: optional free-text notes; defaults to "".
            Example: {"name": "Spring in Japan", "destination": "Tokyo",
            "start_date": "2027-04-01", "end_date": "2027-04-10"}

    Returns:
        The saved trip, including the id it was given. Use this id with
        get_trip and delete_trip.
    """
    return storage.add_trip(trip)


def list_trips() -> list[Trip]:
    """List all saved trips.

    Takes no input. Use this to find a trip's id before calling get_trip or
    delete_trip.

    Returns:
        Every saved trip, ordered by start date (earliest first). An empty
        list if no trips are saved.
    """
    return storage.list_trips()


def get_trip(trip_id: int) -> Trip:
    """Get one saved trip by its id.

    Args:
        trip_id: The trip's id, a whole number such as 3, as returned by
            create_trip or list_trips.

    Returns:
        The saved trip with that id. An unknown id is an error.
    """
    trip = storage.get_trip(trip_id)
    if trip is None:
        raise _not_found(trip_id)
    return trip


def delete_trip(trip_id: int) -> Trip:
    """Permanently delete a saved trip by its id. This cannot be undone.

    Args:
        trip_id: The trip's id, a whole number such as 3, as returned by
            create_trip or list_trips.

    Returns:
        The trip that was deleted, so you can confirm what was removed.
        An unknown id is an error.
    """
    trip = storage.get_trip(trip_id)
    if trip is None or not storage.delete_trip(trip_id):
        raise _not_found(trip_id)
    return trip
