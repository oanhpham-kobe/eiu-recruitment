/* EIU Recruitment Responsive Prototype v1.4
   Targeted UX fixes from user visual UAT:
   - compact Interview/Report status badges
   - interview time = time first, date second, wrap only when necessary
   - mobile Report label width keeps “Thời gian phỏng vấn” on one line
   - bulk selection checkbox fix
   - visible button-flow audit/wiring for the responsive prototype
   No business/security/database behavior is changed. */

state.prototypePager = state.prototypePager || {};
/* v1.3 could call document.querySelector('') when an overlay had no remembered trigger. */
restoreFocus = function(el,fallbackSelector){
  requestAnimationFrame(()=>{
    const fallback = fallbackSelector ? document.querySelector(fallbackSelector) : null;
    const target = el && document.contains(el) ? el : fallback;
    if(target && typeof target.focus==='function') target.focus({preventScroll:true});
  });
};
/* Visual label normalized to the user-approved benchmark wording. */
if(statusLabelsV11.REPORT_SUBMITTED) statusLabelsV11.REPORT_SUBMITTED[0]='Đã gửi báo cáo';

function stopRowPropagation(event){ if(event) event.stopPropagation(); }

function interviewTimeV14(round){
  if(!round) return '–';
  return `<span class="interview-time-v14"><span class="time-range-v14">${round.start} – ${round.end}</span><span class="date-v14">${round.date}</span></span>`;
}

function selectedCountV14(){ return state.selectedIds ? state.selectedIds.size : 0; }

function selectedRoundIdsV14(){
  return [...(state.selectedIds||[])].filter(id=>!!findRound(id));
}

function openPrototypeEmailV14(target){
  const count=selectedCountV14();
  if(!count) return toast(tx('Vui lòng chọn ít nhất một dòng trước.','Select at least one row first.'));
  openModal('prototypeEmailV14',{target,count,page:state.page});
}

function openPrototypeDeleteV14(){
  const count=selectedCountV14();
  if(!count) return toast(tx('Vui lòng chọn ít nhất một dòng trước.','Select at least one row first.'));
  openModal('prototypeDeleteV14',{count,page:state.page});
}

function clearBulkSelectionV14(){
  state.selectedIds.clear();
  render();
}

/* Copy follows the selected interview when possible instead of silently defaulting to a1. */
copyLatest = function(){
  const selected=selectedRoundIdsV14();
  if(selected.length>1) return toast(tx('Chỉ chọn một lịch để sao chép.','Select only one interview to copy.'));
  if(selected.length===1){
    const r=findRound(selected[0]);
    const a=state.applications.find(x=>x.rounds.some(y=>y.id===r.id));
    return openModal('copyRound',{appId:a.id,roundId:r.id});
  }
  if(state.expandedApplication){
    const a=appById(state.expandedApplication),r=currentRound(a);
    return openModal('copyRound',{appId:a.id,roundId:r.id});
  }
  toast(tx('Chọn một lịch hoặc mở Application trước khi sao chép.','Select an interview or open an Application before copying.'));
};


/* Keep visible prototype version aligned with this package. */
const _shellV14=shell;
shell=function(content,title,sub=''){
  return _shellV14(content,title,sub).replace(/Responsive UX-UAT v1\.2|Responsive rebuild v1\.3/g,'Responsive UX-UAT v1.4');
};

/* Current responsive Interview representation, with functional checkboxes and time-first layout. */
interviewPage = function(){
 const rows=state.applications.map(a=>{
   const c=candidate(a.candidateId),cr=currentRound(a),open=state.expandedApplication===a.id,activeRounds=a.rounds.filter(r=>r.active);
   let html=`<tr class="parent-row ${open?'expanded':''}" tabindex="0" onclick="handleAppRow('${a.id}',event)">
     <td class="control-cell"><input class="check" type="checkbox" aria-label="${tx('Chọn lịch của','Select interview for')} ${c.name}" ${state.selectedIds.has(cr.id)?'checked':''} onclick="stopRowPropagation(event)" onchange="toggleSelect('${cr.id}',this.checked)"></td>
     <td class="name-cell"><button class="expand-inline" onclick="stopEvt(event);toggleApp('${a.id}')" aria-expanded="${open?'true':'false'}">${activeRounds.length>1?`<span class="chevron ${open?'open':''}">›</span>`:''}<span><strong>${c.name}</strong><small>${a.position} - ${a.unit}<br>${tx('Vòng hiện tại','Current round')}: ${cr.no}</small></span></button></td>
     <td class="interview-time-cell">${interviewTimeV14(cr)}</td>
     <td>${cr.location}<div class="helper">${cr.format}</div></td>
     <td class="status-cell">${statusBadgeV11(cr.status,'interview','round',cr.id)}</td>
     <td>${cr.note||'–'}<div class="helper">${icon('users')} ${cr.participants.length} ${tx('người tham dự','participants')}</div></td>
     <td class="action-cell"><button class="row-btn" onclick="stopEvt(event);openDrawer('round','${cr.id}')" aria-label="${tx('Xem lịch phỏng vấn','View interview')}">${icon('eye')}</button></td></tr>`;
   if(open){
     html+=activeRounds.filter(r=>r.id!==cr.id).map(r=>`<tr class="child-row interview-history-row" onclick="openDrawer('round','${r.id}')">
       <td class="control-cell"><input class="check" type="checkbox" aria-label="${tx('Chọn','Select')} ${tx('Vòng','Round')} ${r.no}" ${state.selectedIds.has(r.id)?'checked':''} onclick="stopRowPropagation(event)" onchange="toggleSelect('${r.id}',this.checked)"></td>
       <td class="name-cell"><strong>${tx('Vòng','Round')} ${r.no}</strong><span>${r.topic||tx('Chưa nhập Demo Topic','Demo Topic not entered')}</span></td>
       <td class="interview-time-cell">${interviewTimeV14(r)}</td><td>${r.location}</td>
       <td class="status-cell">${statusBadgeV11(r.status,'interview','round',r.id)}</td><td>${r.note||'–'}</td><td class="action-cell">${icon('eye')}</td></tr>`).join('');
   }
   return html;
 }).join('');
 return shell(`<div class="content"><div class="toolbar"><div class="toolbar-left">
   <button class="btn primary" onclick="openModal('createRound')">${icon('plus')} ${tx('Tạo lịch','Create interview')}</button>
   <button class="btn" onclick="copyLatest()">${icon('copy')} ${tx('Sao chép lịch','Copy interview')}</button>
   <button class="btn danger" onclick="openPrototypeDeleteV14()">${icon('trash')} ${tx('Xóa','Delete')}</button>
   ${toolbarStatus('interview','bulk-interview')}
   <button class="btn" onclick="openPrototypeEmailV14('candidate')">${icon('mail')} ${tx('Gửi thư ứng viên','Email candidate')}</button>
   <button class="btn" onclick="openPrototypeEmailV14('participants')">${icon('mail')} ${tx('Gửi thư người tham dự','Email participants')}</button>
   </div><div class="toolbar-right"><div class="searchbox"><input class="input" placeholder="${tx('Tìm kiếm...','Search...')}">${icon('search')}</div><button class="btn" onclick="openModal('responsiveFilters',{page:'interview'})">${icon('filter')} ${tx('Bộ lọc','Filters')}</button></div></div>
   <div class="table-card desktop-table-scroll responsive-table-shell"><table class="data-table interview-table">${colgroup([48,340,250,220,170,360,92])}<thead><tr><th></th><th>${tx('Ứng viên / Application','Candidate / Application')}</th><th>${tx('Thời gian','Time')}</th><th>${tx('Địa điểm','Location')}</th><th>${tx('Trạng thái','Status')}</th><th>${tx('Ghi chú','Note')}</th><th>${tx('Thao tác','Action')}</th></tr></thead><tbody>${rows}</tbody></table>${pager(68)}</div></div>`,'Interview',tx('Quản lý lịch phỏng vấn và người tham dự. Tablet giữ bảng ngang; mobile chuyển structured rows.','Manage schedules and participants. Tablet keeps horizontal tables; mobile uses structured rows.'));
};

/* HR Report uses the same time ordering and functional bulk selection. */
hrReportPage = function(){
 const rows=state.applications.map(a=>{const c=candidate(a.candidateId),r=currentRound(a);return `<tr class="click-row" onclick="if(!event.target.closest('button,input'))openDrawer('hrReport','${a.id}')">
   <td class="control-cell"><input class="check" type="checkbox" aria-label="${tx('Chọn báo cáo của','Select report for')} ${c.name}" ${state.selectedIds.has(a.id)?'checked':''} onclick="stopRowPropagation(event)" onchange="toggleSelect('${a.id}',this.checked)"></td>
   <td class="name-cell"><strong>${c.name}</strong><span>${tx('Vòng','Round')} ${r.no}</span></td><td>${a.position}</td>
   <td class="interview-time-cell">${interviewTimeV14(r)}</td><td>${r.location}</td><td class="status-cell">${statusBadgeV11(a.status,'report','report',a.id)}</td><td>${r.note||'–'}</td>
   <td class="action-cell"><button class="row-btn" onclick="stopEvt(event);openDrawer('hrReport','${a.id}')" aria-label="${tx('Xem báo cáo','View report')}">${icon('eye')}</button></td></tr>`}).join('');
 return shell(`<div class="content"><div class="toolbar"><div class="toolbar-left">${toolbarStatus('report','bulk-report')}<button class="btn" onclick="openPrototypeEmailV14('report')">${icon('mail')} ${tx('Gửi thư','Email')}</button></div><div class="toolbar-right"><div class="searchbox"><input class="input" placeholder="${tx('Tìm kiếm...','Search...')}">${icon('search')}</div><button class="btn" onclick="openModal('responsiveFilters',{page:'report'})">${icon('filter')} ${tx('Bộ lọc','Filters')}</button></div></div>
 <div class="table-card desktop-table-scroll responsive-table-shell"><table class="data-table report-table">${colgroup([48,240,300,240,200,190,300,92])}<thead><tr><th></th><th>${tx('Họ và tên','Name')}</th><th>${tx('Vị trí','Position')}</th><th>${tx('Thời gian phỏng vấn','Interview time')}</th><th>${tx('Địa điểm','Location')}</th><th>${tx('Trạng thái','Status')}</th><th>${tx('Ghi chú','Note')}</th><th>${tx('Thao tác','Action')}</th></tr></thead><tbody>${rows}</tbody></table>${pager(48)}</div></div>`,tx('Báo cáo phỏng vấn (HR)','Interview Reports (HR)'),tx('Một dòng cho mỗi Application, sử dụng Current Round.','One row per Application using the Current Round.'));
};

/* Interviewer report follows the same time-first visual rule. */
interviewerPage = function(){
 const apps=state.applications.filter(a=>currentRound(a).participants.includes(state.currentInterviewer));
 const rows=apps.map(a=>{const c=candidate(a.candidateId),r=currentRound(a),own=state.reports[r.id]?.[state.currentInterviewer];return `<tr class="click-row" onclick="if(!event.target.closest('button,input'))openDrawer('interviewer','${a.id}')"><td class="name-cell"><strong>${c.name}</strong><span>${c.email}</span></td><td>${a.position}</td><td>${tx('Vòng','Round')} ${r.no}</td><td class="interview-time-cell">${interviewTimeV14(r)}</td><td class="status-cell">${statusBadgeV11(a.status,'report')}</td><td class="action-cell"><button class="row-btn" onclick="stopEvt(event);openDrawer('interviewer','${a.id}')" aria-label="${tx('Xem báo cáo','View report')}">${icon('eye')}</button>${own?`<button class="row-btn" onclick="stopEvt(event);openDrawer('interviewer','${a.id}')" aria-label="${tx('Chỉnh sửa báo cáo','Edit report')}">${icon('edit')}</button>`:''}</td></tr>`}).join('');
 return shell(`<div class="content"><div class="toolbar"><div class="toolbar-left"><button class="btn" onclick="toast('${tx('Đã đặt lại bộ lọc mẫu','Sample filters reset')}')">${tx('Đặt lại bộ lọc','Reset filters')}</button></div><div class="toolbar-right"><div class="searchbox"><input class="input" placeholder="${tx('Tìm kiếm theo họ tên, vị trí...','Search by name, position...')}">${icon('search')}</div><button class="btn" onclick="openModal('responsiveFilters',{page:'interviewer-report'})">${icon('filter')} ${tx('Bộ lọc','Filters')}</button></div></div><div class="table-card desktop-table-scroll responsive-table-shell"><table class="data-table interviewer-table">${colgroup([300,270,110,240,200,90])}<thead><tr><th>${tx('Họ và tên','Full name')}</th><th>${tx('Vị trí','Position')}</th><th>${tx('Vòng','Round')}</th><th>${tx('Thời gian phỏng vấn','Interview time')}</th><th>${tx('Trạng thái','Status')}</th><th>${tx('Thao tác','Actions')}</th></tr></thead><tbody>${rows}</tbody></table>${pager(apps.length)}</div></div>`,tx('Báo cáo phỏng vấn của tôi','My Interview Reports'),tx('Nhập báo cáo đánh giá ứng viên sau mỗi buổi phỏng vấn.','Enter candidate evaluation after each interview.'));
};

/* Fix candidate bulk checkbox behavior too: remove preventDefault from checkbox click. */
const _applicationsPageV14 = applicationsPage;
applicationsPage = function(){
  return _applicationsPageV14().replaceAll('onclick="stopEvt(event)" onchange="toggleSelect(', 'onclick="stopRowPropagation(event)" onchange="toggleSelect(')
    .replace(`<button class="btn danger" ${state.selectedIds.size?'':'disabled'}>${icon('trash')} ${tx('Xóa','Delete')}</button>`,`<button class="btn danger" ${state.selectedIds.size?'':'disabled'} onclick="openPrototypeDeleteV14()">${icon('trash')} ${tx('Xóa','Delete')}</button>`)
    .replace(`<button class="btn">${icon('mail')} ${tx('Gửi thư ứng viên','Email candidate')}</button>`,`<button class="btn" onclick="openPrototypeEmailV14('candidate')">${icon('mail')} ${tx('Gửi thư ứng viên','Email candidate')}</button>`);
};

/* Functional pager for prototype verification: changes the active page indicator without pretending to have backend pagination. */
pager = function(count=48){
  const key=state.page||'default';
  const max=Math.max(1,Math.ceil(count/10));
  const current=Math.min(state.prototypePager[key]||1,max);
  const nums=[1,2,3].filter(n=>n<=max);
  return `<div class="pagination"><span>${tx(`Hiển thị 1 đến ${Math.min(10,count)} của ${count} kết quả`,`Showing 1 to ${Math.min(10,count)} of ${count} results`)}</span><div class="pages"><button class="pagebtn" onclick="prototypePageV14('${key}',${Math.max(1,current-1)},${max})" ${current===1?'disabled':''}>‹</button>${nums.map(n=>`<button class="pagebtn ${current===n?'active':''}" onclick="prototypePageV14('${key}',${n},${max})">${n}</button>`).join('')}<button class="pagebtn" onclick="prototypePageV14('${key}',${Math.min(max,current+1)},${max})" ${current===max?'disabled':''}>›</button></div><select class="filter-select" aria-label="${tx('Số dòng mỗi trang','Rows per page')}"><option>${tx('10 / trang','10 / page')}</option></select></div>`;
};
function prototypePageV14(key,page,max){
  state.prototypePager[key]=Math.max(1,Math.min(page,max));
  toast(tx(`Đã chuyển chỉ báo sang trang ${state.prototypePager[key]} (dữ liệu prototype không phân trang thật).`,`Page indicator moved to ${state.prototypePager[key]} (prototype data is not truly paginated).`));
  render();
}

/* Lightweight education repeat-item interactions, still one shared candidate form. */
function addEducationItemV14(button){
  const section=button.closest('.form-section'); if(!section) return;
  const first=section.querySelector('.repeat-item'); if(!first) return;
  const clone=first.cloneNode(true);
  clone.querySelectorAll('input').forEach(i=>{ if(i.type!=='hidden') i.value=''; });
  const count=section.querySelectorAll('.repeat-item').length+1;
  const title=clone.querySelector('.repeat-item-head strong'); if(title) title.textContent=tx(`Học vấn ${count}`,`Education ${count}`);
  section.insertBefore(clone,button.closest('.section-head-row')?.nextSibling || button);
  enhanceResponsiveV14Dom();
}
function removeEducationItemV14(button){
  const item=button.closest('.repeat-item'),section=button.closest('.form-section');
  if(!item||!section) return;
  if(section.querySelectorAll('.repeat-item').length<=1) return toast(tx('Cần giữ ít nhất một mục học vấn.','Keep at least one education item.'));
  item.remove();
}

function prototypeButtonLabelV14(btn){ return (btn.innerText||btn.getAttribute('title')||btn.getAttribute('aria-label')||'').trim().replace(/\s+/g,' '); }
function wirePrototypeButtonsV14(){
  document.querySelectorAll('button').forEach(btn=>{
    if(btn.hasAttribute('onclick') || btn.dataset.prototypeWired==='true' || (btn.type==='submit'&&btn.closest('form'))) return;
    btn.dataset.prototypeWired='true';
    const label=prototypeButtonLabelV14(btn).toLowerCase();
    btn.addEventListener('click',event=>{
      event.stopPropagation();
      if(btn.classList.contains('compact-add')) return addEducationItemV14(btn);
      if(btn.closest('.repeat-item-head') && btn.classList.contains('row-btn')) return removeEducationItemV14(btn);
      if(btn.classList.contains('circle-btn')) return toast(label.includes('help')||label.includes('trợ giúp')||label==='?'?tx('Trợ giúp prototype: dùng các màn hình và nút để UX-UAT.','Prototype help: use the screens and controls for UX-UAT.'):tx('Không có thông báo mới trong prototype.','No new notifications in the prototype.'));
      if(btn.closest('.candidate-actions') && (label.includes('phiếu của tôi')||label.includes('my applications'))) return nav('candidate-applications');
      if(btn.closest('.candidateSidebar,.responsive-sidebar') || btn.classList.contains('nav-item')) return toast(tx('Mục này ngoài phạm vi prototype responsive hiện tại.','This destination is outside the current responsive prototype scope.'));
      if(btn.closest('.permissions-table')) return openModal('prototypeUserV14',{mode:label?'edit':'view'});
      if(btn.closest('.toolbar') && (label.includes('thêm người dùng')||label.includes('add user'))) return openModal('prototypeUserV14',{mode:'add'});
      if(btn.closest('.toolbar') && (label.includes('phân quyền')||label.includes('assign hr'))) return openModal('prototypeUserV14',{mode:'permissions'});
      if(btn.closest('.drawer-actions')||btn.closest('.drawer')||btn.closest('.modal-footer')) return toast(tx(`Đã kiểm tra luồng nút “${prototypeButtonLabelV14(btn)||'Thao tác'}” trong prototype.`,`Prototype flow checked for “${prototypeButtonLabelV14(btn)||'Action'}”.`));
      toast(tx(`Nút “${prototypeButtonLabelV14(btn)||'Thao tác'}” đã được kết nối trong prototype.`,`“${prototypeButtonLabelV14(btn)||'Action'}” is wired in the prototype.`));
    });
  });
}

const _modalHtmlV14=modalHtml;
modalHtml=function(){
  if(state.modal?.type==='prototypeEmailV14'){
    const d=state.modal.data||{};
    const recipient=d.target==='participants'?tx('người tham dự','participants'):d.target==='report'?tx('đối tượng báo cáo','report recipients'):tx('ứng viên','candidate');
    return modalFrame(tx('Xem trước email','Email preview'),`<p>${tx('Đã chọn','Selected')} <b>${d.count||0}</b> ${tx('dòng','rows')}.</p><div class="note-box"><b>${tx('Người nhận','Recipients')}:</b> ${recipient}<br><b>${tx('Chủ đề','Subject')}:</b> ${tx('Email mẫu từ EIU Recruitment','Sample EIU Recruitment email')}</div><p class="helper">${tx('Prototype chỉ kiểm tra luồng responsive; không gửi email thật.','Prototype verifies the responsive flow only; no real email is sent.')}</p>`,`<button class="btn" onclick="closeModal()">${tx('Hủy','Cancel')}</button><button class="btn primary" onclick="closeModal();toast('${tx('Đã chạy luồng gửi email mẫu','Sample email flow completed')}')">${tx('Gửi','Send')}</button>`);
  }
  if(state.modal?.type==='prototypeDeleteV14'){
    const d=state.modal.data||{};
    return modalFrame(tx('Xác nhận xóa','Confirm delete'),`<p>${tx(`Đã chọn ${d.count||0} dòng. Prototype không xóa dữ liệu mẫu vì backend phải kiểm tra điều kiện hard-delete/inactive.`,`Selected ${d.count||0} rows. The prototype does not remove sample data because backend delete/inactive rules must be validated.`)}</p>`,`<button class="btn" onclick="closeModal()">${tx('Hủy','Cancel')}</button><button class="btn danger" onclick="closeModal();clearBulkSelectionV14();toast('${tx('Luồng xác nhận xóa đã được kiểm tra','Delete confirmation flow verified')}')">${tx('Xác nhận','Confirm')}</button>`);
  }
  if(state.modal?.type==='prototypeUserV14'){
    const mode=state.modal.data?.mode||'view';
    return modalFrame(tx('Người dùng & Phân quyền','Users & Permissions'),`<div class="form-grid"><div class="field"><label>${tx('Họ tên','Name')}</label><input class="input" value="TS. Trần Minh Khoa"></div><div class="field"><label>Email EIU</label><input class="input" value="khoa.tm@eiu.edu.vn"></div><div class="field"><label>${tx('Chế độ','Mode')}</label><input class="input" value="${mode}" readonly></div></div><p class="helper">${tx('Prototype kiểm tra khả năng mở/đóng và thao tác responsive; không ghi User/Permission thật.','Prototype verifies responsive open/close and interaction; it does not persist real User/Permission data.')}</p>`,`<button class="btn" onclick="closeModal()">${tx('Hủy','Cancel')}</button><button class="btn primary" onclick="closeModal();toast('${tx('Đã kiểm tra luồng người dùng/phân quyền','User/permission flow verified')}')">${tx('Lưu','Save')}</button>`);
  }
  return _modalHtmlV14();
};

function fixCheckboxClicksV14(){
  document.querySelectorAll('input.check[onclick*="stopEvt"]').forEach(cb=>{
    cb.setAttribute('onclick','stopRowPropagation(event)');
  });
}

function enhanceResponsiveV14Dom(){
  fixCheckboxClicksV14();
  wirePrototypeButtonsV14();
  document.querySelectorAll('.status-interview,.status-report').forEach(el=>el.setAttribute('data-status-compact','true'));
}

/* Chain after v1.3 rendering. */
const _renderV14=render;
render=function(){ _renderV14(); enhanceResponsiveV14Dom(); };
const _renderPortalV14=renderPortal;
renderPortal=function(){ _renderPortalV14(); enhanceResponsiveV14Dom(); };

/* Visible version labels. */
const _loginPageResponsiveV14=loginPage;
loginPage=function(){return _loginPageResponsiveV14().replace(/Responsive rebuild v1\.3|Responsive prototype v1\.2|Clickable prototype v1\.1|Clickable prototype v1\.0/g,'Responsive UX-UAT v1.4');};

render();
