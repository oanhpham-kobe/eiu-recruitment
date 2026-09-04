from pathlib import Path
import argparse,csv,json,re,subprocess,sys,hashlib
import yaml
B=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description='Validate EIU Recruitment Full Handover v1.17')
ap.add_argument('--design-dir',required=True,help='Path to extracted EIU Recruitment Design System v1.8')
ap.add_argument('--responsive-dir',required=True,help='Path to extracted Responsive Prototype v1.10')
ap.add_argument('--no-write',action='store_true',help='Validate without rewriting PACKAGE_VALIDATION.txt')
a=ap.parse_args(); DS=Path(a.design_dir).resolve(); RP=Path(a.responsive_dir).resolve()
r=[]
def c(name,cond,detail=''): r.append((bool(cond),name,detail))
def txt(f):
    p=B/f; return p.read_text(errors='replace') if p.exists() else ''
def dtxt(f):
    p=DS/f; return p.read_text(errors='replace') if p.exists() else ''
def rtxt(f):
    p=RP/f; return p.read_text(errors='replace') if p.exists() else ''
def parse_yaml(f):
    try:return yaml.safe_load(txt(f)),None
    except Exception as e:return {},e

required=[
'00_README.md','FINAL_REVIEW_GUIDE.md','13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md','14_SCOPE_AND_OPEN_ITEMS.md','15_ALL_IN_ONE_SPEC.md','16_AI_REVIEW_AND_BUILD_PROMPT.md',
'37_BACKEND_COMMAND_CONTRACTS.md','39_SECURITY_RLS_MATRIX.md','40_DATABASE_INVARIANTS.md','41_STORAGE_AND_UPLOAD_SECURITY.md','42_PRIVACY_RETENTION_COMPLIANCE.md','43_EMAIL_DELIVERY_SPEC.md','45_PRODUCTION_UAT_GATE.md','46_AUTH_IDENTITY_MODEL.md','48_IDEMPOTENCY_CONCURRENCY_SPEC.md','50_OWNER_DECISIONS_PENDING.md','52_TECHNICAL_GATE_STATUS.md','54_SCHEMA_CONFORMANCE_MATRIX.md','55_COMMAND_COVERAGE_MATRIX.md','59_RLS_POLICY_BLUEPRINT.md','61_ROOT_ADMIN_BREAK_GLASS_RECOVERY.md','66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md','67_WEB_SECURITY_BASELINE.md','68_RATE_LIMIT_POLICY.md','70_SEMANTIC_VALIDATION_GATE.md','73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md','75_RELEASE_EVIDENCE_MATRIX.md','76_DEPENDENCY_BASELINE_POLICY.md','78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md','80_EXTERNAL_REVIEW_V7_RESOLUTION.md','81_RESPONSIVE_PROTOTYPE_INTEGRATION.md','82_TECHNICAL_PRECODE_GATE_V1_9.md','83_EXTERNAL_REVIEW_V7_IMPLEMENTATION_ALIGNMENT_V1_10.md','84_TECHNICAL_PRECODE_GATE_V1_10.md','85_EXTERNAL_REVIEW_V8_IMPLEMENTATION_ALIGNMENT_V1_11.md','86_TECHNICAL_PRECODE_GATE_V1_11.md','87_EXTERNAL_REVIEW_V9_IMPLEMENTATION_ALIGNMENT_V1_12.md','88_TECHNICAL_PRECODE_GATE_V1_12.md','89_EXTERNAL_REVIEW_V10_IMPLEMENTATION_ALIGNMENT_V1_13.md','90_TECHNICAL_PRECODE_GATE_V1_13.md','91_EXTERNAL_REVIEW_V11_IMPLEMENTATION_ALIGNMENT_V1_14.md','92_TECHNICAL_PRECODE_GATE_V1_14.md','95_INDEPENDENT_PLANNER_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_16.md','96_TECHNICAL_PRECODE_GATE_V1_16.md','CHANGELOG_V1_10.md','CHANGELOG_V1_11.md','CHANGELOG_V1_12.md','CHANGELOG_V1_13.md','CHANGELOG_V1_14.md','CHANGELOG_V1_15.md','CHANGELOG_V1_16.md',
'app_spec.yaml','command_registry.yaml','source_registry.yaml','validation_contract.yaml','critical_control_registry.yaml','database_schema.sql','seed_master_data.json','permissions_matrix.csv','status_mapping.csv','technical_review_matrix.csv','tools/generate_all_in_one.py'
]
for f in required:c('file '+f,(B/f).exists())
c('Design dir exists',DS.exists())

app,e=parse_yaml('app_spec.yaml'); c('app_spec parses',e is None and isinstance(app,dict),str(e or ''))
reg,e=parse_yaml('command_registry.yaml'); c('command_registry parses',e is None and isinstance(reg,dict) and isinstance(reg.get('commands'),list),str(e or ''))
sreg,e=parse_yaml('source_registry.yaml'); c('source_registry parses',e is None and isinstance(sreg,dict) and isinstance(sreg.get('documents'),list),str(e or ''))
vc,e=parse_yaml('validation_contract.yaml'); c('validation_contract parses',e is None and isinstance(vc,dict),str(e or ''))
crit,e=parse_yaml('critical_control_registry.yaml'); c('critical_control_registry parses',e is None and isinstance(crit,dict) and isinstance(crit.get('critical_controls'),list),str(e or ''))
try: seed=json.loads(txt('seed_master_data.json')); c('seed parses',isinstance(seed,dict))
except Exception as e: seed={}; c('seed parses',False,str(e))

# Versions and current gate
prod=app.get('product',{})
c('Technical version 1.17',prod.get('document_version')=='1.17' and prod.get('technical_architecture',{}).get('version')=='1.17' and app.get('version')=='1.17')
c('Design version 1.8',prod.get('design_system',{}).get('version')=='1.8' and dtxt('00_README.md').startswith('# EIU Recruitment Design System v1.8'))
c('App spec responsive baseline v1.10',app.get('responsive_prototype',{}).get('version')=='1.10' and app.get('responsive_prototype',{}).get('authority')=='Design System v1.8 + Full Handover v1.17' and app.get('responsive_prototype',{}).get('status')=='READY_FOR_OWNER_VISUAL_UAT')
c('Business core 1.2 frozen',prod.get('business_logic_core',{}).get('version')=='1.2' and prod.get('business_logic_core',{}).get('status')=='FROZEN')
c('Scope current versions','v1.8 CURRENT' in txt('14_SCOPE_AND_OPEN_ITEMS.md') and 'v1.17 TECHNICAL SPECIFICATION FROZEN' in txt('14_SCOPE_AND_OPEN_ITEMS.md'))
c('Gate status current','Design System v1.8' in txt('52_TECHNICAL_GATE_STATUS.md') and 'Technical Architecture v1.17' in txt('52_TECHNICAL_GATE_STATUS.md') and 'Responsive Prototype v1.10' in txt('52_TECHNICAL_GATE_STATUS.md') and 'READY TO IMPLEMENT' in txt('52_TECHNICAL_GATE_STATUS.md'))

# Source governance
hist_expected={'49_TECHNICAL_REVIEW_VERCEL_SUPABASE.md','56_EXTERNAL_REVIEW_V2_RESOLUTION.md','57_TECHNICAL_PRECODE_GATE_V1_4.md','60_EXTERNAL_REVIEW_V3_RESOLUTION.md','65_TECHNICAL_PRECODE_GATE_V1_5.md','69_EXTERNAL_REVIEW_V4_RESOLUTION.md','71_TECHNICAL_PRECODE_GATE_V1_6.md','72_EXTERNAL_REVIEW_V5_RESOLUTION.md','74_TECHNICAL_PRECODE_GATE_V1_7.md','77_EXTERNAL_REVIEW_V6_RESOLUTION.md','79_TECHNICAL_PRECODE_GATE_V1_8.md','80_EXTERNAL_REVIEW_V7_RESOLUTION.md','82_TECHNICAL_PRECODE_GATE_V1_9.md','83_EXTERNAL_REVIEW_V7_IMPLEMENTATION_ALIGNMENT_V1_10.md','84_TECHNICAL_PRECODE_GATE_V1_10.md','85_EXTERNAL_REVIEW_V8_IMPLEMENTATION_ALIGNMENT_V1_11.md','86_TECHNICAL_PRECODE_GATE_V1_11.md','87_EXTERNAL_REVIEW_V9_IMPLEMENTATION_ALIGNMENT_V1_12.md','88_TECHNICAL_PRECODE_GATE_V1_12.md','89_EXTERNAL_REVIEW_V10_IMPLEMENTATION_ALIGNMENT_V1_13.md','90_TECHNICAL_PRECODE_GATE_V1_13.md','91_EXTERNAL_REVIEW_V11_IMPLEMENTATION_ALIGNMENT_V1_14.md','92_TECHNICAL_PRECODE_GATE_V1_14.md','93_EXTERNAL_REVIEW_V12_IMPLEMENTATION_ALIGNMENT_V1_15.md','94_TECHNICAL_PRECODE_GATE_V1_15.md','95_INDEPENDENT_PLANNER_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_16.md','96_TECHNICAL_PRECODE_GATE_V1_16.md'}
status={d.get('file'):d.get('status') for d in sreg.get('documents',[])}
c('Historical registry exact',all(status.get(x)=='HISTORICAL' for x in hist_expected),str({x:status.get(x) for x in sorted(hist_expected)}))
for f in sorted(hist_expected): c('Historical banner '+f,'HISTORICAL / SUPERSEDED' in txt(f))
c('Current review pointer',sreg.get('current_review_resolution')=='97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md')
c('Current precode pointer',sreg.get('current_precode_gate')=='98_TECHNICAL_PRECODE_GATE_V1_17.md')
entry=set(sreg.get('current_entrypoints',[]))
for f in ['00_README.md','FINAL_REVIEW_GUIDE.md','16_AI_REVIEW_AND_BUILD_PROMPT.md','52_TECHNICAL_GATE_STATUS.md','97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md','73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md','78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md','81_RESPONSIVE_PROTOTYPE_INTEGRATION.md','98_TECHNICAL_PRECODE_GATE_V1_17.md']:
    c('Current entrypoint '+f,f in entry)
for f in ['00_README.md','FINAL_REVIEW_GUIDE.md','16_AI_REVIEW_AND_BUILD_PROMPT.md']:
    tt=txt(f)
    c('Current review pointer '+f,'97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md' in tt)
    c('Current gate pointer '+f,'98_TECHNICAL_PRECODE_GATE_V1_17.md' in tt)
    c('Design 1.8 '+f,'Design System v1.8' in tt or 'Design System:** v1.7' in tt or 'Design System v1.8' in tt)
c('README technical current range','responsive prototype' in txt('00_README.md').lower())
c('AI historical rule explicit','HISTORICAL' in txt('16_AI_REVIEW_AND_BUILD_PROMPT.md') and 'must never override current behavior' in txt('16_AI_REVIEW_AND_BUILD_PROMPT.md'))
allone=txt('15_ALL_IN_ONE_SPEC.md')
for f in sorted(hist_expected): c('All-in-One excludes '+f,f'<!-- SOURCE: {f} -->' not in allone)
c('All-in-One includes current v1.17 alignment','<!-- SOURCE: 97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md -->' in allone and '<!-- SOURCE: 98_TECHNICAL_PRECODE_GATE_V1_17.md -->' in allone)
c('All-in-One generated v1.17',allone.startswith('# 15. ALL-IN-ONE SPEC — GENERATED v1.17'))

# Acceptance IDs
acc=txt('13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md')
ids=re.findall(r'(?m)^\s*(?:-\s*)?\*\*(AC-[A-Z0-9-]+)',acc)
dup=sorted({x for x in ids if ids.count(x)>1})
c('Acceptance IDs unique',not dup,f'duplicates={dup}')
for aid in ['AC-STAT-03','AC-STAT-04','AC-STAT-05','AC-PRIV-EDIT-01','AC-PRIV-SESSION-01','AC-CAND-UPD-EMAIL-01','AC-CACHE-02','AC-PART-RESTORE-01','AC-APP-ID-01','AC-APP-ID-02','AC-ACCESS-01','AC-RESOURCE-01','AC-PRIV-IMM-01','AC-USR-DEL-01','AC-NOTIFY-01','AC-PERM-INT-STATUS-01','AC-PERM-INT-STATUS-02','AC-PERM-INT-STATUS-03','AC-FORM-EXP-01','AC-UP-EXP-01','AC-FORM-LIFE-01','AC-OPEN-SUB-01','AC-OPEN-SUB-02','AC-STAT-INACTIVE-01','AC-STAT-INACTIVE-02','AC-PROT-EDU-01','AC-PRIV-NEW-UI-01','AC-REPORT-AUTH-01','AC-PART-OPER-01','AC-PART-OPER-02','AC-PART-OPER-03','AC-PART-OPER-04','AC-SUB-DEL-REACH-01','AC-SCH-SRC-01','AC-STAT-LATEST-01','AC-RP-COPY-01','AC-ROUND-PROV-01','AC-EDU-DB-01','AC-EDU-DB-02','AC-PROTO-SUBSEL-01','AC-PROTO-SUBSEL-02','AC-PART-OPER-CREATE-01','AC-PART-OPER-COPY-01','AC-STAT-LATEST-SQL-01','AC-USR-LIFE-REG-01','AC-INT-UP-FK-01','AC-INT-UP-DEL-01','AC-INT-UP-DEL-02','AC-BULK-CAND-LIFE-01','AC-BULK-CAND-LIFE-02','AC-BULK-INT-DEL-01','AC-BULK-REPORT-01','AC-CRIT-QA-01']:
    c('Acceptance '+aid,aid in acc)

# Submission state machine
statusdoc=txt('07_STATUS_AND_BUSINESS_RULES.md'); contract=txt('37_BACKEND_COMMAND_CONTRACTS.md')
c('Status generic NEW preserve','current status là `NEW` hoặc `READ` → giữ nguyên manual state' in statusdoc and 'preserve existing manual `NEW/READ`' in contract)
c('Status derived no-app fallback READ','derived (`PROCESSED`/`DONE`/`CLOSED`)' in statusdoc and 'return `READ`' in contract)
c('Candidate Reactivate exception READ',app.get('candidate_lifecycle',{}).get('reactivation_no_active_application')=='READ' and 'force the Submission to `READ`' in txt('03_CANDIDATE_FORM_AND_PORTAL.md'))
c('AC08 canonical no-app','preserves manual `NEW/READ`' in acc and 'Candidate Reactivate' in re.search(r'\*\*AC-08 Derived status\*\*.*',acc).group(0))

# Canonical interview predicates
ir=app.get('interview_rounds',{}); sc=app.get('schedule_conflicts',{})
c('access_active canonical',ir.get('access_active')=='application.is_active AND interview.is_active')
c('current_round canonical','highest round_no among access_active' in ir.get('current_round',''))
c('resource_blocking canonical','access_active' in sc.get('resource_blocking','') and 'CANCELLED' in sc.get('resource_blocking','') and 'start_at' in sc.get('resource_blocking',''))
c('All resource blocking conflicts','reactivate_application_non_elapsed_reactivation_conflict_relevant_children' in sc.get('engine_used_by',[]) and 'not only Current Round' in txt('16_AI_REVIEW_AND_BUILD_PROMPT.md'))
for f in ['02_ROLES_PERMISSIONS_AND_NAVIGATION.md','39_SECURITY_RLS_MATRIX.md','59_RLS_POLICY_BLUEPRINT.md','logic_validation/33_PERMISSION_MODEL_FINAL.md']:
    tt=txt(f); c('Parent Application access '+f,'application.is_active' in tt.lower() or 'Application.is_active' in tt)
sql=txt('database_schema.sql')
c('SQL access_active view','create or replace view private.access_active_interviews' in sql and 'a.is_active = true and i.is_active = true' in sql)
c('SQL resource_blocking view','create or replace view private.resource_blocking_interviews' in sql and "schedule_status_code <> 'CANCELLED'" in sql and 'start_at is not null' in sql)
c('SQL no legacy effective view','private.effective_interviews' not in sql)
c('Current view uses access_active','from private.access_active_interviews i1' in sql)
c('Data model no overloaded effective_interview_active','effective_interview_active' not in txt('08_DATA_MODEL_AND_FIELD_DICTIONARY.md'))
c('Data model canonical predicates',all(x in txt('08_DATA_MODEL_AND_FIELD_DICTIONARY.md') for x in ['`access_active =','`current_round`','`resource_blocking =']))
c('Data model durable identity','globally unique across active/inactive history' in txt('08_DATA_MODEL_AND_FIELD_DICTIONARY.md'))
c('Schema matrix durable identity all fields','durable identity: Submission/Unit/Team/Position' in txt('54_SCHEMA_CONFORMANCE_MATRIX.md'))

# Privacy form/edit/immutability
privacy=app.get('privacy',{})
c('Privacy server authority',privacy.get('notice_authority')=='SERVER_PUBLISHED_VERSION_PINNED_TO_FORM_SESSION')
c('Privacy edit required',privacy.get('edit_acknowledgement_required') is True and 'Save requires acknowledgement of that exact version' in contract)
c('Privacy current/effective fail closed','is_current=true AND effective_from<=now()' in privacy.get('form_session_notice_selection','') and 'PRIVACY_NOTICE_UNAVAILABLE' in contract)
c('Start form explicitly pins notice','start_candidate_form_session' in contract and 'presented_privacy_notice_version' in contract and 'effective_from<=now()' in contract)
c('Candidate form session notice NOT NULL','presented_privacy_notice_version text not null' in sql)
c('Candidate EDIT base version NOT NULL condition',"mode_code = 'EDIT_SUBMISSION' and target_submission_id is not null and base_submission_version_no is not null" in sql)
c('Candidate NEW base version NULL condition',"mode_code = 'NEW_SUBMISSION' and target_submission_id is null and base_submission_version_no is null" in sql)
c('Privacy immutable trigger','protect_published_privacy_notice' in sql and 'PUBLISHED_PRIVACY_NOTICE_IMMUTABLE_CREATE_NEW_VERSION' in sql and 'privacy_notice_immutable_guard' in sql)
c('Privacy docs immutable','Once published' in txt('42_PRIVACY_RETENTION_COMPLIANCE.md') and 'immutable' in txt('42_PRIVACY_RETENTION_COMPLIANCE.md'))
c('DS Edit privacy','EDIT_SUBMISSION' in dtxt('PAGE_OVERRIDES_V1_8.md') and 'Save disabled until acknowledged' in dtxt('PAGE_OVERRIDES_V1_8.md'))

# Candidate update notification/cache/version
candup=app.get('candidate_update',{})
c('Candidate Update notification same txn',candup.get('hr_notification')=='OUTBOX_SAME_TRANSACTION_EXACT_SUBMISSION' and 'Enqueue exact-`submission_id` HR notification inside the same transaction before commit' in contract)
c('Notification quota cannot roll back',candup.get('notification_quota_must_not_rollback_valid_save') is True and 'must not invalidate or roll back' in contract)
c('Rate Candidate Update rule','Candidate Update system-side-effect rule' in txt('68_RATE_LIMIT_POLICY.md'))
c('Email trace submission FK','submission_id uuid references public.submissions(submission_id) on delete restrict' in sql and app.get('email',{}).get('submission_trace_fk') is True)
c('File-only Save bumps version',app.get('submission',{}).get('file_only_save_bumps_version') is True and 'file-only successful Save' in contract and 'increments `version_no` exactly once' in contract)
c('Version helper trigger-owned','create or replace function private.bump_submission_aggregate_version' in sql and 'set updated_at = now()' in sql and 'set version_no = version_no + 1' not in re.search(r'create or replace function private\.bump_submission_aggregate_version.*?\$\$;',sql,re.S).group(0))
c('Candidate cache helper SQL','create or replace function private.refresh_candidate_current_profile' in sql and 'order by s.submitted_at desc, s.submission_id desc limit 1' in sql)
c('Candidate cache helper contract','refresh_candidate_current_profile(candidate_id)' in contract and 'latest surviving Submission' in contract)
c('Delete Submission refresh cache','refreshes Candidate current profile afterward' in contract or 'refresh Candidate current profile afterward' in contract or 'refreshes Candidate current profile afterward' in contract)

# Participant restore
c('Restore participant current','`RESTORE_OLD_REPORT`' in contract and '`is_current=true`' in contract and '`removed_at=NULL`' in contract)
c('Restore report unarchive','`is_active=true`, `is_archived=false`' in contract)
c('Restore preserves decision metadata','preserve content and original `decision_updated_at/by`' in contract)
c('Create new report keeps history','old Participant/report stay historical/archived' in contract)

# Durable application identity
application=app.get('application',{})
c('Application durable global',application.get('identity_semantics')=='DURABLE_GLOBAL_IDENTITY' and application.get('duplicate_identity_rows_allowed') is False)
c('Application global unique SQL','create unique index if not exists application_durable_identity_uq' in sql and 'where is_active' not in re.search(r'create unique index if not exists application_durable_identity_uq.*?;',sql,re.S).group(0).lower())
c('Application identity immutable SQL','APPLICATION_DURABLE_IDENTITY_IMMUTABLE' in sql)
c('Application no active partial old index','active_application_identity_uq' not in sql)
c('Application exact same reuses row','Exact duplicate active or inactive resolves to the same row' in contract)
c('AC reactivate no impossible duplicate','another active identical Application' not in acc)

# Internal user maintenance hard delete / delete matrix
matrix=txt('logic_validation/35_DELETE_INACTIVE_MATRIX.md')
c('Internal User maintenance-only matrix','Internal User | **MAINTENANCE_ONLY**' in matrix)
c('Internal User no normal delete command','delete_unused_internal_user' not in [x.get('command') for x in reg.get('commands',[])])
c('Internal User maintenance contract','maintenance-only' in contract.lower() and 'unbound' in contract.lower() and 'non-root' in contract.lower())
c('Internal User no hard-delete Design UI','does **not** expose Internal User hard-delete' in dtxt('PAGE_OVERRIDES_V1_8.md'))
c('Application empty Round1 matrix','auto-created structurally-empty Round 1' in matrix)

# Upload/malware/email wording
c('AC54 frozen upload','PDF/DOC/DOCX/PPT/PPTX/PNG/JPG/JPEG' in acc and 'max 5 MB/file' in acc and 'malware `CLEAN` mandatory' in acc)
c('AC54 no pending approval','owner/IT-approved' not in re.search(r'\*\*AC-54 Upload policy\*\*.*',acc).group(0))
uat=txt('45_PRODUCTION_UAT_GATE.md').lower()
c('Malware mandatory UAT','scanner fail-closed evidence' in uat and 'production malware scanning is mandatory' in uat)
c('No malware if-enabled stale','malware/quarantine rule if enabled' not in uat)
# Email semantics across current normative sources
current_norm=[]
for d in sreg.get('documents',[]):
    if d.get('status')=='CURRENT' and d.get('normative') and (B/d.get('file','')).exists(): current_norm.append(d['file'])
curtext='\n'.join(txt(f).lower() for f in current_norm)
for bad in ['prevents duplicate sends','retries do not duplicate sends','retry must not create duplicate messages']:
    c('No forbidden email wording '+bad,bad not in curtext)
c('Email at-least-once current','at-least-once' in txt('43_EMAIL_DELIVERY_SPEC.md').lower() and 'logical outbox enqueue' in txt('11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md').lower())
c('Email outbox before commit','inside the same candidate submit/update transaction before commit' in txt('11_EMAIL_DOCUMENTS_AND_ACTIVITY_LOG.md').lower())

# Command registry presence + side effects + acceptance
cmds=[x.get('command') for x in reg.get('commands',[]) if x.get('command')]
c('Command registry version 1.17',str(reg.get('version'))=='1.17')
c('Command registry count 59',len(cmds)==59,f'commands={len(cmds)}')
c('Command names unique',len(cmds)==len(set(cmds)))
coverage=txt('55_COMMAND_COVERAGE_MATRIX.md')
missing_contract=[x for x in cmds if x not in contract]
missing_cov=[x for x in cmds if x not in coverage and x!='root_admin_break_glass_recovery']
c('Registry commands in contract',not missing_contract,str(missing_contract))
c('Registry commands in coverage',not missing_cov,str(missing_cov))
missing_ac=[]
for q in reg.get('commands',[]):
    for aid in q.get('acceptance',[]):
        if aid not in acc:missing_ac.append((q.get('command'),aid))
c('Registry acceptance references exist',not missing_ac,str(missing_ac[:20]))
by={x['command']:x for x in reg.get('commands',[]) if x.get('command')}
required_effects={
'start_candidate_form_session':{'pin_current_effective_privacy_notice','capture_base_submission_version_for_edit'},
'update_candidate_submission':{'privacy_acknowledgement','enqueue_hr_notification_exact_submission','refresh_candidate_current_profile_if_latest','bump_submission_aggregate_version'},
'reactivate_application':{'revalidate_non_elapsed_reactivation_conflict_relevant_children','restore_access_active','recalculate_submission_status'},
'readd_interview_participant':{'restore_or_create_participant_report','revalidate_schedule_conflict_when_resource_blocking'},
'delete_unused_candidate':{'cancel_open_form_sessions','durable_storage_cleanup_enqueue'},
'delete_unused_submission':{'reject_retained_production_email_usage','refresh_candidate_current_profile'},
}
for cmd,effects in required_effects.items():
    have=set(by.get(cmd,{}).get('side_effects',[])); c('Side effects '+cmd,effects<=have,f'missing={sorted(effects-have)}')

# Permissions: fail if parser finds zero
try:
    rows=list(csv.DictReader(txt('permissions_matrix.csv').lstrip('\ufeff').splitlines()))
except Exception: rows=[]
c('Permission matrix parses nonzero',len(rows)>0 and 'capability' in (rows[0].keys() if rows else []),f'rows={len(rows)}')
sql_perms=set(re.findall(r"\('([a-z0-9_.]+)'\s*,\s*'",sql))
seed_perms={x.get('code') for x in seed.get('permissions',[]) if isinstance(x,dict) and x.get('code')}
c('Permission SQL/seed nonzero',len(sql_perms)>0 and len(seed_perms)>0,f'sql={len(sql_perms)} seed={len(seed_perms)}')
c('Permission SQL/seed alignment',sql_perms==seed_perms,f'sql_only={sorted(sql_perms-seed_perms)} seed_only={sorted(seed_perms-sql_perms)}')
for perm in ['candidates.delete_unused','emails.history_delete','applications.manage','submissions.status']:
    c('Permission '+perm,perm in sql_perms and perm in coverage)

# SQL duplicate definitions/columns
col_dups=[]
for m in re.finditer(r'create table if not exists\s+([\w.]+)\s*\((.*?)\);',sql,re.S|re.I):
    cols=[]
    for line in m.group(2).splitlines():
        line=line.strip()
        if not line or line.lower().startswith(('constraint ','primary ','unique ','check ','foreign ','or ','and ',')')):continue
        mm=re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+',line)
        if mm:cols.append(mm.group(1).lower())
    d=sorted({x for x in cols if cols.count(x)>1})
    if d:col_dups.append((m.group(1),d))
c('SQL no duplicate table columns',not col_dups,str(col_dups))
for label,pat in [('table',r'create table if not exists\s+(?:public\.)?([a-zA-Z0-9_]+)'),('function',r'create or replace function\s+(?:private\.|public\.)?([a-zA-Z0-9_]+)'),('trigger',r'create trigger\s+([a-zA-Z0-9_]+)')]:
    names=re.findall(pat,sql,re.I); d=sorted({x for x in names if names.count(x)>1}); c('SQL no duplicate '+label,not d,str(d))

# Source semantic currentness - current docs may mention review baseline in explicitly historical/baseline phrasing.
for f in ['FINAL_REVIEW_GUIDE.md','16_AI_REVIEW_AND_BUILD_PROMPT.md','52_TECHNICAL_GATE_STATUS.md']:
    tt=txt(f)
    c('No old gate as current '+f,'74_TECHNICAL_PRECODE_GATE_V1_7.md' not in tt)
    c('No old design current '+f,'Design System: v1.6 CURRENT' not in tt and 'Technical Architecture v1.7' not in tt)

# Security / operational policies
c('Rate policy concrete','OTP request' in txt('68_RATE_LIMIT_POLICY.md') and 'Retry-After' in txt('68_RATE_LIMIT_POLICY.md') and 'TBD' not in txt('68_RATE_LIMIT_POLICY.md'))
sec=txt('67_WEB_SECURITY_BASELINE.md').lower()
for tok in ['content-security-policy','frame-ancestors','referrer-policy','permissions-policy','hsts','csrf','cors','cache-control','redaction']:
    c('Web security '+tok,tok in sec)
run=txt('66_DATA_EXPORT_ARCHIVE_PURGE_RUNBOOK.md')
for tok in ['approval','SHA-256','restore','purge','encrypt','Storage']:
    c('Archive runbook '+tok,tok.lower() in run.lower())
c('Dependency baseline policy','package.json' in txt('76_DEPENDENCY_BASELINE_POLICY.md') and 'lockfile' in txt('76_DEPENDENCY_BASELINE_POLICY.md'))
c('Release click paths','Candidate Edit' in txt('75_RELEASE_EVIDENCE_MATRIX.md') and 'Application Inactive' in txt('75_RELEASE_EVIDENCE_MATRIX.md'))
c('Release breakpoints',all(x in txt('75_RELEASE_EVIDENCE_MATRIX.md') for x in ['375','768','1280','1440']))
c('Release a11y evidence','keyboard' in txt('75_RELEASE_EVIDENCE_MATRIX.md').lower() and 'axe' in txt('75_RELEASE_EVIDENCE_MATRIX.md').lower())


# v1.8 External Review v7 semantic checks
contract=txt('37_BACKEND_COMMAND_CONTRACTS.md'); sql=txt('database_schema.sql'); acc=txt('13_ACCEPTANCE_CRITERIA_AND_TEST_CASES.md'); coverage=txt('55_COMMAND_COVERAGE_MATRIX.md')
by={x['command']:x for x in reg.get('commands',[]) if x.get('command')}

# P0-01 exactly one report status writer + note-only command
status_writers=[q.get('command') for q in reg.get('commands',[]) if 'interviews.report_status_code' in q.get('writes',[])]
single_status_writers=[x for x in status_writers if not str(x).startswith('bulk_')]
batch_status_writers=[x for x in status_writers if str(x).startswith('bulk_')]
c('One single-record report_status writer',single_status_writers==['change_report_status'],str(single_status_writers))
c('One explicit batch report_status writer',batch_status_writers==['bulk_change_report_status'],str(batch_status_writers))
c('HR note command exists','update_hr_report_note' in by and 'update_hr_report_management' not in by)
c('Coverage report status split','| HR Report Status |' in coverage and '| HR Report Note |' in coverage and 'update_hr_report_note' in coverage)
c('Contract status single writer','single trusted mutation path' in contract.lower() and 'update_hr_report_note' in contract)

# P1-01 exhaustive outcome side-effects
outcome_effects={
 'create_or_update_application':{'recalculate_submission_status'},
 'delete_or_inactivate_application':{'recalculate_submission_status'},
 'create_next_interview_round':{'recalculate_submission_status_when_current_changes'},
 'reactivate_interview':{'recalculate_submission_status_when_current_changes'},
 'delete_or_inactivate_interview':{'recalculate_submission_status_when_outcome_changes'},
 'change_report_status':{'recalculate_submission_status'},
 'set_candidate_active':{'recalculate_all_candidate_submissions_by_reactivation_rule'},
 'reactivate_application':{'recalculate_submission_status'},
 'bulk_create_or_update_applications':{'recalculate_affected_submission_statuses'},
}
for cmd,effects in outcome_effects.items():
    have=set(by.get(cmd,{}).get('side_effects',[])); c('Outcome side effects '+cmd,effects<=have,f'missing={sorted(effects-have)}')

# P0-02 staged current-target adversarial invariant
c('SQL stage current-target guard','replace/delete requires exactly one current version' in sql)
c('SQL save current-target recheck','target no longer has exactly one current version' in sql and 'for update of v' in sql.lower())
c('Contract HR current-target recheck','REPLACE/DELETE may target only a logical header with exactly one current version' in contract)
for aid in ['AC-DOC-TARGET-01','AC-DOC-TARGET-02','AC-DOC-TARGET-03','AC-DOC-TARGET-04']:
    c('Acceptance '+aid,aid in acc)

# P0-03 current canonical blocks in place
roles=txt('02_ROLES_PERMISSIONS_AND_NAVIGATION.md'); ui=txt('10_UI_UX_SPEC.md'); dd=txt('08_DATA_MODEL_AND_FIELD_DICTIONARY.md')
c('Interviewer predicate parent active in main block','application.is_active = true' in roles and roles.find('application.is_active = true') < roles.find('## 4. Candidate'))
c('No old Candidate selector block','Candidate selector searches:' not in ui and '`Ứng tuyển` uses a dedicated **SubmissionSelector**' in ui)
c('Document version no duplicated parent/type','A version row does **not** duplicate `submission_id` or `document_type_id`' in dd and 'Document version record:' not in dd)

# P1-02 Email History exact permissions/context/eligibility
c('Email history view permission SQL',"('emails.history_view'" in sql)
c('Email delete requires view dependency',"('emails.history_delete','emails.history_view')" in sql)
c('Email history environment code','create table if not exists public.email_history' in sql and 'environment_code' in re.search(r'create table if not exists public.email_history.*?\);',sql,re.S).group(0))
c('Email delete command contextual','parent contextual read permission' in contract and 'TEST_RECORD' in contract and 'WRONG_RECORD' in contract)
for aid in ['AC-EMAIL-HIST-01','AC-EMAIL-HIST-02']:
    c('Acceptance '+aid,aid in acc)

# P1-03 Active owner lifecycle
c('Application owner trigger includes active','update of submission_id, unit_id, department_team_id, position_id, hr_owner_id, is_active' in sql)
c('Owner lifecycle DB guard','ACTIVE_APPLICATION_OWNER_REASSIGN_REQUIRED' in sql and 'hr_role_owner_lifecycle_guard' in sql)
c('Owner lifecycle contract','Operational owner invariant' in contract and 'reassigned atomically' in contract)
for aid in ['AC-OWNER-LIFE-01','AC-OWNER-LIFE-02']:
    c('Acceptance '+aid,aid in acc)

# P1-04 past-only reactivation
c('Past reactivation predicate','reactivation_conflict_relevant' in txt('73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md') and 'end_at > transaction_now' in txt('73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md'))
c('Reactivate ignores elapsed','fully elapsed' in contract.lower() and 'does not block lifecycle reactivation' in contract.lower())
c('AC past reactivate','AC-APP-REACT-PAST-01' in acc)

# P1-05 permission-detail visibility
sec=txt('39_SECURITY_RLS_MATRIX.md'); dpage=dtxt('PAGE_OVERRIDES_V1_8.md')
c('Non-root permission detail hidden','not another user' in sec.lower() or "does not grant visibility into another user's granular" in sec.lower())
c('Design persona-specific permission column','Non-root Directory Manager' in dpage and 'no other-user granular permission details' in dpage)
c('AC permission visibility','AC-PERM-VIEW-01' in acc)

# P1-06 privacy publication runbook
run78=txt('78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md')
for tok in ['is_current=false','effective_from <= transaction_now','one transaction','rollback']:
    c('Privacy publish '+tok,tok.lower() in run78.lower())
c('Privacy publication referenced','78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md' in contract and '78_PRIVACY_NOTICE_PUBLICATION_RUNBOOK.md' in txt('42_PRIVACY_RETENTION_COMPLIANCE.md'))
c('AC privacy publish','AC-PRIV-PUBLISH-01' in acc)

# P1-07 candidate inactive metadata
candtbl=re.search(r'create table if not exists public.candidates.*?\);',sql,re.S).group(0)
c('Candidate inactive DB check','candidate_inactive_metadata_ck' in candtbl)
c('Candidate inactive contract','inactive_at=now()' in contract and 'clear `inactive_at/inactive_by`' in contract)
c('AC candidate inactive','AC-CAND-INACTIVE-01' in acc)

# P1-08 version coherence
c('Schema header v1.17',sql.startswith('-- App Tuyển dụng EIU\n-- Technical starter schema v1.17 — 2026-09-03'))
c('Design README tracks Full v1.17','Full Handover v1.17' in dtxt('00_README.md'))

# P1-09 report lifecycle DB check
reporttbl=re.search(r'create table if not exists public.interview_reports.*?\);',sql,re.S).group(0)
c('Report lifecycle DB check','interview_report_lifecycle_ck' in reporttbl and 'is_active = true and is_archived = false' in reporttbl and 'is_active = false and is_archived = true' in reporttbl)
c('AC report lifecycle','AC-REPORT-LIFE-01' in acc)

# P1-10 behavior acceptance / guarantee tags
for cmd,tags in {
 'change_report_status':{'single_report_status_writer','current_round_only','same_transaction_submission_recalc'},
 'update_hr_report_note':{'hr_only_note','no_report_status_write'},
 'delete_email_history':{'test_only_if_test_environment','wrong_requires_reason'},
}.items():
    have=set(by.get(cmd,{}).get('guarantees',[])); c('Guarantees '+cmd,tags<=have,f'missing={sorted(tags-have)}')


# v1.9 P2/current-source consolidation hardening
c('Zero UUID Team sentinel reserved','department_team_zero_uuid_reserved_ck' in sql and "department_team_id <> '00000000-0000-0000-0000-000000000000'::uuid" in sql)
c('Zero UUID invariant documented','Zero-UUID Team sentinel' in txt('40_DATABASE_INVARIANTS.md'))
readme=txt('00_README.md')
c('README current review path only','97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md' in readme and '98_TECHNICAL_PRECODE_GATE_V1_17.md' in readme and '72_EXTERNAL_REVIEW_V5_RESOLUTION.md' not in readme and '74_TECHNICAL_PRECODE_GATE_V1_7.md' not in readme)
c('Owner decisions current v1.17','Current status (v1.17)' in txt('50_OWNER_DECISIONS_PENDING.md') and 'v1.16 independent implementation-readiness review' in txt('50_OWNER_DECISIONS_PENDING.md'))
c('UI spec Design v1.8',txt('10_UI_UX_SPEC.md').startswith('# 10. UI/UX Specification — aligned with Design System v1.8'))
legacy_heading_patterns=[r'^## v1\.\d',r'^## Explicit trusted-command addendum — current v1\.',r'^## Inherited .*current in v1\.',r'^## Current .*— v1\.']
current_norm=[d.get('file') for d in sreg.get('documents',[]) if d.get('status')=='CURRENT' and d.get('normative') and str(d.get('file','')).endswith('.md')]
legacy_hits=[]
for f in current_norm:
    if f in {'00_README.md','96_TECHNICAL_PRECODE_GATE_V1_16.md'}: continue
    for i,line in enumerate(txt(f).splitlines(),1):
        if any(re.search(pat,line,re.I) for pat in legacy_heading_patterns): legacy_hits.append(f'{f}:{i}:{line}')
c('Current normative amendment headings consolidated',not legacy_hits,'; '.join(legacy_hits[:12]))
# P2 DB format/actor hardening evidence
c('Audit at-most-one human actor','activity_one_human_actor_ck' in sql and 'security_audit_one_human_actor_ck' in sql)
c('SHA256 format checks',sql.count("~ '^[0-9A-Fa-f]{64}$'") >= 3)

# Source/current version registry
c('Source registry v1.17',str(sreg.get('version'))=='1.17' and sreg.get('technical_architecture')=='1.17' and sreg.get('design_system')=='1.8')
c('Current review/gate pointers',sreg.get('current_review_resolution')=='97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md' and sreg.get('current_precode_gate')=='98_TECHNICAL_PRECODE_GATE_V1_17.md')
current_baseline_text='\n'.join(txt(f) for f in current_norm)
stale_current_patterns=[r'Technical Architecture v1\.9',r'Responsive Prototype v1\.5',r'80_EXTERNAL_REVIEW_V7_RESOLUTION\.md',r'82_TECHNICAL_PRECODE_GATE_V1_9\.md',r'332/332',r'299/299',r'65/65',r'54 unique',r'Review 77',r'Gate 79']
stale_current_hits=[pat for pat in stale_current_patterns if re.search(pat,current_baseline_text,re.I)]
c('CURRENT/NORMATIVE baseline assertions are v1.14 coherent',not stale_current_hits,', '.join(stale_current_hits))
c('Review v6 matrix resolution',all(rid in txt('technical_review_matrix.csv') and 'RESOLVED_V1_9' in next((line for line in txt('technical_review_matrix.csv').splitlines() if line.startswith(rid+',')),'') for rid in ['RV7-P0-01','RV7-P0-02','RV7-P0-03','RV7-P1-01','RV7-P1-10']))

# Design validator + cross design
design_cmd=[sys.executable,str(DS/'tools/validate_design.py')]+(['--no-write'] if a.no_write else [])
proc=subprocess.run(design_cmd,capture_output=True,text=True)
c('Design validator passes',proc.returncode==0,(proc.stdout+proc.stderr).splitlines()[1] if (proc.stdout+proc.stderr).splitlines() else '')
c('DS current 1.8',dtxt('00_README.md').startswith('# EIU Recruitment Design System v1.8'))
c('DS page override Edit privacy','EDIT_SUBMISSION' in dtxt('PAGE_OVERRIDES_V1_8.md'))
c('DS 200/400 a11y','200% text zoom' in dtxt('ACCESSIBILITY.md') and '400% reflow' in dtxt('ACCESSIBILITY.md'))

# Responsive prototype v1.10 cross-layer evidence
c('Responsive dir exists',RP.exists())
c('Responsive version v1.10','v1.10' in rtxt('VERSION.md') and 'v1.10' in rtxt('README.md'))
c('Responsive loads v17 code','responsive-v17.css' in rtxt('index.html') and 'responsive-v17.js' in rtxt('index.html') and 'responsive-v16.js' in rtxt('index.html'))
c('Responsive status anchored not pointer','getBoundingClientRect' in rtxt('responsive-v15.js') and 'clientX' not in rtxt('responsive-v15.js') and 'clientY' not in rtxt('responsive-v15.js'))
c('Responsive outside dismiss','pointerdown' in rtxt('responsive-v15.js') and 'closeStatusMenu' in rtxt('responsive-v15.js'))
c('Responsive Escape dismiss',"event.key==='Escape'" in rtxt('responsive-v15.js'))
c('Responsive badge benchmark documented','144px' in rtxt('RESPONSIVE_CONTRACT_v1.4.md'))
c('Responsive v1.5 retained QA evidence','57/57 PASS' in rtxt('RESPONSIVE_BROWSER_QA_v1.5.md') and '0 FAIL' in rtxt('RESPONSIVE_BROWSER_QA_v1.5.md'))
c('Responsive v1.10 current browser QA evidence','FAIL=0' in rtxt('RESPONSIVE_BROWSER_QA_v1.10.md') and '"version": "1.10"' in rtxt('RESPONSIVE_QA_RESULTS_v1.10.json') and '"fail": 0' in rtxt('RESPONSIVE_QA_RESULTS_v1.10.json'))
c('Responsive v1.10 QA runner current',(RP/'tools/validate_responsive_v110.py').exists() and 'responsive-v110.js' in rtxt('tools/validate_responsive_v110.py'))
c('Responsive integrated current doc','Responsive Prototype v1.10' in txt('81_RESPONSIVE_PROTOTYPE_INTEGRATION.md'))

# External Review v7 direct checks
c('Manual NEW/READ active Application blocked','CANNOT_SET_MANUAL_STATUS_WHILE_ACTIVE_APPLICATION_EXISTS' in sql and 'Neither `NEW` nor `READ` may be written manually while any active Application exists' in contract)
c('Reactivate-only predicate canonical','reactivation_conflict_relevant' in txt('73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md') and 'Application Reactivate-only' in txt('73_DOMAIN_GLOSSARY_AND_CANONICAL_PREDICATES.md') and 'schedule_conflict_relevant' not in '\n'.join(txt(f) for f in current_norm))
for cmd in ['bulk_set_candidate_active','bulk_set_latest_submission_manual_status','bulk_delete_or_inactivate_interviews','bulk_change_interview_schedule_status','bulk_change_report_status']:
    c('Named batch '+cmd,cmd in by and cmd in contract and cmd in coverage and cmd in txt('63_BATCH_OPERATION_SEMANTICS.md'))
c('Active master DB guard','validate_active_master_references' in sql and all(x in sql for x in ['application_active_master_guard','position_active_master_guard','education_active_master_guard','submission_source_active_master_guard','interview_active_master_guard']))
c('Readd active user DB guard','USER_INACTIVE_NOT_SELECTABLE' in sql and 'validate_participant_lifecycle_and_user' in sql)
c('Future participant deactivation guard','FUTURE_INTERVIEW_PARTICIPANT_REASSIGN_REQUIRED' in sql and 'FUTURE_INTERVIEW_PARTICIPANT_REASSIGN_REQUIRED' in contract)
c('Form Session same Candidate guard','validate_form_session_candidate_owner' in sql and 'FORM_SESSION_SUBMISSION_CANDIDATE_MISMATCH' in sql)
c('Privacy DELETE guard','privacy_notice_delete_guard' in sql and 'protect_published_privacy_notice_delete' in sql)
c('Structurally empty Round1 helper','private.is_structurally_empty_default_round' in sql and 'private.is_structurally_empty_default_round' in contract)
c('Participant lifecycle DB guard','participant_lifecycle_user_guard' in sql and 'PARTICIPANT_LIFECYCLE_INVALID' in sql)
c('Candidate verified email immutable','candidate_verified_email_immutable_guard' in sql and 'CANDIDATE_VERIFIED_EMAIL_IMMUTABLE' in sql)
c('Implementation notes use source registry','source_registry.yaml' in txt('12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md') and '37–50' not in txt('12_IMPLEMENTATION_NOTES_VERCEL_SUPABASE.md'))
c('Outbox actor check','email_outbox_one_human_actor_ck' in sql)
c('Production email trace blocks maintenance Submission delete','retained PRODUCTION' in contract and 'blocks `delete_unused_submission()`' in contract and 'MAINTENANCE_ONLY' in contract)


# v1.10 implementation-alignment semantic checks
r16=rtxt('responsive-v16.js')
r17=rtxt('responsive-v17.js')
r19=rtxt('responsive-v19.js')
appjs=rtxt('app.js')
c('Submission demo has no INACTIVE workflow',"status:'INACTIVE'" not in appjs)
c('Candidate lifecycle separated in v16','candidateLifecycleV16' in r16 and 'inactivation did not overwrite Submission status' in r16)
c('Candidate parent derives deterministic latest Submission','latestSubmissionV16' in r16 and 'submissionStatusBadgeV16' in r16)
c('Candidate bulk manual command selection aligned','bulk_set_latest_submission_manual_status' in contract and 'candidate_ids' in contract and 'expected_latest_submission_ids' in contract and 'bulk_set_latest_submission_manual_status' in cmds)
c('Legacy bulk Mark New removed','bulk_mark_submission_new' not in cmds and 'bulk_mark_submission_new' not in contract)
newbulk=by.get('bulk_set_latest_submission_manual_status',{})
c('Bulk latest Submission guarantees',newbulk.get('selection_entity')=='candidate' and {'ALL_OR_NOTHING','candidate_selection_entity','NEW_OR_READ_ONLY','no_active_application_for_manual_state','latest_submission_preview_revalidated'} <= set(newbulk.get('guarantees',[])))
c('Responsive bulk Candidate all-or-nothing','bulkSetLatestSubmissionStatusV17' in r17 and "entity==='bulk-latest-submission'" in r17 and "['NEW','READ']" in r17)
c('Historical Submission read-only','Historical Submissions are read-only' in r16)
navblock=re.search(r"refreshNavConfig = function\(\)\{(.*?)\n\};",r16,re.S)
c('Phase1 nav excludes future routes',bool(navblock) and all(x not in navblock.group(1) for x in ['Dashboard','Reports & Analytics','Positions','Units','Candidate Sources','System Settings','Documents','Settings']))
appblock=re.search(r"applicationsPage = function\(\)\{(.*?)\n\};",r16,re.S)
c('Application Inbox unsupported bulk removed',bool(appblock) and 'prototypeDelete' not in appblock.group(1) and 'Gửi thư ứng viên' not in appblock.group(1) and "icon('trash')" not in appblock.group(1))
drawerblock=re.search(r"hrReportDrawer=function\(aid\)\{(.*?)\n\};",r16,re.S)
c('Aggregate report drawer has no generic Delete',bool(drawerblock) and "icon('trash')" not in drawerblock.group(1) and "tx('Xóa','Delete')" not in drawerblock.group(1))
c('Current Interview owns Report Status','r.reportStatus=status' in r16 and 'Application outcome was not written directly' in r16)
c('Decision-specific timestamp used','decisionUpdatedAt' in r16 and 'decisionChanged' in r16 and 'reportSourceV16' in r16)
c('Candidate CV required authoritative UI','candidateCvIsValidV16' in r16 and "state.candidateFormError='CV_REQUIRED'" in r16)
c('Candidate EDIT staged document operations',all(x in r16 for x in ['ADD','REPLACE','DELETE','cancelCandidateFormV16','stageDeleteCvV16','stageCvV16']))
c('Internal email exact-domain DB check',"internal_email_domain_ck check (lower(email::text) ~ '^[^@[:space:]]+@eiu\\.edu\\.vn$')" in sql and "like '%@eiu.edu.vn'" not in sql.lower())
critical=crit.get('critical_controls',[]) if isinstance(crit,dict) else []
c('Critical controls declare semantics',bool(critical) and all(x.get('control_id') and x.get('page') and x.get('action') and x.get('expected_transition') and x.get('permission') for x in critical))
c('Critical control no generic-toast criterion','generic toast-only fallback is insufficient' in str(crit.get('rule','')).lower())

# External Review v8 targeted semantic validators
single_status=by.get('change_interview_schedule_status',{})
bulk_status=by.get('bulk_change_interview_schedule_status',{})
c('V8 batch Interview status permission parity',single_status.get('permission')=='interviews.status' and bulk_status.get('permission')=='interviews.status' and 'interviews.status` + view' in coverage)
c('V8 permissions matrix granular split','Manage Interview,No,Yes,If interviews.manage,' in txt('permissions_matrix.csv') and 'Change Interview Status,No,Yes,If interviews.status,' in txt('permissions_matrix.csv'))
c('V8 app_spec version coherence retained in v1.17',app.get('version')=='1.17' and prod.get('document_version')=='1.17' and prod.get('technical_architecture',{}).get('version')=='1.17' and app.get('responsive_prototype',{}).get('version')=='1.10')
c('V8 legacy Mark New structured key removed','mark_submission_new' not in app.get('bulk_semantics',{}) and app.get('bulk_semantics',{}).get('submission_manual_status')=='ALL_OR_NOTHING')
open_cmd=by.get('open_submission',{}); open_auth=open_cmd.get('authorization',{}) or {}; cm=open_auth.get('conditional_mutation',{}) or {}
c('V8 open_submission conditional metadata',open_auth.get('base_permission')=='submissions.view' and cm.get('permission')=='submissions.status' and cm.get('transition')=='NEW_TO_READ' and 'submissions.status_code' in cm.get('writes',[]))
rep_cmd=by.get('save_interviewer_report',{}); rep_auth=rep_cmd.get('authorization',{}) or {}; rep_branches=rep_auth.get('any_of',[]) or []
c('V8 interviewer report OR authorization',rep_cmd.get('permission')=='CONDITIONAL_OR' and any(b.get('branch')=='interviewer_own_report' and 'current_participant_context' in b.get('requires',[]) and 'own_report_only' in b.get('requires',[]) for b in rep_branches) and any(b.get('branch')=='authorized_hr' and {'reports.view','reports.edit_interviewer'} <= set(b.get('requires',[])) for b in rep_branches))
c('V8 synchronous Form Session expiry SQL','FORM_SESSION_EXPIRED' in sql and 'form_expires_at <= transaction_timestamp()' in sql and 'candidate_form_session_transition_guard' in sql)
c('V8 synchronous Upload Reservation expiry SQL','UPLOAD_RESERVATION_EXPIRED' in sql and 'reservation_expires_at <= transaction_timestamp()' in sql and 'expired_reservation_count' in sql)
c('V8 expiry contract fail-closed','FORM_SESSION_EXPIRED' in contract and 'UPLOAD_RESERVATION_EXPIRED' in contract and 'housekeeping' in contract.lower())
vc_edu=vc.get('collections',{}).get('education_rows',{})
c('V8 Education contract optional',vc_edu.get('min_items')==0 and vc_edu.get('required_fields')==[])
c('V8 prototype Education optional','educationRowsV17' in r17 and 'Education is not required' in r17 and '.education-row-v17 [required]' in rtxt('tools/validate_responsive_v17.py'))
c('V8 NEW Privacy explicit default','state.candidatePrivacyAckV17=(mode===\'EDIT\')' in r17 and 'NEW Privacy starts unchecked' in rtxt('tools/validate_responsive_v17.py'))
c('V8 privacy-only confirmation','no separate accuracy-attestation checkbox' in r17 and 'Không có accuracy-attestation checkbox/DB record thứ hai' in txt('03_CANDIDATE_FORM_AND_PORTAL.md'))
c('V8 inactive Candidate single-bulk parity','Candidate Active/Inactive does not restrict internal HR manual NEW/READ' in contract and app.get('candidate_lifecycle',{}).get('manual_submission_status_requires_candidate_active') is False and 'Bulk inactive Candidate parity succeeds' in rtxt('tools/validate_responsive_v17.py'))
c('V8 Form Session lifecycle machine contract',vc.get('candidate_form_session_lifecycle',{}).get('terminal_reopen_allowed') is False and app.get('candidate_form_session',{}).get('terminal_reopen_allowed') is False)
c('V8 current START_HERE gate wording retained in v1.17','Technical Architecture v1.17 — TECHNICAL SPECIFICATION FROZEN' in (B.parent/'START_HERE.txt').read_text() and 'Technical Architecture v1.17: **TECHNICAL SPECIFICATION FROZEN**' in txt('52_TECHNICAL_GATE_STATUS.md') and 'Implementation Gate: **READY TO IMPLEMENT**' in txt('52_TECHNICAL_GATE_STATUS.md'))
c('V8 review matrix resolved',all(rid in txt('technical_review_matrix.csv') and 'RESOLVED_V1_11' in next((line for line in txt('technical_review_matrix.csv').splitlines() if line.startswith(rid+',')),'') for rid in ['RV8-P0-01','RV8-P0-02','RV8-P1-01','RV8-P1-02','RV8-P1-03','RV8-P1-04','RV8-P1-05','RV8-P1-06','RV8-P1-07','RV8-P1-08','RV8-P1-09']))
c('V9 review matrix resolved',all(rid in txt('technical_review_matrix.csv') and 'RESOLVED_V1_12' in next((line for line in txt('technical_review_matrix.csv').splitlines() if line.startswith(rid+',')),'') for rid in ['RV9-P0-01','RV9-P0-02','RV9-P0-03','RV9-P1-01','RV9-P1-02','RV9-P1-03','RV9-P1-04','RV9-P1-05','RV9-P1-06','RV9-P1-07']))

# External Review v10 cross-layer validators
vc_edu=vc.get('collections',{}).get('education_rows',{})
c('V10 Education SQL nullable parity',vc_edu.get('required_fields')==[] and all(x in sql for x in ['period_text text,','qualification_id uuid references public.qualification_levels','major text,','institution text']) and all(x not in sql for x in ['period_text text not null','qualification_id uuid not null references public.qualification_levels','major text not null','institution text not null']))
c('V10 exact SubmissionSelector prototype','applicationSubmissionV19' in r19 and 'submissionId' in r19 and 'Backend never guesses the latest Submission' in r19)
c('V10 selected Participant guard all save paths','CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED' in r19 and '_saveRoundV18V19(type,srcId)' in r19)
c('V10 latest-safe SQL helper','private.set_latest_submission_manual_status' in sql and 'p_candidate_id uuid' in sql and 'p_expected_latest_submission_id uuid' in sql and 'LATEST_SUBMISSION_CHANGED' in sql and 'private.set_submission_manual_status(p_submission_id' not in sql)
usr=by.get('set_internal_user_active',{})
c('V10 user lifecycle registry guard','block_active_application_owner_without_reassignment' in usr.get('side_effects',[]) and 'block_nonelapsed_resource_blocking_current_participant_without_reassignment' in usr.get('side_effects',[]) and 'active_user_lifecycle_cannot_strand_future_current_participant' in usr.get('guarantees',[]))
c('V10 FINAL_REVIEW_GUIDE registered current nonnormative',any(d.get('file')=='FINAL_REVIEW_GUIDE.md' and d.get('status')=='CURRENT' and d.get('normative') is False for d in sreg.get('documents',[])))
c('V10 responsive v1.9 browser evidence',(RP/'tools/validate_responsive_v19.py').exists() and all(x in rtxt('tools/validate_responsive_v19.py') for x in ['Application modal uses exact SubmissionSelector','Create blocks inactive selected Participant','Copy blocks inactive prefilled Participant']))
c('V10 review matrix resolved',all(rid in txt('technical_review_matrix.csv') and 'RESOLVED_V1_13' in next((line for line in txt('technical_review_matrix.csv').splitlines() if line.startswith(rid+',')),'') for rid in ['RV10-P0-01','RV10-P0-02','RV10-P0-03','RV10-P1-01','RV10-P1-02','RV10-P1-03','RV10-P1-04','RV10-P1-05']))
c('V10 validator labels current','Technical version 1.17' in txt('tools/validate_package.py') and 'Responsive prototype v1.10 authority' in dtxt('tools/validate_design.py'))
c('V10 manifest verifier derives labels','TARGETS = [ROOT/\'review_pack\', ROOT/\'design_system\', ROOT/\'responsive_prototype\']' in txt('tools/verify_manifests.py') and "replace('# MANIFEST — ','')" in txt('tools/verify_manifests.py'))

# External Review v11 semantic/database/source checks
vcbase=vc.get('current_baseline',{}) or {}
c('V11 current baseline machine coherence v1.17',vcbase=={'full_handover':'1.17','technical_architecture':'1.17','design_system':'1.8','responsive_prototype':'1.10'} and 'Full Handover v1.17' in txt('critical_control_registry.yaml') and 'Responsive Prototype v1.10' in txt('critical_control_registry.yaml'))
c('V11 nullable Education qualification guard',"new.qualification_id is not null and (tg_op='INSERT' or new.qualification_id is distinct from old.qualification_id)" in sql and 'INACTIVE_QUALIFICATION_NOT_SELECTABLE' in sql)
bulk_status=by.get('bulk_change_interview_schedule_status',{})
c('V11 bulk schedule Active Participant parity','validate_current_participants_operationally_eligible' in bulk_status.get('side_effects',[]) and 'shared_candidate_room_interviewer_conflict_recheck' in bulk_status.get('side_effects',[]) and 'no_resource_blocking_interview_with_inactive_current_participant' in bulk_status.get('guarantees',[]))
c('V11 bulk schedule behavior acceptance',all(x in bulk_status.get('acceptance',[]) for x in ['AC-PART-OPER-BULK-01','AC-BULK-SCH-01','AC-SCH-CANDIDATE-BULK-01','AC-SCH-ROOM-BULK-01','AC-SCH-INTERVIEWER-BULK-01']))
c('V11 bulk schedule critical control',any(x.get('control_id')=='INTERVIEW-BULK-SCHEDULE-STATUS' and x.get('permission')=='interviews.status' for x in crit.get('critical_controls',[])))
interview_src=txt('05_HR_INTERVIEW_PAGE.md')
legacy_react='Application Reactivate re-checks every child that would become resource-blocking before commit.'
c('V11 canonical Reactivate present','NON-ELAPSED' in interview_src and 'reactivation_conflict_relevant = resource_blocking AND end_at > transaction_now' in interview_src and 'Fully elapsed historical intervals do **not** block lifecycle recovery' in interview_src)
c('V11 legacy Reactivate forbidden',legacy_react not in interview_src)
c('V11 user command self-contained participant guard','FUTURE_INTERVIEW_PARTICIPANT_REASSIGN_REQUIRED' in re.search(r'### `set_internal_user_active.*?(?=\n### )',contract,re.S).group(0))
c('V11 responsive README authority',rtxt('README.md').startswith('# EIU Recruitment — Responsive Clickable Prototype v1.10') and 'Full Handover **v1.17**' in rtxt('README.md') and 'Full Handover v1.17' in rtxt('VERSION.md'))
c('V11 current source pointers v1.17',sreg.get('version')=='1.17' and sreg.get('technical_architecture')=='1.17' and sreg.get('current_review_resolution')=='97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md' and sreg.get('current_precode_gate')=='98_TECHNICAL_PRECODE_GATE_V1_17.md')
c('V11 acceptance additions',all(x in acc for x in ['AC-EDU-NULL-01','AC-EDU-NULL-02','AC-EDU-NULL-03','AC-PART-OPER-BULK-01','AC-BULK-SCH-01','AC-SCH-CANDIDATE-BULK-01','AC-SCH-ROOM-BULK-01','AC-SCH-INTERVIEWER-BULK-01','AC-REACT-CANON-01','AC-SOURCE-BASELINE-01','AC-RESP-AUTH-01']))
c('V11 review matrix resolved',all(rid in txt('technical_review_matrix.csv') and 'RESOLVED_V1_14' in next((line for line in txt('technical_review_matrix.csv').splitlines() if line.startswith(rid+',')),'') for rid in ['RV11-P0-01','RV11-P0-02','RV11-P0-03','RV11-P1-01','RV11-P1-02','RV11-P1-03','RV11-P1-04','RV11-P1-05']))

c('V11 validators expose no-write mode',"--no-write" in txt('tools/validate_package.py') and "--no-write" in dtxt('tools/validate_design.py') and "--no-write" in rtxt('tools/validate_responsive_v110.py'))

# External Review v12 executable/storage/machine checks
r110=rtxt('responsive-v110.js')
c('V12 responsive single/bulk schedule status shared validator',all(x in r110 for x in ['validateInterviewOperationalTransitionV110','applyInterviewScheduleStatusV110',"entity==='round'","entity==='bulk-interview'"]))
c('V12 responsive schedule status QA evidence',(RP/'tools/validate_responsive_v110.py').exists() and all(x in rtxt('tools/validate_responsive_v110.py') for x in ['RQA-SCH-STATUS-01','RQA-SCH-STATUS-02','RQA-SCH-STATUS-03','RQA-SCH-STATUS-04','RQA-SCH-STATUS-05','RQA-SCH-STATUS-06','RQA-SCH-STATUS-07']))
c('V12 Interview upload parent FK RESTRICT','upload_reservations_interview_fk foreign key (interview_id) references public.interviews(interview_id) on delete restrict' in sql)
c('V12 Interview upload parent index','upload_reservations_interview_idx' in sql and 'on public.upload_reservations(interview_id)' in sql)
c('V12 durable storage cleanup queue','create table if not exists public.storage_cleanup_queue' in sql and 'storage_cleanup_queue' in txt('37_BACKEND_COMMAND_CONTRACTS.md') and 'storage_cleanup_queue' in txt('41_STORAGE_AND_UPLOAD_SECURITY.md'))
c('V12 Interview delete cleanup semantics',all(x in txt('37_BACKEND_COMMAND_CONTRACTS.md') for x in ['Cleanup-capture failure aborts hard-delete','ON DELETE RESTRICT','storage_cleanup_queue']))
bcand=by.get('bulk_set_candidate_active',{})
c('V12 bulk Candidate lifecycle machine parity',all(x in bcand.get('side_effects',[]) for x in ['set_or_clear_inactive_metadata_per_candidate','recalculate_all_candidate_submissions_by_reactivation_rule','audit_per_candidate','audit_batch_event']) and all(x in bcand.get('writes',[]) for x in ['candidates.is_active','candidates.inactive_at','candidates.inactive_by']))
crit_ids={x.get('control_id'):x for x in crit.get('critical_controls',[])}
c('V12 single Interview status critical control','INTERVIEW-SINGLE-SCHEDULE-STATUS' in crit_ids and crit_ids['INTERVIEW-SINGLE-SCHEDULE-STATUS'].get('permission')=='interviews.status' and bool(crit_ids['INTERVIEW-SINGLE-SCHEDULE-STATUS'].get('browser_qa')))
c('V12 bulk Interview status critical browser evidence','INTERVIEW-BULK-SCHEDULE-STATUS' in crit_ids and bool(crit_ids['INTERVIEW-BULK-SCHEDULE-STATUS'].get('browser_qa')))
c('V12 command-specific batch acceptance',all(x in bcand.get('acceptance',[]) for x in ['AC-BULK-CAND-LIFE-01','AC-BULK-CAND-LIFE-02']) and 'AC-BULK-INT-DEL-01' in by.get('bulk_delete_or_inactivate_interviews',{}).get('acceptance',[]) and 'AC-BULK-REPORT-01' in by.get('bulk_change_report_status',{}).get('acceptance',[]))
c('V14 current review/gate files',status.get('97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md')=='CURRENT' and status.get('98_TECHNICAL_PRECODE_GATE_V1_17.md')=='CURRENT' and status.get('95_INDEPENDENT_PLANNER_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_16.md')=='HISTORICAL' and status.get('96_TECHNICAL_PRECODE_GATE_V1_16.md')=='HISTORICAL')
c('V12 stale current review path forbidden','Reviewer: `89 → 73 → 78 → 81 → 90`' not in txt('00_README.md') and 'v1.12 is the current implementation-contract' not in txt('01_PRODUCT_SCOPE_AND_ARCHITECTURE.md'))
c('V12 internal email whitespace hardening','AC-INT-EMAIL-WS-01' in acc and "internal_email_domain_ck check (lower(email::text) ~ '^[^@[:space:]]+@eiu\\.edu\\.vn$')" in sql)

# Independent Review v1.16 source-sync checks
c('IR16 Copy in app_spec conflict engine','copy_interview_schedule' in sc.get('engine_used_by',[]))
c('IR16 Copy in concurrency shared engine','Save Copy (`copy_interview_schedule`)' in txt('48_IDEMPOTENCY_CONCURRENCY_SPEC.md') and 'shared deterministic Candidate/Room/Interviewer' in txt('48_IDEMPOTENCY_CONCURRENCY_SPEC.md'))
qa_results=json.loads(rtxt('RESPONSIVE_QA_RESULTS_v1.10.json')) if (RP/'RESPONSIVE_QA_RESULTS_v1.10.json').exists() else {}
qa_names=[x.get('name','') for x in qa_results.get('results',[])] if isinstance(qa_results,dict) else []
copy_qa_ids=['RP-COPY-01','RP-COPY-02','RP-COPY-03','RP-COPY-04']
c('IR16 critical Copy browser QA IDs resolve',all(any(name.startswith(qid+' ') for name in qa_names) for qid in copy_qa_ids),str([q for q in copy_qa_ids if not any(name.startswith(q+' ') for name in qa_names)]))
c('IR16 used target Round1 Copy QA exists',any(name.startswith('RP-COPY-02 ') for name in qa_names) and 'qaCopyUsed' in rtxt('tools/validate_responsive_v110.py'))
c('IR16 All-in-One generator label v1.17','GENERATED v1.17' in txt('tools/generate_all_in_one.py'))

# Generated equality
proc=subprocess.run([sys.executable,str(B/'tools/generate_all_in_one.py'),'--check'],capture_output=True,text=True)
c('All-in-One deterministic equality',proc.returncode==0,(proc.stdout if proc.returncode==0 else proc.stdout+proc.stderr).strip())

# Review v5 resolution claims all findings addressed and gate is not frozen
c('v1.17 alignment current','Independent Review' in txt('97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md') and 'CURRENT / NORMATIVE' in txt('97_INDEPENDENT_REVIEW_IMPLEMENTATION_ALIGNMENT_V1_17.md'))
review_matrix=txt('technical_review_matrix.csv')

c('Precode gate v1.17 ready to implement','TECHNICAL SPECIFICATION FROZEN' in txt('98_TECHNICAL_PRECODE_GATE_V1_17.md') and 'READY TO IMPLEMENT' in txt('98_TECHNICAL_PRECODE_GATE_V1_17.md'))
c('Production not ready','Production Ready' in txt('00_README.md') and '**NO**' in txt('00_README.md'))

# v1.12 review-v9 leverage checks
c('Operational participant helper in SQL','private.all_current_participants_selectable' in sql and 'CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED' in sql)
c('Operational participant guard in commands',all('validate_current_participants_operationally_eligible' in str(x.get('side_effects',[])) for x in reg.get('commands',[]) if x.get('command') in ['save_interview_schedule','change_interview_schedule_status','reactivate_interview']))
c('Submission delete maintenance-only',next(x for x in reg.get('commands',[]) if x.get('command')=='delete_unused_submission').get('permission')=='MAINTENANCE_ONLY' and 'submissions.delete_unused' not in txt('permissions_matrix.csv') and 'submissions.delete_unused' not in txt('seed_master_data.json'))
c('Single Submission status latest-only','deterministic latest Submission' in contract and 'historical_submission_status_read_only' in str(next(x for x in reg.get('commands',[]) if x.get('command')=='set_submission_manual_status').get('guarantees',[])))
c('Schedule source has full conflict matrix',all(x in txt('05_HR_INTERVIEW_PAGE.md') for x in ['Candidate overlap','Room overlap','Interviewer overlap','[start_at,end_at)','CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED']))
c('Empty Round helper protects copy provenance','i.copied_from_interview_id is null' in sql and 'child.copied_from_interview_id=i.interview_id' in sql)
c('Critical Candidate auth vocabulary canonical','candidate_own_submission' not in txt('critical_control_registry.yaml') and 'candidate_self' in txt('critical_control_registry.yaml'))
c('Responsive retained schedule/copy override',(RP/'responsive-v18.js').exists() and all(x in rtxt('responsive-v18.js') for x in ['conflictKindsV18','isStructurallyEmptyRoundV18','copiedFromInterviewId']))

passed=sum(ok for ok,_,_ in r); failed=len(r)-passed
out=['PACKAGE VALIDATION — Full Handover v1.17 / Design System v1.8 / Responsive v1.10 — 2026-09-03',f'TOTAL={len(r)} PASS={passed} FAIL={failed}','']
for ok,n,d in r: out.append(f"{'PASS' if ok else 'FAIL'} | {n}"+(f' | {d}' if d else ''))
if not a.no_write:
    (B/'PACKAGE_VALIDATION.txt').write_text('\n'.join(out)+'\n')
print('\n'.join(out)); sys.exit(1 if failed else 0)
