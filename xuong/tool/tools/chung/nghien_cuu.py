"""Weekly market research for one workshop: python tools/chung/nghien_cuu.py <nganh> [--out DIR] [--net24 PATH]

nganh: game | tool | mau | sach | studio | app
Writes NGHIEN-CUU/HOC-TOP-<nganh>.md (and, with --net24, 13-Ban-hang-so/HOC-TOP/<nganh>.md + BAN-GIAO/y-tuong/
proposals in the net24-he-thong checkout). The five parts required by KHUON-NHA-MAY mục 2:
  1. top 20 now (public pages / official APIs, no login)   2. rising   3. complaints   4. price tiers   5. >= 3 proposals
Parts 1 and 4 always come from real data. Parts 2, 3 and 5 use the shared AI (tools/chung/ai.py) when a key exists;
for tools, complaints also come straight from wordpress.org 1-3 star review feeds. History table kept at the bottom.
"""
import argparse
import datetime
import html
import json
import re
import statistics
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
TODAY = (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=7)).strftime("%Y-%m-%d")
NAMES = {"game": "Game HTML5", "tool": "Tool (plugin WP, Chrome, script)", "mau": "Mẫu (Notion/Sheets/Excel)",
         "sach": "Sách (ebook, sổ in)", "studio": "Studio (mã nguồn game, asset)", "app": "App (PWA)"}


def get(url, timeout=40):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def next_data(h):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    return json.loads(m.group(1)) if m else {}


def walk(o, test, out):
    if isinstance(o, dict):
        if test(o):
            out.append(o)
        for v in o.values():
            walk(v, test, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, test, out)
    return out


# ---------------------------------------------------------------- sources (each returns rows: name,url,price,metric,src)
def itch(path, n=20):
    rows = []
    h = get("https://itch.io/" + path)
    for c in h.split('class="game_cell ')[1:n + 1]:
        t = re.findall(r'class="title game_link"[^>]*>([^<]+)', c)
        u = re.findall(r'href="(https://[^"]+\.itch\.io/[^"]+)"', c)
        p = re.findall(r'class="price_value">([^<]+)', c)
        gnr = re.findall(r'class="game_genre">([^<]+)', c)
        if t:
            rows.append({"name": html.unescape(t[0]), "url": u[0] if u else "", "price": p[0] if p else "free / PWYW",
                         "metric": "itch.io top-sellers rank", "note": gnr[0] if gnr else "", "src": "itch.io/" + path})
    return rows


def crazygames(cat="puzzle", n=20):
    d = next_data(get(f"https://www.crazygames.com/c/{cat}"))
    seen, rows = set(), []
    for g in walk(d, lambda o: "slug" in o and "name" in o and "categoryName" in o, []):
        if g["slug"] in seen:
            continue
        seen.add(g["slug"])
        rows.append({"name": g["name"], "url": "https://www.crazygames.com/game/" + g["slug"], "price": "free (ads)",
                     "metric": "CrazyGames " + cat + " page order", "note": g.get("categoryName", ""), "src": "crazygames.com/c/" + cat})
        if len(rows) >= n:
            break
    for r in rows[:8]:   # rating of the first games from their own page
        try:
            gd = next_data(get(r["url"]))
            hit = walk(gd, lambda o: isinstance(o, dict) and "upvotes" in o and "downvotes" in o, [])
            if hit:
                up, dn = hit[0]["upvotes"], hit[0]["downvotes"]
                r["metric"] = f"{up:,} likes / {dn:,} dislikes ({100 * up / max(1, up + dn):.0f}% liked)"
        except Exception:
            pass
    return rows


def wporg(browse="popular", n=20):
    q = urllib.parse.urlencode({"action": "query_plugins", "request[browse]": browse, "request[per_page]": n,
                                "request[fields][active_installs]": 1, "request[fields][rating]": 1, "request[fields][num_ratings]": 1})
    d = json.loads(get("https://api.wordpress.org/plugins/info/1.2/?" + q))
    return [{"name": html.unescape(p["name"]), "url": f"https://wordpress.org/plugins/{p['slug']}/", "price": "free",
             "metric": f"{p.get('active_installs', 0):,}+ installs · {p.get('rating', 0) / 20:.1f}★ ({p.get('num_ratings', 0):,})",
             "note": p["slug"], "src": "api.wordpress.org " + browse} for p in d.get("plugins", [])]


def wporg_complaints(slugs, per=6):
    out = []
    for slug in slugs[:5]:
        try:
            x = get(f"https://wordpress.org/support/plugin/{slug}/reviews/feed/")
        except Exception:
            continue
        for item in re.findall(r"<item>(.*?)</item>", x, re.S):
            title = html.unescape(re.sub(r"<[^>]+>", "", (re.findall(r"<title>(.*?)</title>", item, re.S) or [""])[0]))
            body = html.unescape(re.sub(r"<[^>]+>", " ", (re.findall(r"<description>(.*?)</description>", item, re.S) or [""])[0]))
            m = re.search(r"Rating:\s*(\d)", body)
            if m and int(m.group(1)) <= 3:
                out.append(f"{slug} ({m.group(1)}★): {title.strip()} – {' '.join(body.split())[:160]}")
            if len([o for o in out if o.startswith(slug)]) >= per:
                break
    return out


def gumroad(query, n=20):
    """Gumroad Discover search sorted by most reviewed: name, seller, price, rating count (embedded page props)."""
    h = get("https://gumroad.com/discover?" + urllib.parse.urlencode({"query": query, "sort": "most_reviewed"}))
    m = re.search(r'data-page="([^"]{200,})"', h)
    rows = []
    if not m:
        return rows
    d = json.loads(html.unescape(m.group(1)))
    for p in walk(d, lambda o: isinstance(o, dict) and "ratings" in o and "price_cents" in o and "name" in o, [])[:n]:
        rt = p.get("ratings") or {}
        cur = (p.get("currency_code") or "usd").upper()
        price = "free / PWYW" if not p.get("price_cents") else f"${p['price_cents'] / 100:.2f}" if cur == "USD" else f"{p['price_cents'] / 100:.2f} {cur}"
        rows.append({"name": p["name"][:90], "url": (p.get("url") or "").split("?")[0], "price": price,
                     "metric": f"{rt.get('count', 0):,} ratings · {rt.get('average', 0)}★", "note": (p.get("seller") or {}).get("name", ""),
                     "src": "gumroad.com discover: " + query})
    return rows


def gutendex(n=20):
    d = json.loads(get("https://gutendex.com/books/?sort=popular&languages=en"))
    return [{"name": b["title"][:80], "url": f"https://www.gutenberg.org/ebooks/{b['id']}", "price": "public domain (free source)",
             "metric": f"{b.get('download_count', 0):,} downloads/30 days", "note": ", ".join(a["name"] for a in b.get("authors", []))[:60],
             "src": "gutendex.com (Project Gutenberg popular)"} for b in d.get("results", [])[:n]]


def gplay(query, n=20):
    h = get("https://play.google.com/store/search?" + urllib.parse.urlencode({"q": query, "c": "apps", "hl": "en", "gl": "US"}))
    rows, seen = [], set()
    for pkg in re.findall(r'href="/store/apps/details\?id=([\w.]+)"', h):
        if pkg in seen:
            continue
        seen.add(pkg)
        rows.append({"name": pkg, "url": "https://play.google.com/store/apps/details?id=" + pkg, "price": "?", "metric": "Play search rank", "note": "", "src": "play.google.com search: " + query})
        if len(rows) >= n:
            break
    for r in rows[:10]:   # title, rating, installs from the app page
        try:
            p = get(r["url"] + "&hl=en&gl=US")
            t = re.search(r'<h1[^>]*><span[^>]*>([^<]+)</span>', p) or re.search(r"<title>([^<]+?) - Apps on Google Play</title>", p)
            if t:
                r["name"] = html.unescape(t.group(1))
            rate = re.search(r'aria-label="Rated ([0-9.]+) stars out of five stars"', p)
            inst = re.search(r'<div class="ClM7O">([^<]+)</div><div class="g1rdde">Downloads', p)
            r["metric"] = " · ".join(x for x in [(rate.group(1) + "★") if rate else "", (inst.group(1) + " downloads") if inst else ""] if x) or r["metric"]
            r["price"] = "free" if "Install" in p else r["price"]
        except Exception:
            pass
    return rows


SOURCES = {
    "game": [lambda: crazygames("puzzle"), lambda: itch("games/top-sellers/html5")],
    "tool": [lambda: wporg("popular"), lambda: wporg("top-rated")],
    "mau": [lambda: gumroad("notion template", 12), lambda: gumroad("google sheets template", 12)],   # Etsy blocks bots (429): not scraped
    "sach": [lambda: gumroad("ebook guide", 10), gutendex],
    "studio": [lambda: itch("game-assets/top-sellers"), lambda: gumroad("game source code", 8)],
    "app": [lambda: gplay("loan calculator"), lambda: gplay("habit tracker")],
}
AI_TOPICS = {
    "game": "HTML5 browser games on Poki, CrazyGames, Playgama, GameDistribution",
    "tool": "WordPress plugins on CodeCanyon and WordPress.org, Chrome extensions, Gumroad software",
    "mau": "Notion, Google Sheets and Excel templates sold on Gumroad, Etsy and the Notion Marketplace",
    "sach": "Amazon Kindle best sellers in personal finance, self-help, pets and crypto",
    "studio": "game assets and HTML5 game source code on itch.io, GameDev Market, Unity Asset Store, CodeCanyon",
    "app": "Google Play utility apps: calculators, timers, converters, habit trackers",
}


def price_tiers(rows):
    nums = []
    for r in rows:
        m = re.search(r"\$\s?([0-9]+(?:\.[0-9]+)?)", str(r.get("price", "")))
        if m:
            nums.append(float(m.group(1)))
    if not nums:
        return "no list prices on the scanned pages (free / ad-supported / pay what you want)"
    nums.sort()
    return f"low ${nums[0]:.2f} · median ${statistics.median(nums):.2f} · high ${nums[-1]:.2f} ({len(nums)} priced items)"


def run(nganh, out_dir, net24):
    rows, errors = [], []
    for f in SOURCES[nganh]:
        try:
            rows += f()
        except Exception as e:
            errors.append(f"{getattr(f, '__name__', 'source')}: {type(e).__name__}")
    complaints = wporg_complaints([r["note"] for r in rows]) if nganh == "tool" else []
    extra = None
    if ai.available():
        extra = ai.ask_json(
            f"You are a market researcher for {AI_TOPICS[nganh]}. Today is {TODAY}. Use current public data. Return JSON with keys: "
            "top (up to 20 items {name,url,price,metric} of best sellers right now if the list below is short), "
            "rising (5 items {name_or_keyword, evidence}), complaints (5+ recurring complaints from 1-3 star reviews of the top 5), "
            "price_tiers {low,mid,high,what_sells}, proposals (3 items {title, leader_name, leader_url, score_0_100, why_demand, "
            "ten_features_of_leader:[...10], two_ways_to_beat_from_complaints:[...2]}). Only propose items scoring >= 75. "
            "Already collected list: " + json.dumps(rows[:20])[:6000], max_tokens=3500, search=True)
    if extra and extra.get("top") and len(rows) < 10:
        rows += [{**r, "src": "AI + Google Search"} for r in extra["top"]]
    if extra and extra.get("complaints"):
        complaints += [str(c) for c in extra["complaints"]]
    lines = [f"# HỌC TOP – {NAMES[nganh]} ({TODAY})", "",
             "Tự động bởi `tools/chung/nghien_cuu.py` (thứ Hai hằng tuần). Số liệu lấy từ trang công khai/API chính thức, không đăng nhập.", "",
             "## 1. Top 20 đang bán chạy", "", "| # | Tên | Giá | Số đo công khai | Nguồn | Ghi chú |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(rows[:20], 1):
        r = {k: str(v).replace("|", "/") for k, v in r.items()}
        lines.append(f"| {i} | [{r['name']}]({r['url']}) | {r.get('price', '')} | {r.get('metric', '')} | {r.get('src', '')} | {r.get('note', '')} |")
    if not rows:
        lines.append("| – | chưa lấy được (xem lỗi bên dưới) | | | | |")
    lines += ["", "## 2. Đang lên (30 ngày)", ""]
    lines += [f"- {x.get('name_or_keyword', x)} – {x.get('evidence', '')}" for x in (extra or {}).get("rising", [])] or ["- chờ khóa AI (N24_AI_KEY hoặc GEMINI_API_KEY) để đọc Google Trends / mục new & rising"]
    lines += ["", "## 3. Đào lời chê (đánh giá 1–3 sao của top 5)", ""]
    lines += [f"- {c}" for c in complaints] or ["- chờ khóa AI để đọc đánh giá trên sàn"]
    lines += ["", "## 4. Bậc giá", "", "- Từ danh sách trên: " + price_tiers(rows)]
    if extra and extra.get("price_tiers"):
        lines.append("- AI: " + json.dumps(extra["price_tiers"], ensure_ascii=False))
    lines += ["", "## 5. Phiếu đề xuất (≥ 75 điểm)", ""]
    props = [p for p in (extra or {}).get("proposals", []) if int(p.get("score_0_100", 0) or 0) >= 75]
    lines += [f"- **{p['title']}** – {p.get('score_0_100')} điểm · leader [{p.get('leader_name')}]({p.get('leader_url')}) · {p.get('why_demand', '')}" for p in props] or ["- chờ khóa AI; trong lúc chờ xưởng làm theo phiếu có sẵn trong YEU-CAU/agent3/"]
    if errors:
        lines += ["", "Lỗi nguồn lần này: " + "; ".join(errors)]
    out = "\n".join(lines) + "\n"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"HOC-TOP-{nganh}.md"
    hist = ""
    if path.exists():
        old = path.read_text(encoding="utf-8")
        hist = old.split("## Lịch sử", 1)[1] if "## Lịch sử" in old else "\n\n| Ngày | Số mục top | Lời chê | Phiếu |\n|---|---|---|---|\n"
    else:
        hist = "\n\n| Ngày | Số mục top | Lời chê | Phiếu |\n|---|---|---|---|\n"
    hist = hist.rstrip("\n") + f"\n| {TODAY} | {len(rows[:20])} | {len(complaints)} | {len(props)} |\n"
    full = out + "\n## Lịch sử" + hist
    path.write_text(full, encoding="utf-8")
    if net24:
        n = Path(net24)
        (n / "13-Ban-hang-so" / "HOC-TOP").mkdir(parents=True, exist_ok=True)
        (n / "13-Ban-hang-so" / "HOC-TOP" / f"{nganh}.md").write_text(full, encoding="utf-8")
        for p in props:
            slug = re.sub(r"[^a-z0-9]+", "-", p["title"].lower()).strip("-")[:40]
            yt = n / "BAN-GIAO" / "y-tuong" / f"{TODAY.replace('-', '')}-{nganh}-{slug}.md"
            yt.parent.mkdir(parents=True, exist_ok=True)
            yt.write_text(f"# Phiếu đề xuất: {p['title']} (xưởng {nganh})\n\n- Điểm: {p.get('score_0_100')}/100 · ngày {TODAY} · nguồn: nghiên cứu tự động\n"
                          f"- Leader: [{p.get('leader_name')}]({p.get('leader_url')})\n- Vì sao có cầu: {p.get('why_demand', '')}\n\n## 10 đặc điểm leader\n"
                          + "\n".join(f"{i}. {x}" for i, x in enumerate(p.get("ten_features_of_leader", []), 1))
                          + "\n\n## 2 điểm vượt (từ lời chê)\n" + "\n".join(f"- {x}" for x in p.get("two_ways_to_beat_from_complaints", []))
                          + "\n\nAgent 2 chấm trong 48 giờ; quá hạn mà ≥ 80 điểm thì xưởng tự làm.\n", encoding="utf-8")
    print(f"[nghien-cuu] {nganh}: top {len(rows[:20])}, complaints {len(complaints)}, proposals {len(props)}, errors {errors}")
    return {"top": len(rows[:20]), "complaints": len(complaints), "proposals": len(props), "errors": errors}


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = argparse.ArgumentParser()
    a.add_argument("nganh", choices=list(SOURCES))
    a.add_argument("--out", default="NGHIEN-CUU")
    a.add_argument("--net24", default="")
    x = a.parse_args()
    run(x.nganh, Path(x.out), x.net24)
