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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
