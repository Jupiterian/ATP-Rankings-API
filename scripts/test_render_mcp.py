#!/usr/bin/env python3
"""
Test script for AI agent connectivity to deployed MCP server.
Tests all endpoints and verifies responses.

Usage: python test_render_mcp.py https://your-app.onrender.com
"""
import requests
import sys
import json
from datetime import datetime

def test_mcp_server(base_url):
    """Test all MCP endpoints."""
    
    print(f"Testing MCP Server at: {base_url}")
    print("=" * 60)
    print()
    
    tests = []
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/mcp/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ PASS - Status: {data.get('status')}")
            tests.append(True)
        else:
            print(f"   ✗ FAIL - HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ✗ FAIL - {e}")
        tests.append(False)
    
    # Test 2: Manifest
    print("2. Testing manifest...")
    try:
        response = requests.get(f"{base_url}/mcp/manifest", timeout=30)
        if response.status_code == 200:
            data = response.json()
            tools = len(data.get('capabilities', {}).get('tools', []))
            print(f"   ✓ PASS - {tools} tools available")
            tests.append(True)
        else:
            print(f"   ✗ FAIL - HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ✗ FAIL - {e}")
        tests.append(False)
    
    # Test 3: Search players
    print("3. Testing player search...")
    try:
        response = requests.post(
            f"{base_url}/mcp/tools/search_players",
            json={"query": "federer", "limit": 5},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                players = len(data.get('result', {}).get('players', []))
                print(f"   ✓ PASS - Found {players} players")
                tests.append(True)
            else:
                print(f"   ✗ FAIL - Error: {data.get('error')}")
                tests.append(False)
        else:
            print(f"   ✗ FAIL - HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ✗ FAIL - {e}")
        tests.append(False)
    
    # Test 4: Player factfile
    print("4. Testing player factfile...")
    try:
        response = requests.post(
            f"{base_url}/mcp/tools/get_player_factfile",
            json={"player": "Roger Federer"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                weeks_at_1 = data.get('result', {}).get('weeks_at_1', 0)
                print(f"   ✓ PASS - Weeks at #1: {weeks_at_1}")
                tests.append(True)
            else:
                print(f"   ✗ FAIL - Error: {data.get('error')}")
                tests.append(False)
        else:
            print(f"   ✗ FAIL - HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ✗ FAIL - {e}")
        tests.append(False)
    
    # Test 5: Player career
    print("5. Testing player career data...")
    try:
        response = requests.post(
            f"{base_url}/mcp/tools/get_player_career",
            json={"player": "Rafael Nadal"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                weeks = len(data.get('result', {}).get('rankings', []))
                print(f"   ✓ PASS - {weeks} weeks of data")
                tests.append(True)
            else:
                print(f"   ✗ FAIL - Error: {data.get('error')}")
                tests.append(False)
        else:
            print(f"   ✗ FAIL - HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ✗ FAIL - {e}")
        tests.append(False)
    
    # Test 6: Weeks at #1
    print("6. Testing weeks at #1...")
    try:
        response = requests.get(
            f"{base_url}/mcp/tools/get_weeks_at_no1?top_n=5",
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                players = len(data.get('result', []))
                print(f"   ✓ PASS - Top {players} players retrieved")
                tests.append(True)
            else:
                print(f"   ✗ FAIL - Error: {data.get('error')}")
                tests.append(False)
        else:
            print(f"   ✗ FAIL - HTTP {response.status_code}")
            tests.append(False)
    except Exception as e:
        print(f"   ✗ FAIL - {e}")
        tests.append(False)
    
    # Summary
    print()
    print("=" * 60)
    passed = sum(tests)
    total = len(tests)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! MCP server is working correctly.")
        print(f"\nYour MCP server is ready at: {base_url}/mcp/*")
        print("\nNext steps:")
        print("1. Configure your AI agent with this URL")
        print("2. Use the endpoints documented in MCP_README.md")
        print("3. Monitor usage in Render dashboard")
        return True
    else:
        print("✗ Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Verify the deployment completed successfully in Render")
        print("2. Check Render logs for errors")
        print("3. Ensure rankings.db is included in your deployment")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_render_mcp.py <render-url>")
        print("Example: python test_render_mcp.py https://your-app.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    
    print(f"[{datetime.now()}] Starting MCP server tests...")
    print()
    
    success = test_mcp_server(url)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
