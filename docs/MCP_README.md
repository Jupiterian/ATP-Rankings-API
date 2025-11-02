# ATP Rankings MCP Server

Model Context Protocol (MCP) server for ATP Tennis Rankings historical data. Provides programmatic access to player statistics, career data, and rankings history from 1973 to present.

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol for exposing tools and resources to AI language models. This MCP server allows AI assistants to query ATP tennis rankings data directly.

## Quick Start

### Running the Server

The MCP server is integrated into the main FastAPI application:

```bash
python main.py
```

The server runs on `http://localhost:8000` with MCP endpoints under `/mcp/*`

### Health Check

```bash
curl http://localhost:8000/mcp/health
```

### Get Manifest

```bash
curl http://localhost:8000/mcp/manifest
```

## Available Tools

### 1. search_players
Search for tennis players by name.

**POST** `/mcp/tools/search_players`
```json
{
  "query": "federer",
  "limit": 10
}
```

**GET** `/mcp/tools/search_players?q=federer&limit=10`

**Response:**
```json
{
  "ok": true,
  "result": {
    "players": ["Roger Federer", ...]
  }
}
```

### 2. get_player_factfile
Get comprehensive career statistics for a player.

**POST** `/mcp/tools/get_player_factfile`
```json
{
  "player": "Roger Federer"
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "player": "Roger Federer",
    "career_high_rank": 1,
    "career_high_date": "2004-02-02",
    "max_points": "15,903",
    "max_points_date": "2012-11-05",
    "weeks_top_100": 1234,
    "weeks_top_10": 890,
    "weeks_at_1": 310
  }
}
```

### 3. get_player_career
Get time-series data of player's ranking and points history.

**POST** `/mcp/tools/get_player_career`
```json
{
  "player": "Rafael Nadal"
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "player": "Rafael Nadal",
    "ranking_dates": ["2005-08-08", "2005-08-15", ...],
    "rankings": [49, 45, 43, ...],
    "points_dates": ["2005-08-08", "2005-08-15", ...],
    "points": [823, 845, 890, ...]
  }
}
```

### 4. get_weeks_at_no1
Get all players who held #1 ranking and their weeks at #1.

**GET** `/mcp/tools/get_weeks_at_no1?min_weeks=1&top_n=50`

**Response:**
```json
{
  "ok": true,
  "result": [
    {"player": "Novak Djokovic", "weeks": 428},
    {"player": "Roger Federer", "weeks": 310},
    ...
  ]
}
```

### 5. get_all_weeks
Get list of all available weeks in the database.

**GET** `/mcp/tools/get_all_weeks`

**Response:**
```json
{
  "ok": true,
  "result": {
    "weeks": ["2025-04-21", "2025-04-14", ...],
    "total": 2650
  }
}
```

### 6. get_week_rankings
Get complete ATP rankings for a specific week.

**POST** `/mcp/tools/get_week_rankings`
```json
{
  "week": "2023-01-02"
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "week": "2023-01-02",
    "rankings": [
      {"rank": "1", "name": "Carlos Alcaraz", "points": "6,820"},
      {"rank": "2", "name": "Rafael Nadal", "points": "6,020"},
      ...
    ]
  }
}
```

## Error Handling

All tools return a standard response format:

**Success:**
```json
{
  "ok": true,
  "result": { ... }
}
```

**Error:**
```json
{
  "ok": false,
  "error": "Error message"
}
```

HTTP Status codes:
- `200` - Success
- `404` - Resource not found (player or week)
- `500` - Internal server error

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/test_mcp.py -v

# Run specific test class
pytest tests/test_mcp.py::TestMCPSearchPlayers -v
```

## Integration with AI Assistants

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "atp-rankings": {
      "command": "python",
      "args": ["/path/to/main.py"],
      "env": {
        "PORT": "8000"
      }
    }
  }
}
```

### Custom Integration

Use the manifest to discover available tools:

```python
import requests

# Get manifest
manifest = requests.get("http://localhost:8000/mcp/manifest").json()

# List available tools
for tool in manifest["capabilities"]["tools"]:
    print(f"{tool['name']}: {tool['description']}")
```

## Architecture

The MCP server is built on top of the existing ATP Rankings API:

```
┌─────────────────────┐
│    FastAPI App      │
│    (main.py)        │
├─────────────────────┤
│  MCP Router         │  ← /mcp/* endpoints
│  (mcp_router.py)    │
├─────────────────────┤
│  Service Layer      │  ← Business logic
│  (services.py)      │
├─────────────────────┤
│  SQLite Database    │  ← 2,600+ weeks of data
│  (rankings.db)      │
└─────────────────────┘
```

**Benefits:**
- Single process deployment
- Shared database connections
- Consistent error handling
- Easy to test and maintain

## Deployment

### Local Development
```bash
python main.py
# Server runs on http://localhost:8000
# MCP endpoints at http://localhost:8000/mcp/*
```

### Production (Render/Railway/Heroku)

The MCP server is included in the main application. Use the existing `Procfile`:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t atp-rankings-mcp .
docker run -p 8000:8000 -v $(pwd)/rankings.db:/app/rankings.db atp-rankings-mcp
```

## API Documentation

- **REST API Docs**: http://localhost:8000/api-docs
- **MCP Manifest**: http://localhost:8000/mcp/manifest
- **Health Check**: http://localhost:8000/mcp/health

## License

MIT - See main project LICENSE file
