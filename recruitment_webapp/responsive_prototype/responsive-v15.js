/* Responsive UX-UAT v1.5
   Status menu interaction correction:
   - menu anchors to the status badge/toolbar control, never pointer coordinates;
   - same trigger toggles closed;
   - outside click and Escape close without choosing;
   - focus is restored on Escape;
   - scroll repositions the menu; resize closes stale layout state.
*/
let statusMenuTriggerV15 = null;

function statusMenuGroupV15(entity, group){
  if(group) return group;
  if(entity.includes('round') || entity==='bulk-interview') return 'interview';
  if(entity.includes('report') || entity==='bulk-report') return 'report';
  return 'candidate';
}

function statusMenuIdentityV15(entity,id,group){ return `${entity}|${id||''}|${group||''}`; }

function clearStatusTriggerStateV15(){
  if(statusMenuTriggerV15 && statusMenuTriggerV15.isConnected){
    statusMenuTriggerV15.setAttribute('aria-expanded','false');
  }
}

function closeStatusMenuV15({restoreFocus=false}={}){
  const trigger=statusMenuTriggerV15;
  clearStatusTriggerStateV15();
  statusMenuTriggerV15=null;
  state.statusMenu=null;
  renderPortal();
  if(restoreFocus && trigger && trigger.isConnected){
    requestAnimationFrame(()=>trigger.focus({preventScroll:true}));
  }
}

function positionStatusMenuV15(){
  const menu=document.querySelector('.status-popover');
  const trigger=statusMenuTriggerV15;
  if(!menu || !trigger || !trigger.isConnected) return;
  const r=trigger.getBoundingClientRect();
  const margin=12,gap=8;
  const width=menu.offsetWidth;
  const height=menu.offsetHeight;
  let left=r.left;
  left=Math.max(margin,Math.min(left,window.innerWidth-width-margin));
  const roomBelow=window.innerHeight-r.bottom-gap-margin;
  const roomAbove=r.top-gap-margin;
  let top,placement;
  if(roomBelow>=height || roomBelow>=roomAbove){
    top=Math.min(r.bottom+gap,window.innerHeight-height-margin);
    placement='bottom';
  }else{
    top=Math.max(margin,r.top-height-gap);
    placement='top';
  }
  menu.style.left=`${Math.round(left)}px`;
  menu.style.top=`${Math.round(top)}px`;
  menu.dataset.placement=placement;
}

openStatusMenu = function(entity,id,e,group=null){
  if(e){e.preventDefault();e.stopPropagation();}
  const trigger=e?.currentTarget || null;
  const g=statusMenuGroupV15(entity,group);
  const key=statusMenuIdentityV15(entity,id,g);
  const current=state.statusMenu ? statusMenuIdentityV15(state.statusMenu.entity,state.statusMenu.id,state.statusMenu.group) : null;
  if(state.statusMenu && trigger && trigger===statusMenuTriggerV15 && current===key){
    closeStatusMenuV15({restoreFocus:false});
    return;
  }
  clearStatusTriggerStateV15();
  statusMenuTriggerV15=trigger;
  if(trigger){
    trigger.setAttribute('aria-haspopup','menu');
    trigger.setAttribute('aria-expanded','true');
  }
  state.statusMenu={entity,id,group:g};
  renderPortal();
  requestAnimationFrame(()=>{
    positionStatusMenuV15();
    const first=document.querySelector('.status-popover [role="menuitem"]');
    if(first) first.focus({preventScroll:true});
  });
};

closeStatusMenu = function(){ closeStatusMenuV15({restoreFocus:false}); };

statusMenuHtml = function(){
  if(!state.statusMenu)return '';
  const m=state.statusMenu;
  return `<div class="status-popover" role="menu" aria-label="${tx('Chọn trạng thái','Select status')}"><div class="status-popover-title">${tx('Chọn trạng thái','Select status')}</div>${statusGroups[m.group].map(s=>`<button role="menuitem" onclick="setEntityStatus('${m.entity}','${m.id||''}','${s}')"><span class="status-dot ${statusClass(s)}"></span><span>${statusText(s)}</span></button>`).join('')}</div>`;
};

/* Ensure both row badges and toolbar Status controls expose menu state semantics. */
statusBadgeV11 = function(s,group='general',entity=null,id=null){
  const clickable=!!entity&&canEditStatus();
  return `<${clickable?'button':'span'} class="status status-${group} ${statusClass(s)} ${clickable?'status-clickable':''}" ${clickable?`onclick="openStatusMenu('${entity}','${id}',event)" aria-label="${tx('Đổi trạng thái','Change status')}" aria-haspopup="menu" aria-expanded="false"`:''}>${statusText(s)}</${clickable?'button':'span'}>`;
};
toolbarStatus = function(group,entity){return `<button class="btn" onclick="openStatusMenu('${entity}','',event,'${group}')" aria-haspopup="menu" aria-expanded="false">${tx('Status','Status')} ${icon('chevron')}</button>`;};

/* Outside click: dismiss only; do not steal focus from the destination clicked by the user. */
document.addEventListener('pointerdown',event=>{
  if(!state.statusMenu) return;
  if(event.target.closest('.status-popover')) return;
  if(statusMenuTriggerV15 && (event.target===statusMenuTriggerV15 || statusMenuTriggerV15.contains(event.target))) return;
  closeStatusMenuV15({restoreFocus:false});
},true);

/* Capture Escape before older handlers so focus restoration is deterministic. */
document.addEventListener('keydown',event=>{
  if(event.key==='Escape' && state.statusMenu){
    event.preventDefault();
    event.stopImmediatePropagation();
    closeStatusMenuV15({restoreFocus:true});
  }
},true);

/* A fixed menu tied to a table cell must never remain floating after layout movement. */
window.addEventListener('resize',()=>{ if(state.statusMenu) closeStatusMenuV15({restoreFocus:false}); });
window.addEventListener('scroll',()=>{ if(state.statusMenu) requestAnimationFrame(positionStatusMenuV15); },true);

/* Visible version labels. */
const _loginPageResponsiveV15=loginPage;
loginPage=function(){return _loginPageResponsiveV15().replace(/Responsive UX-UAT v1\.4|Responsive rebuild v1\.3/g,'Responsive UX-UAT v1.5');};

render();
