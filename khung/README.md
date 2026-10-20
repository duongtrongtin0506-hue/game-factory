# Drop & Merge frame

A small HTML5 puzzle frame: drop a tile into a column, equal touching tiles merge into the next
tier, merges chain. One engine, five looks, five level rules, one self-contained `index.html`
per game (about 80 KB, no images, no external requests except the portal SDK).

## Files

| File | What it does |
|---|---|
| `engine.js` | Rules, goals, beam-search solver, one-step "plain player". Runs in the browser and in Node. |
| `themes.js` | Five looks (`fruit`, `gems`, `space`, `food`, `animals`): colours + twelve tiers drawn in code. |
| `game.js` | Screens, drawing, input, sound (WebAudio synth), saving, autoplay, cover art. |
| `template.html` | Page shell; `build.py` fills the markers. |
| `variants.json` | One line per game: id, title, theme, rule, seed, level count, optional `portal_ids`. |
| `gen.js` | Level generator: board + goal from the rule, solver must win, drops = solver + slack, difficulty = % of plain-player failures, every 5th level easy. |
| `build.py` | One `index.html` + one zip per portal (GameDistribution, Playgama, CrazyGames, GameMonetize, none). |
| `test.py` | Playwright: replays every level's solution, loads at 360×640 / 640×360 / 1280×720 with a slow CPU and 4G-like network, lets the solver play 10 levels on video, samples FPS, renders covers, screenshots, GIF. |
| `i18n/en.json` | All on-screen text. Add `i18n/es.json` etc. with the same keys; the game picks the browser language. |
| `ads.js` | Shared ad layer (copy of `web/ads.js`): `showAd('midgame'|'rewarded', done)`, `gameplay(on)`, `happy()`, `adPlaying`. |

## Make a new game in 10 minutes

1. Add a line to `variants.json`: `{ "id": "my-game", "title": "My Game", "theme": "fruit", "rule": "reach", "seed": 99, "levels": 40 }`.
   Rules: `reach` (make a tier), `stones` (break stones), `make` (orders), `ice` (melt ice), `score`.
2. `node gen.js my-game` → `levels/my-game.json` (about 10–60 s; same seed = same levels).
3. `python build.py my-game` → `dist/my-game/`.
4. `python test.py my-game` → `proof/my-game/report.json` must say `"pass": true`.

New look: copy one object in `themes.js`, change `tile` colours, `names` and `icon()`. New text: edit `i18n/en.json`.

## Query flags (local testing)

`?level=N` · `?endless=1` · `?autoplay=N&speed=K` (solver plays N levels) · `?selftest=1` (title becomes `selftest:<failures>`) · `?cover=1&w=W&h=H` · `?demo=1&w=W&h=H` · `?fresh=1` (ignore the save).

## Rules in one paragraph

Board `cols × rows`, row 0 at the top. A drop lands on top of its column. Every group of two or more equal
free tiles connected to the tile that just moved merges into it; the new tier is `tier + group size − 1`
(so three equal tiles jump two tiers). Tiles fall, and anything that moved can merge again. Stones never move
and break when a merge touches them. Ice holds a tile that cannot merge until a merge touches the ice.
A level ends when its goal is met, the drops run out, or no column has room.

## Ads and privacy

Interstitials only between levels (at most one per 60 s), rewarded videos only when the player taps
Hint, Hammer (when out), or the extra-drops button. Sound is muted while an ad runs. Progress is stored in
`localStorage` (and the portal's cloud save where the SDK offers it). No analytics, no personal data,
no requests to any server other than the portal SDK.
