"""CỬA 0 – machine self-check of one product folder: python tools/chung/cua0.py <folder> [--web index.html] [--epub file.epub]

Red (exit 1) if any check fails. Writes <folder>/CUA0.json. Checks (KHUON-NHA-MAY mục 3 + mục 8):
  hồ sơ    BAN-GIAO.md, LEADER.md (not for free pulls), LICENSES.md present and non-empty
  license  LICENSES.md names only allowed licenses (CC0, PD, MIT, Apache, BSD, ISC, GPL/LGPL, CC-BY, self-made); no NC/ND/personal-use
  privacy  shipped .html/.js/.css call no host outside the allow list; no analytics / pixel / tracking code
  web      (--web) loads at 360x640, 768x1024, 1280x720 in Chromium with 0 console errors; screenshots saved
  epub     (--epub) epubcheck 0 errors when java + epubcheck.jar are available (EPUBCHECK_JAR), else structural check
"""
import argparse
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ALLOWED_HOSTS = ("html5.api.gamedistribution.com", "api.gamemonetize.com", "sdk.crazygames.com", "bridge.playgama.com",
                 "www.w3.org", "schemas.android.com", "github.com", "creativecommons.org", "opensource.org", "www.gnu.org",
                 "gnu.org", "unlicense.org", "spdx.org", "www.apache.org", "apache.org", "kenney.nl", "opengameart.org",
                 "fonts.googleapis.com", "fonts.gstatic.com", "api.coinbase.com", "www.idpf.org", "purl.org", "localhost", "127.0.0.1")
TRACKERS = re.compile(r"google-analytics\.com|googletagmanager|gtag\(|fbq\(|facebook\.net/.*/fbevents|hotjar|mixpanel|segment\.com/analytics|clarity\.ms|amplitude\.com", re.I)
BAD_LIC = re.compile(r"\bCC[- ]?BY[- ]?(?:\d\.\d[- ])?(?:SA[- ])?N[CD]\b|NonCommercial|NoDerivatives|personal use only|free for personal use|freeware", re.I)
GOOD_LIC = re.compile(r"CC0|Public Domain|MIT|Apache|BSD|ISC|GPL|CC[- ]?BY|self-made|tự tạo|own work|Unlicense|OFL", re.I)


def check(folder, web=None, epub=None, free=False):
    f = Path(folder)
    res = {"folder": str(f), "checks": {}, "notes": []}
    need = ["BAN-GIAO.md", "LICENSES.md"] + ([] if free else ["LEADER.md"])
    miss = [n for n in need if not (f / n).exists() or (f / n).stat().st_size < 40]
    res["checks"]["ho_so"] = not miss
    if miss:
        res["notes"].append("thiếu " + ", ".join(miss))
    lic = (f / "LICENSES.md").read_text(encoding="utf-8", errors="replace") if (f / "LICENSES.md").exists() else ""
    res["checks"]["giay_phep"] = bool(GOOD_LIC.search(lic)) and not BAD_LIC.search(lic)
    if BAD_LIC.search(lic):
        res["notes"].append("giấy phép cấm: " + BAD_LIC.search(lic).group(0))
    hosts, trackers = set(), []
    for p in f.rglob("*"):
        if p.suffix.lower() not in (".html", ".htm", ".js", ".css", ".xhtml", ".json") or "node_modules" in p.parts or p.name.startswith("CUA"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for h in re.findall(r"https?://([a-zA-Z0-9.-]+)", t):
            if not h.endswith(ALLOWED_HOSTS) and h not in ALLOWED_HOSTS:
                hosts.add(h)
        if TRACKERS.search(t):
            trackers.append(p.name)
    res["checks"]["rieng_tu"] = not trackers and not hosts
    if hosts:
        res["notes"].append("gọi máy chủ lạ: " + ", ".join(sorted(hosts)[:10]))
    if trackers:
        res["notes"].append("mã theo dõi trong: " + ", ".join(trackers[:5]))
    if web:
        res["checks"]["ba_co_man_hinh"] = web_check(f, f / web, res)
    if epub:
        res["checks"]["epub"] = epub_check(f / epub, res)
    res["pass"] = all(res["checks"].values())
    (f / "CUA0.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    return res


def web_check(f, page, res):
    from playwright.sync_api import sync_playwright
    errors, shots = [], f / "cua0-anh"
    shots.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w, h in ((360, 640), (768, 1024), (1280, 720)):
            p = b.new_page(viewport={"width": w, "height": h})
            p.on("console", lambda m: errors.append(f"{w}: {m.text}") if m.type == "error" else None)
            p.on("pageerror", lambda e: errors.append(f"{w}: {e}"))
            p.goto(page.resolve().as_uri())
            p.wait_for_timeout(800)
            over = p.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
            if over:
                errors.append(f"{w}: tràn ngang")
            p.screenshot(path=str(shots / f"{w}x{h}.png"))
            p.close()
        b.close()
    if errors:
        res["notes"].append("web: " + "; ".join(errors[:5]))
    return not errors


def epub_check(path, res):
    jar = os.environ.get("EPUBCHECK_JAR", "")
    if jar and Path(jar).exists():
        r = subprocess.run(["java", "-jar", jar, str(path), "--json", "-"], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            n = sum(1 for m in d.get("messages", []) if m.get("severity") in ("ERROR", "FATAL"))
        except Exception:
            n = 0 if r.returncode == 0 else 1
        if n:
            res["notes"].append(f"epubcheck: {n} lỗi")
        res["notes"].append("epubcheck chạy thật")
        return n == 0
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            ok = names[0] == "mimetype" and z.read("mimetype") == b"application/epub+zip" and "META-INF/container.xml" in names
        res["notes"].append("chưa có epubcheck.jar: chỉ kiểm cấu trúc")
        return ok
    except Exception as e:
        res["notes"].append("epub hỏng: " + type(e).__name__)
        return False


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = argparse.ArgumentParser()
    a.add_argument("folder")
    a.add_argument("--web")
    a.add_argument("--epub")
    a.add_argument("--free", action="store_true", help="free pulled-in item: LEADER.md not required")
    x = a.parse_args()
    r = check(x.folder, x.web, x.epub, x.free)
    print(("CỬA 0 XANH " if r["pass"] else "CỬA 0 ĐỎ ") + json.dumps(r["checks"]), "|", "; ".join(r["notes"]))
    sys.exit(0 if r["pass"] else 1)
