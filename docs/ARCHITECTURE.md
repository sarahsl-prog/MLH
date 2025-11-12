# Architecture Documentation

## Overview

The Personal API Security Tester is a lightweight, non-destructive security testing tool designed for developers to quickly validate their own API endpoints for common security misconfigurations and vulnerabilities.

## Design Principles

1. **Non-destructive**: All checks are read-only and safe to run against production systems
2. **Fast**: Minimal dependencies and optimized for quick feedback
3. **Developer-friendly**: Clear, actionable reports with simple pass/warn/fail statuses
4. **Modular**: Easy to extend with new security checks

## Architecture Components

### 1. Core Module (`apisec_tester/core.py`)

The core module contains all security check functions. Each check function:
- Takes an endpoint URL and optional parameters
- Returns a standardized dictionary with results
- Handles exceptions gracefully
- Uses non-destructive HTTP methods (primarily GET)

#### Check Functions

**`check_auth(endpoint, headers, timeout)`**
- Purpose: Detects if endpoints accept unauthenticated requests
- Logic: Sends requests without credentials and checks for 2xx responses
- Returns: `{"endpoint": str, "check": "auth", "status": str, "summary": str}`

**`check_injection(endpoint, param_name, timeout)`**
- Purpose: Tests for reflection and basic SQL injection vulnerabilities
- Logic: Sends benign injection payloads and looks for reflections or SQL errors
- Payloads:
  - SQL: `' OR '1'='1`
  - XSS: `<script>alert(1)</script>`
  - DOM: `" onmouseover="alert(1)`
- Returns: Evidence list with payload reflections or error matches

**`check_rate_limit(endpoint, attempts, pause, timeout)`**
- Purpose: Validates rate limiting implementation
- Logic: Sends burst requests and looks for HTTP 429 responses
- Returns: List of response codes and status determination

**`run_all_checks(endpoint)`**
- Purpose: Convenience function to run all checks on an endpoint
- Returns: List of all check results

### 2. Report Module (`apisec_tester/report.py`)

Handles result aggregation and output formatting.

**`summarize(results)`**
- Aggregates results into human-readable text
- Counts pass/warn/error/info statuses
- Formats each check result as a line item

**`write_report(results, json_path, txt_path)`**
- Writes JSON report for machine processing
- Writes TXT report for human review
- Default outputs: `report.json` and `report.txt`

### 3. CLI Module (`cli.py`)

Provides command-line interface using Click framework.

**Commands:**

1. `run` - Batch mode for CI/CD integration
   - Accepts multiple `--endpoint` arguments
   - Outputs to specified `--output` file
   - Suitable for automation

2. `interactive` - Interactive mode for manual testing
   - Prompts user for endpoints
   - Shows results in console
   - Offers to save report

### 4. Entry Point (`setup.py`)

Defines package metadata and console script entry point:
```
apisec-tester -> cli:cli
```

## Data Flow

```
User Input (CLI)
    ↓
cli.py (Click commands)
    ↓
core.py (Security checks)
    ↓
HTTP Requests → Target API
    ↓
Results Collection
    ↓
report.py (Formatting)
    ↓
Output Files (JSON + TXT)
```

## Result Schema

Each check returns a dictionary with this structure:

```python
{
    "endpoint": "https://api.example.com/endpoint",
    "check": "auth|injection|rate_limit",
    "status": "pass|warn|error|info",
    "summary": "Human-readable description",
    "status_code": 200,  # optional
    "evidence": [],      # optional for injection checks
    "responses": [],     # optional for rate limit checks
    "error": "error msg" # optional on exception
}
```

## Extension Points

### Adding New Checks

1. Create a new function in `core.py`:
```python
def check_new_vulnerability(endpoint: str, **kwargs) -> Dict:
    result = {"endpoint": endpoint, "check": "new_vuln", "status": "unknown"}
    try:
        # Perform non-destructive check
        # Set result["status"] and result["summary"]
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result
```

2. Add to `run_all_checks()` function
3. Write unit tests in `tests/test_core.py`

### Custom Report Formats

Extend `report.py` to support additional formats:
- HTML reports
- CSV exports
- Dashboard integrations

## Security Considerations

### What This Tool Does NOT Do

- **Not a replacement for professional pentesting**
- **Not comprehensive vulnerability scanning**
- **No exploitation or post-exploitation**
- **No authenticated endpoint testing** (by default)

### Safety Features

1. **Non-destructive payloads**: Only read operations, no DELETE/UPDATE
2. **Timeout protection**: All requests have configurable timeouts
3. **Exception handling**: Graceful failure on network issues
4. **Rate limiting**: Controlled request bursts with pauses

### Legal and Ethical Use

**Only test systems you own or have explicit permission to test.**

Unauthorized security testing is illegal under:
- Computer Fraud and Abuse Act (CFAA) in the US
- Computer Misuse Act in the UK
- Similar laws in other jurisdictions

## Performance Characteristics

- **Typical runtime**: 1-5 seconds per endpoint (3 checks)
- **Network overhead**: ~10-15 requests per endpoint
- **Memory footprint**: Minimal (<10MB typical)
- **Concurrency**: Serial execution (future: parallel check support)

## Dependencies

- **requests**: HTTP client library
- **click**: CLI framework
- **loguru**: Structured logging
- **pytest**: Testing framework (dev only)

All dependencies are pinned in `requirements.txt` for reproducibility.

## Testing Strategy

### Unit Tests

Located in `tests/test_core.py`, using pytest and monkeypatching to mock HTTP requests:

```python
def test_check_auth_401(monkeypatch):
    def fake_get(url, headers=None, timeout=0, allow_redirects=True):
        return DummyResponse(status_code=401)
    monkeypatch.setattr(core.requests, 'get', fake_get)
    result = core.check_auth('http://example.test')
    assert result['status'] == 'pass'
```

### Integration Tests

For real-world testing, use the provided test server (see `test_server.py`) which implements vulnerable endpoints.

## Future Enhancements

1. **Parallel execution**: Check multiple endpoints concurrently
2. **Authentication support**: Test authenticated endpoints with tokens
3. **Custom payloads**: User-defined injection strings
4. **CI/CD plugins**: GitHub Actions, GitLab CI integrations
5. **Baseline comparison**: Track security posture over time
6. **OWASP mapping**: Map checks to OWASP Top 10 categories
