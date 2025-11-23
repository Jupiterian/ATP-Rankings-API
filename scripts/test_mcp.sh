#!/bin/bash
# Quick test script for MCP server endpoints

BASE_URL="${BASE_URL:-'https://atp-rankings-data-visualization.onrender.com'}"
echo "Testing MCP Server at: $BASE_URL"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response)"
    fi
}

# Health check
test_endpoint "Health Check" "GET" "/mcp/health"

# Manifest
test_endpoint "Manifest" "GET" "/mcp/manifest"

# Search players (GET)
test_endpoint "Search Players (GET)" "GET" "/mcp/tools/search_players?q=federer&limit=5"

# Search players (POST)
test_endpoint "Search Players (POST)" "POST" "/mcp/tools/search_players" '{"query":"nadal","limit":3}'

# Player factfile
test_endpoint "Player Factfile" "POST" "/mcp/tools/get_player_factfile" '{"player":"Roger Federer"}'

# Player career
test_endpoint "Player Career" "POST" "/mcp/tools/get_player_career" '{"player":"Rafael Nadal"}'

# Weeks at #1
test_endpoint "Weeks at #1" "GET" "/mcp/tools/get_weeks_at_no1"

# All weeks
test_endpoint "All Weeks" "GET" "/mcp/tools/get_all_weeks"

# Week rankings
test_endpoint "Week Rankings" "POST" "/mcp/tools/get_week_rankings" '{"week":"2023-01-02"}'

echo ""
echo "========================================="
echo "Test suite complete!"
echo ""
echo "For detailed responses, run:"
echo "  curl $BASE_URL/mcp/health | jq"
echo "  curl $BASE_URL/mcp/manifest | jq"
