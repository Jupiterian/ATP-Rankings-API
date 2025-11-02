# ATP Rankings MCP Server - Dockerfile
FROM python:3.12-slim

LABEL org.opencontainers.image.title="ATP Rankings MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol server for ATP Tennis Rankings historical data"
LABEL org.opencontainers.image.version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY templates/ templates/

# Copy database (or mount as volume in production)
COPY rankings.db .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/mcp/health')" || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
