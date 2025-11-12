# Installation

These instructions walk through setting up a local development environment for the Personal API Security Tester on Windows (cmd.exe). Adjust commands for other shells/OSes as needed.

Prerequisites

- Python 3.8+ installed and on PATH
- Git (to clone the repo)

1. Clone the repository (if not already present):

```cmd
git clone https://github.com/sarahsl-prog/MLH.git
cd MLH
```

2. Create a virtual environment and activate it:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```cmd
pip install -r requirements.txt
```

4. Install the package in editable mode to expose the `apisec-tester` console script:

```cmd
pip install -e .
```

Notes

- If you prefer to use `pip install -r requirements.txt` only, you can run the CLI directly with `python cli.py` without installing the package.
- On non-Windows systems, replace `.venv\Scripts\activate` with `source .venv/bin/activate`.
