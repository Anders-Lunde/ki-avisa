'use strict';
(() => {
  const c=__COMMENTS_COPY__;
  const root=document.querySelector('[data-comments]');
  if(!root)return;
  const status=root.querySelector('[role="status"]'),form=root.querySelector('form'),list=root.querySelector('[data-comment-list]');
  const more=root.querySelector('[data-comment-more]'),retry=root.querySelector('[data-comment-retry]');
  const submit=form.querySelector('[type="submit"]'),replyStatus=form.querySelector('[data-reply-status]'),cancel=form.querySelector('[data-cancel-reply]');
  const article=root.dataset.comments;
  const base='/api/comments?article='+encodeURIComponent(article);
  let token=null,tokenAt=0,tokenFlight=null,next=null,parent=null,busy=false;
  if(location.origin!=='https://ki-avisa.pages.dev'||root.dataset.preview==='true') {status.textContent=c.preview;return;}
  const element=(tag,text,className)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;};
  async function request(url,options) {
    const response=await fetch(url,{...options,cache:'no-store'});
    let data;
    try{data=await response.json();}catch{throw new Error(c.unavailable);}
    if(!response.ok) {const error=new Error(data.error||c.failed);error.expired=data.error===c.challenge_expired;throw error;}
    return data;
  }
  async function getToken() {
    if(token && Date.now()-tokenAt<6900000)return token;
    if(!tokenFlight)tokenFlight=request('/api/comments/token?article='+encodeURIComponent(article)).then(data=>{token=data.token;tokenAt=Date.now();return token;}).finally(()=>{tokenFlight=null;});
    return tokenFlight;
  }
  async function post(url,data) {
    const current=await getToken();
    // Match the server's minimum form age without a needless user error.
    const remaining=2100-(Date.now()-tokenAt);
    if(remaining>0)await new Promise(resolve=>setTimeout(resolve,remaining));
    try {return await request(url,{method:'POST',headers:{'Content-Type':'application/json','X-KI-Comments':'1'},body:JSON.stringify({...data,token:current})});}
    catch(error) {if(error.expired){token=null;getToken().catch(()=>{});}throw error;}
  }
  function cancelReply(){parent=null;replyStatus.textContent='';cancel.hidden=true;}
  cancel.addEventListener('click',cancelReply);
  function render(item) {
    const card=element('article',undefined,'comment-item');card.id='kommentar-'+item.id;
    const head=element('div',undefined,'comment-meta');
    head.append(element('strong',item.name));
    const time=element('time',new Intl.DateTimeFormat('nb-NO',{dateStyle:'medium',timeStyle:'short',timeZone:'Europe/Oslo'}).format(new Date(item.published_at*1000)));
    time.dateTime=new Date(item.published_at*1000).toISOString();head.append(time);card.append(head);
    if(item.parent_id && item.parent_name) {const link=element('a',c.replying+' '+item.parent_name,'comment-parent');link.href='#kommentar-'+item.parent_id;card.append(link);}
    card.append(element('p',item.body,'comment-text'));
    const actions=element('div',undefined,'comment-actions');
    const reply=element('button',c.reply);reply.type='button';reply.addEventListener('click',()=>{parent=item.id;replyStatus.textContent=c.replying+' '+item.name;cancel.hidden=false;form.elements.body.focus();});
    const report=element('button',c.report);report.type='button';report.addEventListener('click',async()=>{
      if(!confirm(c.report_confirm))return;
      report.disabled=true;
      try{const result=await post('/api/comments/report?article='+encodeURIComponent(article),{id:item.id});status.textContent=result.message;}
      catch(error){status.textContent=error.message;report.disabled=false;}
    });
    actions.append(reply,report);card.append(actions);list.append(card);
  }
  async function load() {
    more.disabled=true;retry.hidden=true;
    try {
      const data=await request(base+(next?'&after='+next:''));
      data.items.forEach(render);next=data.next;
      more.hidden=!next;
      status.textContent=list.children.length?'':c.empty;
    } catch(error){status.textContent=error.message;retry.hidden=false;}
    finally{more.disabled=false;}
  }
  more.addEventListener('click',load);retry.addEventListener('click',load);
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(busy||!form.reportValidity())return;
    busy=true;submit.disabled=true;form.setAttribute('aria-busy','true');
    try {
      const result=await post(base,{name:form.elements.name.value,body:form.elements.body.value,parent_id:parent,website:form.elements.website.value});
      status.textContent=result.message;form.elements.body.value='';cancelReply();token=null;
      getToken().catch(()=>{});
    } catch(error){status.textContent=error.message;}
    finally{busy=false;submit.disabled=false;form.removeAttribute('aria-busy');}
  });
  form.hidden=false;submit.disabled=false;status.textContent=c.loading;
  getToken().catch(error=>{status.textContent=error.message;});load();
})();
