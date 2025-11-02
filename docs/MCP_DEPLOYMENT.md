# MCP Server Deployment Guide

This guide covers deploying the ATP Rankings MCP server to various hosting platforms.

## Quick Deploy Options

### Option 1: Single Process (Recommended)

The MCP server is integrated into the main FastAPI application. Deploy as one service:

```bash
python main.py
```

**Advantages:**
- Simple deployment
- Single process to manage
- Shared database connection
- Lower resource usage

### Option 2: Docker

Use Docker for containerized deployment:

```bash
# Build image
docker build -t atp-rankings-mcp .

# Run container
docker run -d -p 8000:8000 \
  -v $(pwd)/rankings.db:/app/rankings.db:ro \
  --name atp-mcp \
  atp-rankings-mcp

# Check health
curl http://localhost:8000/mcp/health
```

### Option 3: Docker Compose

```bash
docker-compose up -d
```

## Platform-Specific Deployment

### Render.com (Recommended for Web Hosting)

1. **Create New Web Service**
   - Connect your GitHub repository
   - Select: `Web Service`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables** (if needed)
   - None required by default

3. **Database**
   - Include `rankings.db` in your repository
   - OR use Render's disk storage for large DBs

4. **Access**
   - REST API: `https://your-app.onrender.com/api/*`
   - MCP: `https://your-app.onrender.com/mcp/*`

### Railway

1. **Deploy from GitHub**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

2. **Configuration**
   - Railway auto-detects Python and installs requirements
   - Uses Procfile automatically

3. **Access**
   - Railway provides a public URL
   - MCP endpoints: `https://your-app.railway.app/mcp/*`

### Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Launch App**
   ```bash
   fly launch
   # Follow prompts
   ```

3. **Deploy**
   ```bash
   fly deploy
   ```

4. **Access**
   - `https://your-app.fly.dev/mcp/*`

### Heroku

1. **Create Heroku App**
   ```bash
   heroku create atp-rankings-mcp
   ```

2. **Deploy**
   ```bash
   git push heroku main
   ```

3. **Access**
   - `https://atp-rankings-mcp.herokuapp.com/mcp/*`

### AWS EC2 / DigitalOcean / VPS

1. **SSH into server**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install Python & Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3.12 python3-pip
   pip3 install -r requirements.txt
   ```

3. **Run with systemd** (background service)

   Create `/etc/systemd/system/atp-mcp.service`:
   ```ini
   [Unit]
   Description=ATP Rankings MCP Server
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/ATP-Rankings-Data-Visualization
   ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable atp-mcp
   sudo systemctl start atp-mcp
   sudo systemctl status atp-mcp
   ```

4. **Nginx Reverse Proxy** (optional)

   `/etc/nginx/sites-available/atp-mcp`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /mcp/ {
           proxy_pass http://127.0.0.1:8000/mcp/;
           proxy_set_header Host $host;
       }
   }
   ```

## Verifying Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-domain.com/mcp/health

# Manifest
curl https://your-domain.com/mcp/manifest

# Search players
curl -X POST https://your-domain.com/mcp/tools/search_players \
  -H "Content-Type: application/json" \
  -d '{"query":"federer","limit":5}'

# Player factfile
curl -X POST https://your-domain.com/mcp/tools/get_player_factfile \
  -H "Content-Type: application/json" \
  -d '{"player":"Roger Federer"}'
```

## Performance Considerations

### Database Optimization

For large-scale deployments:

1. **Index Creation**
   ```sql
   CREATE INDEX IF NOT EXISTS idx_player_name ON "2023-01-02"(name);
   ```

2. **Connection Pooling**
   - Consider adding SQLAlchemy for connection pooling
   - Update `services.py` to use a connection pool

### Caching

Add Redis caching for frequently accessed data:

```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379)

@lru_cache(maxsize=1000)
def get_player_factfile_cached(player: str):
    # Check Redis first
    cached = redis_client.get(f"factfile:{player}")
    if cached:
        return json.loads(cached)
    
    # Get from DB
    result = get_player_factfile(player)
    
    # Cache for 1 hour
    redis_client.setex(f"factfile:{player}", 3600, json.dumps(result))
    
    return result
```

### Scaling

For high traffic:

1. **Horizontal Scaling**
   - Deploy multiple instances behind a load balancer
   - Use read-only database replicas

2. **CDN**
   - Use Cloudflare or similar for static assets
   - Cache API responses at edge

## Monitoring

### Health Checks

Most platforms support health checks:

```yaml
# Render
healthCheckPath: /mcp/health

# Railway (railway.toml)
[deploy]
healthcheckPath = "/mcp/health"

# Fly.io (fly.toml)
[http_service]
  [http_service.checks]
    [http_service.checks.health]
      path = "/mcp/health"
      interval = "30s"
```

### Logging

View logs:

```bash
# Docker
docker logs -f atp-mcp

# Railway
railway logs

# Heroku
heroku logs --tail

# Fly.io
fly logs
```

## Security

1. **CORS Configuration**
   - Update `main.py` CORS settings for production
   - Restrict origins as needed

2. **Rate Limiting**
   - Add rate limiting middleware
   - Use services like Cloudflare

3. **Environment Variables**
   - Don't commit sensitive data
   - Use platform env var features

## Cost Estimates

### Free Tier Options
- **Render**: 750 hours/month free
- **Railway**: $5 credit/month
- **Fly.io**: Free allowance for small apps
- **Heroku**: Eco dyno ($5/month)

### Paid Options
- **VPS (DigitalOcean)**: $6/month (1GB RAM)
- **AWS EC2**: t2.micro ~$10/month
- **Render Pro**: $7/month

## Troubleshooting

### Common Issues

1. **Port binding errors**
   - Ensure `$PORT` environment variable is used
   - Check Procfile configuration

2. **Database not found**
   - Verify `rankings.db` is in the working directory
   - Check file permissions

3. **Import errors**
   - Ensure all files are deployed
   - Check `requirements.txt` is complete

4. **Slow responses**
   - Add database indexes
   - Implement caching
   - Consider read replicas

## Support

For deployment issues:
- Check logs first
- Verify all files are present
- Test locally before deploying
- Consult platform-specific documentation

GitHub Issues: https://github.com/Jupiterian/ATP-Rankings-Data-Visualization/issues
