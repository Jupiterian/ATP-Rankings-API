"""Import the latest published ATP top 100 from an optional rankings source."""

from datetime import date, datetime, timezone
import sqlite3

import requests


RANKINGS_URL = "https://api.livetennisapi.com/api/public/v1/rankings"


def parse_rankings(payload: dict) -> tuple[str, list[tuple[str, str, str]]]:
    """Validate one complete top 100 before allowing any database writes."""
    try:
        week = payload["meta"]["coverage"]["effective_date"]
        rows = payload["data"]
        published = date.fromisoformat(week)
    except (KeyError, TypeError, ValueError):
        raise ValueError("Rankings response has no valid publication date") from None

    if published.isoformat() != week or published > datetime.now(timezone.utc).date():
        raise ValueError("Rankings publication date is invalid or in the future")
    if not isinstance(rows, list) or len(rows) != 100:
        raise ValueError("Rankings response must contain the complete top 100")

    result = []
    seen = set()
    previous_rank = 0
    for position, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError("Invalid ATP ranking row")
        rank, name, points = row.get("rank"), row.get("player_name"), row.get("points")
        if (
            row.get("system") != "atp"
            or row.get("effective_date") != week
            or type(rank) is not int
            or not 1 <= rank <= 100
            or rank < previous_rank
            or rank not in (position, previous_rank)
            or type(points) is not int
            or points < 0
            or not isinstance(name, str)
            or not name.strip()
        ):
            raise ValueError("Invalid ATP ranking row or mixed publication weeks")
        identity = (rank, name.strip())
        if identity in seen:
            raise ValueError("Duplicate ATP ranking row")
        seen.add(identity)
        previous_rank = rank
        # The existing services expect strings and strip commas from points.
        result.append((str(rank), name.strip(), f"{points:,}"))
    if result[0][0] != "1":
        raise ValueError("Rankings response does not start at rank 1")
    return week, result


def update_latest_rankings(
    connection: sqlite3.Connection, api_key: str
) -> tuple[str, bool]:
    """Fetch and atomically insert a published week, preserving existing weeks.

    This endpoint requires a PRO plan. The weekly update makes one request;
    limit=100 selects the same top 100 as the ATP scraper, without pagination.
    """
    if not api_key.strip():
        raise ValueError("A Live Tennis API key is required")
    try:
        response = requests.get(
            RANKINGS_URL,
            params={"system": "atp", "limit": 100, "offset": 0},
            headers={"X-API-Key": api_key.strip()},
            timeout=15,
            allow_redirects=False,
        )
    except requests.RequestException:
        raise ValueError("Could not reach the Live Tennis API") from None
    try:
        if response.status_code == 403:
            raise ValueError("Live Tennis API rankings require a PRO plan (HTTP 403)")
        if response.status_code != 200:
            raise ValueError(f"Live Tennis API request failed (HTTP {response.status_code})")
        try:
            payload = response.json()
        except ValueError:
            raise ValueError("Live Tennis API returned invalid JSON") from None
    finally:
        response.close()

    week, rows = parse_rankings(payload)
    # A savepoint includes CREATE TABLE in the rollback, even in SQLite's
    # legacy transaction mode. A failed insert must not leave a partial week.
    connection.execute("SAVEPOINT livetennis_week")
    try:
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (week,)
        ).fetchone()
        if not exists:
            # week has already been validated as a canonical ISO date.
            connection.execute(f'CREATE TABLE "{week}" (rank, name, points)')
            connection.executemany(f'INSERT INTO "{week}" VALUES (?, ?, ?)', rows)
    except Exception:
        connection.execute("ROLLBACK TO livetennis_week")
        raise
    finally:
        connection.execute("RELEASE livetennis_week")
    return week, not bool(exists)
