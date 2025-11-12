# Project documentation — Personal API Security Tester

This documentation describes how to set up, run, test, and develop the Personal API Security Tester and related Kali MCP integration code in this repository.

Docs:

- [Installation](installation.md)
- [Usage](usage.md)
- [Testing](testing.md)
- [Integration with Kali MCP](integration.md)
- [Development & Packaging](development.md)

Key files and locations

- `README.md` — high-level project description and quickstart
- `requirements.txt` — pinned dependencies for local development
- `setup.py`, `pyproject.toml` — packaging and console script (`apisec-tester`)
- `cli.py` — Click-based CLI entrypoint
- `apisec_tester/` — package with core checks and report generation
- `scripts/probe_kali.py` — safe probe utility for finding MCP endpoints
- `mcp_server.py` — example client that integrates with a Kali MCP server
- `tests/` — unit and integration tests
