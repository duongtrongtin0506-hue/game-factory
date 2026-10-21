"""License gate for pulled-in open-source items (KHUON-NHA-MAY mục 8).

check_repo("owner/name") reads the GitHub API `license` field. Allowed: CC0, public domain (Unlicense),
MIT, Apache-2.0, BSD-2/3, ISC, Zlib, GPL/LGPL/AGPL (keep license, ship source), CC-BY-4.0.
Empty / NOASSERTION / NC / ND / anything else -> rejected.
CLI: python tools/chung/giay_phep.py owner/name [owner/name ...]
"""
import json
import os
import sys
import urllib.request

ALLOWED = {"cc0-1.0", "unlicense", "mit", "mit-0", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "zlib",
           "gpl-2.0", "gpl-3.0", "lgpl-2.1", "lgpl-3.0", "agpl-3.0", "cc-by-4.0", "0bsd", "wtfpl"}
COPYLEFT = {"gpl-2.0", "gpl-3.0", "lgpl-2.1", "lgpl-3.0", "agpl-3.0"}


def check_repo(full):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "net24-xuong"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(f"https://api.github.com/repos/{full}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    lic = (d.get("license") or {}).get("key") or ""
    return {"repo": full, "license": lic, "spdx": (d.get("license") or {}).get("spdx_id") or "", "ok": lic in ALLOWED,
            "copyleft": lic in COPYLEFT, "stars": d.get("stargazers_count", 0), "pushed": d.get("pushed_at", ""),
            "url": d.get("html_url", ""), "archived": d.get("archived", False)}


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    bad = 0
    for full in sys.argv[1:]:
        r = check_repo(full)
        print(("OK " if r["ok"] else "NO ") + json.dumps(r))
        bad += not r["ok"]
    sys.exit(1 if bad else 0)
