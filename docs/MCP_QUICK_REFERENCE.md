# MCP Server Quick Reference

## Start Server
```bash
python main.py
# Server: http://localhost:8000
# MCP: http://localhost:8000/mcp/*
```

## Essential Endpoints

### Health & Info
- `GET /mcp/health` - Server status
- `GET /mcp/manifest` - MCP capabilities

### Player Data
- `POST /mcp/tools/search_players` - Find players
  ```json
  {"query": "federer", "limit": 10}
  ```

- `POST /mcp/tools/get_player_factfile` - Stats
  ```json
  {"player": "Roger Federer"}
  ```

- `POST /mcp/tools/get_player_career` - Career data
  ```json
  {"player": "Rafael Nadal"}
  ```

### Rankings Data
- `GET /mcp/tools/get_weeks_at_no1` - #1 history
- `GET /mcp/tools/get_all_weeks` - Available weeks
- `POST /mcp/tools/get_week_rankings` - Week data
  ```json
  {"week": "2023-01-02"}
  ```

## Response Format
```json
{
  "ok": true,
  "result": { /* data */ },
  "error": null  // or error message
}
```

## Test
```bash
# All tests
pytest tests/test_mcp.py -v

# Smoke test
./test_mcp.sh

# Manual
curl http://localhost:8000/mcp/health
```

## Deploy
```bash
# Docker
docker-compose up -d

# Render/Railway
git push origin main
# (Auto-deploys with Procfile)
```

## Files
- **services.py** - Business logic
- **mcp_router.py** - MCP endpoints  
- **mcp_manifest.json** - MCP schema
- **tests/test_mcp.py** - Test suite
- **MCP_README.md** - Full docs
- **MCP_DEPLOYMENT.md** - Deploy guide

## Common Issues

**Port in use?**
```bash
# Kill existing server
pkill -f "python main.py"
```

**Import errors?**
```bash
pip install -r requirements.txt
```

**Database not found?**
```bash
# Check database exists
ls -lh rankings.db
```

## Documentation
- MCP Docs: [MCP_README.md](MCP_README.md)
- Deployment: [MCP_DEPLOYMENT.md](MCP_DEPLOYMENT.md)
- API Docs: http://localhost:8000/api-docs
