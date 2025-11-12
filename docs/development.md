# Development & Packaging

Development

- Use a virtual environment for local development. See `docs/installation.md`.
- Run unit tests locally with `pytest` and iterate on code in `apisec_tester/`.
- Use `scripts/probe_kali.py` to discover endpoints on a Kali host when needed.

Packaging

- The project includes `setup.py` and `pyproject.toml` so you can install in editable mode:

```cmd
pip install -e .
```

- The console script `apisec-tester` is provided via `entry_points` in `setup.py` and points to `cli:cli`.

Continuous Integration (suggested)

Add a GitHub Actions workflow that runs unit tests on push/PR. Gate integration tests behind repository secrets and explicit environment variables. Example workflow steps:

1. Checkout code
2. Set up Python
3. Install requirements and the package
4. Run unit tests with `pytest`
5. (Optional) Run integration tests only if a `RUN_INTEGRATION` secret or label is set

Example quick snippet for conditional integration step in GitHub Actions:

```yaml
    - name: Run integration tests
      if: ${{ env.RUN_INTEGRATION == 'true' }}
      run: |
        pytest -q tests/test_kali_mcp_integration.py -q
      env:
        KALI_MCP_INTEGRATION: '1'
        KALI_MCP_URL: ${{ secrets.KALI_MCP_URL }}
```
