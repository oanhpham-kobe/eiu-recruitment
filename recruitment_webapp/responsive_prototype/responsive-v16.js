/* EIU Recruitment Responsive Prototype v1.6
   Alignment layer for Full Handover v1.10.
   Goals:
   - Candidate lifecycle is separate from Submission workflow.
   - Candidate-row status always derives from deterministic latest Submission.
   - Candidate-level bulk NEW/READ resolves latest Submission, all-or-nothing.
   - FUTURE_HIDDEN routes are not rendered in normal Phase-1 persona UAT.
   - Report Status belongs to Current Interview; Application outcome is derived.
   - Final Decision Source uses decisionUpdatedAt, not generic updatedAt.
   - Candidate EDIT uses staged CV ADD/REPLACE/DELETE and CV remains required.
*/
state.candidateFormMode = state.candidateFormMode || 'NEW';
state.candidateFormSubmissionId = state.candidateFormSubmissionId || null;
state.candidateFormError = null;
state.candidateDocStage = state.candidateDocStage || {cvAction:null,cvFileName:null,supporting:[]};
state.portalSubmissions = state.portalSubmissions || [
  {id:'ps1',date:'03/09/2026 06:30',status:'NEW',currentCv:{name:'CV_Nguyen_Thi_An.pdf'},documents:[{name:'Bang_tot_nghiep.pdf',type:'Degree'}]},
  {id:'ps2',date:'24/05/2026 10:32',status:'CLOSED',currentCv:{name:'CV_2026_05.pdf'},documents:[]},
  {id:'ps3',date:'22/05/2025 14:18',status:'DONE',currentCv:{name:'CV_2025.pdf'},documents:[]}
];

function parseViDateTimeV16(value){
  if(!value) return 0;
  const m=String(value).match(/(\d{1,2})\/(\d{1,2})\/(\d{4})(?:\s+(\d{1,2}):(\d{2}))?/);
  if(!m) return Date.parse(value)||0;
  return new Date(Number(m[3]),Number(m[2])-1,Number(m[1]),Number(m[4]||0),Number(m[5]||0)).getTime();
}
function latestSubmissionV16(c){
  return [...(c?.submissions||[])].sort((a,b)=>parseViDateTimeV16(b.date)-parseViDateTimeV16(a.date))[0]||null;
}
function applicationForSubmissionV16(submissionId){
  return state.applications.find(a=>a.submissionId===submissionId)||null;
}
function candidateHasBlockingApplicationV16(c){
  const latest=latestSubmissionV16(c);
  return !!(latest && applicationForSubmissionV16(latest.id));
}
function reportStatusV16(a){
  const r=currentRound(a);
  return r?.reportStatus || a.reportStatus || a.status || 'INTERVIEW_SCHEDULING';
}
function applicationOutcomeV16(a){
  const s=reportStatusV16(a);
  return s==='HIRED'?'HIRED':s==='REJECTED'?'REJECTED':'IN_PROGRESS';
}
function reportSourceV16(rid){
  const rs=state.reports[rid]||{};
  const arr=Object.entries(rs).filter(([_,r])=>r.conclusion||r.job||r.time);
  arr.sort((a,b)=>parseViDateTimeV16(b[1].decisionUpdatedAt||b[1].updatedAt)-parseViDateTimeV16(a[1].decisionUpdatedAt||a[1].updatedAt));
  return arr[0]||null;
}
function initializeV16State(){
  state.applications.forEach(a=>{
    const r=currentRound(a);
    if(r && !r.reportStatus) r.reportStatus=a.status;
    if(r && typeof r.visibleToInterviewers!=='boolean') r.visibleToInterviewers=true;
    const linked=state.candidates.flatMap(c=>c.submissions).find(s=>s.id===a.submissionId);
    if(linked && ['NEW','READ'].includes(linked.status)){
      linked.status = ['HIRED'].includes(reportStatusV16(a)) ? 'DONE' : ['REJECTED'].includes(reportStatusV16(a)) ? 'CLOSED' : 'PROCESSED';
    }
  });
  Object.values(state.reports).forEach(byUser=>Object.entries(byUser).forEach(([uid,rep])=>{
    if((rep.conclusion||rep.job||rep.time) && !rep.decisionUpdatedAt) rep.decisionUpdatedAt=rep.updatedAt||'';
    if((rep.conclusion||rep.job||rep.time) && !rep.decisionUpdatedBy) rep.decisionUpdatedBy=uid;
  }));
}
initializeV16State();

/* Only manual Submission statuses belong in the Candidate/Submission status menu. */
statusGroups.candidate=['NEW','READ'];

function submissionStatusBadgeV16(c){
  const s=latestSubmissionV16(c);
  if(!s) return '<span class="helper">–</span>';
  const editable=canEditStatus() && c.active && ['NEW','READ'].includes(s.status) && !applicationForSubmissionV16(s.id);
  return statusBadgeV11(s.status,'candidate',editable?'latest-submission':null,editable?c.id:null);
}
function candidateLifecycleV16(c){
  return c.active
    ? ''
    : `<span class="candidate-lifecycle inactive">${tx('Candidate Inactive','Candidate Inactive')}</span>`;
}

/* Phase-1 navigation registry only. FUTURE_HIDDEN routes never appear in normal persona UAT. */
refreshNavConfig = function(){
  navConfig.admin=[
    [tx('Quản lý tuyển dụng','Recruitment Management'),[['file',tx('Phiếu ứng tuyển','Applications'),'applications']]],
    [tx('Quản lý quy trình','Process Management'),[['calendar','Interview','interview'],['report',tx('Báo cáo phỏng vấn','Interview Reports'),'hr-report']]],
    [tx('Quản trị hệ thống','System Administration'),[['list',tx('Danh mục','Catalogs'),'placeholder'],['users',tx('Người dùng & Phân quyền','Users & Permissions'),'permissions']]]
  ];
  navConfig.hr=[
    [tx('Quản lý tuyển dụng','Recruitment Management'),[['file',tx('Phiếu ứng tuyển','Applications'),'applications']]],
    [tx('Quản lý quy trình','Process Management'),[['calendar','Interview','interview'],['report',tx('Báo cáo phỏng vấn','Interview Reports'),'hr-report']]],
    [tx('Quản trị','Administration'),[['list',tx('Danh mục','Catalogs'),'placeholder']]]
  ];
  navConfig.interviewer=[
    [tx('Phỏng vấn của tôi','My Interviews'),[['report',tx('Báo cáo phỏng vấn','Interview Reports'),'interviewer-report']]]
  ];
};
refreshNavConfig();

const _navV16=nav;
nav=function(page){
  const allowed={
    admin:new Set(['applications','interview','hr-report','permissions','placeholder']),
    hr:new Set(['applications','interview','hr-report','placeholder']),
    interviewer:new Set(['interviewer-report']),
    candidate:new Set(['candidate-applications','candidate-form'])
  };
  if(state.role && allowed[state.role] && !allowed[state.role].has(page)){
    page=state.role==='interviewer'?'interviewer-report':state.role==='candidate'?'candidate-applications':'applications';
  }
  _navV16(page);
};
if(state.role==='admin' && !['applications','interview','hr-report','permissions','placeholder'].includes(state.page)) state.page='applications';
if(state.role==='hr' && !['applications','interview','hr-report','placeholder'].includes(state.page)) state.page='applications';
if(state.role==='interviewer' && state.page!=='interviewer-report') state.page='interviewer-report';

candidateSidebar = function(){
  return `<aside class="sidebar responsive-sidebar ${state.mobileNavOpen?'open':''}" aria-label="${tx('Điều hướng ứng viên','Candidate navigation')}">
    <div class="mobile-nav-head"><div class="brand"><div class="brand-logo"><span class="brand-mark"><i></i><i></i><i></i><i></i></span><span>EIU</span></div><div class="brand-name">EIU Recruitment System</div></div><button class="mobile-nav-close" onclick="closeMobileNav()" aria-label="${tx('Đóng menu','Close menu')}">${icon('close')}</button></div>
    <div class="nav-scroll"><div class="nav-group"><div class="nav-label">${tx('Ứng viên','Candidate')}</div><button class="nav-item active" onclick="nav('candidate-applications')">${icon('file')} ${tx('Phiếu ứng tuyển','Applications')}</button></div></div>
    <div class="sidebar-user"><div class="avatar">NT</div><div><strong>Nguyễn Thị An</strong><span>${tx('Ứng viên','Candidate')}</span></div></div>
  </aside>`;
};

/* Candidate-level ALL_OR_NOTHING manual status command semantics for the prototype. */
function bulkSetLatestSubmissionStatusV16(status){
  if(!['NEW','READ'].includes(status)) return toast(tx('Chỉ được chọn Mới hoặc Đã đọc.','Only New or Read can be selected.'));
  if(!state.selectedIds.size) return toast(tx('Chọn ít nhất một ứng viên trước.','Select at least one candidate.'));
  const targets=[...state.selectedIds].map(id=>candidate(id));
  const invalid=targets.filter(c=>{
    const s=latestSubmissionV16(c);
    return !c || !c.active || !s || !!applicationForSubmissionV16(s.id);
  });
  if(invalid.length){
    const names=invalid.filter(Boolean).map(c=>c.name).join(', ');
    state.statusMenu=null;
    return toast(tx(`Không cập nhật: batch bị hủy toàn bộ vì Candidate không còn hợp lệ hoặc latest Submission đã có Application${names?`: ${names}`:''}.`,`No update: the entire batch was cancelled because a Candidate is no longer eligible or the latest Submission has an Application${names?`: ${names}`:''}.`));
  }
  targets.forEach(c=>{ latestSubmissionV16(c).status=status; });
  state.statusMenu=null;
  toast(tx(`Đã cập nhật ${targets.length} latest Submission theo chế độ all-or-nothing.`,`Updated ${targets.length} latest Submissions using all-or-nothing semantics.`));
  render();
}
const _setEntityStatusV16Base=setEntityStatus;
setEntityStatus=function(entity,id,status){
  if(entity==='bulk-latest-submission' || entity==='bulk-candidate') return bulkSetLatestSubmissionStatusV16(status);
  if(entity==='latest-submission' || entity==='candidate'){
    const c=candidate(id),s=latestSubmissionV16(c);
    if(!c || !c.active || !s || applicationForSubmissionV16(s.id) || !['NEW','READ'].includes(status)){
      state.statusMenu=null;
      return toast(tx('Latest Submission hiện không cho phép đổi thủ công.','The latest Submission is not currently eligible for a manual status change.'));
    }
    s.status=status; state.statusMenu=null; toast(tx('Đã cập nhật latest Submission.','Latest Submission updated.')); return render();
  }
  if(entity==='submission'){
    state.statusMenu=null;
    return toast(tx('Submission lịch sử chỉ đọc; chỉ latest Submission được đổi thủ công từ dòng Candidate.','Historical Submissions are read-only; only the latest Submission can be changed from the Candidate row.'));
  }
  if(entity==='report'){
    const a=appById(id),r=a&&currentRound(a);
    if(r){r.reportStatus=status;state.statusMenu=null;toast(tx('Đã cập nhật Report Status của Current Interview.','Current Interview Report Status updated.'));return render();}
  }
  if(entity==='bulk-report'){
    if(!state.selectedIds.size) return toast(tx('Chọn ít nhất một báo cáo trước.','Select at least one report.'));
    [...state.selectedIds].forEach(aid=>{const a=appById(aid),r=a&&currentRound(a);if(r)r.reportStatus=status;});
    state.statusMenu=null;toast(tx('Đã cập nhật Report Status; Application outcome không bị ghi trực tiếp.','Report Status updated; Application outcome was not written directly.'));return render();
  }
  return _setEntityStatusV16Base(entity,id,status);
};

/* Inactivation is a Candidate lifecycle mutation only. Reactivation recalculates eligible no-Application latest Submission to READ. */
toggleInactive=function(){
  if(!state.selectedIds.size) return toast(tx('Chọn ít nhất một ứng viên trước.','Select at least one candidate.'));
  [...state.selectedIds].forEach(id=>{
    const c=candidate(id); if(!c) return;
    if(c.active){ c.active=false; return; }
    c.active=true;
    const s=latestSubmissionV16(c);
    if(s && !applicationForSubmissionV16(s.id) && ['NEW','READ'].includes(s.status)) s.status='READ';
  });
  toast(tx('Đã cập nhật Candidate Active/Inactive; thao tác Inactive không ghi đè Submission status.','Candidate Active/Inactive updated; inactivation did not overwrite Submission status.'));
  render();
};

applicationsPage = function(){
  const rows=state.candidates.map(c=>{
    const ordered=[...(c.submissions||[])].sort((a,b)=>parseViDateTimeV16(b.date)-parseViDateTimeV16(a.date));
    const latest=ordered[0],open=state.expandedCandidate===c.id;
    let html=`<tr class="parent-row ${open?'expanded':''} ${c.active?'':'candidate-inactive-row'}" tabindex="0" onclick="handleCandidateRow('${c.id}',event)">
      <td class="control-cell"><input class="check" type="checkbox" ${state.selectedIds.has(c.id)?'checked':''} onclick="stopRowPropagation(event)" onchange="toggleSelect('${c.id}',this.checked)"></td>
      <td class="name-cell"><button class="expand-inline" onclick="stopEvt(event);toggleCandidate('${c.id}')" aria-expanded="${open?'true':'false'}">${ordered.length>1?`<span class="chevron ${open?'open':''}">›</span>`:''}<span><strong>${c.name}</strong><small>${ordered.length>1?tx(`${ordered.length} phiếu`,`${ordered.length} submissions`):tx('1 phiếu','1 submission')} ${candidateLifecycleV16(c)}</small></span></button></td>
      <td class="wrap-anywhere">${c.email}</td><td>${c.dob}</td><td>${c.gender}</td><td>${c.phone}</td>
      <td class="status-cell">${submissionStatusBadgeV16(c)}</td><td>${latest?.note||c.note||'–'}</td>
      <td class="action-cell"><button class="row-btn" onclick="stopEvt(event);openDrawer('candidate','${c.id}')" aria-label="${tx('Xem ứng viên','View candidate')}">${icon('eye')}</button></td></tr>`;
    if(open){
      html+=ordered.slice(1).map(s=>`<tr class="child-row submission-history-row" onclick="openDrawer('submission','${c.id}|${s.id}')"><td></td><td class="name-cell"><strong>${tx('Phiếu lịch sử','Historical submission')}</strong><span>${s.date}</span></td><td></td><td></td><td></td><td></td><td class="status-cell">${statusBadgeV11(s.status,'candidate')}</td><td>${s.note||'–'}</td><td class="action-cell">${icon('eye')}</td></tr>`).join('');
    }
    return html;
  }).join('');
  return shell(`<div class="content"><div class="toolbar"><div class="toolbar-left">
    <button class="btn primary" onclick="openModal('assignApplication')">${icon('plus')} ${tx('Ứng tuyển','Assign application')}</button>
    ${toolbarStatus('candidate','bulk-latest-submission')}
    <button class="btn" onclick="toggleInactive()">${tx('Active / Inactive','Active / Inactive')}</button>
    </div><div class="toolbar-right"><div class="searchbox"><input class="input" placeholder="${tx('Tìm tên, email, SĐT...','Search name, email, phone...')}">${icon('search')}</div><button class="btn responsive-filter-btn" onclick="openModal('responsiveFilters',{page:'applications'})">${icon('filter')} ${tx('Bộ lọc','Filters')}</button></div></div>
    <div class="table-card desktop-table-scroll responsive-table-shell"><table class="data-table applications-table">${colgroup([48,240,250,130,100,150,160,390,92])}<thead><tr><th></th><th>${tx('Tên','Name')}</th><th>Email</th><th>${tx('Ngày sinh','Date of birth')}</th><th>${tx('Giới tính','Gender')}</th><th>${tx('SĐT','Phone')}</th><th>${tx('Trạng thái phiếu','Submission status')}</th><th>HR Note</th><th>${tx('Thao tác','Action')}</th></tr></thead><tbody>${rows}</tbody></table>${pager(240)}</div></div>`,
    tx('Quản lý phiếu ứng tuyển','Application Inbox'),
    tx('Dòng Candidate lấy Status/HR Note từ latest Submission; Candidate Inactive là lifecycle riêng.','Candidate rows derive Status/HR Note from the latest Submission; Candidate Inactive is a separate lifecycle.'));
};

/* Report Status is stored on Current Interview. */
hrReportPage=function(){
  const rows=state.applications.map(a=>{const c=candidate(a.candidateId),r=currentRound(a);return `<tr class="click-row" onclick="if(!event.target.closest('button,input'))openDrawer('hrReport','${a.id}')">
    <td class="control-cell"><input class="check" type="checkbox" ${state.selectedIds.has(a.id)?'checked':''} onclick="stopRowPropagation(event)" onchange="toggleSelect('${a.id}',this.checked)"></td>
    <td class="name-cell"><strong>${c.name}</strong><span>${tx('Vòng','Round')} ${r.no}</span></td><td>${a.position}</td>
    <td class="interview-time-cell">${typeof interviewTimeV14==='function'?interviewTimeV14(r):`${r.date}<br>${r.start} – ${r.end}`}</td><td>${r.location}</td>
    <td class="status-cell">${statusBadgeV11(reportStatusV16(a),'report','report',a.id)}</td><td>${r.hrNote||r.note||'–'}</td>
    <td class="action-cell"><button class="row-btn" onclick="stopEvt(event);openDrawer('hrReport','${a.id}')" aria-label="${tx('Xem báo cáo','View report')}">${icon('eye')}</button></td></tr>`}).join('');
  return shell(`<div class="content"><div class="toolbar"><div class="toolbar-left">${toolbarStatus('report','bulk-report')}<button class="btn" onclick="openPrototypeEmailV14('report')">${icon('mail')} ${tx('Gửi thư','Email')}</button></div><div class="toolbar-right"><div class="searchbox"><input class="input" placeholder="${tx('Tìm kiếm...','Search...')}">${icon('search')}</div><button class="btn" onclick="openModal('responsiveFilters',{page:'report'})">${icon('filter')} ${tx('Bộ lọc','Filters')}</button></div></div>
    <div class="table-card desktop-table-scroll responsive-table-shell"><table class="data-table report-table">${colgroup([48,240,300,240,200,190,300,92])}<thead><tr><th></th><th>${tx('Họ và tên','Name')}</th><th>${tx('Vị trí','Position')}</th><th>${tx('Thời gian phỏng vấn','Interview time')}</th><th>${tx('Địa điểm','Location')}</th><th>${tx('Report Status','Report Status')}</th><th>${tx('HR Note','HR Note')}</th><th>${tx('Thao tác','Action')}</th></tr></thead><tbody>${rows}</tbody></table>${pager(48)}</div></div>`,
    tx('Báo cáo phỏng vấn (HR)','Interview Reports (HR)'),
    tx('Report Status thuộc Current Interview; Application outcome được derive riêng.','Report Status belongs to the Current Interview; Application outcome is derived separately.'));
};
interviewerPage=function(){
  const apps=state.applications.filter(a=>currentRound(a).participants.includes(state.currentInterviewer));
  const rows=apps.map(a=>{const c=candidate(a.candidateId),r=currentRound(a),own=state.reports[r.id]?.[state.currentInterviewer];return `<tr class="click-row" onclick="if(!event.target.closest('button,input'))openDrawer('interviewer','${a.id}')"><td class="name-cell"><strong>${c.name}</strong><span>${c.email}</span></td><td>${a.position}</td><td>${tx('Vòng','Round')} ${r.no}</td><td class="interview-time-cell">${typeof interviewTimeV14==='function'?interviewTimeV14(r):`${r.date}<br>${r.start} – ${r.end}`}</td><td class="status-cell">${statusBadgeV11(reportStatusV16(a),'report')}</td><td class="action-cell"><button class="row-btn" onclick="stopEvt(event);openDrawer('interviewer','${a.id}')">${icon('eye')}</button>${own?`<button class="row-btn" onclick="stopEvt(event);openDrawer('interviewer','${a.id}')">${icon('edit')}</button>`:''}</td></tr>`}).join('');
  return shell(`<div class="content"><div class="toolbar"><div class="toolbar-left"><button class="btn" onclick="toast('${tx('Đã đặt lại bộ lọc mẫu','Sample filters reset')}')">${tx('Đặt lại bộ lọc','Reset filters')}</button></div><div class="toolbar-right"><div class="searchbox"><input class="input" placeholder="${tx('Tìm kiếm theo họ tên, vị trí...','Search by name, position...')}">${icon('search')}</div><button class="btn" onclick="openModal('responsiveFilters',{page:'interviewer-report'})">${icon('filter')} ${tx('Bộ lọc','Filters')}</button></div></div><div class="table-card desktop-table-scroll responsive-table-shell"><table class="data-table interviewer-table">${colgroup([300,270,110,240,200,90])}<thead><tr><th>${tx('Họ và tên','Full name')}</th><th>${tx('Vị trí','Position')}</th><th>${tx('Vòng','Round')}</th><th>${tx('Thời gian phỏng vấn','Interview time')}</th><th>${tx('Report Status','Report Status')}</th><th>${tx('Thao tác','Actions')}</th></tr></thead><tbody>${rows}</tbody></table>${pager(apps.length)}</div></div>`,tx('Báo cáo phỏng vấn của tôi','My Interview Reports'),tx('Report Status là trạng thái Current Interview do HR quản lý.','Report Status is the Current Interview status managed by HR.'));
};

function toggleReportVisibilityV16(aid){
  const a=appById(aid),r=a&&currentRound(a);if(!r)return;
  r.visibleToInterviewers=!r.visibleToInterviewers;
  toast(r.visibleToInterviewers?tx('Đã hiển thị báo cáo với Interviewer.','Report is now visible to Interviewers.'):tx('Đã ẩn báo cáo khỏi Interviewer.','Report hidden from Interviewers.'));
  render();
}
function saveHrNoteV16(aid){
  const a=appById(aid),r=a&&currentRound(a);if(!r)return;
  r.hrNote=$('#hrNoteV16')?.value||'';
  closeModal();toast(tx('Đã lưu HR Note cho Current Interview.','HR Note saved for the Current Interview.'));render();
}

const _modalHtmlV16Base=modalHtml;
modalHtml=function(){
  if(state.modal?.type==='hrNoteV16'){
    const a=appById(state.modal.data?.appId),r=a&&currentRound(a);
    return modalFrame(tx('Chỉnh sửa HR Note','Edit HR Note'),`<div class="field"><label>HR Note</label><textarea id="hrNoteV16" class="textarea">${r?.hrNote||r?.note||''}</textarea></div><p class="helper">${tx('HR Note thuộc Current Interview và không thay đổi Final Decision Source.','HR Note belongs to the Current Interview and does not change the Final Decision Source.')}</p>`,`<button class="btn" onclick="closeModal()">${tx('Hủy','Cancel')}</button><button class="btn primary" onclick="saveHrNoteV16('${a?.id||''}')">${tx('Lưu','Save')}</button>`);
  }
  return _modalHtmlV16Base();
};

hrReportDrawer=function(aid){
  const a=appById(aid),r=currentRound(a),src=reportSourceV16(r.id);
  const visible=r.visibleToInterviewers!==false;
  return `<div class="backdrop" onclick="closeDrawer()"></div><aside class="drawer"><div class="drawer-head"><div class="drawer-title-row"><div><h2>${tx('Báo cáo phỏng vấn','Interview Report')}</h2><div class="drawer-sub">${tx('Current Interview','Current Interview')}: ${tx('Vòng','Round')} ${r.no}</div></div>${closeBtn()}</div>
    <div class="drawer-actions"><button class="btn" onclick="openModal('hrNoteV16',{appId:'${a.id}'})">${icon('edit')} ${tx('Edit HR Note','Edit HR Note')}</button>
    <button class="btn" data-status-key="${statusTriggerKeyV16('report',a.id,'report')}" onclick="openStatusMenu('report','${a.id}',event,'report')">${tx('Đổi Report Status','Change Report Status')} ${icon('chevron')}</button>
    <button class="btn" onclick="toggleReportVisibilityV16('${a.id}')">${icon('eye')} ${visible?tx('Ẩn khỏi Interviewer','Hide from Interviewer'):tx('Hiện với Interviewer','Show to Interviewer')}</button>
    <button class="btn" onclick="openModal('pdf',{appId:'${a.id}'})">${icon('eye')} ${tx('Xem PDF','View PDF')}</button>
    <button class="btn" data-prototype-only="true" onclick="openModal('pdf',{appId:'${a.id}'})">${icon('download')} ${tx('Tải PDF','Download PDF')}</button></div></div>
    <div class="drawer-body"><div class="section"><dl class="kv"><dt>Report Status</dt><dd>${statusBadgeV11(reportStatusV16(a),'report')}</dd><dt>${tx('Application outcome (derived)','Application outcome (derived)')}</dt><dd>${applicationOutcomeV16(a)}</dd><dt>HR</dt><dd>${a.hr}</dd><dt>HR Note</dt><dd>${r.hrNote||r.note||'–'}</dd><dt>${tx('Hiển thị với Interviewer','Visible to Interviewer')}</dt><dd>${visible?tx('Có','Yes'):tx('Không','No')}</dd><dt>${tx('Nguồn kết luận hiện hành','Current decision source')}</dt><dd>${src?state.users[src[0]]?.name||src[0]:tx('Chưa có','None')}</dd><dt>decisionUpdatedAt</dt><dd>${src?.[1]?.decisionUpdatedAt||'–'}</dd></dl></div>
    <div class="section"><div class="section-title">${tx('Báo cáo của Interviewer','Interviewer reports')}</div>${r.participants.map((uid,i)=>reportAccordion(r.id,uid,i)).join('')}</div>
    <div class="section"><div class="section-title">${tx('Kết luận hiện hành','Current conclusion')}</div>${src?`<div class="report-grid"><div class="label">${tx('Kết luận','Conclusion')}</div><div class="value">${src[1].conclusion||'–'}</div><div class="label">${tx('Dự kiến công việc cụ thể được phân công','Expected Specific Job Assigned')}</div><div class="value">${src[1].job||'–'}</div><div class="label">${tx('Thời gian dự kiến tuyển dụng','Expected Recruitment Time')}</div><div class="value">${src[1].time||'–'}</div></div>`:`<div class="helper">${tx('Chưa có kết luận từ Interviewer.','No interviewer conclusion yet.')}</div>`}</div></div></aside>`;
};
interviewerDrawer=function(aid){
  const a=appById(aid),r=currentRound(a),c=candidate(a.candidateId),uid=state.currentInterviewer,rep=state.reports[r.id]?.[uid];
  const editable=!['HIRED','REJECTED'].includes(reportStatusV16(a));
  return `<div class="backdrop" onclick="closeDrawer()"></div><aside class="drawer"><div class="drawer-head"><div class="drawer-title-row"><div><h2>${tx('Chi tiết phỏng vấn & Báo cáo','Interview & Report Details')}</h2><div class="drawer-sub">${c.name} · ${tx('Vòng','Round')} ${r.no}</div></div>${closeBtn()}</div><div class="drawer-actions">${editable?`<button class="btn primary" onclick="openModal('editOwnReport',{appId:'${a.id}'})">${icon(rep?'edit':'report')} ${rep?tx('Edit','Edit'):tx('Báo cáo PV','Interview Report')}</button>`:''}<button class="btn" onclick="openModal('pdf',{appId:'${a.id}'})">${icon('eye')} ${tx('Xem','View')}</button></div></div><div class="drawer-body"><div class="section"><dl class="kv"><dt>Report Status</dt><dd>${statusBadgeV11(reportStatusV16(a),'report')}</dd><dt>${tx('Họ tên','Full name')}</dt><dd>${c.name}</dd><dt>Email</dt><dd>${c.email}</dd><dt>${tx('Vị trí','Position')}</dt><dd>${a.position}</dd><dt>${tx('Thời gian','Time')}</dt><dd>${r.date} · ${r.start} – ${r.end}</dd></dl></div><div class="section"><div class="section-title">${tx('Thông tin báo cáo của tôi','My report information')}</div>${rep?`<div class="report-grid"><div class="label">${tx('Kiến thức chuyên môn','Professional Knowledge')}</div><div>${rep.knowledge||'–'}</div><div class="label">${tx('Kết luận','Conclusion')}</div><div>${rep.conclusion||'–'}</div><div class="label">decisionUpdatedAt</div><div>${rep.decisionUpdatedAt||'–'}</div></div>`:`<div class="helper">${tx('Chưa nhập báo cáo.','No report entered.')}</div>`}</div></div></aside>`;
};

saveReport=function(rid,uid){
  state.reports[rid]=state.reports[rid]||{};
  const old=state.reports[rid][uid]||{};
  const next={
    ...old,
    knowledge:$('#repKnowledge').value,skills:$('#repSkills').value,qualities:$('#repQualities').value,
    strengths:$('#repStrengths').value,other:$('#repOther').value,
    conclusion:$('#repConclusion').value,job:$('#repJob').value,time:$('#repTime').value,
    updatedAt:new Date().toLocaleString('vi-VN')
  };
  const decisionChanged=['conclusion','job','time'].some(k=>(old[k]||'')!==(next[k]||''));
  if(decisionChanged){
    next.decisionUpdatedAt=next.updatedAt;
    next.decisionUpdatedBy=uid;
  }else{
    next.decisionUpdatedAt=old.decisionUpdatedAt||((old.conclusion||old.job||old.time)?old.updatedAt:'');
    next.decisionUpdatedBy=old.decisionUpdatedBy||((old.conclusion||old.job||old.time)?uid:'');
  }
  state.reports[rid][uid]=next;
  closeModal();toast(tx('Đã lưu báo cáo; qualitative-only edit không đổi Final Decision Source.','Report saved; qualitative-only edits do not change the Final Decision Source.'));render();
};
pdfModal=function(aid){
  const a=appById(aid),r=currentRound(a),src=reportSourceV16(r.id);
  return modalFrame(`${tx('Preview Báo cáo phỏng vấn','Interview Report Preview')} — ${tx('Vòng','Round')} ${r.no}`,`<div style="border:1px solid var(--line);padding:22px;background:#fff;min-height:420px"><div style="text-align:center"><b style="color:#144069">EASTERN INTERNATIONAL UNIVERSITY</b><h3 style="margin:12px 0">${tx('BÁO CÁO PHỎNG VẤN TUYỂN DỤNG','RECRUITMENT INTERVIEW REPORT')}</h3><div class="small">${candidate(a.candidateId).name} — ${a.position}</div></div><hr style="border:0;border-top:1px solid var(--line);margin:18px 0">${r.participants.map((uid,i)=>{const u=state.users[uid],rep=state.reports[r.id]?.[uid]||{};return `<div style="margin:16px 0"><b>${tx('Cán bộ phỏng vấn','Interviewer')} ${i+1}: ${u.name}</b><div class="small muted">${u.title}</div><div class="report-grid" style="margin-top:10px"><div class="label">${tx('Kiến thức chuyên môn','Professional Knowledge')}</div><div>${rep.knowledge||'________________________________'}</div><div class="label">${tx('Kỹ năng cần thiết','Necessary Skills')}</div><div>${rep.skills||'________________________________'}</div></div></div>`}).join('')}<hr style="border:0;border-top:1px solid var(--line);margin:18px 0"><b>${tx('Kết luận hiện hành','Current conclusion')}</b><div class="report-grid" style="margin-top:10px"><div class="label">${tx('Kết luận','Conclusion')}</div><div>${src?.[1]?.conclusion||'________________________________'}</div><div class="label">${tx('Dự kiến công việc','Expected job')}</div><div>${src?.[1]?.job||'________________________________'}</div><div class="label">${tx('Thời gian dự kiến tuyển dụng','Expected recruitment time')}</div><div>${src?.[1]?.time||'________________________________'}</div><div class="label">decisionUpdatedAt</div><div>${src?.[1]?.decisionUpdatedAt||'–'}</div></div></div>`,`<button class="btn" onclick="closeModal()">${tx('Đóng','Close')}</button>`);
};

/* Candidate portal: explicit NEW/EDIT with staged documents. */
function resetCandidateDocStageV16(){
  state.candidateDocStage={cvAction:null,cvFileName:null,supporting:[]};
  state.candidateFormError=null;
}
function openCandidateFormV16(mode='NEW',submissionId=null){
  state.candidateFormMode=mode;
  state.candidateFormSubmissionId=submissionId;
  resetCandidateDocStageV16();
  nav('candidate-form');
}
function cancelCandidateFormV16(){
  resetCandidateDocStageV16();
  state.candidateFormMode='NEW';state.candidateFormSubmissionId=null;
  nav('candidate-applications');
}
function currentPortalSubmissionV16(){
  return state.portalSubmissions.find(s=>s.id===state.candidateFormSubmissionId)||null;
}
function stageCvV16(input){
  const file=input?.files?.[0];if(!file)return;
  const current=currentPortalSubmissionV16()?.currentCv;
  state.candidateDocStage.cvAction=current?'REPLACE':'ADD';
  state.candidateDocStage.cvFileName=file.name;
  state.candidateFormError=null;
  render();
}
function stageDeleteCvV16(){
  if(!currentPortalSubmissionV16()?.currentCv)return;
  state.candidateDocStage.cvAction='DELETE';
  state.candidateDocStage.cvFileName=null;
  render();
}
function stageSupportingV16(input){
  state.candidateDocStage.supporting=[...(input?.files||[])].map(f=>f.name);
  render();
}
function candidateCvIsValidV16(){
  const current=currentPortalSubmissionV16()?.currentCv;
  const action=state.candidateDocStage.cvAction;
  return !!((current && action!=='DELETE') || (['ADD','REPLACE'].includes(action) && state.candidateDocStage.cvFileName));
}
function submitCandidateFormV16(event){
  event.preventDefault();
  const form=event.currentTarget;
  if(!form.checkValidity()){form.reportValidity();return;}
  if(!candidateCvIsValidV16()){
    state.candidateFormError='CV_REQUIRED';render();
    requestAnimationFrame(()=>document.getElementById('candidateCvV16')?.focus());
    return;
  }
  const edit=currentPortalSubmissionV16();
  if(state.candidateFormMode==='EDIT' && (!edit || edit.status!=='NEW')){
    state.candidateFormError='STALE';render();return;
  }
  if(state.candidateFormMode==='EDIT'){
    if(['ADD','REPLACE'].includes(state.candidateDocStage.cvAction)) edit.currentCv={name:state.candidateDocStage.cvFileName};
    if(state.candidateDocStage.cvAction==='DELETE') edit.currentCv=null;
    if(state.candidateDocStage.supporting.length) edit.documents.push(...state.candidateDocStage.supporting.map(name=>({name,type:'Other'})));
  }else{
    state.portalSubmissions.unshift({id:'ps'+Date.now(),date:new Date().toLocaleString('vi-VN'),status:'NEW',currentCv:{name:state.candidateDocStage.cvFileName},documents:state.candidateDocStage.supporting.map(name=>({name,type:'Other'}))});
  }
  resetCandidateDocStageV16();
  toast(state.candidateFormMode==='EDIT'?tx('Đã lưu thay đổi staged atomically.','Staged changes saved atomically.'):tx('Đã gửi phiếu ứng tuyển mẫu.','Sample application submitted.'));
  state.candidateFormMode='NEW';state.candidateFormSubmissionId=null;nav('candidate-applications');
}
candidateApplications=function(){
  const submissions=state.portalSubmissions;
  const mobileCards=submissions.map((s,i)=>`<article class="candidate-submission-card" onclick="openDrawer('candidateOwn','c1')"><div class="submission-card-top"><div><div class="submission-index">${tx('Phiếu','Application')} ${i+1}</div><strong>${s.date}</strong></div>${statusBadgeV11(s.status,'candidate')}</div><div class="submission-card-actions">${s.status==='NEW'?`<button class="btn" onclick="stopEvt(event);openCandidateFormV16('EDIT','${s.id}')">${icon('edit')} ${tx('Chỉnh sửa','Edit')}</button>`:''}<button class="btn primary" onclick="stopEvt(event);openDrawer('candidateOwn','c1')">${icon('eye')} ${tx('Xem','View')}</button></div></article>`).join('');
  const desktopRows=submissions.map((s,i)=>`<tr class="click-row" onclick="if(!event.target.closest('button'))openDrawer('candidateOwn','c1')"><td>${i+1}</td><td>${s.date}</td><td class="status-cell">${statusBadgeV11(s.status,'candidate')}</td><td class="action-cell">${s.status==='NEW'?`<button class="row-btn" onclick="stopEvt(event);openCandidateFormV16('EDIT','${s.id}')" aria-label="${tx('Chỉnh sửa','Edit')}">${icon('edit')}</button>`:''}<button class="row-btn" onclick="stopEvt(event);openDrawer('candidateOwn','c1')">${icon('eye')}</button></td></tr>`).join('');
  return `<div class="candidate-shell responsive-candidate-shell ${state.mobileNavOpen?'nav-open':''}">${candidateSidebar()}${mobileNavBackdrop()}<main class="candidate-content">${candidateMobileHeader(tx('Phiếu ứng tuyển','Applications'),tx('Quản lý các phiếu ứng tuyển của bạn','Manage your submitted applications'))}<div class="candidate-actions"><button class="btn primary" onclick="openCandidateFormV16('NEW')">${icon('plus')} ${tx('Tạo phiếu mới','New application')}</button><button class="btn">${icon('file')} ${tx('Phiếu của tôi','My applications')}</button></div><div class="candidate-mobile-list">${mobileCards}</div><div class="candidate-card desktop-table-scroll candidate-desktop-table"><table class="data-table candidate-table">${colgroup([64,220,180,180])}<thead><tr><th>STT</th><th>${tx('Ngày ứng tuyển','Submitted at')}</th><th>${tx('Trạng thái','Status')}</th><th>${tx('Thao tác','Actions')}</th></tr></thead><tbody>${desktopRows}</tbody></table>${pager(submissions.length)}</div></main><div class="prototype-tag">Responsive UX-UAT v1.6</div></div>`;
};
candidateForm=function(){
  const edit=state.candidateFormMode==='EDIT',current=currentPortalSubmissionV16();
  const stage=state.candidateDocStage;
  const error=state.candidateFormError==='CV_REQUIRED'?`<div class="candidate-error-summary" role="alert">${tx('CV là bắt buộc. Giữ CV hiện tại hoặc staged ADD/REPLACE một CV hợp lệ trước khi lưu.','CV is required. Keep the current CV or stage a valid ADD/REPLACE before saving.')}</div>`:state.candidateFormError==='STALE'?`<div class="candidate-error-summary" role="alert">${tx('Phiếu không còn ở trạng thái NEW. Save bị chặn; vui lòng tải lại trạng thái hiện tại.','The Submission is no longer NEW. Save is blocked; reload the current state.')}</div>`:'';
  const currentCv=current?.currentCv;
  const stagedText=stage.cvAction?`${stage.cvAction}${stage.cvFileName?`: ${stage.cvFileName}`:''}`:tx('Chưa có thay đổi staged','No staged change');
  return `<div class="candidate-shell responsive-candidate-shell ${state.mobileNavOpen?'nav-open':''}">${candidateSidebar()}${mobileNavBackdrop()}<main class="candidate-content candidate-form-page">${candidateMobileHeader(edit?tx('Chỉnh sửa phiếu','Edit Application'):tx('Đăng ký mới','New Application'),edit?tx('Document thay đổi theo staged ADD / REPLACE / DELETE; Save mới materialize.','Documents use staged ADD / REPLACE / DELETE; Save materializes the changes.'):tx('CV là bắt buộc trước khi gửi.','CV is required before submission.'),true)}${error}<form class="candidate-form" onsubmit="submitCandidateFormV16(event)">
    <div class="form-section"><h3>01 · ${tx('THÔNG TIN CHUNG','GENERAL INFORMATION')}</h3><div class="form-grid"><div class="field"><label>${tx('Họ tên','Full name')} *</label><input class="input" value="Nguyễn Thị An" required></div><div class="field"><label>Email</label><input class="input" value="candidate@gmail.com" readonly></div><div class="field"><label>${tx('Ngày sinh','Date of birth')} *</label><input class="input" type="date" value="1995-08-15" required></div><div class="field"><label>${tx('Giới tính','Gender')} *</label><select class="select" required><option>${tx('Nữ','Female')}</option><option>${tx('Nam','Male')}</option></select></div><div class="field"><label>${tx('Số điện thoại','Phone')} *</label><input class="input" value="0901 234 567" required></div><div class="field wide"><label>${tx('Địa chỉ hiện tại','Current address')} *</label><input class="input" value="TP. Hồ Chí Minh" required></div></div></div>
    <div class="form-section"><h3>02 · ${tx('QUÁ TRÌNH HỌC TẬP','EDUCATION')}</h3><div class="repeat-item"><div class="form-grid"><div class="field"><label>${tx('Thời gian','Period')} *</label><input class="input" value="2018 – 2022" required></div><div class="field"><label>${tx('Học vấn','Qualification')} *</label><select class="select" required><option>${tx('Cử nhân','Bachelor')}</option><option>${tx('Thạc sĩ','Master')}</option></select></div><div class="field"><label>${tx('Chuyên ngành','Major')} *</label><input class="input" value="Quản trị kinh doanh" required></div><div class="field"><label>${tx('Trường','Institution')} *</label><input class="input" value="Eastern International University" required></div></div></div></div>
    <div class="form-section"><h3>03 · ${tx('HỒ SƠ ĐÍNH KÈM','ATTACHMENTS')}</h3><p class="helper">${tx('CV bắt buộc. EDIT không ghi file ngay: ADD/REPLACE/DELETE chỉ materialize khi Save; Cancel bỏ toàn bộ staged changes.','CV required. EDIT does not write files immediately: ADD/REPLACE/DELETE materialize only on Save; Cancel discards all staged changes.')}</p>
      ${edit?`<div class="current-doc-box"><strong>${tx('CV hiện tại','Current CV')}</strong><div class="staged-doc-row"><span>${currentCv?.name||tx('Không có CV hiện tại','No current CV')}</span>${currentCv?`<button type="button" class="btn danger" onclick="stageDeleteCvV16()">${tx('Stage DELETE','Stage DELETE')}</button>`:''}</div></div>`:''}
      <div class="mobile-upload-stack"><label class="upload-tile"><span class="upload-icon">${icon('file')}</span><span><strong>${edit?tx('ADD / REPLACE CV','ADD / REPLACE CV'):'CV *'}</strong><small>${tx('Chọn file từ thiết bị','Choose a file from device')}</small></span><input id="candidateCvV16" type="file" accept=".pdf,.doc,.docx" onchange="stageCvV16(this)"></label>
      <label class="upload-tile"><span class="upload-icon">${icon('file')}</span><span><strong>${tx('Tài liệu hỗ trợ — staged ADD','Supporting documents — staged ADD')}</strong><small>${tx('Có thể chọn nhiều file','Multiple files allowed')}</small></span><input type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg" onchange="stageSupportingV16(this)"></label></div>
      <div class="pending-upload-note"><b>${tx('Staged CV','Staged CV')}:</b> ${stagedText}${stage.supporting.length?`<br><b>${tx('Staged supporting','Staged supporting')}:</b> ${stage.supporting.join(', ')}`:''}</div>
    </div>
    <div class="form-section privacy-section"><label class="privacy-check"><input id="privacyAck" type="checkbox" checked required><span>${tx('Tôi xác nhận đã đọc và đồng ý với thông báo quyền riêng tư.','I acknowledge the privacy notice.')} *</span></label></div>
    <div class="candidate-form-actions"><button type="button" class="btn" onclick="cancelCandidateFormV16()">${tx('Hủy','Cancel')}</button><button class="btn primary" type="submit">${edit?tx('Lưu','Save'):tx('Gửi phiếu','Submit')}</button></div>
    </form></main><div class="prototype-tag">Responsive UX-UAT v1.6</div></div>`;
};


/* v1.6 portal-safe status anchoring.
   Drawer/modal renderPortal() replaces the trigger DOM node, so reconnect by a deterministic status key. */
function statusTriggerKeyV16(entity,id,group){
  return `${entity}|${id||''}|${statusMenuGroupV15(entity,group)}`;
}
statusBadgeV11=function(s,group='general',entity=null,id=null){
  const clickable=!!entity&&canEditStatus();
  const key=clickable?statusTriggerKeyV16(entity,id,null):'';
  return `<${clickable?'button':'span'} class="status status-${group} ${statusClass(s)} ${clickable?'status-clickable':''}" ${clickable?`data-status-key="${key}" onclick="openStatusMenu('${entity}','${id}',event)" aria-label="${tx('Đổi trạng thái','Change status')}" aria-haspopup="menu" aria-expanded="false"`:''}>${statusText(s)}</${clickable?'button':'span'}>`;
};
toolbarStatus=function(group,entity){
  const key=statusTriggerKeyV16(entity,'',group);
  return `<button class="btn" data-status-key="${key}" onclick="openStatusMenu('${entity}','',event,'${group}')" aria-haspopup="menu" aria-expanded="false">${tx('Status','Status')} ${icon('chevron')}</button>`;
};
openStatusMenu=function(entity,id,e,group=null){
  if(e){e.preventDefault();e.stopPropagation();}
  const g=statusMenuGroupV15(entity,group);
  const key=statusTriggerKeyV16(entity,id,g);
  const current=state.statusMenu?statusTriggerKeyV16(state.statusMenu.entity,state.statusMenu.id,state.statusMenu.group):null;
  const original=e?.currentTarget||null;
  if(state.statusMenu && current===key){
    closeStatusMenuV15({restoreFocus:false});
    return;
  }
  clearStatusTriggerStateV15();
  statusMenuTriggerV15=original;
  if(original){
    original.setAttribute('data-status-key',key);
    original.setAttribute('aria-haspopup','menu');
    original.setAttribute('aria-expanded','true');
  }
  state.statusMenu={entity,id,group:g};
  renderPortal();
  requestAnimationFrame(()=>{
    const escaped=window.CSS&&CSS.escape?CSS.escape(key):key.replace(/"/g,'\\"');
    const replacement=document.querySelector(`[data-status-key="${escaped}"]`);
    if(replacement){
      statusMenuTriggerV15=replacement;
      replacement.setAttribute('aria-haspopup','menu');
      replacement.setAttribute('aria-expanded','true');
    }
    positionStatusMenuV15();
    const first=document.querySelector('.status-popover [role="menuitem"]');
    if(first) first.focus({preventScroll:true});
  });
};

/* v1.6 candidate submit authority.
   responsive-v13 intentionally rebinds form.onsubmit after each render, so its
   handler must delegate to the v1.6 NEW/EDIT transaction instead of the old
   sample-submit/toast path. */
handleCandidateResponsiveSubmit=function(event){
  event.preventDefault();
  const form=event.currentTarget;
  const ack=form.querySelector('#privacyAck');
  const err=form.querySelector('#privacyError');
  if(ack && !ack.checked){
    if(err){
      err.hidden=false;
      err.textContent=tx('Vui lòng xác nhận thông báo quyền riêng tư trước khi gửi phiếu.','Please acknowledge the privacy notice before submitting.');
    }
    ack.setAttribute('aria-invalid','true');
    ack.focus();
    return false;
  }
  if(ack){
    ack.removeAttribute('aria-invalid');
    if(err){err.hidden=true;err.textContent='';}
  }
  submitCandidateFormV16(event);
  return false;
};

/* Visible version labels. */
const _shellV16=shell;
shell=function(content,title,sub=''){return _shellV16(content,title,sub).replace(/Responsive UX-UAT v1\.[0-5]|Responsive rebuild v1\.3/g,'Responsive UX-UAT v1.6');};
const _loginPageV16=loginPage;
loginPage=function(){return _loginPageV16().replace(/Responsive UX-UAT v1\.[0-5]|Responsive rebuild v1\.3|Responsive prototype v1\.2|Clickable prototype v1\.[01]/g,'Responsive UX-UAT v1.6');};

render();
