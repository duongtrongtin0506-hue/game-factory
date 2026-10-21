"""Discord line for a workshop: python tools/chung/bao.py "text"  (secret DISCORD_WEBHOOK; silent if missing)."""
import json
import os
import sys
import urllib.request


def send(text):
    hook = os.environ.get("DISCORD_WEBHOOK")
    if not hook:
        print("[bao] no DISCORD_WEBHOOK:", text)
        return False
    req = urllib.request.Request(hook, data=json.dumps({"content": text[:1900]}).encode(), headers={"Content-Type": "application/json", "User-Agent": "net24-xuong"})
    try:
        urllib.request.urlopen(req, timeout=20)
        return True
    except Exception as e:
        print("[bao] failed:", type(e).__name__)
        return False


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    send(" ".join(sys.argv[1:]))
