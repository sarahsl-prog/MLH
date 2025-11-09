"""Integration tests for a Kali MCP server API.

These tests are gated to avoid running during normal CI or unit test runs.
To execute the integration test set the environment variable:

  KALI_MCP_INTEGRATION=1

Optionally override the host using `KALI_MCP_URL` (defaults to the URL you provided).
"""
import os
import requests
import pytest


KALI_URL = os.getenv("KALI_MCP_URL", "http://192.168.0.250:5000")
ENDPOINT = f"{KALI_URL.rstrip('/')}/mcp/commands"

pytestmark = pytest.mark.skipif(os.getenv("KALI_MCP_INTEGRATION") != "1",
                                reason="Integration tests disabled. Set KALI_MCP_INTEGRATION=1 to run.")


def test_kali_mcp_health():
  """Check the Kali server health endpoint as the primary non-destructive integration check."""
  health_url = f"{KALI_URL.rstrip('/')}/health"
  resp = requests.get(health_url, timeout=10)
  assert resp.status_code == 200, f"unexpected status {resp.status_code}: {resp.text}"
  data = resp.json()
  # Expect a health/status key and optionally tools_status
  assert "status" in data


def test_kali_mcp_execute_command():
  """Try a basic execute_command via POST /api/command and expect a JSON response.

  This is intentionally permissive about the exact response shape because different Kali
  MCP server deployments may return different structures. We only assert that the
  endpoint exists and returns JSON with a successful HTTP code.
  """
  cmd_url = f"{KALI_URL.rstrip('/')}/api/command"
  resp = requests.post(cmd_url, json={"command": "echo hello"}, timeout=10)
  assert resp.status_code == 200, f"unexpected status {resp.status_code}: {resp.text}"
  # ensure response is JSON-decodable
  _ = resp.json()
