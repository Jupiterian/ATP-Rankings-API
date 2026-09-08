"""
Real Model Context Protocol (MCP) server for ATP Rankings API.

Exposes the existing service layer as proper MCP tools over the
Streamable HTTP transport (JSON-RPC 2.0: initialize / tools/list /
tools/call), mounted at a single endpoint (/mcp) so it can be added
as a custom connector in Claude.ai.
"""
from typing import Optional, Any, Dict, List

from mcp.server.fastmcp import FastMCP

from .services import (
    search_players as service_search_players,
    get_player_factfile as service_get_player_factfile,
    get_player_career as service_get_player_career,
    get_weeks_at_no1 as service_get_weeks_at_no1,
    get_all_weeks as service_get_all_weeks,
    get_week_data as service_get_week_data,
)

mcp = FastMCP(
    name="atp-rankings",
    instructions=(
        "Query historical ATP tennis rankings data (1973-present): "
        "search for players, get career fact files and time-series "
        "history, weeks spent at world No. 1, and full rankings for "
        "any given week."
    ),
    stateless_http=True,
)


@mcp.tool()
def search_players(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search for ATP players by (partial) name.

    Args:
        query: Search text to match against player names.
        limit: Maximum number of matching player names to return.
    """
    players = service_search_players(query, limit)
    return {"players": players}


@mcp.tool()
def get_player_factfile(player: str) -> Dict[str, Any]:
    """Get a player's career fact file: career-high rank, peak points,
    and weeks spent in the top 100 / top 10 / at No. 1.

    Args:
        player: Exact player name as it appears in the rankings data.
    """
    return service_get_player_factfile(player)


@mcp.tool()
def get_player_career(player: str) -> Dict[str, Any]:
    """Get a player's full time-series career history: ranking and
    points at every recorded week.

    Args:
        player: Exact player name as it appears in the rankings data.
    """
    return service_get_player_career(player)


@mcp.tool()
def get_weeks_at_no1() -> List[Dict[str, Any]]:
    """Get every player who has held the World No. 1 ranking, along
    with the total number of weeks they held it, sorted descending."""
    return service_get_weeks_at_no1()


@mcp.tool()
def get_all_weeks() -> Dict[str, Any]:
    """Get the list of all rankings weeks available in the database."""
    weeks = service_get_all_weeks()
    return {"weeks": weeks, "total": len(weeks)}


@mcp.tool()
def get_week_rankings(week_date: str) -> Dict[str, Any]:
    """Get the complete ATP rankings for a specific week.

    Args:
        week_date: Week date in YYYY-MM-DD format, e.g. "2023-01-02".
    """
    rankings = service_get_week_data(week_date)
    return {"week": week_date, "rankings": rankings}
