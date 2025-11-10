# Contributing Guide

Thank you for considering contributing to the Personal API Security Tester! This guide will help you get started.

## Code of Conduct

- Be respectful and constructive
- Focus on improving the tool for everyone
- Report security issues privately
- Follow responsible disclosure practices

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Create a new GitHub issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)
   - Sample code or endpoint (if safe to share)

### Suggesting Features

1. Open a GitHub issue with the "enhancement" label
2. Describe the use case and benefit
3. Provide examples if possible
4. Discuss implementation approach

### Contributing Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip and virtualenv
- git

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/apisec-tester.git
cd apisec-tester

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dependencies
pip install -e .
pip install -r requirements.txt

# Verify installation
apisec-tester --help
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apisec_tester --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test function
pytest tests/test_core.py::test_check_auth_401
```

### Code Style

We follow PEP 8 style guidelines:

```bash
# Install development tools
pip install flake8 black isort

# Format code
black apisec_tester/ cli.py tests/

# Sort imports
isort apisec_tester/ cli.py tests/

# Check style
flake8 apisec_tester/ cli.py tests/
```

## Project Structure

```
apisec-tester/
├── apisec_tester/          # Main package
│   ├── __init__.py
│   ├── core.py             # Security check functions
│   └── report.py           # Report generation
├── cli.py                  # Command-line interface
├── tests/                  # Test suite
│   ├── test_core.py        # Unit tests
│   └── test_kali_mcp.py    # Integration tests
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── USAGE.md
│   └── CONTRIBUTING.md
├── scripts/                # Utility scripts
├── setup.py                # Package setup
├── pyproject.toml          # Build configuration
├── requirements.txt        # Dependencies
└── README.md               # Project overview
```

## Adding New Security Checks

### Step 1: Implement the Check Function

Add to `apisec_tester/core.py`:

```python
def check_new_vulnerability(endpoint: str, timeout: float = 5.0) -> Dict:
    """Description of what this check does.

    Args:
        endpoint: The URL to test
        timeout: Request timeout in seconds

    Returns:
        Dict with keys: endpoint, check, status, summary, [error]
    """
    result = {
        "endpoint": endpoint,
        "check": "new_vulnerability",  # Use snake_case name
        "status": "unknown"
    }

    try:
        # 1. Perform non-destructive check
        r = requests.get(endpoint, timeout=timeout)

        # 2. Analyze response
        if condition_indicates_vulnerability:
            result["status"] = "warn"
            result["summary"] = "Vulnerability detected: ..."
        else:
            result["status"] = "pass"
            result["summary"] = "No vulnerability detected."

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result
```

### Step 2: Add to `run_all_checks()`

Update the function in `core.py`:

```python
def run_all_checks(endpoint: str) -> List[Dict]:
    """Run the basic checks and return a list of results."""
    results = []
    results.append(check_auth(endpoint))
    results.append(check_injection(endpoint))
    results.append(check_rate_limit(endpoint))
    results.append(check_new_vulnerability(endpoint))  # Add your check
    return results
```

### Step 3: Write Tests

Add to `tests/test_core.py`:

```python
def test_check_new_vulnerability_pass(monkeypatch):
    """Test when no vulnerability is present."""
    def fake_get(url, timeout=0):
        return DummyResponse(status_code=200, text="safe response")

    monkeypatch.setattr(core.requests, 'get', fake_get)
    result = core.check_new_vulnerability('http://example.test')
    assert result['status'] == 'pass'


def test_check_new_vulnerability_warn(monkeypatch):
    """Test when vulnerability is detected."""
    def fake_get(url, timeout=0):
        return DummyResponse(status_code=200, text="vulnerable response")

    monkeypatch.setattr(core.requests, 'get', fake_get)
    result = core.check_new_vulnerability('http://example.test')
    assert result['status'] == 'warn'


def test_check_new_vulnerability_error(monkeypatch):
    """Test exception handling."""
    def fake_get(url, timeout=0):
        raise requests.ConnectionError("Network error")

    monkeypatch.setattr(core.requests, 'get', fake_get)
    result = core.check_new_vulnerability('http://example.test')
    assert result['status'] == 'error'
    assert 'error' in result
```

### Step 4: Update Documentation

Add your check to `docs/API.md`:

```markdown
#### `check_new_vulnerability(endpoint, timeout=5.0)`

Description of the check and what it tests for.

**Parameters:**
- `endpoint` (str): The URL to test
- `timeout` (float, optional): Request timeout in seconds

**Returns:**
- `dict`: Result dictionary

**Example:**
\```python
result = check_new_vulnerability("https://api.example.com/endpoint")
\```
```

### Step 5: Test Against Test Server

Add a vulnerable endpoint to `test_server.py` if needed, then verify your check works:

```bash
# Start test server
python test_server.py

# Test your new check
python -c "
from apisec_tester.core import check_new_vulnerability
result = check_new_vulnerability('http://localhost:9876/api/test')
print(result)
"
```

## Writing Good Tests

### Use Pytest Fixtures

```python
import pytest

@pytest.fixture
def dummy_response():
    return DummyResponse(status_code=200, text="test")

def test_with_fixture(dummy_response):
    assert dummy_response.status_code == 200
```

### Use Monkeypatching

Mock external dependencies:

```python
def test_with_mock(monkeypatch):
    def fake_get(*args, **kwargs):
        return DummyResponse(200, "mocked")

    monkeypatch.setattr(requests, 'get', fake_get)
    # Test your code that uses requests.get
```

### Test Edge Cases

- Empty responses
- Timeout scenarios
- Invalid URLs
- Network errors
- Unexpected status codes

### Example Test Structure

```python
class TestCheckAuth:
    """Tests for authentication checking."""

    def test_returns_pass_on_401(self, monkeypatch):
        """Should pass when endpoint returns 401."""
        # Setup, Exercise, Assert

    def test_returns_warn_on_200(self, monkeypatch):
        """Should warn when endpoint returns 200 without auth."""

    def test_handles_timeout(self, monkeypatch):
        """Should return error status on timeout."""

    def test_includes_status_code(self, monkeypatch):
        """Result should include HTTP status code."""
```

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass: `pytest`
- [ ] Code follows style guide: `flake8` and `black`
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Follows coding standards
```

### Review Process

1. Automated checks run (tests, linting)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
# Good
Add CORS header check to security tests
Fix timeout handling in check_auth function
Update API documentation for check_injection

# Bad
fix bug
update code
changes
```

### Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

## Security Considerations

### Non-Destructive Checks Only

- Use GET requests when possible
- Avoid DELETE, TRUNCATE, DROP operations
- Don't modify data
- Don't consume excessive resources

### Safe Payloads

```python
# Good: Benign SQL injection check
payload = "' OR '1'='1"

# Bad: Destructive payload
payload = "'; DROP TABLE users; --"
```

### Responsible Testing

- Document potential impacts
- Add warnings for aggressive checks
- Provide configuration options for intensity
- Respect timeouts and rate limits

## Documentation Standards

### Code Comments

```python
def check_auth(endpoint: str, headers: Dict[str, str] = None, timeout: float = 5.0) -> Dict:
    """Check whether an endpoint appears to accept unauthenticated requests.

    This is heuristic-based: it will consider a 2xx response without
    credentials as a potential unauthenticated acceptance.

    Args:
        endpoint: The URL to test
        headers: Optional headers to include in the request
        timeout: Request timeout in seconds (default: 5.0)

    Returns:
        Dict containing:
            - endpoint (str): The tested URL
            - check (str): Check name ("auth")
            - status (str): "pass", "warn", "error", or "info"
            - summary (str): Human-readable result
            - status_code (int, optional): HTTP status code
            - error (str, optional): Error message if failed

    Example:
        >>> result = check_auth("https://api.example.com/users")
        >>> print(result['status'])
        'pass'
    """
```

### Markdown Documentation

- Use clear headers
- Include code examples
- Add links to related docs
- Keep examples simple and runnable

## Release Process

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push --tags`
5. Create GitHub release
6. Build and publish to PyPI (if applicable)

## Getting Help

- Check existing issues and PRs
- Ask questions in GitHub Discussions
- Reach out to maintainers
- Review documentation first

## Recognition

Contributors are recognized in:
- GitHub contributors page
- CHANGELOG.md
- Release notes

Thank you for contributing to making APIs more secure!
