"""
Example scripts for testing the API Security Tester against the test server.

Usage:
1. Start the test server: python test_server.py
2. Run these examples: python test_examples.py

Or import and use individual functions:
    from test_examples import test_all_endpoints
    test_all_endpoints()
"""

from apisec_tester import core, report


def test_single_endpoint():
    """Test a single endpoint."""
    print("Testing single endpoint: http://localhost:9876/api/public")
    print("-" * 60)

    results = core.run_all_checks("http://localhost:9876/api/public")

    for result in results:
        print(f"Check: {result['check']}")
        print(f"Status: {result['status']}")
        print(f"Summary: {result['summary']}")
        print()


def test_all_endpoints():
    """Test all endpoints on the test server."""
    print("Testing all endpoints on test server")
    print("=" * 60)

    endpoints = [
        "http://localhost:9876/api/public",
        "http://localhost:9876/api/protected",
        "http://localhost:9876/api/search",
        "http://localhost:9876/api/data",
        "http://localhost:9876/api/reflected",
        "http://localhost:9876/api/sql-error",
        "http://localhost:9876/api/rate-limited",
    ]

    all_results = []

    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        print("-" * 60)
        try:
            results = core.run_all_checks(endpoint)
            all_results.extend(results)

            for result in results:
                status_icon = {
                    "pass": "✓",
                    "warn": "⚠",
                    "error": "✗",
                    "info": "ℹ"
                }.get(result["status"], "?")

                print(f"  {status_icon} {result['check']:15} [{result['status']:5}] {result.get('summary', '')}")

        except Exception as e:
            print(f"  ✗ Error testing endpoint: {e}")

    # Generate summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    summary = report.summarize(all_results)
    print(summary)

    # Offer to save report
    print("\nSaving report to test_server_report.json and test_server_report.txt")
    report.write_report(
        all_results,
        json_path="test_server_report.json",
        txt_path="test_server_report.txt"
    )
    print("Reports saved!")


def test_individual_checks():
    """Test individual check functions."""
    print("Testing individual check functions")
    print("=" * 60)

    endpoint = "http://localhost:9876/api/search"

    # Test auth check
    print("\n1. Authentication Check")
    print("-" * 60)
    auth_result = core.check_auth(endpoint)
    print(f"Status: {auth_result['status']}")
    print(f"Summary: {auth_result['summary']}")

    # Test injection check
    print("\n2. Injection Check")
    print("-" * 60)
    injection_result = core.check_injection(endpoint, param_name="q")
    print(f"Status: {injection_result['status']}")
    print(f"Summary: {injection_result['summary']}")
    if injection_result.get('evidence'):
        print("Evidence:")
        for evidence in injection_result['evidence']:
            print(f"  - {evidence['type']}: {evidence['payload']}")

    # Test rate limit check
    print("\n3. Rate Limit Check")
    print("-" * 60)
    rate_result = core.check_rate_limit(endpoint, attempts=5, pause=0.1)
    print(f"Status: {rate_result['status']}")
    print(f"Summary: {rate_result['summary']}")
    print(f"Response codes: {rate_result['responses']}")


def test_protected_endpoint_with_auth():
    """Test the protected endpoint with and without authentication."""
    print("Testing protected endpoint with/without authentication")
    print("=" * 60)

    endpoint = "http://localhost:9876/api/protected"

    # Without auth (should fail)
    print("\nWithout authentication:")
    print("-" * 60)
    result_no_auth = core.check_auth(endpoint)
    print(f"Status: {result_no_auth['status']} (expected: pass)")
    print(f"Status Code: {result_no_auth.get('status_code')} (expected: 401)")
    print(f"Summary: {result_no_auth['summary']}")

    # With auth (should succeed)
    print("\nWith authentication:")
    print("-" * 60)
    headers = {"Authorization": "Bearer valid-test-token"}
    result_with_auth = core.check_auth(endpoint, headers=headers)
    print(f"Status: {result_with_auth['status']} (expected: warn, since 2xx without checking auth)")
    print(f"Status Code: {result_with_auth.get('status_code')} (expected: 200)")
    print(f"Summary: {result_with_auth['summary']}")


def test_rate_limited_endpoint():
    """Test the endpoint with rate limiting."""
    print("Testing rate-limited endpoint")
    print("=" * 60)

    endpoint = "http://localhost:9876/api/rate-limited"

    print("\nSending multiple requests to trigger rate limit...")
    result = core.check_rate_limit(endpoint, attempts=6, pause=0.1)

    print(f"Status: {result['status']} (expected: pass)")
    print(f"Responses: {result['responses']} (should contain 429)")
    print(f"Summary: {result['summary']}")

    if 429 in result['responses']:
        print("\n✓ Rate limiting successfully detected!")
    else:
        print("\n⚠ Rate limiting NOT detected")


def test_sql_error_disclosure():
    """Test SQL error disclosure detection."""
    print("Testing SQL error disclosure")
    print("=" * 60)

    endpoint = "http://localhost:9876/api/sql-error"

    print("\nTesting with injection payloads...")
    result = core.check_injection(endpoint, param_name="q")

    print(f"Status: {result['status']} (expected: warn)")
    print(f"Summary: {result['summary']}")

    if result.get('evidence'):
        print("\nEvidence found:")
        for evidence in result['evidence']:
            print(f"  - Type: {evidence['type']}")
            print(f"    Payload: {evidence['payload']}")
            if 'match' in evidence:
                print(f"    Matched: {evidence['match']}")
    else:
        print("\n⚠ No evidence found")


def compare_endpoints():
    """Compare security posture of different endpoints."""
    print("Comparing security posture of endpoints")
    print("=" * 60)

    endpoints = {
        "Public (insecure)": "http://localhost:9876/api/public",
        "Protected (secure)": "http://localhost:9876/api/protected",
        "Search (vulnerable)": "http://localhost:9876/api/search",
        "Rate Limited (secure)": "http://localhost:9876/api/rate-limited",
    }

    comparison = {}

    for name, endpoint in endpoints.items():
        results = core.run_all_checks(endpoint)
        scores = {"pass": 0, "warn": 0, "error": 0, "info": 0}

        for result in results:
            scores[result["status"]] += 1

        comparison[name] = scores

    # Display comparison table
    print("\nSecurity Score Card:")
    print("-" * 60)
    print(f"{'Endpoint':<25} {'PASS':<6} {'WARN':<6} {'ERROR':<6} {'INFO':<6}")
    print("-" * 60)

    for name, scores in comparison.items():
        print(f"{name:<25} {scores['pass']:<6} {scores['warn']:<6} {scores['error']:<6} {scores['info']:<6}")

    print("-" * 60)


def main():
    """Run all example tests."""
    print("\n" + "=" * 60)
    print("API Security Tester - Example Tests")
    print("=" * 60)

    examples = [
        ("1. Test Single Endpoint", test_single_endpoint),
        ("2. Test All Endpoints", test_all_endpoints),
        ("3. Test Individual Checks", test_individual_checks),
        ("4. Test Protected Endpoint", test_protected_endpoint_with_auth),
        ("5. Test Rate-Limited Endpoint", test_rate_limited_endpoint),
        ("6. Test SQL Error Disclosure", test_sql_error_disclosure),
        ("7. Compare Endpoints", compare_endpoints),
    ]

    print("\nAvailable examples:")
    for title, _ in examples:
        print(f"  {title}")

    print("\n" + "=" * 60)

    # Run most comprehensive test
    print("\nRunning comprehensive test (test_all_endpoints)...\n")
    test_all_endpoints()

    print("\n" + "=" * 60)
    print("To run individual examples, import and call them:")
    print("  from test_examples import test_single_endpoint")
    print("  test_single_endpoint()")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
