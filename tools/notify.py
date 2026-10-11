# -*- coding: utf-8 -*-
"""Bao ra ngoai: Discord kenh #game (DISCORD_WEBHOOK) va diem danh healthchecks.io (HC_PING).
Gia tri lay tu bien moi truong (GitHub Secrets) hoac file .env o goc kho (khong len git). Thieu thi bo qua.
Goi mang thu 3 lan gian cach roi thoi; khong bao gio lam hong lan chay."""
import json
import os
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_loaded = False


def env(name):
    global _loaded
    if not _loaded:
        _loaded = True
        path = ROOT / ".env"
        if path.exists():
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                key, sep, value = line.partition("=")
                if sep and not key.strip().startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))
    return os.environ.get(name, "").strip()


def _send(url, data=None):
    headers = {"User-Agent": "game-factory/1.0", "Content-Type": "application/json"}
    for attempt in range(3):
        try:
            urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=20).read()
            return True
        except (OSError, ValueError):
            time.sleep(5 * (attempt + 1))
    return False


def discord(message, alert=False):
    """alert=True them @here (chi dung cho loi)."""
    url = env("DISCORD_WEBHOOK")
    if not url:
        return False
    body = {"content": ("@here " if alert else "") + message[:1900],
            "allowed_mentions": {"parse": ["everyone"] if alert else []}}
    return _send(url, json.dumps(body).encode())


def ping(failed=False):
    url = env("HC_PING")
    return bool(url) and _send(url.rstrip("/") + ("/fail" if failed else ""))
