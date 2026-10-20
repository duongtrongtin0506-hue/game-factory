"""Hand the Drop & Merge games to Agent 2: python khung/giao.py <net24-he-thong folder>

Copies into BAN-GIAO/20261025-game-khung-puzzle/:
  khung/            frame source (engine, game, themes, template, generator, build, test, i18n, ads.js)
  game-0N-<id>/     index.html (no ads, for itch.io / self-hosting), one zip per portal, store media, STORE.md
  bang-chung/       REPORT.md + every game's report.json, screenshots, 5 s GIF, autoplay trailer (mp4)
Run python khung/build.py and python khung/test.py first.
"""
import json
import shutil
import sys
from pathlib import Path

K = Path(__file__).resolve().parent
ROOT = K.parent
PORTAL_NOTE = {
    "gamedistribution": "GameDistribution: upload the zip, then paste the gameId into variants.json portal_ids.gamedistribution and rebuild (the SDK only loads with an id).",
    "playgama": "Playgama: zip has index.html + playgama-bridge-config.json at the root. Run Test Game in the dashboard before Submit.",
    "crazygames": "CrazyGames: upload the zip (SDK v3, gameplayStart/Stop, happytime, cloud save already wired).",
    "gamemonetize": "GameMonetize: needs the game hash in portal_ids.gamemonetize and a rebuild. NOTE: GameMonetize rejected AI-made games on 13/10 – submit last.",
    "none": "No SDK, no ads: itch.io (HTML game, 'This file will be played in the browser'), own website, Play24 Arcade via n24arc_add_original().",
}


def store_md(v, s, rep):
    lines = [f"# {s['title']}", "",
             f"Title ({len(s['title'])} chars): **{s['title']}**", "",
             "## Description (US English)", "", s["open"], ""]
    lines += [f"- {b}" for b in s["bullets"]]
    lines += ["", "## FAQ", ""]
    for q, a in s["faq"]:
        lines += [f"**{q}** {a}", ""]
    lines += ["## Tags", "", ", ".join(s["tags"]) + f" · genre: {s['genre']}", "",
              "## Controls", "", "Tap or click a column to drop. Desktop: 1–6 keys, arrows + Space/Enter. Hammer removes one tile; Hint shows the solver's best column.", "",
              "## Price / model", "",
              "Free to play, ad revenue share on portals (interstitial between levels, optional rewarded video for Hint, Hammer, extra drops). "
              "The leader (2048 Blocks Merge, CrazyGames) is free with ads as well; nothing to charge on portals.", "",
              "## AI disclosure", "",
              "Code, level layouts and drawings were made with AI assistance (Claude) and checked by automatic tests. "
              "itch.io: set 'AI generation disclosure' = Yes (Code, Graphics, Text). CrazyGames/GameDistribution/Playgama: no field; answer truthfully if asked.", "",
              "## Files", ""]
    for z in sorted((K / "dist" / v["id"]).glob("*.zip")):
        portal = z.stem.replace(v["id"] + "-", "")
        lines.append(f"- `{z.name}` – {PORTAL_NOTE.get(portal, portal)}")
    lines += ["- `media/cover-512x512.png`, `cover-512x384.png`, `cover-1280x720.png`, `cover-1920x1080.png`, `cover-720x1280.png`",
              "- `media/shot-*-1280x720.png`, `media/shot-*-720x1280.png` (3 screenshots each way), `media/preview-5s.gif`, `media/trailer.mp4`", "",
              "## Test result", "",
              f"Selftest {rep['selftest']} · autoplay won {len(rep['autoplay']['won'])}/{rep['autoplay']['levels']} · FPS median {rep['fps']['median']} · "
              f"load {rep['loads']} s · console errors {len(rep['errors'])} · zip {max(rep['zip_kb'].values())} KB", ""]
    return "\n".join(lines)


def main():
    net = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent.parent / "net24-he-thong"
    dest = net / "BAN-GIAO" / "20261025-game-khung-puzzle"
    variants = json.loads((K / "variants.json").read_text(encoding="utf-8"))
    store = json.loads((K / "store.json").read_text(encoding="utf-8"))
    src = dest / "khung"
    shutil.rmtree(src, ignore_errors=True)
    src.mkdir(parents=True)
    for f in ["engine.js", "game.js", "themes.js", "template.html", "gen.js", "build.py", "test.py", "giao.py", "variants.json", "store.json", "README.md"]:
        if (K / f).exists():
            shutil.copy2(K / f, src / f)
    shutil.copytree(K / "i18n", src / "i18n")
    shutil.copytree(K / "levels", src / "levels")
    shutil.copy2(ROOT / "web" / "ads.js", src / "ads.js")
    proof = dest / "bang-chung"
    shutil.rmtree(proof, ignore_errors=True)
    proof.mkdir(parents=True)
    shutil.copy2(K / "proof" / "REPORT.md", proof / "REPORT.md")
    for n, v in enumerate(variants, 1):
        vid = v["id"]
        out = dest / f"game-{n:02d}-{vid}"
        shutil.rmtree(out, ignore_errors=True)
        (out / "media").mkdir(parents=True)
        shutil.copy2(K / "dist" / vid / "index.html", out / "index.html")
        for z in (K / "dist" / vid).glob("*.zip"):
            shutil.copy2(z, out / z.name)
        pr = K / "proof" / vid
        for f in pr.glob("cover-*.png"):
            shutil.copy2(f, out / "media" / f.name)
        for f in pr.glob("shot-*.png"):
            shutil.copy2(f, out / "media" / f.name)
        for f in ("preview-5s.gif", "trailer.mp4"):
            if (pr / f).exists():
                shutil.copy2(pr / f, out / "media" / f)
        rep = json.loads((pr / "report.json").read_text(encoding="utf-8"))
        (out / "STORE.md").write_text(store_md(v, store[vid], rep), encoding="utf-8")
        pd = proof / vid
        pd.mkdir()
        for f in pr.glob("size-*.png"):
            shutil.copy2(f, pd / f.name)
        shutil.copy2(pr / "report.json", pd / "report.json")
    total = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
    print("handed over to", dest, f"{total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
