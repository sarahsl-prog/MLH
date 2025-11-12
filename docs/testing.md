# Testing

Unit tests

Run all unit tests with `pytest`:

```cmd
.venv\Scripts\activate
pytest -q
```

Integration tests

Integration tests are gated to avoid accidental network calls. To run the Kali MCP integration test set the environment variable `KALI_MCP_INTEGRATION=1` and optionally `KALI_MCP_URL` if your Kali host is at a different address.

Windows example (cmd.exe):

```cmd
set KALI_MCP_INTEGRATION=1
set KALI_MCP_URL=http://192.168.0.250:5000
pytest -q tests/test_kali_mcp_integration.py -q
```

Notes

- Integration tests perform non-destructive HTTP requests and must only be run against hosts you control or have permission to test.
- The probe script `scripts/probe_kali.py` can help discover endpoints if your Kali server uses alternate paths.
