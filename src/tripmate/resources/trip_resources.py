"""Read-only trip resources: trip://trips and trip://trips/{trip_id}.

These functions are registered in tripmate.app. They never change data.
"""

import json

from mcp.server.mcpserver.exceptions import ResourceNotFoundError

from tripmate import storage


def all_trips() -> str:
    """All saved trips as a JSON list of {id, name, destination, start_date, end_date}."""
    trips = storage.list_trips()
    return json.dumps(
        [
            t.model_dump(
                mode="json",
                include={"id", "name", "destination", "start_date", "end_date"},
            )
            for t in trips
        ]
    )


def one_trip(trip_id: int) -> str:
    """One saved trip as JSON with all its fields plus "days" (first and last day both count)."""
    trip = storage.get_trip(trip_id)
    if trip is None:
        raise ResourceNotFoundError(
            f"No trip with id {trip_id}. Read trip://trips to see the saved trip ids."
        )
    data = trip.model_dump(mode="json")
    data["days"] = (trip.end_date - trip.start_date).days + 1
    return json.dumps(data)
