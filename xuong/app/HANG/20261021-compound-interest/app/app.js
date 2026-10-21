// Compound Interest Calculator – Snoutsmith Apps (MIT). One screen: inputs -> result, remembers the last values, works offline.
const KEY='compound-interest.v1', F=[["Starting amount", "p", 10000, "$"], ["Monthly deposit", "m", 300, "$"], ["Yearly interest rate", "r", 6, "%"], ["Years", "y", 15, "yrs"]];
const money=x=>'$'+(Math.round(x*100)/100).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const saved=(()=>{try{return JSON.parse(localStorage.getItem(KEY))||{}}catch(e){return{}}})();
document.getElementById('form').innerHTML=F.map(f=>`<label for="${f[1]}">${f[0]}</label><div class="row"><input id="${f[1]}" type="number" inputmode="decimal" step="any" value="${saved[f[1]]??f[2]}"><span class="u">${f[3]}</span></div>`).join('');
function out(big,head,rows){document.getElementById('res').innerHTML='<div class="big">'+big.map(b=>`<div>${b[0]}<b>${b[1]}</b></div>`).join('')+'</div>';
document.getElementById('extra').innerHTML='<table><tr>'+head.map(h=>`<th>${h}</th>`).join('')+'</tr>'+rows.map(r=>'<tr>'+r.map(c=>`<td>${c}</td>`).join('')+'</tr>').join('')+'</table>';}
let tm=null;function timerUI(v){if(document.getElementById('clock'))return;const box=document.createElement('section');box.className='card';box.innerHTML='<div id="clock"></div><div class="btns"><button id="go">Start</button><button class="alt" id="rs">Reset</button></div>';
document.getElementById('res').before(box);let left=v.f*60,run=false;const show=()=>document.getElementById('clock').textContent=String(Math.floor(left/60)).padStart(2,'0')+':'+String(left%60).padStart(2,'0');show();
document.getElementById('go').onclick=()=>{run=!run;document.getElementById('go').textContent=run?'Pause':'Start';if(run)tm=setInterval(()=>{left--;show();if(left<=0){clearInterval(tm);run=false;const k='done-'+new Date().toDateString();localStorage.setItem(k,+(localStorage.getItem(k)||0)+1);try{navigator.vibrate&&navigator.vibrate(300)}catch(e){}left=v.f*60;show();calc();}},1000);else clearInterval(tm);};
document.getElementById('rs').onclick=()=>{clearInterval(tm);run=false;left=+document.getElementById('f').value*60;document.getElementById('go').textContent='Start';show();};}
function calc(){const v={};F.forEach(f=>v[f[1]]=parseFloat(document.getElementById(f[1]).value)||0);try{localStorage.setItem(KEY,JSON.stringify(v))}catch(e){}
const n=12,i=v.r/100/n,k=v.y*n;let b=v.p,dep=v.p,rows=[];for(let t=1;t<=k;t++){b=b*(1+i)+v.m;dep+=v.m;if(t%12===0)rows.push([t/12,dep,b]);}
out([["Final balance",money(b)],["Total deposited",money(dep)],["Interest earned",money(b-dep)]],["Year","Deposited","Balance"],rows.map(r=>[r[0],money(r[1]),money(r[2])]));
}
document.getElementById('form').addEventListener('input',calc);calc();
if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js');
let ev;addEventListener('beforeinstallprompt',e=>{e.preventDefault();ev=e;const b=document.getElementById('install');b.hidden=false;b.onclick=()=>ev.prompt();});
