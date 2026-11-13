"""Pydantic models for TripMate trips."""

from datetime import date
from typing import Self

from pydantic import BaseModel, Field, model_validator


class TripIn(BaseModel):
    """A trip to create. Has every field except the database id."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description='A short name for the trip, 1-100 characters, e.g. "Spring in Japan".',
    )
    destination: str = Field(
        description='The destination city name, e.g. "Tokyo".',
    )
    start_date: date = Field(
        description="The first day of the trip, in YYYY-MM-DD format.",
    )
    end_date: date = Field(
        description="The last day of the trip, in YYYY-MM-DD format. Must not be before start_date.",
    )
    notes: str = Field(
        default="",
        description="Optional free-text notes about the trip. Defaults to an empty string.",
    )

    @model_validator(mode="after")
    def check_dates(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError(
                f"end_date ({self.end_date}) is before start_date ({self.start_date})"
            )
        return self


class Trip(TripIn):
    """A stored trip, including its database id."""

    id: int = Field(description="The unique id of the stored trip.")
