"""Probe script to discover Kali MCP endpoints on a host.

Safe, non-destructive checks:
- GET on a set of candidate paths
- POST {'command':'ping'} to candidate command endpoints

Prints a compact report to stdout.
"""
import requests
import os
import json


KALI_URL = os.getenv("KALI_MCP_URL", "http://192.168.0.250:5000").rstrip("/")

CANDIDATE_PATHS = [
    "/",
    "/mcp",
    "/mcp/",
    "/mcp/commands",
    "/api",
    "/api/mcp",
    "/api/mcp/commands",
    "/commands",
    "/mcp/commands/ping",
]


def probe_get(path: str):
    url = f"{KALI_URL}{path}"
    try:
        r = requests.get(url, timeout=5)
        return {"path": path, "url": url, "method": "GET", "status": r.status_code, "content_type": r.headers.get("content-type", "")}
    except Exception as e:
        return {"path": path, "url": url, "method": "GET", "error": str(e)}


def probe_post_ping(path: str):
    url = f"{KALI_URL}{path}"
    try:
        r = requests.post(url, json={"command": "ping"}, timeout=5)
        # try to parse JSON safely
        try:
            data = r.json()
        except Exception:
            data = None
        return {"path": path, "url": url, "method": "POST", "status": r.status_code, "json": data, "text_snippet": (r.text[:200] if r.text else "")}
    except Exception as e:
        return {"path": path, "url": url, "method": "POST", "error": str(e)}


def main():
    results = {"gets": [], "posts": []}
    print(f"Probing {KALI_URL} for candidate MCP endpoints...\n")
    for p in CANDIDATE_PATHS:
        g = probe_get(p)
        results["gets"].append(g)
        print(f"GET {g['url']} -> {g.get('status') or g.get('error')}")
    print("\nNow trying POST ping on likely command endpoints...\n")
    post_targets = ["/mcp/commands", "/api/mcp/commands", "/commands", "/mcp/commands/ping"]
    for p in post_targets:
        res = probe_post_ping(p)
        results["posts"].append(res)
        status = res.get("status") or res.get("error")
        print(f"POST {res['url']} -> {status}")
        if res.get("json"):
            print("  JSON:", json.dumps(res["json"]))
        elif res.get("text_snippet"):
            print("  Text snippet:", res["text_snippet"]) 

    # write a small file for debugging
    out_path = os.path.join(os.getcwd(), "kali_probe_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote probe report to {out_path}")


if __name__ == "__main__":
    main()
