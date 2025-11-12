"""
Lightweight Test Server for API Security Tester

This server provides intentionally vulnerable endpoints for testing the
apisec-tester tool. DO NOT use these patterns in production code.

Run: python test_server.py
Server will start on http://localhost:9876
"""

from flask import Flask, request, jsonify, make_response
import time
from functools import wraps

app = Flask(__name__)

# Store for rate limiting simulation
request_counts = {}


def reset_rate_limits():
    """Reset rate limiting counters."""
    global request_counts
    request_counts = {}


# Middleware to track requests
@app.before_request
def track_requests():
    endpoint = request.endpoint
    if endpoint:
        request_counts[endpoint] = request_counts.get(endpoint, 0) + 1


@app.route('/')
def index():
    """Root endpoint with server info."""
    return jsonify({
        "name": "API Security Test Server",
        "version": "1.0.0",
        "purpose": "Testing API security checks",
        "warning": "This server has intentionally vulnerable endpoints. DO NOT expose to public internet.",
        "endpoints": {
            "/api/public": "Public endpoint (no authentication required) - WARN expected",
            "/api/protected": "Protected endpoint (requires auth) - PASS expected",
            "/api/search": "Search endpoint (vulnerable to injection) - WARN expected",
            "/api/data": "Data endpoint (no rate limiting) - WARN expected",
            "/api/reflected": "Reflected XSS endpoint - WARN expected",
            "/api/sql-error": "SQL error disclosure endpoint - WARN expected",
            "/api/rate-limited": "Rate limited endpoint - PASS expected",
            "/api/status": "Server status endpoint"
        },
        "instructions": [
            "Test with: apisec-tester run --endpoint http://localhost:9876/api/public --output report.json",
            "Or test all: python -c 'from test_examples import test_all_endpoints; test_all_endpoints()'"
        ]
    }), 200


@app.route('/api/public', methods=['GET', 'POST'])
def api_public():
    """
    Public endpoint - returns 200 without authentication.
    Expected result: WARN on auth check (endpoint accepts unauthenticated requests)
    """
    return jsonify({
        "message": "This is a public endpoint",
        "data": ["item1", "item2", "item3"],
        "authenticated": False,
        "vulnerability": "No authentication required"
    }), 200


@app.route('/api/protected', methods=['GET', 'POST'])
def api_protected():
    """
    Protected endpoint - requires Authorization header.
    Expected result: PASS on auth check (returns 401 without auth)
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            "error": "Unauthorized",
            "message": "This endpoint requires authentication",
            "hint": "Include Authorization: Bearer <token> header"
        }), 401

    # Simple token validation (in real apps, validate JWT properly)
    token = auth_header.replace('Bearer ', '')
    if token != 'valid-test-token':
        return jsonify({
            "error": "Forbidden",
            "message": "Invalid or expired token"
        }), 403

    return jsonify({
        "message": "Access granted to protected resource",
        "data": {"secret": "confidential-data"},
        "authenticated": True
    }), 200


@app.route('/api/search', methods=['GET'])
def api_search():
    """
    Search endpoint - vulnerable to reflection attacks.
    Expected result: WARN on injection check (reflects user input)
    """
    query = request.args.get('q', '')

    # VULNERABILITY: Directly reflecting user input without sanitization
    return jsonify({
        "query": query,
        "message": f"Search results for: {query}",  # Reflection vulnerability
        "results": [
            {"id": 1, "title": f"Result containing {query}"},
            {"id": 2, "title": "Another result"}
        ],
        "vulnerability": "Reflected user input without sanitization"
    }), 200


@app.route('/api/reflected', methods=['GET'])
def api_reflected():
    """
    Endpoint that reflects XSS payloads in response.
    Expected result: WARN on injection check (XSS reflection)
    """
    param = request.args.get('q', '')

    # VULNERABILITY: Reflects XSS payloads
    html_content = f"""
    <html>
        <body>
            <h1>Search Results</h1>
            <p>You searched for: {param}</p>
        </body>
    </html>
    """

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response


@app.route('/api/sql-error', methods=['GET'])
def api_sql_error():
    """
    Endpoint that exposes SQL errors.
    Expected result: WARN on injection check (SQL error disclosure)
    """
    query = request.args.get('q', '')

    # VULNERABILITY: Simulated SQL error disclosure
    if "'" in query or '"' in query:
        return jsonify({
            "error": "SQL syntax error",
            "message": f"mysql error: You have an error in your SQL syntax near '{query}' at line 1",
            "query": f"SELECT * FROM users WHERE name = '{query}'",
            "vulnerability": "SQL error disclosure reveals database structure"
        }), 500

    return jsonify({
        "message": "Query executed successfully",
        "results": []
    }), 200


@app.route('/api/data', methods=['GET'])
def api_data():
    """
    Data endpoint - no rate limiting.
    Expected result: WARN on rate limit check (no 429 responses)
    """
    return jsonify({
        "message": "Data endpoint without rate limiting",
        "data": {"key": "value"},
        "timestamp": time.time(),
        "request_count": request_counts.get('api_data', 0),
        "vulnerability": "No rate limiting implemented"
    }), 200


@app.route('/api/rate-limited', methods=['GET'])
def api_rate_limited():
    """
    Rate limited endpoint - returns 429 after threshold.
    Expected result: PASS on rate limit check (returns 429)
    """
    max_requests = 3
    count = request_counts.get('api_rate_limited', 0)

    if count > max_requests:
        return jsonify({
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please try again later.",
            "retry_after": 60
        }), 429

    return jsonify({
        "message": "Rate limited endpoint",
        "data": {"key": "value"},
        "requests_remaining": max(0, max_requests - count)
    }), 200


@app.route('/api/status', methods=['GET'])
def api_status():
    """Server status and statistics."""
    return jsonify({
        "status": "running",
        "endpoints_hit": request_counts,
        "total_requests": sum(request_counts.values())
    }), 200


@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset rate limiting counters."""
    reset_rate_limits()
    return jsonify({
        "message": "Rate limit counters reset",
        "status": "success"
    }), 200


@app.route('/api/cors-misconfigured', methods=['GET', 'OPTIONS'])
def api_cors():
    """
    Endpoint with misconfigured CORS (allows all origins).
    Future enhancement: add CORS check to apisec-tester
    """
    response = jsonify({
        "message": "Endpoint with permissive CORS",
        "data": {"sensitive": "information"},
        "vulnerability": "CORS allows requests from any origin"
    })

    # VULNERABILITY: Overly permissive CORS
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = '*'

    return response, 200


@app.route('/api/verbose-error', methods=['GET'])
def api_verbose_error():
    """
    Endpoint that exposes verbose error messages.
    Future enhancement: add verbose error check to apisec-tester
    """
    try:
        # Simulate error
        result = 1 / 0
    except Exception as e:
        # VULNERABILITY: Exposing stack traces and internal details
        import traceback
        return jsonify({
            "error": "Internal Server Error",
            "exception": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "vulnerability": "Verbose error messages expose internal implementation"
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Custom 404 handler."""
    return jsonify({
        "error": "Not Found",
        "message": f"Endpoint {request.path} not found",
        "available_endpoints": [
            "/",
            "/api/public",
            "/api/protected",
            "/api/search",
            "/api/data",
            "/api/reflected",
            "/api/sql-error",
            "/api/rate-limited",
            "/api/status"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Custom 500 handler."""
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("API Security Test Server")
    print("=" * 60)
    print("Starting server on http://localhost:9876")
    print()
    print("Available endpoints:")
    print("  GET  /                       - Server information")
    print("  GET  /api/public             - Public endpoint (no auth)")
    print("  GET  /api/protected          - Protected endpoint (requires auth)")
    print("  GET  /api/search?q=<query>   - Search (reflection vulnerability)")
    print("  GET  /api/reflected?q=<query>- XSS reflection")
    print("  GET  /api/sql-error?q=<query>- SQL error disclosure")
    print("  GET  /api/data               - No rate limiting")
    print("  GET  /api/rate-limited       - With rate limiting")
    print("  GET  /api/status             - Server statistics")
    print("  POST /api/reset              - Reset rate limit counters")
    print()
    print("Test with:")
    print("  apisec-tester run \\")
    print("    --endpoint http://localhost:9876/api/public \\")
    print("    --endpoint http://localhost:9876/api/protected \\")
    print("    --endpoint http://localhost:9876/api/search \\")
    print("    --endpoint http://localhost:9876/api/data \\")
    print("    --output test_report.json")
    print()
    print("WARNING: This server has intentionally vulnerable endpoints.")
    print("         DO NOT expose to the public internet!")
    print("=" * 60)
    print()

    # Run Flask development server
    app.run(host='127.0.0.1', port=9876, debug=False)
