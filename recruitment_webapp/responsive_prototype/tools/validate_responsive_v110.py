from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse,re,json,sys
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('--no-write',action='store_true'); a=ap.parse_args()
html=(root/'index.html').read_text(encoding='utf-8')
html=re.sub(r'<link rel="preconnect"[^>]*>','',html)
html=re.sub(r'<link href="https://fonts.googleapis.com[^\"]+"[^>]*>','',html)
css_files=['styles.css','responsive-v12.css','responsive-v13.css','responsive-v14.css','responsive-v15.css','responsive-v16.css','responsive-v17.css','responsive-v18.css','responsive-v19.css']
js_files=['app.js','v11-overrides.js','responsive-v12.js','responsive-v13.js','responsive-v14.js','responsive-v15.js','responsive-v16.js','responsive-v17.js','responsive-v18.js','responsive-v19.js','responsive-v110.js']
for f in css_files:
    html=html.replace(f'<link rel="stylesheet" href="{f}" />',f'<style>{(root/f).read_text(encoding="utf-8")}</style>')
for f in js_files:
    js=(root/f).read_text(encoding='utf-8')
    js=js.replace("localStorage.getItem('eiuRecruitmentLang') || 'vi'","'vi'")
    js=re.sub(r"localStorage\.setItem\([^;]+\);?",'',js)
    html=html.replace(f'<script src="{f}"></script>',f'<script>{js}</script>')

results=[]
def check(name,ok,detail=''):
    row={'name':name,'pass':bool(ok),'detail':str(detail)}
    results.append(row); print(('PASS' if ok else 'FAIL'),name,detail)

readme=(root/'README.md').read_text(encoding='utf-8')
version=(root/'VERSION.md').read_text(encoding='utf-8')
check('Responsive README/VERSION authority v1.10 + Full v1.17',readme.startswith('# EIU Recruitment — Responsive Clickable Prototype v1.10') and 'Full Handover **v1.17**' in readme and 'Business baseline: **Full Handover v1.17**' in version)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':430,'height':844})
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.on('console',lambda m: errors.append('console:'+m.text) if m.type=='error' else None)
    page.set_content(html,wait_until='load');page.wait_for_timeout(100)

    # Required responsive matrix: no page-level overflow on core patched routes.
    for width,height in [(360,800),(390,844),(430,844),(768,1024),(1024,768),(1280,800)]:
        page.set_viewport_size({'width':width,'height':height})
        for role,route in [('admin','applications'),('admin','hr-report'),('candidate','candidate-form')]:
            page.evaluate("x=>{state.role=x[0];state.lang='vi';state.page=x[1];state.selectedIds.clear();state.drawer=null;state.modal=null;render()}",[role,route])
            page.wait_for_timeout(25)
            sw=page.evaluate('document.documentElement.scrollWidth');cw=page.evaluate('document.documentElement.clientWidth')
            check(f'no page overflow {role}/{route} {width}x{height}',sw<=cw+1,f'{sw}/{cw}')

    page.set_viewport_size({'width':1280,'height':800})
    # Phase-1 nav.
    page.evaluate("state.role='admin';state.page='applications';state.lang='vi';state.selectedIds.clear();render()");page.wait_for_timeout(30)
    navtxt=page.locator('.responsive-sidebar').inner_text()
    check('Phase1 admin nav hides FUTURE_HIDDEN',all(x not in navtxt for x in ['Dashboard','Báo cáo & Thống kê','Vị trí tuyển dụng','Phòng / Ban','Nguồn ứng viên','Cài đặt hệ thống']),navtxt.replace('\n',' | '))
    page.evaluate("state.role='interviewer';state.page='interviewer-report';render()");page.wait_for_timeout(20)
    intnav=page.locator('.responsive-sidebar').inner_text()
    check('Interviewer nav hides Home/Documents/Settings',all(x not in intnav for x in ['Dashboard','Tài liệu','Cài đặt']),intnav.replace('\n',' | '))
    page.evaluate("state.role='candidate';state.page='candidate-applications';render()");page.wait_for_timeout(20)
    candnav=page.locator('.responsive-sidebar').inner_text()
    check('Candidate nav only applications','Trang chủ' not in candnav and 'Hồ sơ cá nhân' not in candnav,candnav.replace('\n',' | '))

    # Candidate / Submission separation + UI.
    page.evaluate("state.role='admin';state.page='applications';state.selectedIds.clear();render()");page.wait_for_timeout(30)
    check('Application Inbox bulk Delete removed',page.locator('.toolbar-left .btn.danger').count()==0)
    check('Application Inbox bulk candidate email removed',page.get_by_role('button',name=re.compile('Gửi thư ứng viên')).count()==0)
    c8=page.locator('.applications-table tbody tr.parent-row').filter(has_text='Nguyễn Thị H').first
    check('Inactive Candidate lifecycle shown separately','Candidate Inactive' in c8.inner_text(),c8.inner_text().replace('\n',' | '))
    c8_status=c8.locator('.status').inner_text()
    check('Inactive Candidate preserves Submission workflow',c8_status in ['Đã đọc','Read'],c8_status)
    check('Demo Submission has no INACTIVE',page.evaluate("state.candidates.flatMap(c=>c.submissions).every(s=>s.status!=='INACTIVE')"))
    check('Historical Submission statuses are read-only',page.locator('.submission-history-row .status-clickable').count()==0)

    # Single latest Submission manual menu: only NEW/READ.
    c6=page.locator('.applications-table tbody tr.parent-row').filter(has_text='Đỗ Thị F').first
    c6.locator('.status-clickable').click();page.wait_for_timeout(20)
    opts=[x.strip() for x in page.locator('.status-popover [role=menuitem]').all_inner_texts()]
    check('Latest Submission menu only NEW READ',len(opts)==2 and any('Mới' in x for x in opts) and any('Đã đọc' in x for x in opts),opts)
    # same-trigger toggle / outside / Escape retained
    page.keyboard.press('Escape');page.wait_for_timeout(20)
    check('Escape closes latest Submission menu',page.locator('.status-popover').count()==0)
    check('Escape restores focus',page.evaluate("document.activeElement && document.activeElement.classList.contains('status-clickable')"))

    # Candidate-level single/bulk parity: inactive Candidate remains eligible if no active Application.
    page.keyboard.press('Escape');page.wait_for_timeout(10)
    c8=page.locator('.applications-table tbody tr.parent-row').filter(has_text='Nguyễn Thị H').first
    check('Inactive Candidate latest status remains clickable',c8.locator('.status-clickable').count()==1)
    before_inactive=page.evaluate("latestSubmissionV16(candidate('c8')).status")
    c8.locator('.status-clickable').click();page.wait_for_timeout(15)
    target_label='Mới' if before_inactive=='READ' else 'Đã đọc'
    page.locator('.status-popover [role=menuitem]').filter(has_text=target_label).click();page.wait_for_timeout(30)
    after_inactive=page.evaluate("latestSubmissionV16(candidate('c8')).status")
    check('Single manual status allowed for inactive Candidate',before_inactive!=after_inactive,f'{before_inactive}->{after_inactive}')

    # c6 + c8 (inactive) succeeds together; inactivity alone must not abort the batch.
    page.evaluate("state.selectedIds=new Set(['c6','c8']);render()");page.wait_for_timeout(20)
    page.locator('.toolbar-left').get_by_role('button',name='Status').click();page.locator('.status-popover [role=menuitem]').filter(has_text='Đã đọc').click();page.wait_for_timeout(40)
    check('Bulk inactive Candidate parity succeeds',page.evaluate("latestSubmissionV16(candidate('c6')).status==='READ' && latestSubmissionV16(candidate('c8')).status==='READ'"))

    # Active-Application member remains invalid and rolls back the entire batch.
    before=page.evaluate("latestSubmissionV16(candidate('c6')).status")
    page.evaluate("state.selectedIds=new Set(['c6','c1']);render()");page.wait_for_timeout(20)
    page.locator('.toolbar-left').get_by_role('button',name='Status').click();page.locator('.status-popover [role=menuitem]').filter(has_text='Mới').click();page.wait_for_timeout(40)
    after=page.evaluate("latestSubmissionV16(candidate('c6')).status")
    check('Bulk active-Application member rolls back whole batch',before==after,f'{before}->{after}')
    check('Candidate has no duplicated workflow status property',page.evaluate("state.candidates.every(c=>!Object.prototype.hasOwnProperty.call(c,'status'))"))

    # Inactivation preserves latest Submission status.
    prev=page.evaluate("latestSubmissionV16(candidate('c6')).status")
    page.evaluate("state.selectedIds=new Set(['c6']);toggleInactive()");page.wait_for_timeout(30)
    check('Inactivation changes Candidate lifecycle',page.evaluate("candidate('c6').active") is False)
    check('Inactivation preserves Submission status',page.evaluate("latestSubmissionV16(candidate('c6')).status")==prev)
    # reactivate back for clean state
    page.evaluate("state.selectedIds=new Set(['c6']);toggleInactive()");page.wait_for_timeout(20)

    # HR Report aggregate drawer / current interview status.
    page.evaluate("state.role='admin';state.page='hr-report';state.selectedIds.clear();render()");page.wait_for_timeout(30)
    page.locator('.report-table tbody tr').first.locator('.row-btn').click();page.wait_for_timeout(30)
    dtxt=page.locator('.drawer').inner_text()
    check('Aggregate report drawer has no generic Delete','Xóa' not in dtxt and 'Delete' not in dtxt,dtxt[:300])
    check('Aggregate drawer exposes required controls',all(x in dtxt for x in ['Edit HR Note','Report Status','PDF']))
    old_app=page.evaluate("appById('a1').status")
    old_report=page.evaluate("reportStatusV16(appById('a1'))")
    page.get_by_role('button',name=re.compile('Đổi Report Status')).click();page.wait_for_timeout(20)
    # choose Follow-up if available and different
    page.locator('.status-popover [role=menuitem]').filter(has_text='Đã gửi Báo cáo').click();page.wait_for_timeout(30)
    new_report=page.evaluate("reportStatusV16(appById('a1'))")
    new_app=page.evaluate("appById('a1').status")
    check('Report Status writes Current Interview',old_report!=new_report and new_report=='REPORT_SUBMITTED',f'{old_report}->{new_report}')
    check('Report Status does not directly mutate Application status',old_app==new_app,f'{old_app}->{new_app}')

    # Final Decision Source qualitative-only edit.
    page.evaluate("state.drawer=null;state.modal=null;state.role='interviewer';state.page='interviewer-report';render()");page.wait_for_timeout(20)
    before_src=page.evaluate("(()=>{const x=reportSourceV16('r11');return x&&[x[0],x[1].decisionUpdatedAt]})()")
    page.evaluate("openModal('editOwnReport',{appId:'a1'})");page.wait_for_timeout(30)
    page.locator('#repKnowledge').fill('Qualitative-only edit v1.6')
    page.get_by_role('button',name='Lưu').last.click();page.wait_for_timeout(35)
    after_src=page.evaluate("(()=>{const x=reportSourceV16('r11');return x&&[x[0],x[1].decisionUpdatedAt]})()")
    check('Qualitative-only edit keeps Final Decision Source',before_src==after_src,f'{before_src}->{after_src}')

    # Candidate Education requiredness + NEW Privacy + CV-required staged document semantics.
    page.evaluate("state.role='candidate';openCandidateFormV16('NEW')");page.wait_for_timeout(30)
    check('NEW Privacy starts unchecked',page.locator('#privacyAck').is_checked() is False)
    edu_required=page.locator('.education-row-v17 [required]').count()
    check('Education fields are not invented as required',edu_required==0,edu_required)
    # Current prototype starts with one optional sample row; removing the last row must be allowed.
    page.locator('.education-row-v17 .row-btn').click();page.wait_for_timeout(20)
    check('Education permits zero rows',page.locator('.education-row-v17').count()==0 and page.locator('.education-empty').count()==1)
    page.get_by_role('button',name='Thêm').click();page.wait_for_timeout(20)
    check('Education add remains repeatable',page.locator('.education-row-v17').count()==1)

    # Explicitly acknowledge privacy, then verify CV remains independently required.
    page.locator('#privacyAck').check();page.wait_for_timeout(10)
    page.locator('.candidate-form button[type=submit]').click();page.wait_for_timeout(30)
    check('New Candidate form blocks submit without CV',page.evaluate("state.page")=='candidate-form' and page.locator('.candidate-error-summary').count()==1)
    count_before=page.evaluate("state.portalSubmissions.length")
    page.locator('#candidateCvV16').set_input_files({'name':'CV_Test.pdf','mimeType':'application/pdf','buffer':b'%PDF-1.4 test'})
    page.wait_for_timeout(25)
    check('Privacy explicit choice survives staged-file rerender',page.locator('#privacyAck').is_checked() is True)
    page.locator('.candidate-form button[type=submit]').click();page.wait_for_timeout(40)
    check('New Candidate form accepts staged CV ADD',page.evaluate("state.portalSubmissions.length")==count_before+1)

    # Edit current NEW submission, stage DELETE -> CV required blocks; then replace and Cancel -> original survives.
    page.evaluate("openCandidateFormV16('EDIT','ps1')");page.wait_for_timeout(30)
    original_cv=page.evaluate("currentPortalSubmissionV16().currentCv.name")
    page.get_by_role('button',name=re.compile('Stage DELETE')).click();page.wait_for_timeout(20)
    page.locator('.candidate-form button[type=submit]').click();page.wait_for_timeout(30)
    check('EDIT staged DELETE cannot violate CV required',page.evaluate("state.page")=='candidate-form' and page.locator('.candidate-error-summary').count()==1)
    page.locator('#candidateCvV16').set_input_files({'name':'CV_Replacement.pdf','mimeType':'application/pdf','buffer':b'%PDF-1.4 replacement'})
    page.wait_for_timeout(25)
    check('EDIT stages REPLACE',page.evaluate("state.candidateDocStage.cvAction")=='REPLACE')
    page.get_by_role('button',name='Hủy').last.click();page.wait_for_timeout(35)
    check('Cancel discards staged replacement',page.evaluate("state.portalSubmissions.find(s=>s.id==='ps1').currentCv.name")==original_cv)
    check('Cancel clears staged state',page.evaluate("state.candidateDocStage.cvAction") is None)

    # v1.8 schedule conflict matrix via deterministic helper.
    page.evaluate("state.role='admin';state.page='interview';state.modal=null;state.drawer=null;render()")
    page.wait_for_timeout(20)
    # same Candidate overlap against existing a1/r11
    ck=page.evaluate("conflictKindsV18(appById('a1'),'x','15/05/2025','09:30','09:45','Other room',['u4'])")
    check('Schedule blocks same-Candidate overlap','Candidate' in ck,ck)
    rk=page.evaluate("conflictKindsV18(appById('a2'),'x','15/05/2025','09:30','09:45','Phòng Kỹ thuật 201 – EIU',['u4'])")
    check('Schedule blocks Room overlap','Room' in rk,rk)
    ik=page.evaluate("conflictKindsV18(appById('a2'),'x','15/05/2025','09:30','09:45','Other room',['u1'])")
    check('Schedule blocks Interviewer overlap','Interviewer' in ik,ik)
    adj=page.evaluate("conflictKindsV18(appById('a2'),'x','15/05/2025','10:00','10:30','Other room',['u4'])")
    check('Adjacent end-start interval allowed',len(adj)==0,adj)
    cancel=page.evaluate("(()=>{const r=findRound('r11'),old=r.status;r.status='CANCELLED';const x=conflictKindsV18(appById('a2'),'x','15/05/2025','09:30','09:45','Phòng Kỹ thuật 201 – EIU',['u1']);r.status=old;return x})()")
    check('CANCELLED round ignored by conflict engine',len(cancel)==0,cancel)

    # Copy semantics: fresh target with empty Round1 is filled, not Round2; source logistics copied, topic blank.
    page.evaluate("state.applications.push({id:'qaCopy',submissionId:'qaS',candidateId:'c8',unit:'QA',team:'QA',position:'QA',hr:'QA',status:'AWAITING_INTERVIEW',rounds:[{id:'qaR1',no:1,topic:'',date:'',start:'',end:'',format:'',location:'',status:'AVAILABLE',note:'',participants:[],active:true}]})")
    page.evaluate("openModal('copyRound',{appId:'a1',roundId:'r11'})");page.wait_for_timeout(20)
    page.locator('#roundApp').select_option('qaCopy')
    page.locator('#roundParticipants').select_option('u1,u2,u3')
    check('Copy modal prefills source date',page.locator('#roundDate').input_value()=='2025-05-15',page.locator('#roundDate').input_value())
    page.get_by_role('button',name='Xác nhận').last.click();page.wait_for_timeout(30)
    cp=page.evaluate("(()=>{const a=appById('qaCopy'),r=a.rounds[0];return {count:a.rounds.length,no:r.no,topic:r.topic,date:r.date,start:r.start,end:r.end,location:r.location,prov:r.copiedFromInterviewId}})()")
    check('RP-COPY-01 Copy fills empty target Round1',cp['count']==1 and cp['no']==1,cp)
    check('RP-COPY-03 Copy keeps Demo Topic blank',cp['topic']=='',cp)
    check('RP-COPY-04 Copy preserves source schedule logistics',cp['date']=='15/05/2025' and cp['start']=='09:00' and cp['end']=='10:00' and cp['location']=='Phòng Kỹ thuật 201 – EIU',cp)
    check('Copy records provenance',cp['prov']=='r11',cp)
    check('Copied Round no longer structurally empty',page.evaluate("isStructurallyEmptyRoundV18(appById('qaCopy').rounds[0])") is False)

    # Stable critical-control evidence: when target Round1 is already business-used, Save Copy creates next legal round.
    page.evaluate("state.applications=state.applications.filter(a=>a.id!=='qaCopy');state.applications.push({id:'qaCopyUsed',submissionId:'qaSU',candidateId:'c7',unit:'QA',team:'QA',position:'QA used target',hr:'QA',status:'AWAITING_INTERVIEW',rounds:[{id:'qaUR1',no:1,topic:'Already used',date:'',start:'',end:'',format:'',location:'',status:'AVAILABLE',note:'',participants:[],active:true}]});openModal('copyRound',{appId:'a1',roundId:'r11'})");page.wait_for_timeout(20)
    page.locator('#roundApp').select_option('qaCopyUsed')
    page.locator('#roundParticipants').select_option('u1,u2,u3')
    page.get_by_role('button',name='Xác nhận').last.click();page.wait_for_timeout(30)
    cp_used=page.evaluate("(()=>{const a=appById('qaCopyUsed'),rs=[...a.rounds].sort((x,y)=>x.no-y.no),r2=rs[1];return {count:rs.length,r1Topic:rs[0].topic,r2No:r2&&r2.no,r2Topic:r2&&r2.topic,date:r2&&r2.date,start:r2&&r2.start,end:r2&&r2.end,location:r2&&r2.location,prov:r2&&r2.copiedFromInterviewId}})()")
    check('RP-COPY-02 Copy used target Round1 creates next legal round',cp_used['count']==2 and cp_used['r1Topic']=='Already used' and cp_used['r2No']==2 and cp_used['r2Topic']=='' and cp_used['prov']=='r11',cp_used)


    # v1.9 exact SubmissionSelector: same Candidate has distinct exact Submission choices.
    page.evaluate("state.role='admin';state.page='applications';state.modal=null;state.drawer=null;render();openModal('assignApplication')");page.wait_for_timeout(25)
    subsel=page.locator('#applicationSubmissionV19')
    vals=subsel.locator('option').evaluate_all("els=>els.map(e=>({value:e.value,text:e.textContent}))")
    c1vals=[x for x in vals if 'Nguyễn Văn A' in x['text']]
    check('Application modal uses exact SubmissionSelector',subsel.count()==1 and all(x['value'].startswith('s') for x in vals),vals[:4])
    check('Same Candidate Submissions remain distinct',len(c1vals)>=3 and len({x['value'] for x in c1vals})==len(c1vals),c1vals)
    check('SubmissionSelector displays date and status',all('Submitted:' in x['text'] and 'Status:' in x['text'] for x in c1vals),c1vals)
    subsel.select_option('s2');page.get_by_role('button',name='Lưu').last.click();page.wait_for_timeout(25)
    check('Application Save returns exact submission_id',page.evaluate("state.lastApplicationAssignmentV19&&state.lastApplicationAssignmentV19.submissionId")=='s2',page.evaluate("state.lastApplicationAssignmentV19&&[state.lastApplicationAssignmentV19.submissionId,state.lastApplicationAssignmentV19.candidateId]"))

    # v1.9 Active Participant guard on Create and Copy.
    page.evaluate("state.role='admin';state.page='interview';state.users.u1.active=false;state.modal=null;render();openModal('createRound')");page.wait_for_timeout(20)
    before_create=page.evaluate("state.applications.reduce((n,a)=>n+a.rounds.length,0)")
    page.evaluate("saveRound('createRound','')");page.wait_for_timeout(20)
    after_create=page.evaluate("state.applications.reduce((n,a)=>n+a.rounds.length,0)")
    create_err=page.locator('#conflictBox').inner_text()
    check('Create blocks inactive selected Participant',before_create==after_create and 'CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED' in create_err,f'{before_create}->{after_create} {create_err}')
    page.evaluate("closeModal();state.applications.push({id:'qaInactiveCopy',submissionId:'qaIC',candidateId:'c8',unit:'QA',team:'QA',position:'QA inactive copy',hr:'QA',status:'AWAITING_INTERVIEW',rounds:[{id:'qaICR1',no:1,topic:'',date:'',start:'',end:'',format:'',location:'',status:'AVAILABLE',note:'',participants:[],active:true}]});openModal('copyRound',{appId:'a1',roundId:'r11'})");page.wait_for_timeout(20)
    page.locator('#roundApp').select_option('qaInactiveCopy')
    before_copy=page.evaluate("appById('qaInactiveCopy').rounds.length")
    page.evaluate("saveRound('copyRound','r11')");page.wait_for_timeout(20)
    after_copy=page.evaluate("appById('qaInactiveCopy').rounds.length")
    copy_err=page.locator('#conflictBox').inner_text() if page.locator('#conflictBox').count() else ''
    copy_parts=page.locator('#roundParticipants').input_value() if page.locator('#roundParticipants').count() else ''
    check('Copy blocks inactive prefilled Participant',before_copy==after_copy and 'CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED' in copy_err,f'{before_copy}->{after_copy} parts={copy_parts} u1={page.evaluate("state.users.u1.active")} err={copy_err}')
    page.evaluate("state.users.u1.active=true;closeModal()")

    # v1.10 single/bulk Interview Schedule Status operational-transition parity.
    page.evaluate("state.role='admin';state.page='interview';state.selectedIds.clear();state.users.u1.active=true;render()")
    # Single CANCELLED -> operational with inactive Participant must block.
    single_inactive=page.evaluate("""(()=>{const r=findRound('r41');const old={status:r.status};state.users.u1.active=false;setEntityStatus('round','r41','SCHEDULED');const out={status:r.status,last:state.lastInterviewStatusTransitionV110};state.users.u1.active=true;r.status=old.status;render();return out})()""")
    check('RQA-SCH-STATUS-01 single inactive Participant blocks',single_inactive['status']=='CANCELLED' and single_inactive['last']['ok'] is False and single_inactive['last']['failures'][0]['code']=='CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED',single_inactive)

    # Bulk must prevalidate the full set and rollback every selected Interview.
    bulk_inactive=page.evaluate("""(()=>{const r41=findRound('r41'),r31=findRound('r31');const o41=r41.status,o31=r31.status;r41.status='CANCELLED';r31.status='CANCELLED';state.users.u1.active=false;state.selectedIds=new Set(['r41','r31']);setEntityStatus('bulk-interview','','SCHEDULED');const out={r41:r41.status,r31:r31.status,last:state.lastInterviewStatusTransitionV110};state.users.u1.active=true;r41.status=o41;r31.status=o31;state.selectedIds.clear();render();return out})()""")
    check('RQA-SCH-STATUS-02 bulk inactive Participant rolls back all',bulk_inactive['r41']=='CANCELLED' and bulk_inactive['r31']=='CANCELLED' and bulk_inactive['last']['ok'] is False,bulk_inactive)

    # Candidate-only conflict on status activation.
    candidate_conf=page.evaluate("""(()=>{const r=findRound('r12');const old={status:r.status,date:r.date,start:r.start,end:r.end,location:r.location,participants:[...r.participants]};Object.assign(r,{status:'CANCELLED',date:'15/05/2025',start:'09:30',end:'09:45',location:'Other room',participants:['u4']});setEntityStatus('round','r12','SCHEDULED');const out={status:r.status,last:state.lastInterviewStatusTransitionV110};Object.assign(r,old);render();return out})()""")
    check('RQA-SCH-STATUS-03 single Candidate conflict blocks',candidate_conf['status']=='CANCELLED' and 'Candidate' in (candidate_conf['last']['failures'][0].get('conflicts') or []),candidate_conf)

    # Room-only conflict on status activation.
    room_conf=page.evaluate("""(()=>{const r=findRound('r41');const old={status:r.status,date:r.date,start:r.start,end:r.end,location:r.location,participants:[...r.participants]};Object.assign(r,{status:'CANCELLED',date:'15/05/2025',start:'09:30',end:'09:45',location:'Phòng Kỹ thuật 201 – EIU',participants:['u4']});setEntityStatus('round','r41','SCHEDULED');const out={status:r.status,last:state.lastInterviewStatusTransitionV110};Object.assign(r,old);render();return out})()""")
    check('RQA-SCH-STATUS-04 single Room conflict blocks',room_conf['status']=='CANCELLED' and 'Room' in (room_conf['last']['failures'][0].get('conflicts') or []),room_conf)

    # Interviewer-only conflict on status activation.
    interviewer_conf=page.evaluate("""(()=>{const r=findRound('r41');const old={status:r.status,date:r.date,start:r.start,end:r.end,location:r.location,participants:[...r.participants]};Object.assign(r,{status:'CANCELLED',date:'15/05/2025',start:'09:30',end:'09:45',location:'Other room',participants:['u1']});setEntityStatus('round','r41','SCHEDULED');const out={status:r.status,last:state.lastInterviewStatusTransitionV110};Object.assign(r,old);render();return out})()""")
    check('RQA-SCH-STATUS-05 single Interviewer conflict blocks',interviewer_conf['status']=='CANCELLED' and 'Interviewer' in (interviewer_conf['last']['failures'][0].get('conflicts') or []),interviewer_conf)

    # One conflicting item in bulk keeps all selected rows unchanged.
    bulk_conf=page.evaluate("""(()=>{const r41=findRound('r41'),r31=findRound('r31');const o41={status:r41.status,date:r41.date,start:r41.start,end:r41.end,location:r41.location,participants:[...r41.participants]},o31={status:r31.status};Object.assign(r41,{status:'CANCELLED',date:'15/05/2025',start:'09:30',end:'09:45',location:'Phòng Kỹ thuật 201 – EIU',participants:['u4']});r31.status='CANCELLED';state.selectedIds=new Set(['r41','r31']);setEntityStatus('bulk-interview','','SCHEDULED');const out={r41:r41.status,r31:r31.status,last:state.lastInterviewStatusTransitionV110};Object.assign(r41,o41);r31.status=o31.status;state.selectedIds.clear();render();return out})()""")
    check('RQA-SCH-STATUS-06 bulk conflict rolls back every selected Interview',bulk_conf['r41']=='CANCELLED' and bulk_conf['r31']=='CANCELLED' and bulk_conf['last']['ok'] is False,bulk_conf)

    # [start,end) adjacency remains valid under the status-transition path.
    adjacent=page.evaluate("""(()=>{const r=findRound('r41');const old={status:r.status,date:r.date,start:r.start,end:r.end,location:r.location,participants:[...r.participants]};Object.assign(r,{status:'CANCELLED',date:'15/05/2025',start:'10:00',end:'10:30',location:'Phòng Kỹ thuật 201 – EIU',participants:['u1']});setEntityStatus('round','r41','SCHEDULED');const out={status:r.status,last:state.lastInterviewStatusTransitionV110};Object.assign(r,old);render();return out})()""")
    check('RQA-SCH-STATUS-07 adjacent activation allowed',adjacent['status']=='SCHEDULED' and adjacent['last']['ok'] is True,adjacent)

    # Core route page-level overflow smoke matrix.
    route_cases=[('admin','applications'),('admin','interview'),('admin','hr-report'),('admin','permissions'),('candidate','candidate-form'),('candidate','candidate-applications'),('interviewer','interviewer-report')]
    for role,route in route_cases:
        for w in [375,430,768,1280]:
            page.set_viewport_size({'width':w,'height':900})
            if role=='candidate' and route=='candidate-form': page.evaluate("state.role='candidate';openCandidateFormV16('NEW')")
            else: page.evaluate("([role,route])=>{state.role=role;state.page=route;state.modal=null;state.drawer=null;state.mobileNavOpen=false;state.selectedIds.clear();render()}",[role,route])
            page.wait_for_timeout(15)
            overflow=page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
            check(f'No page overflow {role}/{route} {w}',not overflow,f'scroll={page.evaluate("document.documentElement.scrollWidth")} inner={w}')

    # Exact-domain schema assertion is checked package-side; browser should have no JS errors.
    check('No JS/console errors',not errors,errors)
    browser.close()

summary={'version':'1.10','total':len(results),'pass':sum(x['pass'] for x in results),'fail':sum(not x['pass'] for x in results),'results':results}
if not a.no_write:
    (root/'RESPONSIVE_QA_RESULTS_v1.10.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
md=[f"# Responsive Browser QA v1.10", "", f"**TOTAL={summary['total']} PASS={summary['pass']} FAIL={summary['fail']}**", "", "Executed against the effective load chain through `responsive-v110.js` using headless Chromium.", "", "| Result | Check | Detail |","|---|---|---|"]
for x in results:
    detail=x['detail'].replace('|','\\|').replace('\n',' ')
    if len(detail)>160: detail=detail[:157]+'...'
    md.append(f"| {'PASS' if x['pass'] else 'FAIL'} | {x['name']} | {detail} |")
if not a.no_write:
    (root/'RESPONSIVE_BROWSER_QA_v1.10.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(f"TOTAL={summary['total']} PASS={summary['pass']} FAIL={summary['fail']}")
sys.exit(1 if summary['fail'] else 0)
