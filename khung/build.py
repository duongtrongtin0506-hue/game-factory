"""Build the Drop & Merge games: python khung/build.py [variant-id]

For every variant in khung/variants.json: one self-contained index.html per portal
(ads layer web/ads.js with PORTAL and GAME_ID filled in) and one zip per portal:
  khung/dist/<id>/<portal>/index.html (+ playgama-bridge-config.json for Playgama)
  khung/dist/<id>/<id>-<portal>.zip
  khung/dist/<id>/index.html = the 'none' build, for local testing.
Levels come from khung/levels/<id>.json (make them with: node khung/gen.js).
GAME_ID for GameDistribution / GameMonetize: variants.json -> "portal_ids": {"gamedistribution": "..."}.
"""
import json
import sys
import zipfile
from pathlib import Path

K = Path(__file__).resolve().parent
ROOT = K.parent
PORTALS = ["gamedistribution", "playgama", "crazygames", "gamemonetize", "none"]
PG_CONFIG = json.dumps({"advertisement": {"minimumDelayBetweenInterstitial": 60,
                                          "interstitial": {"placements": [{"id": "level_completed"}]},
                                          "rewarded": {"placements": [{"id": "reward"}]}}}, indent=2) + "\n"


def read(p):
    return (K / p).read_text(encoding="utf-8")


def strings():
    out = {}
    for f in sorted((K / "i18n").glob("*.json")):
        out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return out


def page(v, portal):
    themes = read("themes.js")
    levels = json.loads(read(f"levels/{v['id']}.json"))
    ads = (ROOT / "web" / "ads.js").read_text(encoding="utf-8")
    ads = ads.replace("/*PORTAL*/", portal).replace("/*GAME_ID*/", v.get("portal_ids", {}).get(portal, ""))
    meta = {k: v[k] for k in ("id", "title", "theme", "rule")}
    page_color = "#0A0A0B" if v["theme"] in ("gems", "space") else "#FFFBF5"
    html = read("template.html")
    for mark, value in (("/*TITLE*/", v["title"]), ("/*PAGE*/", page_color), ("/*ADS*/", ads), ("/*ENGINE*/", read("engine.js")),
                        ("/*THEMES*/", themes), ("/*VARIANT*/", json.dumps(meta)), ("/*LEVELS*/", json.dumps(levels, separators=(",", ":"))),
                        ("/*STR*/", json.dumps(strings(), ensure_ascii=False)), ("/*GAME*/", read("game.js"))):
        assert mark in html, mark
        html = html.replace(mark, value, 1)
    return html


def build(v):
    out = K / "dist" / v["id"]
    for portal in PORTALS:
        stage = out / portal
        stage.mkdir(parents=True, exist_ok=True)
        html = page(v, portal)
        (stage / "index.html").write_text(html, encoding="utf-8", newline="\n")
        files = {"index.html": html}
        if portal == "playgama":
            (stage / "playgama-bridge-config.json").write_text(PG_CONFIG, encoding="utf-8", newline="\n")
            files["playgama-bridge-config.json"] = PG_CONFIG
        with zipfile.ZipFile(out / f"{v['id']}-{portal}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for name, text in files.items():
                info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, text)
        if portal == "none":
            (out / "index.html").write_text(html, encoding="utf-8", newline="\n")
    size = (out / "none" / "index.html").stat().st_size
    print(f"{v['id']}: {len(PORTALS)} portals, index.html {size / 1024:.0f} KB")


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for v in json.loads(read("variants.json")):
        if not only or v["id"] == only:
            build(v)


if __name__ == "__main__":
    main()
