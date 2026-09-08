# ATP Rankings MCP Server

A real Model Context Protocol (MCP) server for ATP Tennis Rankings historical data. Provides programmatic access to player statistics, career data, and rankings history from 1973 to present.

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) is a standardized JSON-RPC 2.0 protocol for exposing tools and resources to AI language models. This server implements the protocol properly using the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), speaking `initialize` / `tools/list` / `tools/call` over the **Streamable HTTP** transport at a single endpoint — so it can be added directly as a custom connector in Claude.ai or any other MCP-compatible client.

> **Note:** This project also still exposes a legacy set of REST-style endpoints under `/mcp/*` (e.g. `/mcp/health`, `/mcp/tools/search_players`) for backwards compatibility. Those are plain REST endpoints named after MCP concepts — they are **not** a real MCP server and will not work with Claude.ai's custom connector flow. Use the single `/mcp` endpoint described below instead.

## Quick Start

### Running the Server

The MCP server is integrated into the main FastAPI application:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The full app runs on `http://localhost:8000`:
- REST API: `http://localhost:8000/api/*`
- **MCP server (Streamable HTTP): `http://localhost:8000/mcp`**
- Legacy REST-style "MCP" endpoints (deprecated): `http://localhost:8000/mcp/*`

### Testing the Handshake

See [Testing](#testing) below for a script that verifies `initialize` / `tools/list` / `tools/call` all work before you deploy.

## Available Tools

### 1. search_players
Search for tennis players by (partial) name.

- **query** (string, required): search text to match against player names
- **limit** (integer, default `10`): maximum number of results

### 2. get_player_factfile
Get a player's career fact file: career-high rank, peak points, and weeks spent in the top 100 / top 10 / at No. 1.

- **player** (string, required): exact player name as it appears in the rankings data

### 3. get_player_career
Get a player's full time-series career history (rankings and points at every recorded week).

- **player** (string, required): exact player name as it appears in the rankings data

### 4. get_weeks_at_no1
Get every player who has held the World No. 1 ranking, with total weeks held, sorted descending. No arguments.

### 5. get_all_weeks
Get the list of all rankings weeks available in the database. No arguments.

### 6. get_week_rankings
Get the complete ATP rankings for a specific week.

- **week_date** (string, required): week date in `YYYY-MM-DD` format, e.g. `"2023-01-02"`

All tools wrap the same service layer (`src/services.py`) used by the REST API, so results are always consistent between `/api/*` and `/mcp`.

## Error Handling

Per the MCP spec, tool errors (e.g. player or week not found) are returned as a normal JSON-RPC result with `isError: true` and a human-readable message in `content`, rather than an HTTP error status — this is what lets an MCP client (like Claude) see and react to the error within the conversation.

## Testing

A test script is included at `scripts/test_mcp_handshake.py`. It exercises `initialize`, `tools/list`, and a couple of `tools/call` requests against a running server.

```bash
# Against a local server
python scripts/test_mcp_handshake.py http://localhost:8000

# Against your deployed server
python scripts/test_mcp_handshake.py https://your-app.onrender.com
```

Or with raw `curl`:

```bash
# 1. Initialize
curl -i -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl-test","version":"0.1"}}}'

# 2. List tools
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# 3. Call a tool
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_players","arguments":{"query":"djokovic","limit":5}}}'
```

The server runs in `stateless_http` mode, so no session ID needs to be tracked between requests — each call above works independently.

The legacy REST-style tests still live in `tests/test_mcp.py` and exercise the `/mcp/tools/*` endpoints; they are unaffected by this server.

## Integration with AI Assistants

### Claude.ai (custom connector)

In Claude.ai, go to **Settings → Connectors → Add custom connector** and enter your deployed server's `/mcp` URL, e.g.:

```
https://your-app.onrender.com/mcp
```

No authentication is required.

### Claude Desktop

Claude Desktop's config connects to a *local* MCP server process rather than a remote HTTP URL, so instead point it at a local `mcp-remote`/HTTP-capable launcher, or run the FastAPI app locally and use `http://localhost:8000/mcp` with an MCP client that supports Streamable HTTP.

### Custom Integration

Any MCP client that supports the Streamable HTTP transport can connect directly to `/mcp` and use the standard `initialize` → `tools/list` → `tools/call` flow — no separate manifest endpoint is needed (tool discovery happens via `tools/list`).

## Architecture

```
┌──────────────────────────────┐
│         FastAPI App          │
│         (main.py)            │
├───────────────┬───────────────┤
│  REST API     │   MCP Server   │  ← /mcp (Streamable HTTP, JSON-RPC 2.0)
│  (/api/*)     │  (mcp_server.py)│
├───────────────┴───────────────┤
│         Service Layer         │  ← Business logic (services.py)
├────────────────────────────────┤
│         SQLite Database        │  ← 2,600+ weeks of data
│         (rankings.db)          │
└────────────────────────────────┘
```

**Benefits:**
- Single process deployment
- Shared database connections and service layer with the REST API
- Standards-compliant MCP transport, usable by Claude.ai and any other MCP client
- Existing REST API (`/api/*`) is untouched

## Deployment

### Local Development
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
# REST API at http://localhost:8000/api/*
# MCP server at http://localhost:8000/mcp
```

### Production (Render/Railway/Heroku)

No changes needed to the existing `Procfile`:

```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

The MCP server is mounted on the same FastAPI app and deploys with it automatically.

## API Documentation

- **REST API Docs**: http://localhost:8000/api-docs
- **MCP Endpoint**: http://localhost:8000/mcp
- **Legacy MCP-style Health Check** (deprecated): http://localhost:8000/mcp/health

## License

MIT - See main project LICENSE file
