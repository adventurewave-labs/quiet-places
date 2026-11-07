#!/usr/bin/env python3
"""Check that every place's source URL resolves.

Report only: prints PASS, REDIR, or FAIL per entry. Exit 1 if any FAIL, so a
sweep pass or CI job can gate on it. Tries urllib HEAD, then GET, then an
alternate trust store, then curl, because some hosts reject probes that
browsers accept.
"""

import json
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "places.json"
TIMEOUT = 20
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def fetch(url, method="HEAD", context=None):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=context) as resp:
        return resp.status, resp.geturl()


def check(url):
    attempts = []
    for method in ("HEAD", "GET"):
        try:
            return fetch(url, method)
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 501):
                continue  # host rejects this method; try the other
            return None, f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001
            attempts.append(str(e))
    # alternate trust store (macOS python often lacks the system bundle)
    try:
        import certifi

        ctx = ssl.create_default_context(cafile=certifi.where())
        for method in ("HEAD", "GET"):
            try:
                return fetch(url, method, context=ctx)
            except Exception as e:  # noqa: BLE001
                attempts.append(f"certifi/{method}: {e}")
    except ImportError:
        attempts.append("certifi not installed")
    # last resort: curl, which uses the OS trust store
    try:
        out = subprocess.run(
            ["curl", "-sIL", "-o", "/dev/null", "-w", "%{http_code} %{url_effective}", "--max-time", str(TIMEOUT), url],
            capture_output=True, text=True, timeout=TIMEOUT + 5,
        ).stdout.strip()
        code, _, final = out.partition(" ")
        if code.isdigit() and int(code) == 200:
            return 200, final or url
        attempts.append(f"curl: {out}")
    except Exception as e:  # noqa: BLE001
        attempts.append(f"curl: {e}")
    return None, attempts[-1] if attempts else "unknown"


def main():
    places = json.loads(DATA_FILE.read_text(encoding="utf-8"))["places"]
    failures = 0
    for p in places:
        status, info = check(p["url"])
        if status == 200:
            result = "PASS" if info == p["url"] else "REDIR"
            detail = f"-> {info}" if result == "REDIR" else ""
        elif status:
            result, failures = f"HTTP {status}", failures + 1
            detail = ""
        else:
            result, failures = "FAIL", failures + 1
            detail = str(info)[:120]
        print(f"{result:8} {p['slug']:24} {p['url']}  {detail}")
    print(f"\n{len(places) - failures}/{len(places)} reachable, {failures} failures")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
