from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name, cond): checks.append((name,bool(cond)))

def text(name): return (ROOT/name).read_text(encoding='utf-8')

idx=text('index.html'); readme=text('README.md'); css13=text('responsive-v13.css'); js13=text('responsive-v13.js'); contract=text('RESPONSIVE_CONTRACT_v1.3.md')
check('index version v1.3','v1.3' in idx)
check('index loads responsive-v13.css','responsive-v13.css' in idx)
check('index loads responsive-v13.js','responsive-v13.js' in idx)
check('README authority Handover v1.8','Full Handover **v1.8**' in readme)
check('README authority Design v1.7','Design System **v1.7**' in readme)
check('Discovery exists',(ROOT/'RESPONSIVE_REBUILD_DISCOVERY_v1.3.md').exists())
check('Audit matrix exists',(ROOT/'RESPONSIVE_AUDIT_MATRIX_v1.3.md').exists())
check('Responsive contract exists',(ROOT/'RESPONSIVE_CONTRACT_v1.3.md').exists())
check('Final report exists',(ROOT/'RESPONSIVE_REBUILD_FINAL_REPORT_v1.3.md').exists())
check('Current QA exists',(ROOT/'RESPONSIVE_BROWSER_QA_v1.3.md').exists())
check('Current UX UAT exists',(ROOT/'RESPONSIVE_UX_UAT_CHECKLIST_v1.3.md').exists())
check('Reduced motion', 'prefers-reduced-motion' in css13)
check('Visible focus', ':focus-visible' in css13)
check('Very narrow 360 contract','360px' in contract)
check('Large mobile 430 contract','430px' in contract)
check('Nav inert support',"setAttribute('inert'" in js13)
check('Nav aria-hidden support',"aria-hidden" in js13)
check('Overlay aria-modal',"aria-modal" in js13)
check('Overlay focus trap',"event.key==='Tab'" in js13)
check('Escape behavior',"event.key==='Escape'" in js13)
check('Focus restoration','restoreFocus' in js13)
check('Toast live region',"aria-live" in js13)
check('Form labels normalized','normalizeFormLabels' in js13)
check('Privacy error/focus','privacyError' in js13 and "ack.focus()" in js13)
check('Scrollable table keyboard','tabIndex=0' in js13)
check('Mobile signout available','mobile-sidebar-signout' in js13 and 'mobile-sidebar-signout' in css13)
check('No innerWidth responsive branching','innerWidth' not in js13)
check('Browser QA results exist',(ROOT/'RESPONSIVE_QA_RESULTS_v1.3.json').exists())
if (ROOT/'RESPONSIVE_QA_RESULTS_v1.3.json').exists():
    data=json.loads((ROOT/'RESPONSIVE_QA_RESULTS_v1.3.json').read_text())
    check('Browser QA all pass',len(data)>=10 and all(r['ok'] for r in data))
    widths={r['viewport'].split('x')[0] for r in data}
    check('QA covers 360/390/430/768/1024/1280',{'360','390','430','768','1024','1280'}.issubset(widths))
    check('QA constrained height',any(r['viewport']=='390x600' for r in data))
check('Preview screenshots exist',(ROOT/'screenshots_preview_v13').exists() and len(list((ROOT/'screenshots_preview_v13').glob('*.png')))>=8)
check('Old QA marked historical',(ROOT/'RESPONSIVE_BROWSER_QA_v1.2_HISTORICAL.md').exists())
check('Version file v1.3','Version: **v1.3**' in text('VERSION.md'))

for n,ok in checks: print(('PASS' if ok else 'FAIL')+' | '+n)
passed=sum(ok for _,ok in checks); total=len(checks)
out='\n'.join([f"{'PASS' if ok else 'FAIL'} | {n}" for n,ok in checks]+['',f'TOTAL={total} PASS={passed} FAIL={total-passed}'])+'\n'
(ROOT/'PROTOTYPE_VALIDATION_v1.3.txt').write_text(out,encoding='utf-8')
print(f'TOTAL={total} PASS={passed} FAIL={total-passed}')
sys.exit(0 if passed==total else 1)
