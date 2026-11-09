'use strict';
document.addEventListener('click',async event=>{
  const button=event.target.closest('button[data-action]');
  if(!button)return;
  if(button.dataset.action==='delete'&&!confirm('Slette kommentaren permanent?'))return;
  const status=document.getElementById('moderation-status');
  button.disabled=true;
  try {
    const response=await fetch('/moderering',{method:'POST',headers:{'Content-Type':'application/json','X-KI-Comments':'1'},body:JSON.stringify({id:Number(button.dataset.id),action:button.dataset.action})});
    if(!response.ok)throw new Error();
    button.closest('article').remove();
    status.textContent='Handlingen er lagret.';
  } catch {status.textContent='Kunne ikke lagre. Oppdater siden og kontroller status før du prøver igjen.';button.disabled=false;}
});
