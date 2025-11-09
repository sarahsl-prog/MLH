"""Tests for interacting with a Kali MCP server API.

These tests intentionally mock `requests` so they don't perform network IO.
They demonstrate expected request shapes and basic response handling for a
simple 'ping' command and an auth-failure scenario.
"""
from typing import Any, Dict

import requests


class DummyResponse:
    def __init__(self, status_code: int = 200, json_data: Dict[str, Any] = None, text: str = ""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self) -> Dict[str, Any]:
        return self._json


def test_kali_mcp_ping(monkeypatch):
    """Verify that sending a ping command returns an expected pong-like response."""
    endpoint = "http://localhost:5000/mcp/commands"
    payload = {"command": "ping"}
    expected = {"status": "ok", "result": "pong"}

    def fake_post(url, json=None, headers=None, timeout=5):
        # Basic assertions about the outgoing request shape
        assert url == endpoint
        assert json == payload
        return DummyResponse(status_code=200, json_data=expected)

    monkeypatch.setattr(requests, "post", fake_post)

    resp = requests.post(endpoint, json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["result"] == "pong"


def test_kali_mcp_auth_failure(monkeypatch):
    """Simulate an authentication failure from the MCP server (401 response)."""
    endpoint = "http://localhost:5000/mcp/commands"
    payload = {"command": "status"}

    def fake_post(url, json=None, headers=None, timeout=5):
        assert url == endpoint
        return DummyResponse(status_code=401, json_data={"error": "unauthorized"}, text="Unauthorized")

    monkeypatch.setattr(requests, "post", fake_post)

    resp = requests.post(endpoint, json=payload)
    assert resp.status_code == 401
    data = resp.json()
    assert data.get("error") == "unauthorized"
