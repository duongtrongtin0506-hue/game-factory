// Word Counter – Selection & Page – Snoutsmith Tools (MIT)
(async()=>{const txt=await inPage(()=>{const s=String(getSelection());return s.trim()?{t:s,sel:true}:{t:document.body?document.body.innerText:'',sel:false};});
const t=isExt?txt:{t:'Demo text: select text on any page and open Word Counter to count it instantly. It also counts the whole page when nothing is selected.',sel:true};
const w=(t.t.match(/\S+/g)||[]).length;$('#w').textContent=w.toLocaleString();$('#c').textContent=t.t.length.toLocaleString();$('#r').textContent=Math.max(1,Math.round(w/238));$('#s').textContent=Math.max(1,Math.round(w/150));
$('#src').textContent=t.sel?'Counting your selection':'Nothing selected – counting the whole page';})();
