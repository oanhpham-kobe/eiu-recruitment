/* EIU Recruitment responsive rebuild v1.3
   Purpose: normalize responsive/accessibility behavior without duplicating business logic.
   Baseline: Full Handover v1.8 + Design System v1.7. */

state.mobileNavOpen = !!state.mobileNavOpen;
let responsiveOverlayTrigger = null;
let responsiveLastNavTriggerWasCandidate = false;
let responsiveEnhancementSeq = 0;

function isNarrowNavigation(){ return window.matchMedia('(max-width: 1279px)').matches; }
function getFocusable(root){
  if(!root) return [];
  return [...root.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])')]
    .filter(el=>!el.hasAttribute('hidden') && el.getClientRects().length && getComputedStyle(el).visibility!=='hidden');
}
function restoreFocus(el, fallbackSelector){
  requestAnimationFrame(()=>{
    const target = el && document.contains(el) ? el : document.querySelector(fallbackSelector||'');
    if(target && typeof target.focus==='function') target.focus({preventScroll:true});
  });
}

/* Mobile navigation: one render path, managed focus, background inert, screen-reader hidden when closed. */
const _toggleMobileNavV13 = toggleMobileNav;
toggleMobileNav = function(){
  const opening = !state.mobileNavOpen;
  responsiveLastNavTriggerWasCandidate = !!document.activeElement?.classList?.contains('candidate-hamb');
  state.mobileNavOpen = opening;
  render();
  requestAnimationFrame(()=>{
    if(opening){
      const close = document.querySelector('.responsive-sidebar.open .mobile-nav-close');
      if(close) close.focus();
    } else {
      restoreFocus(null, responsiveLastNavTriggerWasCandidate?'.candidate-hamb':'.hamb');
    }
  });
};
closeMobileNav = function(){
  if(!state.mobileNavOpen) return;
  state.mobileNavOpen=false;
  render();
  restoreFocus(null,responsiveLastNavTriggerWasCandidate?'.candidate-hamb':'.hamb');
};

/* Remember trigger for Drawer/Modal and restore it after close. */
const _openDrawerV13 = openDrawer;
openDrawer = function(type,id){ responsiveOverlayTrigger=document.activeElement; _openDrawerV13(type,id); };
const _openModalV13 = openModal;
openModal = function(type,data={}){ responsiveOverlayTrigger=document.activeElement; _openModalV13(type,data); };
const _closeDrawerV13 = closeDrawer;
closeDrawer = function(){ const t=responsiveOverlayTrigger; _closeDrawerV13(); responsiveOverlayTrigger=null; restoreFocus(t); };
const _closeModalV13 = closeModal;
closeModal = function(){ const t=responsiveOverlayTrigger; _closeModalV13(); responsiveOverlayTrigger=null; restoreFocus(t); };

/* Candidate header retains VI|EN and an accessible back action on very narrow screens. */
const _candidateMobileHeaderV13 = candidateMobileHeader;
candidateMobileHeader = function(title,helper,back=false){
  return `<div class="candidate-head responsive-candidate-head"><div class="candidate-head-main"><button class="hamb candidate-hamb" type="button" onclick="toggleMobileNav()" aria-controls="mobile-primary-nav" aria-expanded="${state.mobileNavOpen?'true':'false'}" aria-label="${tx('Mở menu','Open menu')}">☰</button><div><h1>${title}</h1><div class="helper">${helper}</div></div></div><div class="candidate-head-actions">${languageSwitcher()}${back?`<button class="btn" type="button" aria-label="${tx('Quay lại Phiếu của tôi','Back to My applications')}" onclick="nav('candidate-applications')">← <span>${tx('Phiếu của tôi','My applications')}</span></button>`:`<div class="candidate-user-compact"><div class="avatar">NT</div><span>${tx('Ứng viên','Candidate')}</span></div>`}</div></div>`;
};

/* Candidate Form: replace inline submit behavior with one observable validation path. */
function handleCandidateResponsiveSubmit(event){
  event.preventDefault();
  const form=event.currentTarget;
  const ack=form.querySelector('#privacyAck');
  const err=form.querySelector('#privacyError');
  if(ack && !ack.checked){
    if(err){err.hidden=false;err.textContent=tx('Vui lòng xác nhận thông báo quyền riêng tư trước khi gửi phiếu.','Please acknowledge the privacy notice before submitting.');}
    ack.setAttribute('aria-invalid','true');
    ack.focus();
    return false;
  }
  if(ack){ack.removeAttribute('aria-invalid');if(err){err.hidden=true;err.textContent='';}}
  const invalid=[...form.querySelectorAll('input,select,textarea')].find(el=>!el.checkValidity());
  if(invalid){invalid.reportValidity();invalid.focus();return false;}
  toast(tx('Đã gửi phiếu ứng tuyển mẫu','Sample application submitted'));
  nav('candidate-applications');
  return false;
}

function normalizeFormLabels(){
  let idx=0;
  document.querySelectorAll('.field,.field-row').forEach(group=>{
    const label=group.querySelector(':scope > label');
    if(!label || label.querySelector('input,select,textarea')) return;
    const control=group.querySelector(':scope > input,:scope > select,:scope > textarea,:scope > .input,:scope > .select,:scope > .textarea');
    if(!control) return;
    if(!control.id) control.id=`responsive-field-${state.page||'page'}-${++idx}`;
    label.htmlFor=control.id;
  });
}

function labelIconOnlyButtons(){
  document.querySelectorAll('.signout-btn').forEach(btn=>btn.setAttribute('aria-label',tx('Đăng xuất','Sign out')));
  const labels={eye:tx('Xem chi tiết','View details'),edit:tx('Chỉnh sửa','Edit'),trash:tx('Xóa','Delete'),close:tx('Đóng','Close'),download:tx('Tải xuống','Download'),chevron:tx('Mở rộng','Expand')};
  document.querySelectorAll('button').forEach(btn=>{
    if(btn.getAttribute('aria-label') || btn.textContent.trim()) return;
    const use=btn.querySelector('use');
    const href=use?.getAttribute('href')||'';
    const key=href.replace('#i-','');
    if(labels[key]) btn.setAttribute('aria-label',labels[key]);
  });
}

function addMobileSidebarSignout(){
  document.querySelectorAll('.responsive-sidebar .sidebar-user').forEach(user=>{
    if(user.querySelector('.mobile-sidebar-signout')) return;
    const b=document.createElement('button');
    b.type='button';b.className='mobile-sidebar-signout';b.innerHTML=icon('logout');
    b.setAttribute('aria-label',tx('Đăng xuất','Sign out'));
    b.addEventListener('click',()=>{state.mobileNavOpen=false;state.role=null;state.page='login';render();});
    user.appendChild(b);
  });
}

function syncMobileNavAccessibility(){
  const narrow=isNarrowNavigation();
  const sidebar=document.querySelector('.responsive-sidebar');
  const main=document.querySelector('.main,.candidate-content');
  if(!sidebar) return;
  sidebar.id='mobile-primary-nav';
  const open=narrow && !!state.mobileNavOpen;
  if(narrow){
    sidebar.setAttribute('aria-hidden',open?'false':'true');
    if(open){sidebar.removeAttribute('inert');sidebar.setAttribute('role','dialog');sidebar.setAttribute('aria-modal','true');}
    else {sidebar.setAttribute('inert','');sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal');}
    if(main){ if(open) main.setAttribute('inert',''); else main.removeAttribute('inert'); }
  }else{
    sidebar.setAttribute('aria-hidden','false');sidebar.removeAttribute('inert');sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal');
    if(main) main.removeAttribute('inert');
  }
  document.querySelectorAll('.hamb').forEach(h=>{h.setAttribute('aria-controls','mobile-primary-nav');h.setAttribute('aria-expanded',state.mobileNavOpen?'true':'false');});
}

function normalizeScrollableTables(){
  document.querySelectorAll('.desktop-table-scroll').forEach((scroller,i)=>{
    if(scroller.scrollWidth>scroller.clientWidth+1){
      scroller.tabIndex=0;
      if(!scroller.getAttribute('aria-label')) scroller.setAttribute('aria-label',tx('Bảng dữ liệu có thể cuộn ngang','Horizontally scrollable data table'));
    }else if(scroller.getAttribute('tabindex')==='0'){
      scroller.removeAttribute('tabindex');
    }
  });
}

function enhanceOverlayAccessibility(){
  const overlay=document.querySelector('.modal,.drawer');
  const hasOverlay=!!overlay;
  document.body.classList.toggle('overlay-is-open',hasOverlay);
  const app=document.getElementById('app');
  if(app){
    if(hasOverlay){app.setAttribute('inert','');app.setAttribute('aria-hidden','true');}
    else {app.removeAttribute('inert');app.removeAttribute('aria-hidden');}
  }
  if(!overlay) return;
  overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');
  const heading=overlay.querySelector('h2,h3');
  if(heading){if(!heading.id) heading.id=`responsive-dialog-title-${++responsiveEnhancementSeq}`;overlay.setAttribute('aria-labelledby',heading.id);}
  const close=overlay.querySelector('.drawer-close,.modal-head .row-btn,.drawer-head .row-btn');
  if(close && !close.getAttribute('aria-label')) close.setAttribute('aria-label',tx('Đóng','Close'));
  requestAnimationFrame(()=>{
    if(!overlay.contains(document.activeElement)){
      const first=close || getFocusable(overlay)[0];
      if(first) first.focus({preventScroll:true});
    }
  });
}

function enhanceToast(){
  const t=document.querySelector('.toast');
  if(t){t.setAttribute('role','status');t.setAttribute('aria-live','polite');t.setAttribute('aria-atomic','true');}
}

function enhanceCandidateForm(){
  const form=document.querySelector('.candidate-form');
  if(!form) return;
  form.noValidate=true;
  form.onsubmit=handleCandidateResponsiveSubmit;
  const ack=form.querySelector('#privacyAck');
  if(ack){
    ack.setAttribute('aria-describedby','privacyError');
    let err=form.querySelector('#privacyError');
    if(!err){err=document.createElement('div');err.id='privacyError';err.className='field-error';err.setAttribute('role','alert');err.hidden=true;ack.closest('.privacy-check')?.insertAdjacentElement('afterend',err);}
    ack.addEventListener('change',()=>{if(ack.checked){ack.removeAttribute('aria-invalid');err.hidden=true;err.textContent='';}});
  }
}

function enhanceResponsiveV13Dom(){
  document.documentElement.lang=state.lang==='en'?'en':'vi';
  normalizeFormLabels();
  labelIconOnlyButtons();
  addMobileSidebarSignout();
  syncMobileNavAccessibility();
  normalizeScrollableTables();
  enhanceCandidateForm();
  enhanceOverlayAccessibility();
  enhanceToast();
}

/* Wrap rendering once; no separate mobile business logic is introduced. */
const _renderV13=render;
render=function(){_renderV13();enhanceResponsiveV13Dom();};
const _renderPortalV13=renderPortal;
renderPortal=function(){_renderPortalV13();enhanceOverlayAccessibility();enhanceToast();labelIconOnlyButtons();normalizeFormLabels();};

/* Escape + focus trap for nav/dialog/drawer; native controls remain the interaction source. */
document.addEventListener('keydown',event=>{
  if(event.key==='Escape'){
    if(state.modal){event.preventDefault();closeModal();return;}
    if(state.drawer){event.preventDefault();closeDrawer();return;}
    if(state.statusMenu){state.statusMenu=null;renderPortal();return;}
    if(state.mobileNavOpen){event.preventDefault();closeMobileNav();return;}
  }
  if(event.key==='Tab'){
    const root=document.querySelector('.modal,.drawer') || (state.mobileNavOpen && isNarrowNavigation()?document.querySelector('.responsive-sidebar.open'):null);
    if(!root) return;
    const items=getFocusable(root);if(!items.length)return;
    const first=items[0],last=items[items.length-1];
    if(event.shiftKey && document.activeElement===first){event.preventDefault();last.focus();}
    else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first.focus();}
  }
});

window.addEventListener('resize',()=>{syncMobileNavAccessibility();normalizeScrollableTables();});

/* Visible version labels for this rebuilt prototype. */
const _loginPageResponsiveV13=loginPage;
loginPage=function(){return _loginPageResponsiveV13().replace(/Responsive prototype v1\.2|Clickable prototype v1\.1|Clickable prototype v1\.0/g,'Responsive rebuild v1.3');};

render();
