# Personal API Security Tester

A small, fast tool to run lightweight security checks against your API endpoints and generate a short "report card." It's designed for developers to quickly validate their own projects for common misconfigurations and obvious vulnerabilities (authentication bypass, basic injection attempts, and simple rate-limit checks). This is not a replacement for a professional penetration test.

## Key Goals

- **Fast**: Repeatable checks you can run locally or in CI
- **Clear**: Actionable report card for developers
- **Simple**: Minimal configuration and dependencies
- **Safe**: Non-destructive testing only

## What It Does

- **Authentication checks**: Detects endpoints that accept unauthenticated requests where authentication is expected
- **Injection attempts**: Sends lightweight payloads to detect common reflexive vulnerabilities (SQL/NoSQL injection, XSS) without destructive actions
- **Rate limiting**: Issues controlled burst requests to determine whether endpoints enforce throttling
- **Report generation**: Creates both JSON (machine-readable) and text (human-readable) reports with pass/warn/fail for each check

## Documentation

- **[Usage Guide](docs/USAGE.md)** - Installation, quickstart, and examples
- **[API Documentation](docs/API.md)** - Function reference and parameters
- **[Architecture](docs/ARCHITECTURE.md)** - Design principles and extension points
- **[Contributing](docs/CONTRIBUTING.md)** - Guidelines for contributors

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/apisec-tester.git
cd apisec-tester

# Create and activate virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### 2. Test with the Test Server

Start the test server (includes intentionally vulnerable endpoints):

```bash
python test_server.py
```

In another terminal, run the security checks:

```bash
apisec-tester run \
  --endpoint http://localhost:9876/api/public \
  --endpoint http://localhost:9876/api/protected \
  --endpoint http://localhost:9876/api/search \
  --output report.json
```

Or run the comprehensive test examples:

```bash
python test_examples.py
```

### 3. Test Your Own API

```bash
apisec-tester run \
  --endpoint https://api.example.com/users \
  --endpoint https://api.example.com/posts \
  --output report.json
```

### 4. Interactive Mode

```bash
apisec-tester interactive
```

## Report Output

After running checks, you'll get two files:

- **`report.json`** - Machine-readable JSON with detailed results
- **`report.txt`** - Human-friendly summary with pass/warn/fail counts

Example text report:
```
- [PASS] auth @ https://api.example.com/users: Endpoint requires authentication/authorization.
- [WARN] injection @ https://api.example.com/search: Reflections detected for injection payloads.
- [WARN] rate_limit @ https://api.example.com/data: No rate limiting detected.

Report card:
PASS: 1  WARN: 2  ERROR: 0  INFO: 0
```

## Test Server

The repository includes `test_server.py` - a lightweight Flask server with intentionally vulnerable endpoints for testing:

- **`/api/public`** - No authentication required
- **`/api/protected`** - Requires Bearer token
- **`/api/search`** - Vulnerable to reflection/XSS
- **`/api/sql-error`** - Exposes SQL errors
- **`/api/data`** - No rate limiting
- **`/api/rate-limited`** - Has rate limiting

Start it with:
```bash
python test_server.py
```

Server runs on `http://localhost:9876`

## Security Checks Performed

| Check | Description | Pass Criteria | Warn Criteria |
|-------|-------------|---------------|---------------|
| **auth** | Authentication requirement | Returns 401/403 without credentials | Returns 2xx without credentials |
| **injection** | SQL injection and XSS | No reflections or SQL errors | Payloads reflected or SQL errors exposed |
| **rate_limit** | Rate limiting enforcement | Returns HTTP 429 | No throttling detected |

## Security & Legal

**⚠️ IMPORTANT**: Only run this tool against systems you own or have explicit permission to test. Unauthorized testing is illegal and unethical.

- The tool intentionally avoids destructive payloads
- However, it still performs automated requests that could affect service availability
- Use cautiously against production systems
- Always get written authorization before testing third-party systems

## Project Structure

```
apisec-tester/
├── apisec_tester/          # Main package
│   ├── __init__.py
│   ├── core.py             # Security check functions
│   └── report.py           # Report generation
├── cli.py                  # Command-line interface
├── test_server.py          # Test server with vulnerable endpoints
├── test_examples.py        # Example usage scripts
├── tests/                  # Unit and integration tests
│   ├── test_core.py
│   └── test_kali_mcp*.py
├── docs/                   # Comprehensive documentation
│   ├── USAGE.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── CONTRIBUTING.md
├── requirements.txt        # Python dependencies
├── setup.py                # Package installation
└── README.md               # This file
```

## Programmatic Usage

```python
from apisec_tester import core, report

# Run all checks on an endpoint
results = core.run_all_checks("https://api.example.com/users")

# Generate and print summary
summary = report.summarize(results)
print(summary)

# Save reports
report.write_report(results, json_path="scan.json", txt_path="scan.txt")
```

Individual checks:

```python
from apisec_tester.core import check_auth, check_injection, check_rate_limit

# Check authentication
auth_result = check_auth("https://api.example.com/users")

# Check for injection vulnerabilities
injection_result = check_injection("https://api.example.com/search", param_name="q")

# Check rate limiting
rate_result = check_rate_limit("https://api.example.com/data", attempts=10)
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: API Security Check
on: [pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      - name: Run security checks
        run: |
          apisec-tester run \
            --endpoint http://staging.example.com/api/users \
            --output security-report.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: |
            security-report.json
            security-report.txt
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

- Keep changes small and well-tested
- Include unit tests for new checks
- Update documentation
- Follow PEP 8 style guidelines

## License

[Add your license here]

## Disclaimer

This tool is provided for educational and authorized security testing purposes only. The authors assume no liability for misuse or damage caused by this tool.
