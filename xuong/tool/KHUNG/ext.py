"""Khung tiện ích Chrome MV3 – chép cấu trúc 3 tiện ích MIT nhiều sao (HỌC 21/10: kazuki-sf/YouTube_Summary_with_ChatGPT 865★,
kazuki-sf/ChatGPT_Extension 457★, SimGus/chrome-extension-v3-starter 403★):

CHECKLIST CẤU TRÚC (≤ 15 dòng):
 1. manifest.json MV3, tên + mô tả rõ, phiên bản
 2. Một popup làm đúng 1 việc, mở là dùng
 3. Quyền tối thiểu, giải trình từng quyền trong README
 4. Icon 16/48/128
 5. Lưu lựa chọn bằng chrome.storage
 6. Không tải mã từ xa, không theo dõi
 7. README có ảnh + cách cài (Load unpacked / Web Store) + LICENSE MIT
 8. Trang chính sách riêng tư (Chrome Web Store đòi)
 9. Nhân bản: đổi tiện ích = đổi popup + quyền + 1 tính năng thêm
Popup chạy được cả ngoài Chrome (chế độ demo) để kiểm tự động 3 cỡ màn hình.

python KHUNG/ext.py <slug> <out-dir>
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ACCENT = "#00A884"
COMMON_JS = """const isExt=typeof chrome!=='undefined'&&chrome.tabs&&chrome.storage;
const store={get:(k,d)=>new Promise(r=>{if(isExt)chrome.storage.local.get(k,v=>r(v[k]??d));else{try{r(JSON.parse(localStorage.getItem(k))??d)}catch(e){r(d)}}}),
set:(k,v)=>isExt?chrome.storage.local.set({[k]:v}):localStorage.setItem(k,JSON.stringify(v))};
const $=s=>document.querySelector(s);const say=t=>{$('#msg').textContent=t;setTimeout(()=>$('#msg').textContent='',2200);};
async function activeTab(){if(!isExt)return{id:0,title:'Demo page – Snoutsmith Tools',url:'https://example.com/demo-article'};const[t]=await chrome.tabs.query({active:true,currentWindow:true});return t;}
async function inPage(fn){if(!isExt)return fn();const t=await activeTab();const[r]=await chrome.scripting.executeScript({target:{tabId:t.id},func:fn});return r.result;}
"""
TOOLS = {
    "tab-tidy": dict(
        name="Tab Tidy – Close Duplicate Tabs", short="Tab Tidy", glyph="⧉", perms=["tabs"],
        why={"tabs": "read the URL of open tabs to find duplicates and to sort them"},
        desc="Close duplicate tabs in one click and sort the rest by website.",
        extra="Sort tabs by website (added feature)",
        body="<div class='big' id='n'>–</div><div class='sub'>duplicate tabs in this window</div><button id='go'>Close duplicates</button><button class='alt' id='sort'>Sort by website</button>",
        js="""async function tabs(){if(!isExt)return[{id:1,url:'https://example.com/x'},{id:2,url:'https://example.com/x'},{id:3,url:'https://example.org/'},{id:4,url:'https://example.com/x#top'}];return chrome.tabs.query({currentWindow:true});}
const key=u=>u.split('#')[0];async function dups(){const seen=new Set(),d=[];for(const t of await tabs()){const k=key(t.url||'');if(seen.has(k))d.push(t.id);else seen.add(k);}return d;}
async function show(){$('#n').textContent=(await dups()).length;}
$('#go').onclick=async()=>{const d=await dups();if(isExt&&d.length)await chrome.tabs.remove(d);say(d.length+' tabs closed');store.set('closed',(await store.get('closed',0))+d.length);show();};
$('#sort').onclick=async()=>{const t=await tabs();const s=[...t].sort((a,b)=>new URL(a.url).hostname.localeCompare(new URL(b.url).hostname));if(isExt)for(let i=0;i<s.length;i++)await chrome.tabs.move(s[i].id,{index:i});say('Sorted '+s.length+' tabs');};
show();"""),
    "copy-link": dict(
        name="Copy Link As – Markdown, HTML, Plain", short="Copy Link As", glyph="⎘", perms=["activeTab"],
        why={"activeTab": "read the title and URL of the current tab, only when you click the icon"},
        desc="Copy the current page as a Markdown, HTML or plain-text link with one click.",
        extra="Remembers your favourite format (added feature)",
        body="<div class='sub' id='t'></div><div class='row'><button data-f='md'>Markdown</button><button data-f='html' class='alt'>HTML</button><button data-f='txt' class='alt'>Plain</button></div><pre id='out'></pre>",
        js="""const F={md:t=>`[${t.title}](${t.url})`,html:t=>`<a href="${t.url}">${t.title}</a>`,txt:t=>`${t.title} – ${t.url}`};
(async()=>{const t=await activeTab();$('#t').textContent=t.title;const fav=await store.get('fav','md');$('#out').textContent=F[fav](t);
document.querySelectorAll('[data-f]').forEach(b=>{b.className=b.dataset.f===fav?'':'alt';b.onclick=async()=>{const s=F[b.dataset.f](t);$('#out').textContent=s;try{await navigator.clipboard.writeText(s);say('Copied')}catch(e){say('Copy blocked – select the text below')}store.set('fav',b.dataset.f);document.querySelectorAll('[data-f]').forEach(x=>x.className=x===b?'':'alt');};});})();"""),
    "word-counter": dict(
        name="Word Counter – Selection & Page", short="Word Counter", glyph="Aa", perms=["activeTab", "scripting"],
        why={"activeTab": "act on the current tab only after you click", "scripting": "read the selected text (or the page text) to count it"},
        desc="Count words, characters and reading time of the selected text or the whole page.",
        extra="Reading and speaking time (added feature)",
        body="<div class='grid'><div><b id='w'>–</b>words</div><div><b id='c'>–</b>characters</div><div><b id='r'>–</b>min read</div><div><b id='s'>–</b>min speak</div></div><div class='sub' id='src'></div>",
        js="""(async()=>{const txt=await inPage(()=>{const s=String(getSelection());return s.trim()?{t:s,sel:true}:{t:document.body?document.body.innerText:'',sel:false};});
const t=isExt?txt:{t:'Demo text: select text on any page and open Word Counter to count it instantly. It also counts the whole page when nothing is selected.',sel:true};
const w=(t.t.match(/\\S+/g)||[]).length;$('#w').textContent=w.toLocaleString();$('#c').textContent=t.t.length.toLocaleString();$('#r').textContent=Math.max(1,Math.round(w/238));$('#s').textContent=Math.max(1,Math.round(w/150));
$('#src').textContent=t.sel?'Counting your selection':'Nothing selected – counting the whole page';})();"""),
    "page-check": dict(
        name="Page Check – Quick SEO Stats", short="Page Check", glyph="✓", perms=["activeTab", "scripting"],
        why={"activeTab": "act on the current tab only after you click", "scripting": "read headings, links, images and meta tags of the page"},
        desc="See title length, meta description, headings, links and images without alt text on any page.",
        extra="Flags images missing alt text (added feature)",
        body="<table id='tb'></table>",
        js="""(async()=>{const r=await inPage(()=>({title:document.title,desc:(document.querySelector('meta[name=description]')||{}).content||'',h1:document.querySelectorAll('h1').length,h2:document.querySelectorAll('h2').length,
links:document.querySelectorAll('a[href]').length,imgs:document.images.length,noalt:[...document.images].filter(i=>!i.alt).length}));
const d=isExt?r:{title:'Demo page – Snoutsmith Tools',desc:'A short demo description.',h1:1,h2:4,links:38,imgs:6,noalt:2};
const ok=(c,t)=>`<span style="color:${c?'#00A884':'#C0392B'}">${t}</span>`;
$('#tb').innerHTML=[['Title',d.title.length+' chars',d.title.length>=30&&d.title.length<=60],['Meta description',d.desc.length+' chars',d.desc.length>=70&&d.desc.length<=160],['H1',d.h1,d.h1===1],['H2',d.h2,true],['Links',d.links,true],['Images',d.imgs,true],['Images without alt',d.noalt,d.noalt===0]]
.map(r=>`<tr><td>${r[0]}</td><td>${ok(r[2],r[1])}</td></tr>`).join('');})();"""),
    "color-grab": dict(
        name="Color Grab – Eyedropper & Palette", short="Color Grab", glyph="◉", perms=["storage"],
        why={"storage": "keep your last 12 picked colours on this computer"},
        desc="Pick any colour on screen, copy HEX or RGB, and keep a palette of your last 12 colours.",
        extra="Palette history with one-click copy (added feature)",
        body="<button id='pick'>Pick a colour</button><div class='row' id='pal'></div><div class='sub'>Click a swatch to copy its HEX</div>",
        js="""const rgb=h=>`rgb(${parseInt(h.slice(1,3),16)}, ${parseInt(h.slice(3,5),16)}, ${parseInt(h.slice(5,7),16)})`;
async function draw(){const p=await store.get('pal',isExt?[]:['#00A884','#E8833A','#2D7FF9','#7A4DE8','#B23A48']);$('#pal').innerHTML=p.map(c=>`<button class="sw" title="${c} · ${rgb(c)}" style="background:${c}" data-c="${c}"></button>`).join('');
document.querySelectorAll('.sw').forEach(b=>b.onclick=async()=>{try{await navigator.clipboard.writeText(b.dataset.c)}catch(e){}say(b.dataset.c+' copied');});}
$('#pick').onclick=async()=>{if(!window.EyeDropper){say('Eyedropper needs Chrome 95+');return;}try{const r=await new EyeDropper().open();const p=[r.sRGBHex,...(await store.get('pal',[])).filter(c=>c!==r.sRGBHex)].slice(0,12);await store.set('pal',p);try{await navigator.clipboard.writeText(r.sRGBHex)}catch(e){}say(r.sRGBHex+' copied');draw();}catch(e){}};draw();"""),
}
POPUP = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{short}</title><style>
*{{box-sizing:border-box}}body{{margin:0;min-width:300px;max-width:100%;font:14px/1.4 system-ui,Segoe UI,Arial;color:#10241E;background:#F3FBF8}}
header{{background:{accent};color:#fff;padding:12px 14px;font-weight:700}}main{{padding:14px}}button{{border:0;border-radius:999px;padding:10px 14px;font-weight:700;background:{accent};color:#fff;margin:4px 4px 4px 0;cursor:pointer}}
button.alt{{background:#DDEFE8;color:#10241E}}.big{{font:700 40px system-ui;color:{accent}}}.sub{{color:#5B6E67;margin:6px 0 10px;overflow-wrap:anywhere}}.row{{display:flex;flex-wrap:wrap;gap:6px}}
pre{{white-space:pre-wrap;word-break:break-all;background:#fff;border-radius:10px;padding:10px;font-size:12px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}.grid div{{background:#fff;border-radius:12px;padding:10px;color:#5B6E67}}
.grid b{{display:block;font-size:22px;color:{accent}}}table{{width:100%;border-collapse:collapse}}td{{padding:6px 4px;border-bottom:1px solid #DDEFE8}}.sw{{width:34px;height:34px;padding:0;border-radius:10px}}#msg{{min-height:18px;color:{accent};font-weight:700}}
</style></head><body><header>{short}</header><main>{body}<div id="msg"></div></main><script src="common.js"></script><script src="popup.js"></script></body></html>"""


def icon(path, size, glyph):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 4, fill=ACCENT)
    for name in ("seguisym.ttf", "DejaVuSans.ttf", "arial.ttf"):
        try:
            f = ImageFont.truetype(name, int(size * 0.55))
            break
        except Exception:
            f = ImageFont.load_default()
    d.text((size / 2, size / 2), glyph, font=f, fill="#FFFFFF", anchor="mm")
    im.save(path)


def build(slug, out):
    t = TOOLS[slug]
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps({"manifest_version": 3, "name": t["name"], "short_name": t["short"], "version": "1.0.0", "description": t["desc"],
                                                   "action": {"default_popup": "popup.html", "default_title": t["short"]}, "permissions": t["perms"],
                                                   "icons": {"16": "icon-16.png", "48": "icon-48.png", "128": "icon-128.png"}}, indent=1), encoding="utf-8")
    (out / "popup.html").write_text(POPUP.format(short=t["short"], accent=ACCENT, body=t["body"]), encoding="utf-8")
    (out / "common.js").write_text(COMMON_JS, encoding="utf-8")
    (out / "popup.js").write_text(f"// {t['name']} – Snoutsmith Tools (MIT)\n" + t["js"] + "\n", encoding="utf-8")
    for s in (16, 48, 128):
        icon(out / f"icon-{s}.png", s, t["glyph"])
    (out / "PRIVACY.md").write_text(f"# Privacy – {t['short']}\n\n{t['short']} runs only in your browser. It collects no personal data, has no analytics, sends nothing to any server and loads no remote code.\n"
                                    + ("It stores only your settings/palette with chrome.storage on this computer.\n" if "storage" in t["perms"] or "fav" in t["js"] else "") + "\nContact: tools.snoutsmith.com\n", encoding="utf-8")
    (out / "README.md").write_text(f"# {t['name']}\n\n![screenshot](screenshot.png)\n\n{t['desc']}\n\nAdded feature: {t['extra']}.\n\n## Install\n\n1. Download and unzip.\n"
                                   "2. Open `chrome://extensions`, switch on Developer mode, click **Load unpacked** and pick the folder.\n3. Pin the icon and click it.\n\n"
                                   "## Permissions (and why)\n\n" + "\n".join(f"- `{p}` – {w}" for p, w in t["why"].items()) + "\n\nNo remote code, no tracking. See PRIVACY.md.\n\n## License\n\nMIT – see LICENSE.\n", encoding="utf-8")
    (out / "LICENSE").write_text("MIT License\n\nCopyright (c) 2026 Snoutsmith Tools\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.\n", encoding="utf-8")
    return {"name": t["name"], "perms": t["perms"]}


if __name__ == "__main__":
    print(build(sys.argv[1], Path(sys.argv[2])))
