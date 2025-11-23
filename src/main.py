"""FastAPI application for ATP Rankings data visualization."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from typing import List, Dict, Any
from pathlib import Path

# Import service layer and MCP router
from .services import (
    get_all_weeks,
    get_week_data,
    search_players as service_search_players,
    get_player_factfile as service_get_player_factfile,
    get_player_career as service_get_player_career,
    get_weeks_at_no1 as service_get_weeks_at_no1
)
from .mcp_router import router as mcp_router

app = FastAPI(title="ATP Rankings Database")

from starlette.requests import Request
from starlette.responses import Response

# Smart HEAD handler
@app.api_route("/{path:path}", methods=["HEAD"])
async def smart_head_handler(request: Request, path: str):
    # Normalize path (no leading slash)
    request_path = "/" + path

    # Check if any GET route matches this path
    for route in app.routes:
        if "GET" in getattr(route, "methods", []):
            if hasattr(route, "path") and route.path == request_path:
                return Response(status_code=200)

    # If no GET route exists for this path → behave normally
    return Response(status_code=404)

# Add CORS middleware for MCP client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include MCP router
app.include_router(mcp_router)

# Setup templates & static assets
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database path (kept for compatibility)
DB_PATH = "rankings.db"


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with all available weeks."""
    weeks = get_all_weeks()
    
    # Group weeks by year for better organization
    weeks_by_year = {}
    for week in weeks:
        year = week.split("-")[0]
        if year not in weeks_by_year:
            weeks_by_year[year] = []
        weeks_by_year[year].append(week)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "weeks_by_year": weeks_by_year,
            "total_weeks": len(weeks)
        }
    )


@app.get("/api-docs", response_class=HTMLResponse)
async def api_documentation(request: Request):
    """Render the API documentation page."""
    return templates.TemplateResponse(
        "api_docs.html",
        {"request": request}
    )


@app.get("/week/{week_date}", response_class=HTMLResponse)
async def week_page(request: Request, week_date: str):
    """Render a specific week's rankings page."""
    try:
        rankings = get_week_data(week_date)
        all_weeks = get_all_weeks()
        
        # Find previous and next weeks for navigation
        current_index = all_weeks.index(week_date)
        prev_week = all_weeks[current_index + 1] if current_index + 1 < len(all_weeks) else None
        next_week = all_weeks[current_index - 1] if current_index - 1 >= 0 else None
        
        return templates.TemplateResponse(
            "week.html",
            {
                "request": request,
                "week_date": week_date,
                "rankings": rankings,
                "prev_week": prev_week,
                "next_week": next_week
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weeks")
async def api_weeks():
    """API endpoint to get all available weeks."""
    return {"weeks": get_all_weeks()}


@app.get("/api/week/{week_date}")
async def api_week_data(week_date: str):
    """API endpoint to get ranking data for a specific week."""
    try:
        rankings = get_week_data(week_date)
        return {"week": week_date, "rankings": rankings}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    """Render the player comparison/stats page."""
    return templates.TemplateResponse("comparison.html", {"request": request})


@app.get("/weeks-at-no1", response_class=HTMLResponse)
async def weeks_at_no1_page(request: Request):
    """Render the weeks at number 1 histogram page."""
    return templates.TemplateResponse("weeks_at_no1.html", {"request": request})


@app.get("/api/players/search")
async def search_players_endpoint(q: str, limit: int = 10):
    """Search for players in the database."""
    try:
        players = service_search_players(q, limit)
        return {"players": players}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/player/factfile")
async def get_player_factfile_endpoint(player: str):
    """Get player factfile/statistics."""
    try:
        factfile = service_get_player_factfile(player)
        return factfile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/player/career")
async def get_player_career_endpoint(player: str):
    """Get player career data for charting (rankings and points over time)."""
    try:
        career = service_get_player_career(player)
        return career
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/weeks-at-no1")
async def api_weeks_at_no1():
    """API endpoint to get all players and their weeks at number 1."""
    try:
        result = service_get_weeks_at_no1()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
