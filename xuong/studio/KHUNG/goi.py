"""Khung gói asset Studio – chép cấu trúc gói CC0 tải nhiều nhất (Kenney, HỌC 21/10):

CHECKLIST CẤU TRÚC (≤ 15 dòng):
 1. Thư mục PNG/ tên tệp thống nhất (<chude>_<goc>_<so>.png)
 2. Spritesheet PNG + atlas JSON (dạng TexturePacker "hash", đọc được bằng Phaser/PixiJS)
 3. Trang xem trước preview.html: lưới mọi hình, ô tìm theo tên, nền ca-rô
 4. Demo chạy được (demo.html): hình rơi/nảy, bấm để thêm
 5. LICENSE (CC0) + CREDITS (nguồn từng gói)
 6. README có ảnh, cách dùng trong Phaser/PixiJS
 7. Ảnh xem trước + GIF
 8. Nhân bản: đổi chủ đề = đổi danh sách 3 gói nguồn

python KHUNG/goi.py <chu-de> <out-dir>
"""
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image

UA = "Mozilla/5.0 (net24 xuong-studio; CC0 asset bundler)"
THEMES = {
    "platformer": ("Platformer Starter Bundle", ["new-platformer-pack", "pixel-platformer", "abstract-platformer"]),
    "puzzle": ("Puzzle Pieces Bundle", ["puzzle-pack-2", "physics-assets", "shape-characters"]),
    "ui": ("Game UI Kit Bundle", ["ui-pack", "ui-pack-rpg-expansion", "input-prompts"]),
    "space": ("Space Game Bundle", ["simple-space", "planets", "space-shooter-extension"]),
    "tiles": ("Top-Down Tiles Bundle", ["tiny-town", "tiny-dungeon", "micro-roguelike"]),
    "icons": ("Game Icons Bundle", ["game-icons", "board-game-icons", "emotes-pack"]),
}
MAX_PER_PACK = 90
MAX_SIDE = 256


def fetch(url):
    return subprocess.run(["curl", "-sfL", "-A", UA, url], capture_output=True, check=True).stdout


def pack_zip(slug):
    page = fetch(f"https://kenney.nl/assets/{slug}").decode("utf-8", "replace")
    m = re.search(r"https://kenney\.nl/media/pages/assets/[^\"']+\.zip", page)
    if not m:
        raise RuntimeError("no zip for " + slug)
    return m.group(0), zipfile.ZipFile(io.BytesIO(fetch(m.group(0))))


def license_ok(z):
    for n in z.namelist():
        if re.search(r"licen[cs]e", n, re.I) and n.lower().endswith(".txt"):
            t = z.read(n).decode("utf-8", "replace")
            return "CC0" in t or "Creative Commons Zero" in t or "public domain" in t.lower(), t[:400]
    return False, ""


def pick_pngs(z):
    names = [n for n in z.namelist() if n.lower().endswith(".png") and "__MACOSX" not in n]
    # Kenney: prefer the default-size PNG set, skip spritesheets, previews and @2x/double copies.
    skip = re.compile(r"(sheet|spritesheet|preview|sample|thumbnail|double|@2x|vector|tilemap_packed|tilemap\.png)", re.I)
    cand = [n for n in sorted(names) if not skip.search(n)]
    # spread the pick over the whole pack (sorted names cluster by type: enemies, tiles, items…)
    step = max(1, len(cand) / (MAX_PER_PACK * 1.6))
    picked, out, i = set(), [], 0.0
    while i < len(cand) and len(out) < MAX_PER_PACK:
        n = cand[int(i)]
        i += step
        if n in picked:
            continue
        picked.add(n)
        try:
            im = Image.open(io.BytesIO(z.read(n)))
        except Exception:
            continue
        if max(im.size) > MAX_SIDE or min(im.size) < 8:
            continue
        out.append((n, im.convert("RGBA")))
    return out


def shelf_pack(items, width=2048, pad=2):
    """Simple shelf packer → (sheet image, frames dict)."""
    items = sorted(items, key=lambda t: -t[1].height)
    x = y = row_h = 0
    pos = []
    for name, im in items:
        if x + im.width + pad > width:
            x, y, row_h = 0, y + row_h + pad, 0
        pos.append((name, im, x, y))
        x += im.width + pad
        row_h = max(row_h, im.height)
    h = y + row_h
    sheet = Image.new("RGBA", (width, max(1, h)), (0, 0, 0, 0))
    frames = {}
    for name, im, px, py in pos:
        sheet.paste(im, (px, py))
        frames[name] = {"frame": {"x": px, "y": py, "w": im.width, "h": im.height}, "rotated": False, "trimmed": False,
                        "spriteSourceSize": {"x": 0, "y": 0, "w": im.width, "h": im.height}, "sourceSize": {"w": im.width, "h": im.height}}
    return sheet, frames


PREVIEW = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} – preview</title>
<style>body{{margin:0;font-family:system-ui,Segoe UI,Arial;background:#F4F6FB;color:#14213D}}header{{padding:28px 32px;background:#2D7FF9;color:#fff;overflow-wrap:anywhere}}h1{{margin:0;font-weight:500}}
*{{box-sizing:border-box}}input{{margin:16px 32px;padding:10px 14px;border-radius:999px;border:1px solid #cfd8ea;width:calc(100% - 64px);max-width:320px}}#g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:10px;padding:0 32px 32px}}
.c{{background:#fff repeating-conic-gradient(#eef1f7 0 25%,#fff 0 50%) 0 0/16px 16px;border-radius:12px;padding:10px;text-align:center;font-size:10px;color:#56627a;word-break:break-all}}
.c img{{display:block;margin:0 auto 6px;max-width:72px;max-height:72px;image-rendering:pixelated}}</style></head><body>
<header><h1>{title}</h1><div>{count} sprites · CC0 · spritesheet + JSON atlas · <a style="color:#fff" href="demo.html">play the demo</a></div></header>
<input id="q" placeholder="Search sprites…"><div id="g"></div>
<script>const N={names};const g=document.getElementById('g');function draw(f){{g.innerHTML='';N.filter(n=>n.includes(f)).forEach(n=>{{const d=document.createElement('div');d.className='c';d.innerHTML='<img loading="lazy" src="PNG/'+n+'"><span>'+n+'</span>';g.appendChild(d);}});}}
draw('');document.getElementById('q').oninput=e=>draw(e.target.value.toLowerCase());</script></body></html>"""

DEMO = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} – demo</title>
<style>html,body{{margin:0;height:100%;background:#14213D;overflow:hidden}}canvas{{display:block}}#t{{position:fixed;left:16px;top:12px;color:#fff;font:600 14px system-ui,Arial}}</style></head><body>
<div id="t">{title} – click or tap to drop sprites</div><canvas id="c"></canvas><script>
const atlas={atlas};const img=new Image();img.src='spritesheet.png';const keys=Object.keys(atlas.frames);
const c=document.getElementById('c'),g=c.getContext('2d');let W,H,list=[];function fit(){{W=c.width=innerWidth;H=c.height=innerHeight;}}fit();onresize=fit;
let seed=7;function rnd(){{seed=(seed*16807)%2147483647;return seed/2147483647;}}
function add(x,y){{const k=keys[Math.floor(rnd()*keys.length)];const f=atlas.frames[k].frame;const s=Math.min(2,64/Math.max(f.w,f.h)*1.4);list.push({{f,x,y,vx:(rnd()-.5)*6,vy:-rnd()*4,s,a:0,va:(rnd()-.5)*.1}});if(list.length>140)list.shift();}}
c.onpointerdown=e=>{{for(let i=0;i<6;i++)add(e.clientX,e.clientY);}};
let t=0;function loop(){{t++;if(t%9===0)add(W*(.15+rnd()*.7),-40);g.fillStyle='#14213D';g.fillRect(0,0,W,H);
for(const p of list){{p.vy+=.25;p.x+=p.vx;p.y+=p.vy;p.a+=p.va;const h=p.f.h*p.s/2;if(p.y>H-h){{p.y=H-h;p.vy*=-.62;p.vx*=.9;}}if(p.x<0||p.x>W)p.vx*=-1;
g.save();g.translate(p.x,p.y);g.rotate(p.a);g.imageSmoothingEnabled=false;g.drawImage(img,p.f.x,p.f.y,p.f.w,p.f.h,-p.f.w*p.s/2,-p.f.h*p.s/2,p.f.w*p.s,p.f.h*p.s);g.restore();}}
requestAnimationFrame(loop);}}img.onload=loop;</script></body></html>"""


def build(theme, out):
    title, packs = THEMES[theme]
    out.mkdir(parents=True, exist_ok=True)
    stage = out / "_goi"
    (stage / "PNG").mkdir(parents=True, exist_ok=True)
    items, credits = [], []
    for slug in packs:
        url, z = pack_zip(slug)
        ok, lic = license_ok(z)
        if not ok:
            print("skip (license not CC0):", slug)
            continue
        got = pick_pngs(z)
        for i, (n, im) in enumerate(got, 1):
            base = re.sub(r"[^a-z0-9]+", "-", Path(n).stem.lower()).strip("-")
            name = f"{theme}_{slug.replace('-', '')[:12]}_{i:03d}_{base[:24]}.png"
            im.save(stage / "PNG" / name)
            items.append((name, im))
        credits.append({"pack": slug, "page": f"https://kenney.nl/assets/{slug}", "zip": url, "sprites": len(got), "license": "CC0 1.0 (license.txt in the original zip)"})
    sheet, frames = shelf_pack(items)
    sheet.save(stage / "spritesheet.png", optimize=True)
    atlas = {"frames": frames, "meta": {"app": "net24 xuong-studio", "image": "spritesheet.png", "format": "RGBA8888", "size": {"w": sheet.width, "h": sheet.height}, "scale": "1"}}
    (stage / "spritesheet.json").write_text(json.dumps(atlas, indent=1), encoding="utf-8")
    names = sorted(n for n, _ in items)
    (stage / "preview.html").write_text(PREVIEW.format(title=title, count=len(items), names=json.dumps(names)), encoding="utf-8")
    (stage / "demo.html").write_text(DEMO.format(title=title, atlas=json.dumps(atlas)), encoding="utf-8")
    (stage / "LICENSE.txt").write_text("CC0 1.0 Universal (public domain dedication).\nAll sprites come from Kenney (kenney.nl) packs released under CC0; see CREDITS.md.\n"
                                       "Bundle layout, naming, atlas, preview and demo pages: also released under CC0 by Snoutsmith Studio.\n"
                                       "You may use, modify and sell games made with these assets, with or without credit.\n", encoding="utf-8")
    (stage / "CREDITS.md").write_text("# Credits\n\n" + "\n".join(f"- Kenney – {c['pack']} ({c['page']}), {c['sprites']} sprites, {c['license']}" for c in credits)
                                      + "\n\nCredit is not required by CC0, but Kenney deserves it: https://kenney.nl\n", encoding="utf-8")
    (stage / "README.md").write_text(f"# {title}\n\n![preview](preview-1600x1200.png)\n\n{len(items)} CC0 sprites from {len(credits)} Kenney packs, renamed into one scheme "
                                     f"(`{theme}_<pack>_<nnn>_<name>.png`), packed into one `spritesheet.png` with a TexturePacker-style `spritesheet.json` atlas.\n\n"
                                     "## Use\n\n- Phaser 3: `this.load.atlas('sprites', 'spritesheet.png', 'spritesheet.json'); this.add.image(x, y, 'sprites', '<file name>.png');`\n"
                                     "- PixiJS: `const sheet = await PIXI.Assets.load('spritesheet.json'); new PIXI.Sprite(sheet.textures['<file name>.png']);`\n"
                                     "- Plain files: everything is also in `PNG/`.\n\n## Files\n\n`PNG/` · `spritesheet.png` · `spritesheet.json` · `preview.html` (browse + search) · `demo.html` (playable) · `LICENSE.txt` · `CREDITS.md`\n", encoding="utf-8")
    return {"title": title, "sprites": len(items), "packs": credits, "sheet": list(sheet.size)}


if __name__ == "__main__":
    print(build(sys.argv[1], Path(sys.argv[2])))
