# API Documentation

## Core Module (`apisec_tester.core`)

### Functions

#### `check_auth(endpoint, headers=None, timeout=5.0)`

Checks whether an endpoint accepts unauthenticated requests.

**Parameters:**
- `endpoint` (str): The URL to test
- `headers` (dict, optional): Custom headers to send with the request
- `timeout` (float, optional): Request timeout in seconds (default: 5.0)

**Returns:**
- `dict`: Result dictionary with the following keys:
  - `endpoint` (str): The tested endpoint URL
  - `check` (str): Always "auth"
  - `status` (str): One of "pass", "warn", "error", "info"
  - `status_code` (int, optional): HTTP response code
  - `summary` (str): Human-readable result description
  - `error` (str, optional): Error message if exception occurred

**Status Values:**
- `"pass"`: Endpoint requires authentication (401/403 response)
- `"warn"`: Endpoint returned 2xx without credentials
- `"info"`: Received other status code
- `"error"`: Request failed with exception

**Example:**
```python
from apisec_tester.core import check_auth

result = check_auth("https://api.example.com/users")
# {
#     "endpoint": "https://api.example.com/users",
#     "check": "auth",
#     "status": "warn",
#     "status_code": 200,
#     "summary": "Endpoint returned 2xx without credentials — possible missing auth."
# }
```

---

#### `check_injection(endpoint, param_name='q', timeout=5.0)`

Tests for reflection and basic injection vulnerabilities.

**Parameters:**
- `endpoint` (str): The URL to test
- `param_name` (str, optional): Query parameter name to inject payloads into (default: "q")
- `timeout` (float, optional): Request timeout in seconds (default: 5.0)

**Returns:**
- `dict`: Result dictionary with the following keys:
  - `endpoint` (str): The tested endpoint URL
  - `check` (str): Always "injection"
  - `status` (str): One of "pass", "warn", "error"
  - `evidence` (list): List of detected vulnerabilities, each with:
    - `payload` (str): The test payload
    - `type` (str): Either "reflection" or "sql_error"
    - `match` (str, optional): Matched SQL error string
  - `summary` (str): Human-readable result description
  - `error` (str, optional): Error message if exception occurred

**Payloads Tested:**
- `' OR '1'='1` - SQL injection
- `<script>alert(1)</script>` - XSS
- `" onmouseover="alert(1)` - DOM XSS

**SQL Error Patterns:**
- "SQL syntax"
- "mysql"
- "syntax error"
- "unterminated string literal"

**Status Values:**
- `"pass"`: No reflections or SQL errors detected
- `"warn"`: Reflections or SQL errors found
- `"error"`: Request failed with exception

**Example:**
```python
from apisec_tester.core import check_injection

result = check_injection("https://api.example.com/search", param_name="query")
# {
#     "endpoint": "https://api.example.com/search",
#     "check": "injection",
#     "status": "warn",
#     "evidence": [
#         {
#             "payload": "<script>alert(1)</script>",
#             "type": "reflection"
#         }
#     ],
#     "summary": "Reflections or error strings detected for injection-like payloads."
# }
```

---

#### `check_rate_limit(endpoint, attempts=5, pause=0.1, timeout=5.0)`

Tests for rate limiting by sending a burst of requests.

**Parameters:**
- `endpoint` (str): The URL to test
- `attempts` (int, optional): Number of requests to send (default: 5)
- `pause` (float, optional): Seconds to wait between requests (default: 0.1)
- `timeout` (float, optional): Request timeout in seconds (default: 5.0)

**Returns:**
- `dict`: Result dictionary with the following keys:
  - `endpoint` (str): The tested endpoint URL
  - `check` (str): Always "rate_limit"
  - `status` (str): One of "pass", "warn", "error"
  - `responses` (list): List of HTTP status codes received
  - `summary` (str): Human-readable result description
  - `error` (str, optional): Error message if exception occurred

**Status Values:**
- `"pass"`: HTTP 429 (Too Many Requests) observed
- `"warn"`: No rate limiting detected
- `"error"`: Request failed with exception

**Example:**
```python
from apisec_tester.core import check_rate_limit

result = check_rate_limit("https://api.example.com/data", attempts=10, pause=0.05)
# {
#     "endpoint": "https://api.example.com/data",
#     "check": "rate_limit",
#     "status": "pass",
#     "responses": [200, 200, 200, 429, 429, 429, 429, 429, 429, 429],
#     "summary": "Rate limiting observed (429 returned)."
# }
```

---

#### `run_all_checks(endpoint)`

Convenience function to run all available checks on an endpoint.

**Parameters:**
- `endpoint` (str): The URL to test

**Returns:**
- `list[dict]`: List of result dictionaries from all checks

**Example:**
```python
from apisec_tester.core import run_all_checks

results = run_all_checks("https://api.example.com/endpoint")
# [
#     {"endpoint": "...", "check": "auth", "status": "pass", ...},
#     {"endpoint": "...", "check": "injection", "status": "warn", ...},
#     {"endpoint": "...", "check": "rate_limit", "status": "warn", ...}
# ]
```

---

## Report Module (`apisec_tester.report`)

### Functions

#### `summarize(results)`

Generates a human-readable summary from check results.

**Parameters:**
- `results` (list[dict]): List of result dictionaries from security checks

**Returns:**
- `str`: Formatted text summary with:
  - Line-by-line check results
  - Overall counts of pass/warn/error/info statuses

**Example:**
```python
from apisec_tester.report import summarize

results = [
    {"endpoint": "https://api.example.com/users", "check": "auth", "status": "pass", "summary": "Auth required"},
    {"endpoint": "https://api.example.com/users", "check": "injection", "status": "warn", "summary": "Reflection detected"}
]

summary = summarize(results)
print(summary)
# - [PASS] auth @ https://api.example.com/users: Auth required
# - [WARN] injection @ https://api.example.com/users: Reflection detected
#
# Report card:
# PASS: 1  WARN: 1  ERROR: 0  INFO: 0
```

---

#### `write_report(results, json_path='report.json', txt_path='report.txt')`

Writes check results to both JSON and text files.

**Parameters:**
- `results` (list[dict]): List of result dictionaries from security checks
- `json_path` (str, optional): Path for JSON output (default: "report.json")
- `txt_path` (str, optional): Path for text output (default: "report.txt")

**Returns:**
- `None`

**Side Effects:**
- Creates JSON file with structured results
- Creates text file with human-readable summary

**Example:**
```python
from apisec_tester.core import run_all_checks
from apisec_tester.report import write_report

results = run_all_checks("https://api.example.com/endpoint")
write_report(results, json_path="my_report.json", txt_path="my_report.txt")
```

**JSON Output Format:**
```json
{
  "results": [
    {
      "endpoint": "https://api.example.com/endpoint",
      "check": "auth",
      "status": "pass",
      "status_code": 401,
      "summary": "Endpoint requires authentication/authorization."
    }
  ]
}
```

---

## CLI Module (`cli`)

### Commands

#### `apisec-tester run`

Runs security checks in batch mode.

**Options:**
- `--endpoint` (required, multiple): One or more endpoint URLs to test
- `--output` (optional): JSON output file path (default: "report.json")

**Example:**
```bash
apisec-tester run \
  --endpoint https://api.example.com/users \
  --endpoint https://api.example.com/posts \
  --output security_report.json
```

---

#### `apisec-tester interactive`

Runs security checks in interactive mode with prompts.

**Example:**
```bash
apisec-tester interactive

# Personal API Security Tester — interactive mode
# Enter endpoint (blank to finish): https://api.example.com/users
# Enter endpoint (blank to finish): https://api.example.com/posts
# Enter endpoint (blank to finish):
# Running quick checks for 2 endpoint(s)...
#  - https://api.example.com/users
#  - https://api.example.com/posts
#
# ---
#
# [Results displayed here]
#
# Save report to report.json? [y/N]:
```

---

## Constants

### `INJECTION_PAYLOADS`

List of test payloads used by `check_injection()`:
```python
[
    "' OR '1'='1",              # SQL injection
    "<script>alert(1)</script>", # XSS
    '" onmouseover="alert(1)'    # DOM XSS
]
```

### `SQL_ERRORS`

List of SQL error patterns searched in responses:
```python
[
    "SQL syntax",
    "mysql",
    "syntax error",
    "unterminated string literal"
]
```

---

## Type Hints

The codebase uses Python type hints for better IDE support:

```python
from typing import Dict, List

def check_auth(endpoint: str, headers: Dict[str, str] = None, timeout: float = 5.0) -> Dict:
    ...

def run_all_checks(endpoint: str) -> List[Dict]:
    ...
```

---

## Error Handling

All check functions follow a consistent error handling pattern:

```python
try:
    # Perform check
    result["status"] = "pass" | "warn" | "info"
    result["summary"] = "..."
except Exception as e:
    result["status"] = "error"
    result["error"] = str(e)
return result
```

This ensures checks never raise uncaught exceptions and always return a valid result dictionary.
