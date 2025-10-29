"""FastAPI application for ATP Rankings data visualization."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
from typing import List, Dict, Any
from pathlib import Path

app = FastAPI(title="ATP Rankings Database")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Database path
DB_PATH = "rankings.db"


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_weeks() -> List[str]:
    """Get all available weeks (table names) from the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name DESC;")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables


def get_week_data(week: str) -> List[Dict[str, Any]]:
    """Get ranking data for a specific week."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (week,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Week {week} not found")
    
    # Get data from the week table
    cur.execute(f'SELECT * FROM "{week}";')
    rows = cur.fetchall()
    conn.close()
    
    # Convert to list of dicts
    data = []
    for row in rows:
        data.append({
            "rank": row["rank"],
            "name": row["name"],
            "points": row["points"]
        })
    
    return data


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
    rankings = get_week_data(week_date)
    return {"week": week_date, "rankings": rankings}


@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    """Render the player comparison/stats page."""
    return templates.TemplateResponse("comparison.html", {"request": request})


@app.get("/weeks-at-no1", response_class=HTMLResponse)
async def weeks_at_no1_page(request: Request):
    """Render the weeks at number 1 histogram page."""
    return templates.TemplateResponse("weeks_at_no1.html", {"request": request})


@app.get("/api/players/search")
async def search_players(q: str, limit: int = 10):
    """Search for players in the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get all tables
    tables = get_all_weeks()
    
    # Collect unique player names that match the query
    players = set()
    search_query = q.lower()
    
    for table in tables[:100]:  # Search through recent tables for performance
        try:
            cur.execute(f'SELECT DISTINCT name FROM "{table}" WHERE LOWER(name) LIKE ?', (f'%{search_query}%',))
            rows = cur.fetchall()
            for row in rows:
                players.add(row[0])
                if len(players) >= limit * 2:  # Get more than needed to filter
                    break
        except:
            continue
        
        if len(players) >= limit * 2:
            break
    
    conn.close()
    
    # Sort and limit results
    sorted_players = sorted(list(players))[:limit]
    return {"players": sorted_players}


@app.get("/api/player/factfile")
async def get_player_factfile(player: str):
    """Get player factfile/statistics."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    tables = get_all_weeks()
    
    # Gather ranking data
    ranking_dates = []
    rankings = []
    
    for table in tables:
        try:
            cur.execute(f'SELECT rank FROM "{table}" WHERE name = ?', (player,))
            row = cur.fetchone()
            if row:
                rank_str = row[0].replace('T', '')
                try:
                    ranking_dates.append(table)
                    rankings.append(int(rank_str))
                except:
                    continue
        except:
            continue
    
    if not rankings:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Player {player} not found")
    
    # Calculate career high
    career_high = min(rankings)
    career_high_idx = rankings.index(career_high)
    career_high_date = ranking_dates[career_high_idx]
    
    # Gather points data
    points_dates = []
    points = []
    
    for table in tables:
        try:
            cur.execute(f'SELECT points FROM "{table}" WHERE name = ?', (player,))
            row = cur.fetchone()
            if row:
                points_str = row[0].replace(',', '').replace('-', '0')
                try:
                    points_val = int(points_str)
                    points_dates.append(table)
                    points.append(points_val)
                except:
                    continue
        except:
            continue
    
    # Calculate max points
    max_points = max(points) if points else 0
    max_points_date = "No Points System"
    if max_points > 0:
        max_points_idx = points.index(max_points)
        max_points_date = points_dates[max_points_idx]
    
    # Calculate stats
    weeks_top_100 = len(rankings)
    weeks_top_10 = sum(1 for r in rankings if r <= 10)
    weeks_at_1 = sum(1 for r in rankings if r == 1)
    
    conn.close()
    
    return {
        "player": player,
        "career_high_rank": career_high,
        "career_high_date": career_high_date,
        "max_points": f"{max_points:,}" if max_points > 0 else "-",
        "max_points_date": max_points_date,
        "weeks_top_100": weeks_top_100,
        "weeks_top_10": weeks_top_10,
        "weeks_at_1": weeks_at_1
    }


@app.get("/api/player/career")
async def get_player_career(player: str):
    """Get player career data for charting (rankings and points over time)."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    tables = get_all_weeks()
    
    # Gather ranking data
    ranking_dates = []
    rankings = []
    
    for table in tables:
        try:
            cur.execute(f'SELECT rank FROM "{table}" WHERE name = ?', (player,))
            row = cur.fetchone()
            if row:
                rank_str = row[0].replace('T', '')
                try:
                    ranking_dates.append(table)
                    rankings.append(int(rank_str))
                except:
                    continue
        except:
            continue
    
    # Gather points data
    points_dates = []
    points = []
    
    for table in tables:
        try:
            cur.execute(f'SELECT points FROM "{table}" WHERE name = ?', (player,))
            row = cur.fetchone()
            if row:
                points_str = row[0].replace(',', '').replace('-', '0')
                try:
                    points_val = int(points_str)
                    if points_val > 0:  # Only include non-zero points
                        points_dates.append(table)
                        points.append(points_val)
                except:
                    continue
        except:
            continue
    
    conn.close()
    
    if not rankings and not points:
        raise HTTPException(status_code=404, detail=f"Player {player} not found")
    
    return {
        "player": player,
        "ranking_dates": ranking_dates,
        "rankings": rankings,
        "points_dates": points_dates,
        "points": points
    }


@app.get("/api/weeks-at-no1")
async def api_weeks_at_no1():
    """API endpoint to get all players and their weeks at number 1."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    tables = get_all_weeks()
    player_weeks = {}
    
    # Go through all weeks and count how many times each player was #1
    for table in tables:
        try:
            cur.execute(f'SELECT name FROM "{table}" WHERE rank = "1" OR rank = "T1"')
            row = cur.fetchone()
            if row:
                player_name = row[0]
                if player_name not in player_weeks:
                    player_weeks[player_name] = 0
                player_weeks[player_name] += 1
        except:
            continue
    
    conn.close()
    
    # Convert to list of dictionaries
    result = [
        {"player": player, "weeks": weeks}
        for player, weeks in player_weeks.items()
    ]
    
    # Sort by weeks descending
    result.sort(key=lambda x: x["weeks"], reverse=True)
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
