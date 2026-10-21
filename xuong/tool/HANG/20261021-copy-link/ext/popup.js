// Copy Link As – Markdown, HTML, Plain – Snoutsmith Tools (MIT)
const F={md:t=>`[${t.title}](${t.url})`,html:t=>`<a href="${t.url}">${t.title}</a>`,txt:t=>`${t.title} – ${t.url}`};
(async()=>{const t=await activeTab();$('#t').textContent=t.title;const fav=await store.get('fav','md');$('#out').textContent=F[fav](t);
document.querySelectorAll('[data-f]').forEach(b=>{b.className=b.dataset.f===fav?'':'alt';b.onclick=async()=>{const s=F[b.dataset.f](t);$('#out').textContent=s;try{await navigator.clipboard.writeText(s);say('Copied')}catch(e){say('Copy blocked – select the text below')}store.set('fav',b.dataset.f);document.querySelectorAll('[data-f]').forEach(x=>x.className=x===b?'':'alt');};});})();
