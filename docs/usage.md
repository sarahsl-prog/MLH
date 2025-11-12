# Usage

Basic CLI

After installing the package (or running `python cli.py`), you can use the console script:

```cmd
apisec-tester run --endpoint https://api.example.com/login --endpoint https://api.example.com/items --output report.json
```

This runs the default set of checks against each endpoint and writes `report.json` and `report.txt` with the results.

Interactive mode

```cmd
apisec-tester interactive
```

This prompts for endpoints one at a time and prints a summary. You can save the report when prompted.

Programmatic usage

You can import the package in Python code:

```py
from apisec_tester import core, report

results = core.run_all_checks('https://api.example.com')
report.write_report(results, json_path='report.json', txt_path='report.txt')
```

Report format

- `report.json` contains a JSON object with a `results` array. Each item has fields like `endpoint`, `check`, `status`, and `summary`.
- `report.txt` is a human-friendly summary and a short report card.
