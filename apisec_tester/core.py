"""Core non-destructive checks for the Personal API Security Tester.

Each function returns a small dict with results; these are intentionally simple so
they're easy to test and extend.
"""
from typing import Dict, List
import time

import requests


def check_auth(endpoint: str, headers: Dict[str, str] = None, timeout: float = 5.0) -> Dict:
    """Check whether an endpoint appears to accept unauthenticated requests.

    This is heuristic-based: it will consider a 2xx response without credentials as a potential
    unauthenticated acceptance. It's not authoritative — just a quick heuristic.
    """
    headers = headers or {}
    result = {"endpoint": endpoint, "check": "auth", "status": "unknown"}
    try:
        r = requests.get(endpoint, headers=headers, timeout=timeout, allow_redirects=False)
        result["status_code"] = r.status_code
        if r.status_code >= 200 and r.status_code < 300:
            # 2xx responses without auth supplied -> warn
            result["status"] = "warn"
            result["summary"] = "Endpoint returned 2xx without credentials — possible missing auth."
        elif r.status_code in (401, 403):
            result["status"] = "pass"
            result["summary"] = "Endpoint requires authentication/authorization."
        else:
            result["status"] = "info"
            result["summary"] = f"Received HTTP {r.status_code}."
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result


INJECTION_PAYLOADS = ["' OR '1'='1", "<script>alert(1)</script>", '" onmouseover="alert(1)']
SQL_ERRORS = ["SQL syntax", "mysql", "syntax error", "unterminated string literal"]


def check_injection(endpoint: str, param_name: str = "q", timeout: float = 5.0) -> Dict:
    """Send benign injection-like payloads and look for reflections or error messages.

    This function is intentionally non-destructive: it only sends read (GET) requests and
    looks for obvious reflections or error messages.
    """
    result = {"endpoint": endpoint, "check": "injection", "status": "unknown", "evidence": []}
    try:
        for p in INJECTION_PAYLOADS:
            r = requests.get(endpoint, params={param_name: p}, timeout=timeout)
            text = r.text or ""
            if p in text:
                result["evidence"].append({"payload": p, "type": "reflection"})
            else:
                # crude SQL error check
                for err in SQL_ERRORS:
                    if err.lower() in text.lower():
                        result["evidence"].append({"payload": p, "type": "sql_error", "match": err})
        if result["evidence"]:
            result["status"] = "warn"
            result["summary"] = "Reflections or error strings detected for injection-like payloads."
        else:
            result["status"] = "pass"
            result["summary"] = "No obvious reflection or SQL errors detected for basic payloads."
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result


def check_rate_limit(endpoint: str, attempts: int = 5, pause: float = 0.1, timeout: float = 5.0) -> Dict:
    """Send a small burst of requests and look for status 429 or signs of throttling.

    This performs a few fast GETs and reports if any 429 responses are returned.
    """
    result = {"endpoint": endpoint, "check": "rate_limit", "status": "unknown", "responses": []}
    try:
        for i in range(attempts):
            r = requests.get(endpoint, timeout=timeout)
            result["responses"].append(r.status_code)
            time.sleep(pause)
        if 429 in result["responses"]:
            result["status"] = "pass"
            result["summary"] = "Rate limiting observed (429 returned)."
        else:
            # heuristic: if many distinct 2xx/5xx pattern -> warn that no throttling detected
            result["status"] = "warn"
            result["summary"] = "No 429 responses observed — endpoint may not enforce rate limits."
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result


def run_all_checks(endpoint: str) -> List[Dict]:
    """Run the basic checks and return a list of results."""
    results = []
    results.append(check_auth(endpoint))
    results.append(check_injection(endpoint))
    results.append(check_rate_limit(endpoint))
    return results
