#!/usr/bin/env python3
"""
Keep-alive script for Render free tier.
Pings the MCP server every 10 minutes to prevent cold starts.

Usage: python keep_alive.py https://your-app.onrender.com
"""
import requests
import time
import sys
from datetime import datetime

def ping_server(url):
    """Ping the MCP health endpoint."""
    try:
        response = requests.get(f"{url}/mcp/health", timeout=30)
        if response.status_code == 200:
            print(f"[{datetime.now()}] ✓ Server is alive (HTTP {response.status_code})")
            return True
        else:
            print(f"[{datetime.now()}] ✗ Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python keep_alive.py <render-url>")
        print("Example: python keep_alive.py https://your-app.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    interval = 600  # 10 minutes
    
    print(f"Starting keep-alive for {url}")
    print(f"Ping interval: {interval} seconds")
    print("-" * 50)
    
    while True:
        ping_server(url)
        time.sleep(interval)

if __name__ == "__main__":
    main()
