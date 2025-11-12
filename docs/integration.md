# Integration with Kali MCP

This project includes optional integration with a Kali MCP server. The example client and the integration tests assume the Kali server exposes the following endpoints:

- `GET /health` — returns JSON status information including `status` and optionally `tools_status`.
- `POST /api/command` — accepts `{"command": "..."}` and returns JSON with the command output or status.

The repository includes:

- `mcp_server.py` — example code that configures a `KaliToolsClient` to call the above endpoints and exposes tools via a local MCP server wrapper.
- `scripts/probe_kali.py` — safe probe utility to discover the correct endpoints if they differ.
- `tests/test_kali_mcp_integration.py` — gated integration tests that verify the health endpoint and a benign command execution.

Running the integration tests

Set the environment variable `KALI_MCP_INTEGRATION=1` before running the tests. You can also set `KALI_MCP_URL` to point to a specific host.

Safety

- Integration tests are non-destructive: `POST /api/command` in tests uses benign commands like `echo hello`.
- Only run these tests against machines you own or have explicit permission to test.
