"""Offline regression tests for the optional weekly rankings import."""

from copy import deepcopy
from pathlib import Path
import runpy
import sqlite3
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import livetennis


@pytest.fixture
def payload():
    return {
        "data": [
            {"system": "atp", "rank": rank, "player_name": f"Player {rank}",
             "player_id": None, "points": 15000 - rank,
             "effective_date": "2026-08-31"}
            for rank in range(1, 101)
        ],
        "meta": {"limit": 100, "offset": 0, "count": 100, "has_more": True,
                 "coverage": {"effective_date": "2026-08-31"}},
    }


@pytest.fixture
def response(monkeypatch, payload):
    response = Mock(status_code=200)
    response.json.return_value = payload
    monkeypatch.setattr(livetennis.requests, "get", Mock(return_value=response))
    return response


def test_import_preserves_schema_names_and_publication_date(response, payload):
    payload["data"][0]["player_name"] = "Christopher O'Connell"
    with sqlite3.connect(":memory:") as conn:
        assert livetennis.update_latest_rankings(conn, "test-key") == ("2026-08-31", True)
        rows = conn.execute('SELECT * FROM "2026-08-31"').fetchall()
    assert len(rows) == 100
    assert rows[0] == ("1", "Christopher O'Connell", "14,999")
    livetennis.requests.get.assert_called_once_with(
        livetennis.RANKINGS_URL,
        params={"system": "atp", "limit": 100, "offset": 0},
        headers={"X-API-Key": "test-key"}, timeout=15, allow_redirects=False,
    )
    response.close.assert_called_once()


def test_existing_week_is_not_overwritten(response):
    with sqlite3.connect(":memory:") as conn:
        conn.execute('CREATE TABLE "2026-08-31" (rank, name, points)')
        conn.execute('INSERT INTO "2026-08-31" VALUES ("1", "Existing", "123")')
        assert livetennis.update_latest_rankings(conn, "test-key") == ("2026-08-31", False)
        assert conn.execute('SELECT * FROM "2026-08-31"').fetchall() == [("1", "Existing", "123")]


def test_tied_ranks_with_different_players_are_valid(payload):
    payload["data"][98]["rank"] = 98
    week, rows = livetennis.parse_rankings(payload)
    assert week == "2026-08-31"
    assert rows[97][0] == rows[98][0] == "98"


@pytest.mark.parametrize("change", [
    lambda p: p.pop("meta"),
    lambda p: p.update(data={}),
    lambda p: p["data"].pop(),
    lambda p: p["data"].append(deepcopy(p["data"][-1])),
    lambda p: p["data"][0].update(system="wta"),
    lambda p: p["data"][0].update(effective_date="2026-08-24"),
    lambda p: p["data"][0].update(player_name=None),
    lambda p: p["data"][0].update(player_name=" "),
    lambda p: p["data"][0].update(rank=True),
    lambda p: p["data"][0].update(rank=0),
    lambda p: p["data"][-1].update(rank=101),
    lambda p: p["data"][1].update(rank=3),
    lambda p: p["data"][0].update(points=None),
    lambda p: p["data"][0].update(points=True),
    lambda p: p["data"][0].update(points=-1),
    lambda p: p["data"].reverse(),
    lambda p: p["data"].__setitem__(1, deepcopy(p["data"][0])),
    lambda p: p["meta"]["coverage"].update(effective_date='2026-08-31"; DROP TABLE x;--'),
    lambda p: p["meta"]["coverage"].update(effective_date="20260831"),
    lambda p: p["meta"]["coverage"].update(effective_date="2999-01-01"),
])
def test_bad_snapshot_never_creates_a_week(response, payload, change):
    change(payload)
    with sqlite3.connect(":memory:") as conn:
        with pytest.raises(ValueError):
            livetennis.update_latest_rankings(conn, "test-key")
        assert conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == []


@pytest.mark.parametrize("body", [None, [], "invalid", {"meta": None}])
def test_invalid_response_shape(body):
    with pytest.raises(ValueError):
        livetennis.parse_rankings(body)


@pytest.mark.parametrize("status", [301, 401, 403, 429, 500])
def test_http_failures_are_safe_and_not_retried(response, status):
    response.status_code = status
    with sqlite3.connect(":memory:") as conn:
        with pytest.raises(ValueError, match="PRO plan" if status == 403 else f"HTTP {status}"):
            livetennis.update_latest_rankings(conn, "test-key")
        assert conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == []
    response.json.assert_not_called()
    response.close.assert_called_once()
    livetennis.requests.get.assert_called_once()


def test_transport_error_does_not_expose_key(response):
    livetennis.requests.get.side_effect = requests.Timeout("sensitive-key")
    with sqlite3.connect(":memory:") as conn:
        with pytest.raises(ValueError, match="Could not reach") as error:
            livetennis.update_latest_rankings(conn, "sensitive-key")
    assert "sensitive-key" not in str(error.value)


def test_invalid_json_closes_response(response):
    response.json.side_effect = ValueError("secret response body")
    with sqlite3.connect(":memory:") as conn:
        with pytest.raises(ValueError, match="returned invalid JSON"):
            livetennis.update_latest_rankings(conn, "test-key")
    response.close.assert_called_once()


def test_insert_failure_rolls_back_the_entire_week(response):
    class FailingConnection(sqlite3.Connection):
        def executemany(self, statement, rows):
            super().executemany(statement, rows[:1])
            raise sqlite3.OperationalError("simulated write failure")

    with sqlite3.connect(":memory:", factory=FailingConnection) as conn:
        with pytest.raises(sqlite3.OperationalError, match="simulated write failure"):
            livetennis.update_latest_rankings(conn, "test-key")
        assert conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == []


def test_import_is_visible_to_existing_services(response, tmp_path, monkeypatch):
    from src import services
    database = tmp_path / "rankings.db"
    with sqlite3.connect(database) as conn:
        livetennis.update_latest_rankings(conn, "test-key")
    monkeypatch.setattr(services, "DB_PATH", str(database))
    assert services.get_week_data("2026-08-31")[0]["points"] == "14,999"
    assert services.get_player_factfile("Player 1")["career_high_rank"] == 1
    assert services.search_players("Player 1")


@pytest.mark.parametrize("status,exit_code", [(200, 0), (403, 1)])
def test_weekly_entrypoint_uses_no_atp_requests(
    response, monkeypatch, tmp_path, status, exit_code
):
    response.status_code = status
    database = tmp_path / "rankings.db"
    connect = sqlite3.connect
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: connect(database))
    monkeypatch.setenv("LIVETENNIS_API_KEY", "test-key")
    scraper = Mock(side_effect=AssertionError("ATP must not be called"))
    monkeypatch.setitem(sys.modules, "generate", SimpleNamespace(
        collectData=scraper, extract_weeks=scraper, fetch_atp_page=scraper,
    ))
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(PROJECT_ROOT / "scripts/filler.py"), run_name="__main__")
    assert error.value.code == exit_code
    scraper.assert_not_called()


def test_no_key_keeps_the_atp_path(monkeypatch):
    monkeypatch.delenv("LIVETENNIS_API_KEY", raising=False)
    scraper = Mock(side_effect=RuntimeError("stop before a network request"))
    monkeypatch.setitem(sys.modules, "generate", SimpleNamespace(
        collectData=Mock(), extract_weeks=Mock(), fetch_atp_page=scraper,
    ))
    with pytest.raises(SystemExit):
        runpy.run_path(str(PROJECT_ROOT / "scripts/filler.py"), run_name="__main__")
    scraper.assert_called_once()
