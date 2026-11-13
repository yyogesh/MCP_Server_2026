uv run mcp dev src/tripmate/app.py

# macOS / Linux / Git Bash
claude mcp add tripmate -- uv run --directory "$(pwd)" tripmate

# Windows PowerShell
claude mcp add tripmate --scope project -- uv run --directory "$PWD" tripmate

local

Project ==>.mcp.json

User ==> /.claude.json


claude mcp remove tripmate
claude mcp get tripmate     # show the saved command


# run and test
uv run tripmate                          # start the server (stdio, waits quietly)
uv run mcp dev src/tripmate/app.py       # open MCP Inspector
uv run client.py                         # run our test client

# Claude Code
claude mcp add tripmate -- uv run --directory "$(pwd)" tripmate
claude mcp list                          # status of all servers
claude mcp get tripmate                  # saved command for one server
claude mcp remove tripmate
/mcp                                     # inside claude: status, tools, reconnect

# git
git add -A && git commit -m "Session 1: TripMate with time tools"

claude mcp add tripmate -e TRIPMATE_DB=./practice.db -- uv run --directory "$(pwd)" tripmate


claude mcp add tripmate -e TRIPMATE_DB="$(pwd)/data/practice.db" -- uv run --directory "$(pwd)" tripmate


def trip_days(start_date: date, end_date: date) -> int:


from pydantic import BaseModel, Field
from datetime import date

class TripIn(BaseModel):
    name: str = Field(description="Name of the trip")
    destination: str = Field(description="Destination city")
    start_date: date
    end_date: date
    notes: str = ""

response_model= TripIn


def create_trip(trip: TripIn):

def create_trip(trip: TripIn) -> Trip:


TripIn(
    name="Winter in Japan",
    destination="Tokyo",
    start_date=date(2026, 12, 20),
    end_date=date(2026, 12, 24)
)


Trip(
    id=1,
    name="Winter in Japan",
    destination="Tokyo",
    start_date=date(2026, 12, 20),
    end_date=date(2026, 12, 24),
    notes=""
)


.claude/
  rules/
    mcp-tools.md


Hooks
