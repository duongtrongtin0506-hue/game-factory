const isExt=typeof chrome!=='undefined'&&chrome.tabs&&chrome.storage;
const store={get:(k,d)=>new Promise(r=>{if(isExt)chrome.storage.local.get(k,v=>r(v[k]??d));else{try{r(JSON.parse(localStorage.getItem(k))??d)}catch(e){r(d)}}}),
set:(k,v)=>isExt?chrome.storage.local.set({[k]:v}):localStorage.setItem(k,JSON.stringify(v))};
const $=s=>document.querySelector(s);const say=t=>{$('#msg').textContent=t;setTimeout(()=>$('#msg').textContent='',2200);};
async function activeTab(){if(!isExt)return{id:0,title:'Demo page – Snoutsmith Tools',url:'https://example.com/demo-article'};const[t]=await chrome.tabs.query({active:true,currentWindow:true});return t;}
async function inPage(fn){if(!isExt)return fn();const t=await activeTab();const[r]=await chrome.scripting.executeScript({target:{tabId:t.id},func:fn});return r.result;}
