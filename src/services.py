"""
Service layer for ATP Rankings data access.
Contains reusable business logic for both REST API and MCP endpoints.
"""
import sqlite3
from typing import List, Dict, Any, Tuple
from pathlib import Path

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
        raise ValueError(f"Week {week} not found")
    
    # Get data from the week table
    cur.execute(f'SELECT * FROM "{week}";')
    rows = cur.fetchall()
    conn.close()
    
    data = []
    for row in rows:
        data.append({
            "rank": row["rank"],
            "name": row["name"],
            "points": row["points"]
        })
    
    return data


def search_players(query: str, limit: int = 10) -> List[str]:
    """Search for players in the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    tables = get_all_weeks()
    players = set()
    search_query = query.lower()
    
    for table in tables[:100]:  # Search through recent tables for performance
        try:
            cur.execute(f'SELECT DISTINCT name FROM "{table}" WHERE LOWER(name) LIKE ?', (f'%{search_query}%',))
            rows = cur.fetchall()
            for row in rows:
                players.add(row[0])
                if len(players) >= limit * 2:
                    break
        except:
            continue
        
        if len(players) >= limit * 2:
            break
    
    conn.close()
    
    # Sort and limit results
    sorted_players = sorted(list(players))[:limit]
    return sorted_players


def get_player_factfile(player: str) -> Dict[str, Any]:
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
        raise ValueError(f"Player {player} not found")
    
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


def get_player_career(player: str) -> Dict[str, Any]:
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
        raise ValueError(f"Player {player} not found")
    
    return {
        "player": player,
        "ranking_dates": ranking_dates,
        "rankings": rankings,
        "points_dates": points_dates,
        "points": points
    }


def get_weeks_at_no1() -> List[Dict[str, Any]]:
    """Get all players and their weeks at number 1."""
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
