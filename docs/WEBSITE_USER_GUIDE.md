# ATP Rankings Website User Guide

This guide describes the key features, core functionality, and day-to-day operation of the ATP Rankings Database website.

## Website overview

The ATP Rankings Database is a FastAPI web application for exploring historical ATP rankings. It lets users browse weekly ranking snapshots, search players, compare player careers, visualize weeks at world number one, and access the same data through REST and MCP endpoints.

## Key features

- **Historical rankings archive:** Browse more than 2,600 weekly ATP ranking tables, grouped by year from the home page.
- **Weekly rankings pages:** Open any ranking week to view ranked players, ranking positions, and points for that date.
- **Player filtering:** Filter weekly ranking tables directly in the browser to quickly find a player.
- **Player comparison:** Search for players, display statistical factfiles, and compare ranking or points histories with interactive charts.
- **Weeks at number one chart:** View and filter a leaderboard of players who reached ATP number one.
- **REST API access:** Use documented JSON endpoints for weeks, weekly rankings, player search, player factfiles, career data, and weeks-at-number-one data.
- **MCP integration:** Connect AI assistants and other MCP-compatible clients to the rankings dataset through the included MCP endpoints.
- **Responsive interface:** The site uses shared theme styles for desktop and mobile-friendly navigation.

## Main website pages

### Home page (`/`)

The home page is the central navigation hub. Use it to:

1. Review the total number of available ranking weeks and the coverage span.
2. Open API documentation, raw weeks JSON, player comparison, weeks-at-number-one, or MCP health links.
3. Search for a specific ranking date, such as `2010-01-04`.
4. Expand a year and select an individual week.

### Weekly rankings page (`/week/{week_date}`)

A weekly rankings page shows the ranking table for one Monday snapshot. Use it to:

1. Review each player rank, name, and points total.
2. Type in the filter box to narrow the visible table rows by player name.
3. Use the previous and next week buttons to move through the archive.
4. Return to the archive with the back-to-archive button.

### Player comparison page (`/compare`)

The player comparison page supports player-level research. Use it to:

1. Type a player name into the search field.
2. Select a suggested player result when available.
3. Add one or more players to the comparison area.
4. Review factfile statistics, including career-high rank, career-high date, maximum points, weeks in the top 100, weeks in the top 10, and weeks at number one.
5. Switch between ranking-history and points-history charts.
6. Remove players from the comparison when finished.

### Weeks at number one page (`/weeks-at-no1`)

The weeks-at-number-one page summarizes ATP number one history. Use it to:

1. Review the number-one leaderboard visualization.
2. Set a minimum-weeks threshold.
3. Choose how many leaderboard entries to display.
4. Update the chart to focus on the selected range.
5. Navigate to home, player comparison, or API documentation.

### API documentation page (`/api-docs`)

The API documentation page lists supported REST endpoints, parameters, example requests, and response shapes. Use it when building integrations, scripts, dashboards, or tests against the rankings data.

## REST API operations

Use these endpoints for programmatic access:

- `GET /api/weeks`: Return all available ranking weeks.
- `GET /api/week/{week_date}`: Return rankings for a selected week.
- `GET /api/players/search?q={query}&limit={limit}`: Search player names.
- `GET /api/player/factfile?player={player}`: Return summary statistics for a player.
- `GET /api/player/career?player={player}`: Return a player's ranking and points time series.
- `GET /api/weeks-at-no1`: Return the number-one leaderboard.

## MCP operations

The MCP server is mounted under `/mcp` and is intended for AI assistant access. Common operations include:

- `GET /mcp/health`: Confirm the MCP server is available.
- `GET /mcp/manifest`: Inspect MCP capabilities and tool definitions.
- `POST /mcp/tools/search_players`: Search for player names.
- `POST /mcp/tools/get_player_factfile`: Retrieve player summary statistics.
- `POST /mcp/tools/get_player_career`: Retrieve career time-series data.
- `GET /mcp/tools/get_weeks_at_no1`: Retrieve number-one leaderboard data.
- `GET /mcp/tools/get_all_weeks`: Retrieve available ranking weeks.
- `POST /mcp/tools/get_week_rankings`: Retrieve rankings for a selected week.

## How to run the website locally

1. Install dependencies with `pip install -r requirements.txt`.
2. Start the FastAPI application with `uvicorn src.main:app --reload`.
3. Open `http://localhost:8000` in a browser.
4. Navigate from the home page or call JSON endpoints directly.

## Typical workflows

### Find a player's rank in a specific week

1. Open the home page.
2. Search for or expand the target year.
3. Select the desired week.
4. Type the player name into the weekly page filter box.

### Compare two players

1. Open `/compare`.
2. Search for the first player and add the result.
3. Search for the second player and add the result.
4. Review both factfile cards.
5. Switch between ranking and points charts as needed.

### Build a simple API integration

1. Call `/api/weeks` to discover valid week dates.
2. Call `/api/week/{week_date}` for rankings from a chosen week.
3. Call `/api/players/search` before requesting exact player data.
4. Call `/api/player/factfile` or `/api/player/career` for player-specific analysis.

## Maintenance and data updates

- Run `python scripts/filler.py` to add the latest rankings data.
- Run `python scripts/generate.py` only when a full database rebuild is needed.
- Run `python scripts/debug.py` to inspect or troubleshoot database table issues.
- Run `pytest tests/test_mcp.py -v` to validate MCP behavior.

## Operational notes

- The site reads from the local SQLite database file `rankings.db`.
- The web application serves templates from `templates/` and static assets from `static/`.
- No authentication is required by default.
- CORS is enabled for broad client access; restrict it before deploying in sensitive production environments.
