# Usage Guide

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/apisec-tester.git
cd apisec-tester

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
apisec-tester --help
```

---

## Quick Start

### 1. Test a Single Endpoint

```bash
apisec-tester run --endpoint https://api.example.com/users --output report.json
```

This will:
- Run all security checks on the endpoint
- Generate `report.json` (machine-readable)
- Generate `report.txt` (human-readable)

### 2. Test Multiple Endpoints

```bash
apisec-tester run \
  --endpoint https://api.example.com/users \
  --endpoint https://api.example.com/posts \
  --endpoint https://api.example.com/comments \
  --output full_scan.json
```

### 3. Interactive Mode

For manual testing with guided prompts:

```bash
apisec-tester interactive
```

---

## Command-Line Interface

### `run` Command

Batch mode for automated testing:

```bash
apisec-tester run [OPTIONS]
```

**Options:**
- `--endpoint TEXT` (required, multiple): Endpoint URL(s) to test
- `--output TEXT`: Output file path (default: "report.json")

**Examples:**

Test API endpoints with custom output:
```bash
apisec-tester run \
  --endpoint https://api.myapp.com/login \
  --endpoint https://api.myapp.com/search \
  --output api_security_scan.json
```

### `interactive` Command

Interactive mode with prompts:

```bash
apisec-tester interactive
```

**Flow:**
1. Prompts for endpoint URLs (one per line)
2. Enter blank line to finish
3. Runs all checks
4. Displays results in console
5. Offers to save report

---

## Understanding the Report

### Text Report Format

```
- [PASS] auth @ https://api.example.com/users: Endpoint requires authentication/authorization.
- [WARN] injection @ https://api.example.com/users: Reflections or error strings detected for injection-like payloads.
- [WARN] rate_limit @ https://api.example.com/users: No 429 responses observed — endpoint may not enforce rate limits.

Report card:
PASS: 1  WARN: 2  ERROR: 0  INFO: 0
```

### JSON Report Format

```json
{
  "results": [
    {
      "endpoint": "https://api.example.com/users",
      "check": "auth",
      "status": "pass",
      "status_code": 401,
      "summary": "Endpoint requires authentication/authorization."
    },
    {
      "endpoint": "https://api.example.com/users",
      "check": "injection",
      "status": "warn",
      "evidence": [
        {
          "payload": "<script>alert(1)</script>",
          "type": "reflection"
        }
      ],
      "summary": "Reflections or error strings detected for injection-like payloads."
    },
    {
      "endpoint": "https://api.example.com/users",
      "check": "rate_limit",
      "status": "warn",
      "responses": [200, 200, 200, 200, 200],
      "summary": "No 429 responses observed — endpoint may not enforce rate limits."
    }
  ]
}
```

### Status Codes

- **PASS**: Check passed, security control is in place
- **WARN**: Potential security issue detected
- **ERROR**: Check failed to execute (network error, timeout, etc.)
- **INFO**: Informational result, not a security concern

---

## Programmatic Usage

### Python API

```python
from apisec_tester import core, report

# Test a single endpoint
results = core.run_all_checks("https://api.example.com/users")

# Generate and display summary
summary = report.summarize(results)
print(summary)

# Save reports
report.write_report(results, json_path="scan.json", txt_path="scan.txt")
```

### Individual Checks

```python
from apisec_tester.core import check_auth, check_injection, check_rate_limit

# Authentication check
auth_result = check_auth("https://api.example.com/users")
print(auth_result)
# {"endpoint": "...", "check": "auth", "status": "pass", ...}

# Injection check with custom parameter
injection_result = check_injection(
    "https://api.example.com/search",
    param_name="query"
)

# Rate limit check with custom settings
rate_result = check_rate_limit(
    "https://api.example.com/data",
    attempts=10,
    pause=0.05,
    timeout=3.0
)
```

---

## Common Use Cases

### 1. Pre-Deployment Security Check

Add to your CI/CD pipeline:

```yaml
# .github/workflows/security-check.yml
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
            --endpoint http://staging.example.com/api/posts \
            --output security-report.json
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: |
            security-report.json
            security-report.txt
```

### 2. Local Development Testing

Create a test script:

```python
# test_my_api.py
from apisec_tester import core, report

endpoints = [
    "http://localhost:8000/api/users",
    "http://localhost:8000/api/posts",
    "http://localhost:8000/api/comments",
]

all_results = []
for endpoint in endpoints:
    print(f"Testing {endpoint}...")
    results = core.run_all_checks(endpoint)
    all_results.extend(results)

report.write_report(all_results, json_path="local_test.json", txt_path="local_test.txt")
print("Report saved!")
```

Run it:
```bash
python test_my_api.py
```

### 3. Scheduled Security Audits

Use cron to schedule regular checks:

```bash
# crontab -e
# Run security check every day at 2 AM
0 2 * * * cd /path/to/apisec-tester && .venv/bin/apisec-tester run --endpoint https://api.myapp.com/users --output /var/log/security/daily-$(date +\%Y\%m\%d).json
```

### 4. Testing with Authentication Headers

```python
from apisec_tester.core import check_auth, check_injection, check_rate_limit

# Test authenticated endpoints
headers = {
    "Authorization": "Bearer your-token-here",
    "X-API-Key": "your-api-key"
}

# Run checks with custom headers
auth_result = check_auth(
    "https://api.example.com/protected",
    headers=headers
)

# For authenticated testing, a PASS should indicate 2xx responses
# This tests if the auth token is working correctly
if auth_result["status"] == "warn":
    print("Authenticated endpoint is accessible!")
```

---

## Testing Against the Test Server

The repository includes a lightweight test server with intentionally vulnerable endpoints for testing:

### Start the Test Server

```bash
python test_server.py
```

The server runs on `http://localhost:9876` with the following endpoints:

- `/api/public` - Open endpoint (no auth)
- `/api/protected` - Requires auth
- `/api/search` - Vulnerable to injection
- `/api/data` - No rate limiting

### Test the Server

```bash
apisec-tester run \
  --endpoint http://localhost:9876/api/public \
  --endpoint http://localhost:9876/api/protected \
  --endpoint http://localhost:9876/api/search \
  --endpoint http://localhost:9876/api/data \
  --output test_server_report.json
```

Expected results:
- `/api/public`: WARN on auth check (no auth required)
- `/api/protected`: PASS on auth check (returns 401)
- `/api/search`: WARN on injection check (reflects payloads)
- `/api/data`: WARN on rate limit check (no throttling)

---

## Troubleshooting

### Connection Errors

**Error:** `Connection refused` or `Connection timeout`

**Solutions:**
- Verify the endpoint URL is correct
- Check if the server is running
- Verify network connectivity
- Increase timeout: `check_auth(endpoint, timeout=10.0)`

### SSL Certificate Errors

**Error:** `SSL certificate verify failed`

**Solution (only for testing):**
```python
import requests
from apisec_tester import core

# Disable SSL verification (NOT recommended for production)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Note: core.py would need modification to support verify=False
```

### Rate Limiting During Testing

**Error:** Your own tests trigger rate limits

**Solution:**
- Reduce attempts: `check_rate_limit(endpoint, attempts=3)`
- Increase pause: `check_rate_limit(endpoint, pause=1.0)`
- Test against staging/development environments

---

## Best Practices

### 1. Test in Development First

Always test against development or staging environments before production:

```bash
# Good
apisec-tester run --endpoint https://staging.myapp.com/api

# Use caution
apisec-tester run --endpoint https://production.myapp.com/api
```

### 2. Respect Rate Limits

Even though the tool is non-destructive, be mindful of API rate limits:

```python
# Use conservative settings
check_rate_limit(endpoint, attempts=3, pause=1.0)
```

### 3. Version Control Reports

Add reports to `.gitignore` to avoid committing sensitive information:

```gitignore
# .gitignore
report.json
report.txt
*_report.json
*_report.txt
```

### 4. Review Reports Regularly

Set up a process to review security reports:
- Weekly manual review
- Automated alerts on status changes
- Track improvements over time

### 5. Combine with Other Tools

This tool is lightweight and focused. Combine it with:
- OWASP ZAP for comprehensive scanning
- Burp Suite for manual testing
- Static analysis tools (bandit, semgrep)
- Dependency scanners (pip-audit, safety)

---

## Legal and Ethical Guidelines

### Always Get Permission

Only test systems you own or have explicit written permission to test.

### Authorized Testing Scenarios

- Your own development/staging environments
- Production systems you own
- Systems where you have a signed authorization
- Bug bounty programs with explicit scope

### Unauthorized Testing

Never test:
- Third-party APIs without permission
- Competitor systems
- Production systems without authorization
- Educational/government systems (unless explicitly allowed)

### Responsible Disclosure

If you discover vulnerabilities:
1. Document the issue
2. Contact the security team privately
3. Provide time for remediation
4. Do not publicly disclose until fixed

---

## Getting Help

- GitHub Issues: Report bugs and request features
- Documentation: Refer to `docs/` directory
- Examples: See `examples/` directory (if available)
- Community: Join discussions on GitHub

## Next Steps

- Read `docs/ARCHITECTURE.md` for technical details
- Check `docs/API.md` for function references
- Review `docs/CONTRIBUTING.md` to contribute
- Explore the test suite in `tests/`
