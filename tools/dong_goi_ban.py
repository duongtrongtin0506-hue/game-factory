# -*- coding: utf-8 -*-
"""Dong goi san pham ban ma nguon: python tools/dong_goi_ban.py <ma san pham>  (vd C1, B1, A1, AG = goi 9 tro)
Ghi ban/<ma>/<ma>.zip gom ma nguon khong nen, README.md tieng Anh, LICENSE.txt. Ma san pham theo bang trong BAN-MA-NGUON.md.
Nhom A can ban/<tro>/index.html do tools/tach_tro.py tao ra truoc. Ban chay thu va anh chup lam rieng."""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI_NOTE = "The code was written with the help of an AI assistant (Claude) and tested by automated scripts."

LICENSE = """{name} - Commercial License

You may use this code in unlimited personal and commercial projects, modify it, and publish games or products built with it.
You may NOT resell, redistribute or share the source code itself (original or modified) as a code product, template or asset pack.
The code comes as is, without warranty. {ai}
"""

SOLVER = "Generates puzzle levels with a seeded generator, checks every level with an exact solver (so each one is solvable), and measures difficulty."


def tool(code, name, py, data, blurb):
    return {"name": name, "files": [f"tools/{py}", f"levels/{data}.json", f"content-queue/{data}.json"], "readme": f"""# {name}

{blurb} {SOLVER}

## Run
Python 3.9+, no extra packages.

    python tools/{py} verify        re-solve every level in levels/ and content-queue/
    python tools/{py} fill 60       generate new levels for 60 seconds into content-queue/
    python tools/{py} take 20       move 20 levels from the queue into levels/

Levels are plain JSON, so any engine (Unity, Godot, Phaser, plain JS) can read them. Sample data is included.

## Customise
Board size, difficulty limits and the queue size are constants at the top of tools/{py}.

## Notes
{AI_NOTE}
"""}


PRODUCTS = {
    "C1": {"name": "HTML5 Portal Ads Layer",
           "files": ["web/ads.js", "tools/test_ads.js"],
           "readme": f"""# HTML5 Portal Ads Layer

One small file (web/ads.js) that puts the ad SDKs of the big HTML5 game portals behind the same four calls:
CrazyGames (SDK v3), GameDistribution, GameMonetize and Playgama Bridge, plus a no-ads mode for itch.io and local testing.

## Use
1. Paste the file into your game (before your game code), set `PORTAL` to `'crazygames'`, `'gamedistribution'`, `'gamemonetize'`, `'playgama'` or `'none'`, and `GAME_ID` where the portal gives you one.
2. Call `showAd('midgame', ok => ...)` at natural breaks and `showAd('rewarded', ok => ...)` when the player asks for a reward. `ok` is true when the reward may be given.
3. Call `gameplay(true/false)` when a round starts/stops and `happy()` on a win (CrazyGames).
4. Read `adPlaying` in your loop to freeze the game and mute sound while an ad is on screen.
5. Optional: define `onPortalReady()` to run code once the SDK is up.

Rules built in: a rewarded ad is never held back, midgame ads are at least 60 seconds apart (`MIDGAME_GAP`), a failed or blocked SDK never freezes the game.
Playgama needs `playgama-bridge-config.json` next to index.html (see their docs).

## Test
    node tools/test_ads.js
runs the layer against fake SDKs of every portal and prints one line; exit code 1 on a mismatch.

## Notes
{AI_NOTE} Checked against the portals' public docs in October 2026; SDKs change, re-check before release.
"""},
    "B1": tool("B1", "Sliding Car Puzzle Generator + Solver", "carjam.py", "car-jam", "6x6 sliding-car (traffic jam) puzzles: free the red car through the exit."),
    "B2": tool("B2", "Color Sort Puzzle Generator + Solver", "bobasort.py", "boba-sort", "Colour-sorting (pour into cups) puzzles; the A* solver returns the minimum number of moves."),
    "B3": tool("B3", "Triple Tile Puzzle Generator + Solver", "tiletrio.py", "tile-trio", "Match-three-tiles stack puzzles with a seed-based generator."),
    "B4": tool("B4", "One-Stroke Puzzle Generator + Solver", "oneline.py", "one-line", "One-stroke (fill every cell with one path) grid puzzles."),
}

GAMES = {"A1": "Balloon Pop", "A2": "Whack a Mole", "A3": "Number Tap", "A4": "Ink or Word", "A5": "Memory Pairs",
         "A6": "Quick Math", "A7": "Odd Tile", "A8": "Simon Pads", "A9": "Basket Catch"}
SLUG = {"A1": "balloon", "A2": "mole", "A3": "number", "A4": "stroop", "A5": "memory",
        "A6": "math", "A7": "odd", "A8": "simon", "A9": "catch"}
for k, n in GAMES.items():
    PRODUCTS[k] = {"name": n + " - HTML5 Game", "files": [f"ban/{SLUG[k]}/index.html"], "readme": f"""# {n} - HTML5 Game

A single-file HTML5 canvas game: menu, high score, sound toggle, touch and mouse, and a ready place to plug in portal ads.

## Run
Open index.html in a browser (or serve the folder with any static server). No build step, no dependencies.

## Customise
Colours, texts and difficulty are constants near the top of the script in index.html. Ads: add your portal SDK call where the file says `AD HOOK`.

## Notes
{AI_NOTE}
"""}


# Goi cung chu de: ca 9 tro + che do Journey (khong can tach_tro). Tep ghi dang (nguon, ten trong zip).
PRODUCTS["AG"] = {"name": "9 Reflex Mini Games Bundle",
                  "files": [("dist/tap-arcade/none/index.html", "game/index.html"), ("web/tap-arcade/index.src.html", "source/index.src.html"),
                            ("levels/tap-arcade.json", "source/levels.json"), ("web/ads.js", "source/ads.js")],
                  "readme": """# 9 Reflex Mini Games Bundle

Nine tap and reflex mini games in one HTML5 file, with a 45-stage Journey mode. Pure JavaScript and canvas, no engine, no image or sound files.

## Features

- 9 games: Balloon Pop, Whack a Mole, Number Tap, Ink or Word (Stroop), Memory Pairs, Quick Math, Odd Tile, Simon Pads, Basket Catch
- Journey mode: 45 stages read from one JSON file, each with a goal and a star rating
- One HTML file, about 65 KB, loads in under a second; every shape is drawn in code and every sound is synthesised, so there are no assets to license
- Works with mouse and touch, portrait and landscape, phone to desktop; progress saved in localStorage
- Ad layer included for CrazyGames, GameDistribution, Playgama and GameMonetize (midgame and rewarded); set two constants to switch it on
- Tested with Playwright in Chromium and WebKit

## Run it

Open `game/index.html` in a browser, or upload the `game` folder to any web host. Nothing to install.

## What is in the box

- `game/index.html` - the game, ready to publish, ads switched off.
- `source/index.src.html` - the same game before the stages and the ad layer are pasted in. The markers `/*LEVELS*/` and `/*ADS*/` show where `levels.json` and `ads.js` go.
- `source/levels.json` - the 45 Journey stages: which mini game, the goal and the star thresholds.
- `source/ads.js` - the portal ad layer.

To rebuild `game/index.html` after editing the source: replace `/*LEVELS*/` with the content of `levels.json` and `/*ADS*/` with the content of `ads.js`, and save the result as `index.html`.

## Change the look

Colours, corner radius and fonts are constants near the top of the script (search for `const C =` and `const FONT`). All drawing is canvas code, one function per mini game (`balloonGame`, `moleGame`, `numberGame`, `stroopGame`, `memoryGame`, `mathGame`, `oddGame`, `simonGame`, `catchGame`). The title text is in `<title>` and in the menu drawing function.

## Add or change stages

Edit `source/levels.json` and rebuild. Each stage names a mini game and its goal. Opening the game on localhost with `?selftest=1` checks every stage and puts the result in the page title.

## Switch on ads

In the built `index.html` set `const PORTAL` to one of `'crazygames'`, `'gamedistribution'`, `'playgama'`, `'gamemonetize'` and, for GameDistribution and GameMonetize, set `const GAME_ID` to the id the portal gives you. Ads never load on localhost. The game calls `showAd('midgame', done)` between stages and `showAd('rewarded', done)` when the player asks for a reward; you do not need to touch those calls.

## Useful URL switches

These only work on a local test server (localhost): `?stage=N` opens Journey stage N, `?play=<game>` opens one mini game, `?selftest=1` runs the built-in checks.

## Notes
""" + AI_NOTE + "\n"}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in PRODUCTS:
        sys.exit("dung: python tools/dong_goi_ban.py <" + "|".join(PRODUCTS) + ">")
    code = sys.argv[1]
    p = PRODUCTS[code]
    files = [f if isinstance(f, tuple) else (f, f.replace("ban/", "", 1)) for f in p["files"]]
    missing = [f for f, _ in files if not (ROOT / f).exists()]
    if missing:
        sys.exit("thieu tep: " + ", ".join(missing) + (" (chay tools/tach_tro.py truoc)" if code.startswith("A") else ""))
    out = ROOT / "ban" / code
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"{code}.zip"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f, name in files:
            z.write(ROOT / f, name)
        z.writestr("README.md", p["readme"])
        z.writestr("LICENSE.txt", LICENSE.format(name=p["name"], ai=AI_NOTE))
    print(f"da ghi {dest.relative_to(ROOT)} ({dest.stat().st_size // 1024} KB, {len(p['files']) + 2} tep)")


if __name__ == "__main__":
    main()
