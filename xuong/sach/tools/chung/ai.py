"""Shared AI for every factory workshop (copied into each repo, pinned by tools/chung/VERSION).

ask(prompt) tries, in order:
  1. the system's shared AI: POST https://coinnew24.com/wp-json/n24/v1/ai  (secret N24_AI_KEY -> header X-N24-AI)
  2. Gemini with Google Search grounding (secret GEMINI_API_KEY)
Fuse: at most AI_DAILY_CAP calls per workshop per day (default 40), counted in NHAT-KY/ai-dem.json.
No key at all -> returns None and the caller records "chờ khóa AI" instead of failing.
"""
import datetime
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COUNT = ROOT / "NHAT-KY" / "ai-dem.json"
CAP = int(os.environ.get("AI_DAILY_CAP", "40"))
AGENT = os.environ.get("XUONG", ROOT.name)


def _today():
    return (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=7)).strftime("%Y-%m-%d")


def _count(add=0):
    data = {}
    try:
        data = json.loads(COUNT.read_text(encoding="utf-8"))
    except Exception:
        pass
    n = data.get(_today(), 0) + add
    if add:
        data = {k: v for k, v in data.items() if k >= (datetime.date.today() - datetime.timedelta(days=30)).isoformat()}
        data[_today()] = n
        COUNT.parent.mkdir(parents=True, exist_ok=True)
        COUNT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return n


def available():
    return bool(os.environ.get("N24_AI_KEY") or os.environ.get("GEMINI_API_KEY"))


def _post(url, body, headers, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def ask(prompt, max_tokens=1500, search=False):
    if _count() >= CAP:
        print(f"[ai] fuse: {CAP} calls today, skipped")
        return None
    key = os.environ.get("N24_AI_KEY")
    if key:
        try:
            out = _post(os.environ.get("N24_AI_URL") or "https://coinnew24.com/wp-json/n24/v1/ai",
                        {"prompt": prompt, "agent": "xuong-" + AGENT, "max": max_tokens}, {"X-N24-AI": key})
            _count(1)
            if out.get("text"):
                return out["text"]
        except Exception as e:
            print("[ai] shared AI failed:", type(e).__name__)
    gkey = os.environ.get("GEMINI_API_KEY")
    if gkey:
        body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": max_tokens}}
        if search:
            body["tools"] = [{"google_search": {}}]
        try:
            out = _post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", body, {"x-goog-api-key": gkey})
            _count(1)
            return "".join(p.get("text", "") for p in out["candidates"][0]["content"]["parts"])
        except Exception as e:
            print("[ai] gemini failed:", type(e).__name__)
    return None


def ask_json(prompt, max_tokens=1500, search=False):
    """ask() and parse the first {...} or [...] block; None if no AI or no JSON."""
    text = ask(prompt + "\n\nAnswer with JSON only.", max_tokens, search)
    if not text:
        return None
    for a, b in (("{", "}"), ("[", "]")):
        i, j = text.find(a), text.rfind(b)
        if i >= 0 and j > i:
            try:
                return json.loads(text[i:j + 1])
            except Exception:
                continue
    return None
