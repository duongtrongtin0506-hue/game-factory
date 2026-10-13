# -*- coding: utf-8 -*-
"""Dong goi moi game cho tung cong: python tools/build.py
  dist/<game>/<cong>/index.html   va   dist/<game>/<game>-<cong>.zip
Nguon moi game la web/<game>/index.src.html. Buoc nay ghep vao do:
  /*LEVELS*/  man choi tu levels/<game>.json
  /*ADS*/     lop quang cao chung web/ads.js, voi PORTAL = cong dang dong goi va GAME_ID = ma game o cong do (specs/<game>.json, muc portal_ids)
web/<game>/index.html la ban cong 'gamemonetize' (de chay thu tren may); cong 'none' = khong quang cao: itch.io, kiem thu."""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ["tap-arcade", "boba-sort", "car-jam", "tile-trio", "one-line", "merge-harvest"]
PORTALS = ["gamemonetize", "crazygames", "gamedistribution", "none"]
PAR = {"car-jam"}   # game can them mang PAR (so buoc it nhat cua tung man)
NO_LEVELS = {"merge-harvest"}   # tro vo tan: khong co levels/<game>.json, nguon chi can dau /*ADS*/


def with_levels(game):
    """-> (nguon da ghep man, so man)."""
    src = (ROOT / "web" / game / "index.src.html").read_text(encoding="utf-8")
    if game in NO_LEVELS:
        if src.count("/*ADS*/") != 1:
            raise SystemExit(f"Can dung 1 dau /*ADS*/ trong web/{game}/index.src.html")
        return src, 0
    levels = json.loads((ROOT / "levels" / f"{game}.json").read_text(encoding="utf-8"))
    for mark in ("/*LEVELS*/", "/*ADS*/"):
        if src.count(mark) != 1:
            raise SystemExit(f"Can dung 1 dau {mark} trong web/{game}/index.src.html")
    code = "const LEVELS = [\n" + ",\n".join(f"  '{r['board']}'" for r in levels) + "\n];"
    if game in PAR:
        code += "\nconst PAR = [" + ",".join(str(r["moves"]) for r in levels) + "];"
    return src.replace("/*LEVELS*/", code), len(levels)


def with_ads(src, game, portal):
    ads = (ROOT / "web" / "ads.js").read_text(encoding="utf-8").strip()
    ids = json.loads((ROOT / "specs" / f"{game}.json").read_text(encoding="utf-8")).get("portal_ids", {})
    for mark, value in (("/*PORTAL*/", portal), ("/*GAME_ID*/", ids.get(portal, ""))):
        if ads.count(mark) != 1:
            raise SystemExit(f"Can dung 1 dau {mark} trong web/ads.js")
        ads = ads.replace(mark, value)
    return src.replace("/*ADS*/", ads)


def build():
    out = []
    for game in GAMES:
        src, _ = with_levels(game)
        for portal in PORTALS:
            html = with_ads(src, game, portal)
            stage = ROOT / "dist" / game / portal
            stage.mkdir(parents=True, exist_ok=True)
            (stage / "index.html").write_text(html, encoding="utf-8", newline="\n")
            with zipfile.ZipFile(ROOT / "dist" / game / f"{game}-{portal}.zip", "w", zipfile.ZIP_DEFLATED) as z:
                z.write(stage / "index.html", "index.html")
            if portal == "gamemonetize":
                (ROOT / "web" / game / "index.html").write_text(html, encoding="utf-8", newline="\n")
        out.append(f"{game} {len(html.encode('utf-8')) // 1024}KB")
    return out


if __name__ == "__main__":
    print("da dong goi: " + ", ".join(build()))
