"""
Model Context Protocol (MCP) router for ATP Rankings API.
Provides MCP-compliant endpoints that wrap the existing service layer.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
import json
from pathlib import Path

from src.services import (
    search_players,
    get_player_factfile,
    get_player_career,
    get_weeks_at_no1,
    get_all_weeks,
    get_week_data
)

router = APIRouter(prefix="/mcp", tags=["MCP"])


# Pydantic models for MCP requests
class MCPResponse(BaseModel):
    """Standard MCP response wrapper."""
    ok: bool
    result: Optional[Any] = None
    error: Optional[str] = None


class SearchPlayersRequest(BaseModel):
    query: str = Field(..., description="Search query for player name")
    limit: int = Field(10, description="Maximum number of results")


class PlayerRequest(BaseModel):
    player: str = Field(..., description="Exact player name")


class WeeksAtNo1Request(BaseModel):
    min_weeks: int = Field(1, description="Minimum weeks at #1 to include")
    top_n: Optional[int] = Field(None, description="Limit to top N players")


class WeekRequest(BaseModel):
    week: str = Field(..., description="Week date in YYYY-MM-DD format")


@router.get("/health")
async def mcp_health():
    """MCP health check endpoint."""
    return {"status": "ok", "service": "atp-rankings-mcp"}


@router.get("/manifest")
async def mcp_manifest():
    """Return the MCP manifest describing server capabilities."""
    manifest_path = Path(__file__).parent / "mcp_manifest.json"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    return manifest


@router.post("/tools/search_players")
async def mcp_search_players(request: SearchPlayersRequest):
    """MCP tool: Search for players by name."""
    try:
        players = search_players(request.query, request.limit)
        return MCPResponse(ok=True, result={"players": players})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )


@router.post("/tools/get_player_factfile")
async def mcp_get_player_factfile(request: PlayerRequest):
    """MCP tool: Get player factfile/statistics."""
    try:
        factfile = get_player_factfile(request.player)
        return MCPResponse(ok=True, result=factfile)
    except ValueError as e:
        return JSONResponse(
            status_code=404,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )


@router.post("/tools/get_player_career")
async def mcp_get_player_career(request: PlayerRequest):
    """MCP tool: Get player career time-series data."""
    try:
        career = get_player_career(request.player)
        return MCPResponse(ok=True, result=career)
    except ValueError as e:
        return JSONResponse(
            status_code=404,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )


@router.post("/tools/get_weeks_at_no1")
async def mcp_get_weeks_at_no1(request: Optional[WeeksAtNo1Request] = None):
    """MCP tool: Get weeks at number 1 for all players."""
    try:
        if request is None:
            request = WeeksAtNo1Request()
        
        data = get_weeks_at_no1()
        
        # Apply filters
        if request.min_weeks > 1:
            data = [p for p in data if p["weeks"] >= request.min_weeks]
        
        if request.top_n:
            data = data[:request.top_n]
        
        return MCPResponse(ok=True, result=data)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )


@router.get("/tools/get_all_weeks")
async def mcp_get_all_weeks():
    """MCP tool: Get all available weeks."""
    try:
        weeks = get_all_weeks()
        return MCPResponse(ok=True, result={"weeks": weeks, "total": len(weeks)})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )


@router.post("/tools/get_week_rankings")
async def mcp_get_week_rankings(request: WeekRequest):
    """MCP tool: Get rankings for a specific week."""
    try:
        rankings = get_week_data(request.week)
        return MCPResponse(ok=True, result={"week": request.week, "rankings": rankings})
    except ValueError as e:
        return JSONResponse(
            status_code=404,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=MCPResponse(ok=False, error=str(e)).dict()
        )


# Convenience GET endpoints for simpler access
@router.get("/tools/search_players")
async def mcp_search_players_get(q: str, limit: int = 10):
    """MCP tool: Search for players (GET version)."""
    return await mcp_search_players(SearchPlayersRequest(query=q, limit=limit))


@router.get("/tools/get_weeks_at_no1")
async def mcp_get_weeks_at_no1_get(min_weeks: int = 1, top_n: Optional[int] = None):
    """MCP tool: Get weeks at #1 (GET version)."""
    return await mcp_get_weeks_at_no1(WeeksAtNo1Request(min_weeks=min_weeks, top_n=top_n))
