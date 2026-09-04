/* Responsive Prototype v1.7 — External Review v8 alignment.
   Supersedes only the targeted v1.6 semantics below; retained v1.5/v1.6 interaction behavior remains authoritative elsewhere. */

function submissionStatusBadgeV17(c){
  const s=latestSubmissionV16(c);
  if(!s) return '<span class="helper">–</span>';
  // Candidate lifecycle is independent: inactive portal access does not block internal HR NEW/READ.
  const editable=canEditStatus() && ['NEW','READ'].includes(s.status) && !applicationForSubmissionV16(s.id);
  return statusBadgeV11(s.status,'candidate',editable?'latest-submission':null,editable?c.id:null);
}
submissionStatusBadgeV16=submissionStatusBadgeV17;

function bulkSetLatestSubmissionStatusV17(status){
  if(!['NEW','READ'].includes(status)) return toast(tx('Chỉ được chọn Mới hoặc Đã đọc.','Only New or Read can be selected.'));
  if(!state.selectedIds.size) return toast(tx('Chọn ít nhất một ứng viên trước.','Select at least one candidate.'));
  const targets=[...state.selectedIds].map(id=>candidate(id));
  const invalid=targets.filter(c=>{
    const s=c&&latestSubmissionV16(c);
    return !c || !s || !!applicationForSubmissionV16(s.id);
  });
  if(invalid.length){
    const names=invalid.filter(Boolean).map(c=>c.name).join(', ');
    state.statusMenu=null;
    return toast(tx(`Không cập nhật: batch bị hủy toàn bộ vì latest Submission không hợp lệ hoặc đã có Application${names?`: ${names}`:''}.`,`No update: the entire batch was cancelled because a latest Submission is invalid or already has an Application${names?`: ${names}`:''}.`));
  }
  targets.forEach(c=>{latestSubmissionV16(c).status=status;});
  state.statusMenu=null;
  toast(tx(`Đã cập nhật ${targets.length} latest Submission; Candidate Inactive không tạo rule riêng.`,`Updated ${targets.length} latest Submissions; Candidate Inactive does not create a separate rule.`));
  render();
}
bulkSetLatestSubmissionStatusV16=bulkSetLatestSubmissionStatusV17;

const _setEntityStatusV17Base=setEntityStatus;
setEntityStatus=function(entity,id,status){
  if(entity==='bulk-latest-submission' || entity==='bulk-candidate') return bulkSetLatestSubmissionStatusV17(status);
  if(entity==='latest-submission' || entity==='candidate'){
    const c=candidate(id),s=c&&latestSubmissionV16(c);
    if(!c || !s || applicationForSubmissionV16(s.id) || !['NEW','READ'].includes(status)){
      state.statusMenu=null;
      return toast(tx('Latest Submission hiện không cho phép đổi thủ công.','The latest Submission is not currently eligible for a manual status change.'));
    }
    s.status=status; state.statusMenu=null;
    toast(tx('Đã cập nhật latest Submission; Candidate lifecycle không bị thay đổi.','Latest Submission updated; Candidate lifecycle was not changed.'));
    return render();
  }
  return _setEntityStatusV17Base(entity,id,status);
};

function resetEducationV17(){
  state.candidateEducationRowsV17=[{period:'2018 – 2022',qualification:'Cử nhân',major:'Quản trị kinh doanh',school:'Eastern International University'}];
}
function addEducationV17(){
  state.candidateEducationRowsV17=state.candidateEducationRowsV17||[];
  state.candidateEducationRowsV17.push({period:'',qualification:'',major:'',school:''});
  render();
}
function removeEducationV17(index){
  state.candidateEducationRowsV17=state.candidateEducationRowsV17||[];
  state.candidateEducationRowsV17.splice(index,1);
  render();
}
const _openCandidateFormV17Base=openCandidateFormV16;
openCandidateFormV16=function(mode='NEW',submissionId=null){
  resetEducationV17();
  // NEW must require an explicit action; EDIT demo represents the same pinned notice already acknowledged.
  state.candidatePrivacyAckV17=(mode==='EDIT');
  return _openCandidateFormV17Base(mode,submissionId);
};

function educationRowsV17(){
  const rows=state.candidateEducationRowsV17||[];
  if(!rows.length) return `<div class="helper education-empty">${tx('Chưa có quá trình học tập. Có thể thêm nếu cần.','No education row yet. Add one if needed.')}</div>`;
  return rows.map((row,i)=>`<div class="repeat-item education-row-v17" data-education-index="${i}"><div class="repeat-item-head"><strong>${tx('Học vấn','Education')} ${i+1}</strong><button type="button" class="row-btn" onclick="removeEducationV17(${i})" aria-label="${tx('Xóa mục học vấn','Remove education row')}">${icon('trash')}</button></div><div class="form-grid"><div class="field"><label>${tx('Thời gian','Period')}</label><input class="input" value="${row.period||''}"></div><div class="field"><label>${tx('Học vấn','Qualification')}</label><select class="select"><option value="">${tx('Chọn nếu có','Select if applicable')}</option><option ${row.qualification==='Cử nhân'?'selected':''}>${tx('Cử nhân','Bachelor')}</option><option ${row.qualification==='Thạc sĩ'?'selected':''}>${tx('Thạc sĩ','Master')}</option></select></div><div class="field"><label>${tx('Chuyên ngành','Major')}</label><input class="input" value="${row.major||''}"></div><div class="field"><label>${tx('Trường','Institution')}</label><input class="input" value="${row.school||''}"></div></div></div>`).join('');
}

candidateForm=function(){
  const edit=state.candidateFormMode==='EDIT',current=currentPortalSubmissionV16();
  const stage=state.candidateDocStage;
  const error=state.candidateFormError==='CV_REQUIRED'?`<div class="candidate-error-summary" role="alert">${tx('CV là bắt buộc. Giữ CV hiện tại hoặc staged ADD/REPLACE một CV hợp lệ trước khi lưu.','CV is required. Keep the current CV or stage a valid ADD/REPLACE before saving.')}</div>`:state.candidateFormError==='STALE'?`<div class="candidate-error-summary" role="alert">${tx('Phiếu không còn ở trạng thái NEW. Save bị chặn; vui lòng tải lại trạng thái hiện tại.','The Submission is no longer NEW. Save is blocked; reload the current state.')}</div>`:'';
  const currentCv=current?.currentCv;
  const stagedText=stage.cvAction?`${stage.cvAction}${stage.cvFileName?`: ${stage.cvFileName}`:''}`:tx('Chưa có thay đổi staged','No staged change');
  const privacyChecked=state.candidatePrivacyAckV17?'checked':''; // NEW starts false; EDIT same-version demo starts satisfied.
  return `<div class="candidate-shell responsive-candidate-shell ${state.mobileNavOpen?'nav-open':''}">${candidateSidebar()}${mobileNavBackdrop()}<main class="candidate-content candidate-form-page">${candidateMobileHeader(edit?tx('Chỉnh sửa phiếu','Edit Application'):tx('Đăng ký mới','New Application'),edit?tx('Document thay đổi theo staged ADD / REPLACE / DELETE; Save mới materialize.','Documents use staged ADD / REPLACE / DELETE; Save materializes the changes.'):tx('CV và xác nhận quyền riêng tư là bắt buộc trước khi gửi.','CV and privacy acknowledgement are required before submission.'),true)}${error}<form class="candidate-form" onsubmit="submitCandidateFormV16(event)">
    <div class="form-section"><h3>01 · ${tx('THÔNG TIN CHUNG','GENERAL INFORMATION')}</h3><div class="form-grid"><div class="field"><label>${tx('Họ tên','Full name')} *</label><input class="input" value="Nguyễn Thị An" required></div><div class="field"><label>Email</label><input class="input" value="candidate@gmail.com" readonly></div><div class="field"><label>${tx('Ngày sinh','Date of birth')} *</label><input class="input" type="date" value="1995-08-15" required></div><div class="field"><label>${tx('Giới tính','Gender')} *</label><select class="select" required><option>${tx('Nữ','Female')}</option><option>${tx('Nam','Male')}</option></select></div><div class="field"><label>${tx('Số điện thoại','Phone')} *</label><input class="input" value="0901 234 567" required></div><div class="field wide"><label>${tx('Địa chỉ hiện tại','Current address')} *</label><input class="input" value="TP. Hồ Chí Minh" required></div></div></div>
    <div class="form-section"><div class="section-head-row"><div><h3>02 · ${tx('QUÁ TRÌNH HỌC TẬP','EDUCATION')}</h3><p class="helper">${tx('Phase 1 chưa bắt buộc Education; có thể để trống hoặc thêm nhiều dòng.','Education is not required in the current Phase 1 contract; leave empty or add multiple rows.')}</p></div><button type="button" class="btn compact-add" onclick="addEducationV17()">${icon('plus')} ${tx('Thêm','Add')}</button></div>${educationRowsV17()}</div>
    <div class="form-section"><h3>03 · ${tx('HỒ SƠ ĐÍNH KÈM','ATTACHMENTS')}</h3><p class="helper">${tx('CV bắt buộc. EDIT không ghi file ngay: ADD/REPLACE/DELETE chỉ materialize khi Save; Cancel bỏ toàn bộ staged changes.','CV required. EDIT does not write files immediately: ADD/REPLACE/DELETE materialize only on Save; Cancel discards all staged changes.')}</p>
      ${edit?`<div class="current-doc-box"><strong>${tx('CV hiện tại','Current CV')}</strong><div class="staged-doc-row"><span>${currentCv?.name||tx('Không có CV hiện tại','No current CV')}</span>${currentCv?`<button type="button" class="btn danger" onclick="stageDeleteCvV16()">${tx('Stage DELETE','Stage DELETE')}</button>`:''}</div></div>`:''}
      <div class="mobile-upload-stack"><label class="upload-tile"><span class="upload-icon">${icon('file')}</span><span><strong>${edit?tx('ADD / REPLACE CV','ADD / REPLACE CV'):'CV *'}</strong><small>${tx('Chọn file từ thiết bị','Choose a file from device')}</small></span><input id="candidateCvV16" type="file" accept=".pdf,.doc,.docx" onchange="stageCvV16(this)"></label>
      <label class="upload-tile"><span class="upload-icon">${icon('file')}</span><span><strong>${tx('Tài liệu hỗ trợ — staged ADD','Supporting documents — staged ADD')}</strong><small>${tx('Có thể chọn nhiều file','Multiple files allowed')}</small></span><input type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg" onchange="stageSupportingV16(this)"></label></div>
      <div class="pending-upload-note"><b>${tx('Staged CV','Staged CV')}:</b> ${stagedText}${stage.supporting.length?`<br><b>${tx('Staged supporting','Staged supporting')}:</b> ${stage.supporting.join(', ')}`:''}</div>
    </div>
    <div class="form-section privacy-section"><div class="privacy-title-row"><div><h3>04 · ${tx('XÁC NHẬN QUYỀN RIÊNG TƯ','PRIVACY ACKNOWLEDGEMENT')}</h3><div class="privacy-version">${tx('Phiên bản thông báo','Notice version')}: EIU-REC-2026-09</div></div>${icon('lock')}</div><p class="helper">${tx('Đây là xác nhận duy nhất của Phase 1; không có checkbox xác nhận độ chính xác riêng.','This is the only Phase 1 acknowledgement; there is no separate accuracy-attestation checkbox.')}</p><label class="privacy-check"><input id="privacyAck" type="checkbox" ${privacyChecked} onchange="state.candidatePrivacyAckV17=this.checked" required><span>${tx('Tôi xác nhận đã đọc và đồng ý với thông báo quyền riêng tư.','I acknowledge that I have read and agree to the privacy notice.')} *</span></label><div id="privacyError" class="field-error" hidden></div></div>
    <div class="candidate-form-actions"><button type="button" class="btn" onclick="cancelCandidateFormV16()">${tx('Hủy','Cancel')}</button><button class="btn primary" type="submit">${edit?tx('Lưu','Save'):tx('Gửi phiếu','Submit')}</button></div>
    </form></main><div class="prototype-tag">Responsive UX-UAT v1.7</div></div>`;
};

const _shellV17=shell;
shell=function(content,title,sub=''){return _shellV17(content,title,sub).replace(/Responsive UX-UAT v1\.6/g,'Responsive UX-UAT v1.7');};
const _loginPageV17=loginPage;
loginPage=function(){return _loginPageV17().replace(/Responsive UX-UAT v1\.6/g,'Responsive UX-UAT v1.7');};

render();
