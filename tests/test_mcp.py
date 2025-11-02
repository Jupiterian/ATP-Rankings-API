"""
Tests for MCP endpoints.
Run with: pytest tests/test_mcp.py -v
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app

client = TestClient(app)


class TestMCPHealth:
    """Test MCP health and manifest endpoints."""
    
    def test_health_endpoint(self):
        """Test MCP health check returns OK."""
        response = client.get("/mcp/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
    
    def test_manifest_endpoint(self):
        """Test MCP manifest returns valid schema."""
        response = client.get("/mcp/manifest")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "capabilities" in data
        assert "tools" in data["capabilities"]


class TestMCPSearchPlayers:
    """Test player search MCP tool."""
    
    def test_search_players_post_success(self):
        """Test searching for players via POST."""
        response = client.post(
            "/mcp/tools/search_players",
            json={"query": "federer", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data
        assert "players" in data["result"]
        assert len(data["result"]["players"]) > 0
    
    def test_search_players_get_success(self):
        """Test searching for players via GET."""
        response = client.get("/mcp/tools/search_players?q=nadal&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "players" in data["result"]
    
    def test_search_players_no_results(self):
        """Test search with query that returns no results."""
        response = client.post(
            "/mcp/tools/search_players",
            json={"query": "zzzznonexistent", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert len(data["result"]["players"]) == 0


class TestMCPPlayerFactfile:
    """Test player factfile MCP tool."""
    
    def test_get_factfile_success(self):
        """Test getting factfile for existing player."""
        response = client.post(
            "/mcp/tools/get_player_factfile",
            json={"player": "Roger Federer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data
        result = data["result"]
        assert result["player"] == "Roger Federer"
        assert "career_high_rank" in result
        assert "weeks_at_1" in result
        assert "weeks_top_10" in result
    
    def test_get_factfile_not_found(self):
        """Test getting factfile for non-existent player."""
        response = client.post(
            "/mcp/tools/get_player_factfile",
            json={"player": "Nonexistent Player"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False
        assert "error" in data


class TestMCPPlayerCareer:
    """Test player career data MCP tool."""
    
    def test_get_career_success(self):
        """Test getting career data for existing player."""
        response = client.post(
            "/mcp/tools/get_player_career",
            json={"player": "Rafael Nadal"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data
        result = data["result"]
        assert result["player"] == "Rafael Nadal"
        assert "ranking_dates" in result
        assert "rankings" in result
        assert len(result["rankings"]) > 0
    
    def test_get_career_not_found(self):
        """Test getting career for non-existent player."""
        response = client.post(
            "/mcp/tools/get_player_career",
            json={"player": "Fake Player Name"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False


class TestMCPWeeksAtNo1:
    """Test weeks at number 1 MCP tool."""
    
    def test_get_weeks_at_no1_get(self):
        """Test getting weeks at #1 via GET."""
        response = client.get("/mcp/tools/get_weeks_at_no1")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data
        assert len(data["result"]) > 0
        # Check first player has most weeks
        assert data["result"][0]["weeks"] > 100
    
    def test_get_weeks_at_no1_with_filters(self):
        """Test filtering weeks at #1 results."""
        response = client.get("/mcp/tools/get_weeks_at_no1?min_weeks=200&top_n=5")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        # All results should have >= 200 weeks
        for player in data["result"]:
            assert player["weeks"] >= 200
        # Should have at most 5 results
        assert len(data["result"]) <= 5


class TestMCPAllWeeks:
    """Test getting all weeks MCP tool."""
    
    def test_get_all_weeks(self):
        """Test getting list of all available weeks."""
        response = client.get("/mcp/tools/get_all_weeks")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data
        assert "weeks" in data["result"]
        assert "total" in data["result"]
        assert data["result"]["total"] > 2000  # Should have 2600+ weeks


class TestMCPWeekRankings:
    """Test getting specific week rankings MCP tool."""
    
    def test_get_week_rankings_success(self):
        """Test getting rankings for a valid week."""
        response = client.post(
            "/mcp/tools/get_week_rankings",
            json={"week": "2023-01-02"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data
        result = data["result"]
        assert result["week"] == "2023-01-02"
        assert "rankings" in result
        assert len(result["rankings"]) > 0
    
    def test_get_week_rankings_not_found(self):
        """Test getting rankings for non-existent week."""
        response = client.post(
            "/mcp/tools/get_week_rankings",
            json={"week": "2099-12-31"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["ok"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
