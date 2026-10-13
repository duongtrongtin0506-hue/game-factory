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
# Goi nop cong: phat-hanh/<cong>/<game>/ = zip + mo-ta.md. Chi game co muc "store" trong specs moi duoc dong goi.
# cong -> (trang nop, cac anh bia can nop lay tu assets-goc/<game>/, ghi chu)
RELEASE = {
    "crazygames": ("https://developer.crazygames.com/", ["cover-1920x1080.png", "cover-800x1200.png", "cover-800x800.png", "preview-landscape-1920x1080.mp4", "preview-portrait-1080x1620.mp4"],
                   "Tai len tep index.html trong zip (hoac ca zip). Bai bi tu choi khong tai ban moi duoc: tao bai nop moi. Anh bia va video phai tai lai moi lan doi ban."),
    "gamemonetize": ("https://gamemonetize.com/account/", ["cover-512x384.jpg", "cover-512x512.jpg", "cover-512x340.jpg"],
                     "Moi game can GameId rieng: tao game tren cong, chep GameId vao specs/<game>.json muc portal_ids.gamemonetize, build lai roi moi tai zip."),
    "gamedistribution": ("https://developer.gamedistribution.com/", ["cover-512x512.jpg", "cover-512x384.jpg", "cover-1920x1080.png"],
                         "Can tai khoan da kich hoat va gameId (portal_ids.gamedistribution). Co anh cong yeu cau: chua xac minh, xem CONG.md."),
}
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


def release():
    """Sau build(): ghi phat-hanh/<cong>/<game>/<game>.zip + mo-ta.md. Zip co ngay gio co dinh de khong doi khi noi dung khong doi. -> so goi."""
    count = 0
    for game in GAMES:
        spec = json.loads((ROOT / "specs" / f"{game}.json").read_text(encoding="utf-8"))
        store = spec.get("store")
        if not store:
            continue
        for portal, (link, covers, note) in RELEASE.items():
            out = ROOT / "phat-hanh" / portal / game
            out.mkdir(parents=True, exist_ok=True)
            info = zipfile.ZipInfo("index.html", (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            with zipfile.ZipFile(out / f"{game}.zip", "w") as z:
                z.writestr(info, (ROOT / "dist" / game / portal / "index.html").read_bytes())
            have = [c for c in covers if (ROOT / "assets-goc" / game / c).exists()]
            missing = [c for c in covers if c not in have]
            need_id = portal in spec.get("portal_ids", {}) and not spec["portal_ids"][portal]
            lines = [f"# {store['title']} -> {portal}", "",
                     f"- Submit page: {link}",
                     f"- Game file: `phat-hanh/{portal}/{game}/{game}.zip` (index.html at the root)",
                     "- Covers / video: " + (", ".join(f"`assets-goc/{game}/{c}`" for c in have) or "none yet"),
                     *([f"- MISSING (run `python tools/quay.py {game}`): " + ", ".join(missing)] if missing else []),
                     *([f"- BLOCKED: portal_ids.{portal} is empty in specs/{game}.json"] if need_id else []),
                     f"- Note: {note}", "",
                     f"Title: {store['title']}", "", f"Short description: {store['short']}", "", f"Description: {store['long']}", "",
                     f"How to play: {store['how_to_play']}", "", f"Controls: {store['controls']}", "",
                     f"Category: {store['category']}", "", "Tags: " + ", ".join(store["tags"]), "",
                     "Orientation: portrait and landscape. Language: English. Devices: desktop, mobile, tablet.", ""]
            (out / "mo-ta.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
            count += 1
    return count


if __name__ == "__main__":
    print("da dong goi: " + ", ".join(build()))
    print(f"goi nop cong: {release()} (phat-hanh/<cong>/<game>/)")
