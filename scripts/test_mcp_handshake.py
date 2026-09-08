#!/usr/bin/env python3
"""
Test script for the real MCP server (JSON-RPC 2.0 over Streamable HTTP).

Verifies the initialize / tools/list / tools/call handshake against a
running instance of the app before deploying, or against an already
deployed server.

Usage:
    python scripts/test_mcp_handshake.py [base_url]

    base_url defaults to http://localhost:8000
"""
import json
import sys

import requests

DEFAULT_BASE_URL = "http://localhost:8000"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def parse_response(response: requests.Response) -> dict:
    """Parse either a plain JSON body or a single-event SSE body."""
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        for line in response.text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[len("data:"):].strip())
        raise ValueError(f"No data line found in SSE response: {response.text!r}")
    return response.json()


def rpc(base_url: str, method: str, params: dict, request_id: int) -> dict:
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
    response = requests.post(f"{base_url}/mcp", headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return parse_response(response)


def main() -> int:
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else DEFAULT_BASE_URL

    print(f"Testing MCP server at: {base_url}/mcp")
    print("=" * 60)

    ok = True

    # 1. initialize
    print("1. initialize...")
    try:
        result = rpc(
            base_url,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test-mcp-handshake", "version": "0.1"},
            },
            request_id=1,
        )
        server_info = result.get("result", {}).get("serverInfo", {})
        print(f"   PASS - server: {server_info.get('name')} v{server_info.get('version')}")
    except Exception as e:
        print(f"   FAIL - {e}")
        ok = False

    # 2. tools/list
    print("2. tools/list...")
    tool_names = []
    try:
        result = rpc(base_url, "tools/list", {}, request_id=2)
        tools = result.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        expected = {
            "search_players",
            "get_player_factfile",
            "get_player_career",
            "get_weeks_at_no1",
            "get_all_weeks",
            "get_week_rankings",
        }
        missing = expected - set(tool_names)
        if missing:
            print(f"   FAIL - missing tools: {missing}")
            ok = False
        else:
            print(f"   PASS - {len(tool_names)} tools found: {', '.join(tool_names)}")
    except Exception as e:
        print(f"   FAIL - {e}")
        ok = False

    # 3. tools/call - get_all_weeks
    print("3. tools/call get_all_weeks...")
    try:
        result = rpc(base_url, "tools/call", {"name": "get_all_weeks", "arguments": {}}, request_id=3)
        tool_result = result.get("result", {})
        if tool_result.get("isError"):
            print(f"   FAIL - tool returned error: {tool_result}")
            ok = False
        else:
            structured = tool_result.get("structuredContent", {}).get("result", {})
            total = structured.get("total")
            print(f"   PASS - {total} weeks available")
    except Exception as e:
        print(f"   FAIL - {e}")
        ok = False

    # 4. tools/call - search_players
    print("4. tools/call search_players...")
    try:
        result = rpc(
            base_url,
            "tools/call",
            {"name": "search_players", "arguments": {"query": "djokovic", "limit": 5}},
            request_id=4,
        )
        tool_result = result.get("result", {})
        if tool_result.get("isError"):
            print(f"   FAIL - tool returned error: {tool_result}")
            ok = False
        else:
            players = tool_result.get("structuredContent", {}).get("result", {}).get("players", [])
            print(f"   PASS - found players: {players}")
    except Exception as e:
        print(f"   FAIL - {e}")
        ok = False

    # 5. tools/call - not-found error path
    print("5. tools/call get_player_factfile (expected error)...")
    try:
        result = rpc(
            base_url,
            "tools/call",
            {"name": "get_player_factfile", "arguments": {"player": "Nonexistent Player XYZ"}},
            request_id=5,
        )
        tool_result = result.get("result", {})
        if tool_result.get("isError"):
            print("   PASS - tool correctly reported isError=true")
        else:
            print(f"   FAIL - expected isError=true, got: {tool_result}")
            ok = False
    except Exception as e:
        print(f"   FAIL - {e}")
        ok = False

    print("=" * 60)
    if ok:
        print("All checks passed. Connector URL to use in Claude.ai:")
        print(f"  {base_url}/mcp")
        return 0
    else:
        print("Some checks failed - see above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
