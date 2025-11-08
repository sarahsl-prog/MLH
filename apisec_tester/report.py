"""Report generation helpers for the Personal API Security Tester."""
from typing import List, Dict
import json


def summarize(results: List[Dict]) -> str:
    lines = []
    overall = {"pass": 0, "warn": 0, "error": 0, "info": 0}
    for r in results:
        status = r.get("status", "info")
        overall[status] = overall.get(status, 0) + 1
        lines.append(f"- [{status.upper()}] {r.get('check')} @ {r.get('endpoint')}: {r.get('summary', '')}")
    lines.append("")
    lines.append("Report card:")
    lines.append(f"PASS: {overall.get('pass',0)}  WARN: {overall.get('warn',0)}  ERROR: {overall.get('error',0)}  INFO: {overall.get('info',0)}")
    return "\n".join(lines)


def write_report(results: List[Dict], json_path: str = "report.json", txt_path: str = "report.txt") -> None:
    payload = {"results": results}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    summary = summarize(results)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(summary)
