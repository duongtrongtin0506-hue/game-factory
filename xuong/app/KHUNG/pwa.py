"""Khung PWA – chép cấu trúc 3 PWA MIT nhiều sao (HỌC 21/10: cocopon/llumino-pwa 94★, ovk/clcalc 46★, chrisdiana/pwa-calculator 33★):

CHECKLIST CẤU TRÚC (≤ 15 dòng):
 1. Một trang, một màn nhập, kết quả hiện ngay khi gõ
 2. manifest.webmanifest: tên, icon 192/512 (maskable), màu, display standalone
 3. service worker lưu mọi tệp → chạy offline
 4. Cài được như app (nút Install khi trình duyệt cho phép)
 5. Mobile trước, nút/ô lớn, chạy 360 px
 6. Nhớ lần nhập trước (localStorage)
 7. Không đăng nhập, không theo dõi, trang chính sách riêng tư
 8. Không framework, nhẹ (< 50 KB)
 9. Sáng/tối theo máy
10. Nhân bản: đổi app = đổi ô nhập + hàm tính + bảng kết quả
Thêm cho Google Play: twa-manifest.json sẵn cho Bubblewrap.

python KHUNG/pwa.py <slug> <out-dir>
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ACCENT = "#7A4DE8"

APPS = {
    "compound-interest": dict(
        name="Compound Interest Calculator", short="Compound", glyph="%",
        desc="See how savings grow with compound interest and monthly deposits – offline, no ads, no sign-up.",
        inputs=[("Starting amount", "p", 10000, "$"), ("Monthly deposit", "m", 300, "$"), ("Yearly interest rate", "r", 6, "%"), ("Years", "y", 15, "yrs")],
        js="""const n=12,i=v.r/100/n,k=v.y*n;let b=v.p,dep=v.p,rows=[];for(let t=1;t<=k;t++){b=b*(1+i)+v.m;dep+=v.m;if(t%12===0)rows.push([t/12,dep,b]);}
out([["Final balance",money(b)],["Total deposited",money(dep)],["Interest earned",money(b-dep)]],["Year","Deposited","Balance"],rows.map(r=>[r[0],money(r[1]),money(r[2])]));"""),
    "loan-payment": dict(
        name="Loan Payment Calculator", short="Loan", glyph="$",
        desc="Monthly payment, total interest and a full amortization table for any loan – works offline.",
        inputs=[("Loan amount", "a", 25000, "$"), ("Yearly interest rate", "r", 7.5, "%"), ("Term", "y", 5, "yrs")],
        js="""const i=v.r/100/12,n=Math.round(v.y*12);const pay=i?v.a*i/(1-Math.pow(1+i,-n)):v.a/n;let b=v.a,rows=[],tot=0;
for(let t=1;t<=n;t++){const int=b*i;b=b-(pay-int);tot+=int;if(t%12===0||t===n)rows.push([t,money(pay*t),money(Math.max(0,b))]);}
out([["Monthly payment",money(pay)],["Total interest",money(tot)],["Total paid",money(pay*n)]],["Month","Paid so far","Balance left"],rows);"""),
    "tip-split": dict(
        name="Tip & Bill Splitter", short="Tip Split", glyph="÷",
        desc="Split a bill with tip between friends in seconds, rounded the way you like – offline, no ads.",
        inputs=[("Bill total", "b", 86.4, "$"), ("Tip", "t", 18, "%"), ("People", "n", 4, "ppl")],
        js="""const tip=v.b*v.t/100,tot=v.b+tip,n=Math.max(1,Math.round(v.n)),each=tot/n,up=Math.ceil(each);
out([["Each pays",money(each)],["Tip",money(tip)],["Total",money(tot)]],["Option","Each","Total collected"],[["Exact",money(each),money(each*n)],["Round up to $1",money(up),money(up*n)],["Tip 15%",money(v.b*1.15/n),money(v.b*1.15)],["Tip 20%",money(v.b*1.2/n),money(v.b*1.2)]]);"""),
    "unit-converter": dict(
        name="Everyday Unit Converter", short="Units", glyph="⇄",
        desc="Convert length, weight, temperature, volume and speed instantly – one screen, offline.",
        inputs=[("Value", "x", 10, "")],
        js="""const x=v.x,f=(a,b)=>[a,b];out([["Kilometres → miles",(x*0.621371).toFixed(3)],["Kilograms → pounds",(x*2.20462).toFixed(3)],["°C → °F",(x*9/5+32).toFixed(1)]],["From","To","Result"],
[["cm","inches",(x/2.54).toFixed(3)],["m","feet",(x*3.28084).toFixed(3)],["km","miles",(x*0.621371).toFixed(3)],["kg","lb",(x*2.20462).toFixed(3)],["g","oz",(x/28.3495).toFixed(3)],
["°C","°F",(x*9/5+32).toFixed(1)],["°F","°C",((x-32)*5/9).toFixed(1)],["litres","US gallons",(x*0.264172).toFixed(3)],["ml","US fl oz",(x/29.5735).toFixed(3)],["km/h","mph",(x*0.621371).toFixed(3)]]);"""),
    "pomodoro-timer": dict(
        name="Pomodoro Focus Timer", short="Focus", glyph="◔",
        desc="A clean 25/5 focus timer with long breaks and a session count – installs like an app, works offline.",
        inputs=[("Focus minutes", "f", 25, "min"), ("Short break", "s", 5, "min"), ("Long break", "l", 15, "min"), ("Rounds before long break", "k", 4, "")],
        js="""const plan=[];for(let r=1;r<=v.k;r++){plan.push(["Focus "+r,v.f+" min"]);plan.push([r==v.k?"Long break":"Break",(r==v.k?v.l:v.s)+" min"]);}
const total=v.k*v.f+(v.k-1)*v.s+v.l;out([["Cycle length",total+" min"],["Focus time",v.k*v.f+" min"],["Sessions done today",String(+(localStorage.getItem('done-'+new Date().toDateString())||0))]],["Step","Length",""],plan.map(p=>[p[0],p[1],""]));
timerUI(v);"""),
}

INDEX = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name}</title><meta name="description" content="{desc}"><meta name="theme-color" content="{accent}">
<link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png"><link rel="stylesheet" href="style.css"></head>
<body><main><header><div class="lab">Snoutsmith Apps</div><h1>{name}</h1><button id="install" hidden>Install</button></header>
<section class="card" id="form">{fields}</section><section class="card" id="res"></section><section class="card" id="extra"></section>
<p class="foot">Runs on your device, works offline, nothing is sent anywhere. <a href="privacy.html">Privacy</a></p></main><script src="app.js"></script></body></html>"""
CSS = """:root{--bg:#F7F5FF;--card:#fff;--ink:#1A1A2E;--soft:#6B6880;--line:#E6E1F5;--accent:ACCENTX}
@media (prefers-color-scheme:dark){:root{--bg:#121019;--card:#1D1A28;--ink:#F1EEFA;--soft:#A39FB8;--line:#2C2840}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,Arial}
main{max-width:560px;margin:0 auto;padding:20px 16px 40px}h1{font:500 30px/1.1 Georgia,serif;margin:6px 0 0}.lab{font:600 11px ui-monospace,Consolas,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
header{display:flex;flex-wrap:wrap;align-items:end;justify-content:space-between;gap:12px;margin-bottom:16px}#install{background:var(--accent);color:#fff;border:0;border-radius:999px;padding:10px 18px;font-weight:600}
.card{background:var(--card);border-radius:16px;padding:16px;margin-bottom:14px;box-shadow:0 2px 20px rgba(60,40,120,.07)}label{display:block;font-size:13px;color:var(--soft);margin:8px 0 4px}
.row{display:flex;gap:8px;align-items:center}input{width:100%;font-size:20px;padding:12px;border:1px solid var(--line);border-radius:12px;background:transparent;color:var(--ink)}.u{min-width:34px;color:var(--soft)}
.big{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}.big div{background:var(--bg);border-radius:12px;padding:12px}.big b{display:block;font-size:22px;color:var(--accent)}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:7px 4px;border-bottom:1px solid var(--line)}th{color:var(--soft);font-weight:600}
.foot{font-size:12px;color:var(--soft);text-align:center}.foot a{color:var(--accent)}#clock{font:600 56px ui-monospace,Consolas,monospace;text-align:center;margin:8px 0}.btns{display:flex;gap:8px;justify-content:center}
.btns button{border:0;border-radius:999px;padding:12px 22px;font-weight:700;background:var(--accent);color:#fff}.btns button.alt{background:var(--line);color:var(--ink)}""".replace("ACCENTX", ACCENT)
APPJS = """// {name} – Snoutsmith Apps (MIT). One screen: inputs -> result, remembers the last values, works offline.
const KEY='{slug}.v1', F={fields};
const money=x=>'$'+(Math.round(x*100)/100).toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}});
const saved=(()=>{{try{{return JSON.parse(localStorage.getItem(KEY))||{{}}}}catch(e){{return{{}}}}}})();
document.getElementById('form').innerHTML=F.map(f=>`<label for="${{f[1]}}">${{f[0]}}</label><div class="row"><input id="${{f[1]}}" type="number" inputmode="decimal" step="any" value="${{saved[f[1]]??f[2]}}"><span class="u">${{f[3]}}</span></div>`).join('');
function out(big,head,rows){{document.getElementById('res').innerHTML='<div class="big">'+big.map(b=>`<div>${{b[0]}}<b>${{b[1]}}</b></div>`).join('')+'</div>';
const nums=rows.map(r=>parseFloat(String(r[r.length-1]).replace(/[^0-9.-]/g,''))),ok=rows.length>1&&nums.every(x=>isFinite(x)&&x>=0);let svg='';
if(ok){{const mx=Math.max(...nums,1),w=100/rows.length;svg='<svg viewBox="0 0 100 42" style="width:100%;height:150px" role="img" aria-label="'+head[head.length-1]+' chart">'+nums.map((x,i)=>`<rect x="${{i*w+w*.15}}" y="${{40-38*x/mx}}" width="${{w*.7}}" height="${{38*x/mx}}" rx="1" fill="var(--accent)" opacity="${{.45+.55*(i+1)/nums.length}}"/>`).join('')+'</svg>';}}
document.getElementById('extra').innerHTML=svg+'<table><tr>'+head.map(h=>`<th>${{h}}</th>`).join('')+'</tr>'+rows.map(r=>'<tr>'+r.map(c=>`<td>${{c}}</td>`).join('')+'</tr>').join('')+'</table>';}}
let tm=null;function timerUI(v){{if(document.getElementById('clock'))return;const box=document.createElement('section');box.className='card';box.innerHTML='<div id="clock"></div><div class="btns"><button id="go">Start</button><button class="alt" id="rs">Reset</button></div>';
document.getElementById('res').before(box);let left=v.f*60,run=false;const show=()=>document.getElementById('clock').textContent=String(Math.floor(left/60)).padStart(2,'0')+':'+String(left%60).padStart(2,'0');show();
document.getElementById('go').onclick=()=>{{run=!run;document.getElementById('go').textContent=run?'Pause':'Start';if(run)tm=setInterval(()=>{{left--;show();if(left<=0){{clearInterval(tm);run=false;const k='done-'+new Date().toDateString();localStorage.setItem(k,+(localStorage.getItem(k)||0)+1);try{{navigator.vibrate&&navigator.vibrate(300)}}catch(e){{}}left=v.f*60;show();calc();}}}},1000);else clearInterval(tm);}};
document.getElementById('rs').onclick=()=>{{clearInterval(tm);run=false;left=+document.getElementById('f').value*60;document.getElementById('go').textContent='Start';show();}};}}
function calc(){{const v={{}};F.forEach(f=>v[f[1]]=parseFloat(document.getElementById(f[1]).value)||0);try{{localStorage.setItem(KEY,JSON.stringify(v))}}catch(e){{}}
{js}
}}
document.getElementById('form').addEventListener('input',calc);calc();
if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js');
let ev;addEventListener('beforeinstallprompt',e=>{{e.preventDefault();ev=e;const b=document.getElementById('install');b.hidden=false;b.onclick=()=>ev.prompt();}});
"""
SW = """const C='{slug}-v1',FILES=['./','index.html','app.js','style.css','manifest.webmanifest','icon-192.png','icon-512.png','privacy.html'];
self.addEventListener('install',e=>e.waitUntil(caches.open(C).then(c=>c.addAll(FILES))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))));
self.addEventListener('fetch',e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));
"""
PRIVACY = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Privacy – {name}</title><link rel="stylesheet" href="style.css"></head>
<body><main><h1>Privacy</h1><div class="card"><p>{name} runs entirely on your device. It has no accounts, no analytics, no ads and no trackers, and it sends nothing to any server.</p>
<p>The only thing it stores is your last inputs{extra}, kept in your browser's local storage so the app opens where you left it. Clear your browser data to remove them.</p>
<p>Contact: apps.snoutsmith.com</p></div><p class="foot"><a href="index.html">Back to the app</a></p></main></body></html>"""


def icon(path, size, glyph):
    im = Image.new("RGB", (size, size), ACCENT)
    d = ImageDraw.Draw(im)
    d.ellipse([size * 0.16, size * 0.16, size * 0.84, size * 0.84], fill="#FFFFFF")
    try:
        f = ImageFont.truetype("seguisym.ttf", int(size * 0.38))
    except Exception:
        try:
            f = ImageFont.truetype("DejaVuSans.ttf", int(size * 0.38))
        except Exception:
            f = ImageFont.load_default()
    d.text((size / 2, size / 2), glyph, font=f, fill=ACCENT, anchor="mm")
    im.save(path)


def build(slug, out):
    a = APPS[slug]
    out.mkdir(parents=True, exist_ok=True)
    fields = json.dumps([[l, k, d, u] for l, k, d, u in a["inputs"]])
    (out / "index.html").write_text(INDEX.format(name=a["name"], desc=a["desc"], accent=ACCENT, fields=""), encoding="utf-8")
    (out / "style.css").write_text(CSS, encoding="utf-8")
    (out / "app.js").write_text(APPJS.format(name=a["name"], slug=slug, fields=fields, js=a["js"]), encoding="utf-8")
    (out / "sw.js").write_text(SW.format(slug=slug), encoding="utf-8")
    (out / "privacy.html").write_text(PRIVACY.format(name=a["name"], extra=" and today's finished sessions" if "pomodoro" in slug else ""), encoding="utf-8")
    icon(out / "icon-192.png", 192, a["glyph"])
    icon(out / "icon-512.png", 512, a["glyph"])
    (out / "manifest.webmanifest").write_text(json.dumps({"name": a["name"], "short_name": a["short"], "description": a["desc"], "start_url": "./index.html", "scope": "./",
                                                          "display": "standalone", "background_color": "#F7F5FF", "theme_color": ACCENT,
                                                          "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                                                                    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, indent=1), encoding="utf-8")
    (out / "twa-manifest.json").write_text(json.dumps({"packageId": "com.snoutsmith.apps." + slug.replace("-", ""), "host": "apps.snoutsmith.com", "name": a["name"],
                                                       "launcherName": a["short"], "display": "standalone", "themeColor": ACCENT, "navigationColor": ACCENT,
                                                       "backgroundColor": "#F7F5FF", "startUrl": f"/{slug}/", "iconUrl": f"https://apps.snoutsmith.com/{slug}/icon-512.png",
                                                       "maskableIconUrl": f"https://apps.snoutsmith.com/{slug}/icon-512.png", "webManifestUrl": f"https://apps.snoutsmith.com/{slug}/manifest.webmanifest",
                                                       "appVersionCode": 1, "appVersion": "1.0.0", "signingKey": {"path": "./android.keystore", "alias": "android"},
                                                       "enableNotifications": False, "fallbackType": "customtabs"}, indent=1), encoding="utf-8")
    (out / "LICENSE").write_text("MIT License\n\nCopyright (c) 2026 Snoutsmith Apps\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.\n", encoding="utf-8")
    size = sum(p.stat().st_size for p in out.iterdir() if p.suffix in (".html", ".js", ".css", ".webmanifest"))
    return {"name": a["name"], "kb_code": round(size / 1024, 1)}


if __name__ == "__main__":
    print(build(sys.argv[1], Path(sys.argv[2])))
