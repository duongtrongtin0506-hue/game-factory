# -*- coding: utf-8 -*-
"""Dong goi moi game cho tung cong: python tools/build.py
  dist/<game>/<cong>/index.html   va   dist/<game>/<game>-<cong>.zip
Moi goi la index.html cua game voi hang PORTAL doi theo cong ('none' = khong quang cao: itch.io, chay thu).
Ca 5 game: ghep levels/<game>.json vao web/<game>/index.src.html truoc."""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ["tap-arcade", "boba-sort", "car-jam", "tile-trio", "one-line"]
PORTALS = ["gamemonetize", "crazygames", "none"]
FLAG = "const PORTAL = 'gamemonetize';"


def merge_levels(game, par):
    """Ghep man vao game. par: co ghi them mang PAR (so buoc it nhat) hay khong."""
    levels = json.loads((ROOT / "levels" / f"{game}.json").read_text(encoding="utf-8"))
    src = (ROOT / "web" / game / "index.src.html").read_text(encoding="utf-8")
    if "/*LEVELS*/" not in src:
        raise SystemExit(f"Khong thay dau /*LEVELS*/ trong web/{game}/index.src.html")
    code = "const LEVELS = [\n" + ",\n".join(f"  '{r['board']}'" for r in levels) + "\n];"
    if par:
        code += "\nconst PAR = [" + ",".join(str(r["moves"]) for r in levels) + "];"
    (ROOT / "web" / game / "index.html").write_text(src.replace("/*LEVELS*/", code), encoding="utf-8", newline="\n")
    return len(levels)


def build():
    merge_levels("car-jam", par=True)
    merge_levels("boba-sort", par=False)
    merge_levels("tile-trio", par=False)
    merge_levels("one-line", par=False)
    merge_levels("tap-arcade", par=False)
    out = []
    for game in GAMES:
        src = (ROOT / "web" / game / "index.html").read_text(encoding="utf-8")
        if FLAG not in src:
            raise SystemExit(f"Khong thay hang PORTAL trong web/{game}/index.html")
        for portal in PORTALS:
            stage = ROOT / "dist" / game / portal
            stage.mkdir(parents=True, exist_ok=True)
            (stage / "index.html").write_text(src.replace(FLAG, f"const PORTAL = '{portal}';"), encoding="utf-8", newline="\n")
            with zipfile.ZipFile(ROOT / "dist" / game / f"{game}-{portal}.zip", "w", zipfile.ZIP_DEFLATED) as z:
                z.write(stage / "index.html", "index.html")
        out.append(f"{game} {len(src.encode('utf-8')) // 1024}KB")
    return out


if __name__ == "__main__":
    print("da dong goi: " + ", ".join(build()))
