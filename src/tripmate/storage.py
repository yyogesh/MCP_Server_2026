"""SQLite storage for trips, using only the standard library sqlite3.

The database path comes from the TRIPMATE_DB environment variable and
defaults to ~/.tripmate/trips.db. Each call opens its own connection.
"""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

from tripmate.models import Trip, TripIn

_SCHEMA = """
CREATE TABLE IF NOT EXISTS trips (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date  TEXT NOT NULL,
    end_date    TEXT NOT NULL,
    notes       TEXT NOT NULL DEFAULT ''
)
"""

_COLUMNS = "id, name, destination, start_date, end_date, notes"


def _db_path() -> Path:
    env = os.environ.get("TRIPMATE_DB")
    path = Path(env) if env else Path.home() / ".tripmate" / "trips.db"
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn


def _row_to_trip(row: sqlite3.Row) -> Trip:
    return Trip.model_validate(dict(row))


def add_trip(trip: TripIn) -> Trip:
    """Store a new trip and return it with its assigned id."""
    with closing(_connect()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO trips (name, destination, start_date, end_date, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                trip.name,
                trip.destination,
                trip.start_date.isoformat(),
                trip.end_date.isoformat(),
                trip.notes,
            ),
        )
        return Trip(id=cur.lastrowid, **trip.model_dump())


def list_trips() -> list[Trip]:
    """Return all trips, ordered by start date then id."""
    with closing(_connect()) as conn:
        rows = conn.execute(
            f"SELECT {_COLUMNS} FROM trips ORDER BY start_date, id"
        ).fetchall()
    return [_row_to_trip(r) for r in rows]


def get_trip(trip_id: int) -> Trip | None:
    """Return the trip with this id, or None if it does not exist."""
    with closing(_connect()) as conn:
        row = conn.execute(
            f"SELECT {_COLUMNS} FROM trips WHERE id = ?", (trip_id,)
        ).fetchone()
    return _row_to_trip(row) if row else None


def delete_trip(trip_id: int) -> bool:
    """Delete the trip with this id. Return True if a trip was deleted."""
    with closing(_connect()) as conn, conn:
        cur = conn.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
        return cur.rowcount > 0
