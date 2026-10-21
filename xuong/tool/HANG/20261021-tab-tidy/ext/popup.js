// Tab Tidy – Close Duplicate Tabs – Snoutsmith Tools (MIT)
async function tabs(){if(!isExt)return[{id:1,url:'https://example.com/x'},{id:2,url:'https://example.com/x'},{id:3,url:'https://example.org/'},{id:4,url:'https://example.com/x#top'}];return chrome.tabs.query({currentWindow:true});}
const key=u=>u.split('#')[0];async function dups(){const seen=new Set(),d=[];for(const t of await tabs()){const k=key(t.url||'');if(seen.has(k))d.push(t.id);else seen.add(k);}return d;}
async function show(){$('#n').textContent=(await dups()).length;}
$('#go').onclick=async()=>{const d=await dups();if(isExt&&d.length)await chrome.tabs.remove(d);say(d.length+' tabs closed');store.set('closed',(await store.get('closed',0))+d.length);show();};
$('#sort').onclick=async()=>{const t=await tabs();const s=[...t].sort((a,b)=>new URL(a.url).hostname.localeCompare(new URL(b.url).hostname));if(isExt)for(let i=0;i<s.length;i++)await chrome.tabs.move(s[i].id,{index:i});say('Sorted '+s.length+' tabs');};
show();
