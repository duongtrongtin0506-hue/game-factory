// Loan Payment Calculator – Snoutsmith Apps (MIT). One screen: inputs -> result, remembers the last values, works offline.
const KEY='loan-payment.v1', F=[["Loan amount", "a", 25000, "$"], ["Yearly interest rate", "r", 7.5, "%"], ["Term", "y", 5, "yrs"]];
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
const i=v.r/100/12,n=Math.round(v.y*12);const pay=i?v.a*i/(1-Math.pow(1+i,-n)):v.a/n;let b=v.a,rows=[],tot=0;
for(let t=1;t<=n;t++){const int=b*i;b=b-(pay-int);tot+=int;if(t%12===0||t===n)rows.push([t,money(pay*t),money(Math.max(0,b))]);}
out([["Monthly payment",money(pay)],["Total interest",money(tot)],["Total paid",money(pay*n)]],["Month","Paid so far","Balance left"],rows);
}
document.getElementById('form').addEventListener('input',calc);calc();
if('serviceWorker'in navigator)navigator.serviceWorker.register('sw.js');
let ev;addEventListener('beforeinstallprompt',e=>{e.preventDefault();ev=e;const b=document.getElementById('install');b.hidden=false;b.onclick=()=>ev.prompt();});
