from pathlib import Path
from playwright.sync_api import sync_playwright
import re, json
root=Path(__file__).resolve().parents[1]
html=(root/'index.html').read_text(encoding='utf-8')
html=re.sub(r'<link rel="preconnect"[^>]*>','',html)
html=re.sub(r'<link href="https://fonts.googleapis.com[^\"]+"[^>]*>','',html)
for f in ['styles.css','responsive-v12.css','responsive-v13.css','responsive-v14.css']:
    html=html.replace(f'<link rel="stylesheet" href="{f}" />',f'<style>{(root/f).read_text(encoding="utf-8")}</style>')
for f in ['app.js','v11-overrides.js','responsive-v12.js','responsive-v13.js','responsive-v14.js']:
    js=(root/f).read_text(encoding='utf-8')
    js=js.replace("localStorage.getItem('eiuRecruitmentLang') || 'vi'","'vi'")
    js=re.sub(r"localStorage\.setItem\([^;]+\);?",'',js)
    html=html.replace(f'<script src="{f}"></script>',f'<script>{js}</script>')

results=[]
def check(name, ok, detail=''):
    results.append({'name':name,'pass':bool(ok),'detail':detail})
    print(('PASS' if ok else 'FAIL'),name,detail)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':430,'height':844})
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.on('console',lambda m: errors.append('console:'+m.text) if m.type=='error' else None)
    page.set_content(html,wait_until='load');page.wait_for_timeout(80)

    # Layout/viewports
    for width,height in [(360,800),(390,844),(430,844),(768,1024),(1024,768),(1280,800)]:
        page.set_viewport_size({'width':width,'height':height})
        for route in ['interview','hr-report']:
            page.evaluate("p=>{state.role='admin';state.lang='vi';state.page=p;state.selectedIds.clear();render()}",route);page.wait_for_timeout(20)
            sw=page.evaluate('document.documentElement.scrollWidth');cw=page.evaluate('document.documentElement.clientWidth')
            check(f'no page overflow {route} {width}x{height}',sw<=cw+1,f'{sw}/{cw}')

    # Interview badge compact + time order
    page.set_viewport_size({'width':430,'height':844});page.evaluate("state.role='admin';state.lang='vi';state.page='interview';state.selectedIds.clear();render()");page.wait_for_timeout(30)
    b=page.locator('.interview-table .status').first.bounding_box();check('Interview badge width benchmark',abs(b['width']-144)<1,f"{b['width']}px")
    t=page.locator('.interview-table .interview-time-v14').first.inner_text().replace('\n',' ')
    check('Interview time first then date',t.strip().startswith('14:00 – 15:30') and t.strip().endswith('20/05/2025'),t)
    check('Interview time stays one visual line at 430',page.locator('.interview-table .interview-time-v14').first.bounding_box()['height']<30,str(page.locator('.interview-table .interview-time-v14').first.bounding_box()))

    # Report label + badge benchmark
    page.evaluate("state.page='hr-report';state.selectedIds.clear();render()");page.wait_for_timeout(30)
    rc=page.locator('.report-table tbody tr').first.locator('td').nth(3)
    check('Report mobile time header no-wrap',rc.evaluate("e=>getComputedStyle(e,'::before').whiteSpace")=='nowrap',rc.get_attribute('data-label'))
    rb=page.locator('.report-table .status').nth(1)
    check('Report badge benchmark width',abs(rb.bounding_box()['width']-144)<1,f"{rb.bounding_box()['width']}px {rb.inner_text()}")
    check('Report benchmark wording',rb.inner_text()=='Đã gửi báo cáo',rb.inner_text())

    # English long badge wraps within same width
    page.evaluate("setLang('en');state.page='interview';render()");page.wait_for_timeout(30)
    eb=page.locator('.interview-table .status').filter(has_text='Awaiting Confirmation').first
    ebb=eb.bounding_box();check('English long status same compact width',abs(ebb['width']-144)<1,f"{ebb}")
    check('English long status wraps',ebb['height']>34,f"{ebb['height']}px")

    # Bulk checkbox + toolbar flows: Applications
    page.evaluate("state.lang='vi';state.page='applications';state.selectedIds.clear();render()");page.wait_for_timeout(30)
    cb=page.locator('.applications-table input.check').first;cb.click();page.wait_for_timeout(30)
    check('Applications bulk checkbox toggles',page.evaluate('state.selectedIds.size')==1 and page.locator('.applications-table input.check').first.is_checked(),str(page.evaluate('state.selectedIds.size')))
    delbtn=page.locator('.toolbar-left .btn.danger').first;check('Applications delete enables after select',not delbtn.is_disabled())
    page.get_by_role('button',name=re.compile('Gửi thư ứng viên')).first.click();page.wait_for_timeout(20);check('Applications email opens preview',page.locator('.modal').count()==1);page.keyboard.press('Escape')
    # status bulk update
    page.locator('.toolbar-left').get_by_role('button',name='Status').click();page.wait_for_timeout(15)
    page.locator('.status-popover button').filter(has_text='Đang xử lý').click();page.wait_for_timeout(30)
    check('Applications bulk status updates selected candidate',page.evaluate("state.candidates[0].status")=='PROCESSED',page.evaluate("state.candidates[0].status"))

    # Interview bulk + copy + email + delete confirmation
    page.evaluate("state.page='interview';state.selectedIds.clear();render()");page.wait_for_timeout(20)
    page.locator('.interview-table input.check').first.click();page.wait_for_timeout(20)
    check('Interview bulk checkbox toggles',page.evaluate('state.selectedIds.size')==1)
    page.locator('.toolbar-left').get_by_role('button',name='Status').click();page.locator('.status-popover button').filter(has_text='Đã xác nhận').click();page.wait_for_timeout(25)
    check('Interview bulk status updates selected round',page.evaluate("findRound('r12').status")=='CONFIRMED',page.evaluate("findRound('r12').status"))
    page.get_by_role('button',name=re.compile('Sao chép lịch')).click();page.wait_for_timeout(20);check('Copy interview opens copy modal',page.evaluate("state.modal && state.modal.type")=='copyRound',str(page.evaluate("state.modal && state.modal.type")));page.keyboard.press('Escape')
    page.get_by_role('button',name=re.compile('Gửi thư người tham dự')).click();page.wait_for_timeout(20);check('Interview participant email opens preview',page.evaluate("state.modal && state.modal.type")=='prototypeEmailV14');page.keyboard.press('Escape')
    page.get_by_role('button',name='Xóa').click();page.wait_for_timeout(20);check('Interview delete opens confirmation',page.evaluate("state.modal && state.modal.type")=='prototypeDeleteV14');page.keyboard.press('Escape')

    # Report bulk
    page.evaluate("state.page='hr-report';state.selectedIds.clear();render()");page.locator('.report-table input.check').first.click();page.wait_for_timeout(20)
    check('Report bulk checkbox toggles',page.evaluate('state.selectedIds.size')==1)
    page.locator('.toolbar-left').get_by_role('button',name='Status').click();page.locator('.status-popover button').filter(has_text='Tuyển dụng').click();page.wait_for_timeout(20)
    check('Report bulk status updates selected application',page.evaluate("appById('a1').status")=='HIRED',page.evaluate("appById('a1').status"))

    # Candidate form add/remove education + privacy validation
    page.evaluate("state.role='candidate';state.page='candidate-form';render()");page.wait_for_timeout(30)
    initial=page.locator('.candidate-form .repeat-item').count();page.locator('.compact-add').click();page.wait_for_timeout(20)
    check('Candidate education Add works',page.locator('.candidate-form .repeat-item').count()==initial+1)
    page.locator('.candidate-form .repeat-item').nth(1).locator('.repeat-item-head .row-btn').click();page.wait_for_timeout(20)
    check('Candidate education Remove works',page.locator('.candidate-form .repeat-item').count()==initial)
    ack=page.locator('#privacyAck');
    if ack.is_checked(): ack.uncheck()
    page.locator('.candidate-form button[type="submit"]').click();page.wait_for_timeout(30)
    check('Candidate privacy validation keeps form open',page.evaluate('state.page')=='candidate-form')
    check('Candidate privacy error announced',page.locator('#privacyError').is_visible())

    # Permissions actions
    page.evaluate("state.role='admin';state.page='permissions';render()");page.wait_for_timeout(30)
    page.get_by_role('button',name=re.compile('Thêm người dùng')).click();page.wait_for_timeout(20);check('Add user button opens responsive modal',page.evaluate("state.modal && state.modal.type")=='prototypeUserV14');page.keyboard.press('Escape')
    page.get_by_role('button',name=re.compile('Phân quyền HR')).click();page.wait_for_timeout(20);check('Assign HR permissions button opens responsive modal',page.evaluate("state.modal && state.modal.type")=='prototypeUserV14');page.keyboard.press('Escape')

    # Drawer/modal button surfaces: no dead controls after opening representative overlays
    overlay_cases=[
      ('candidate', "state.role='admin';state.page='applications';render();openDrawer('candidate','c1')"),
      ('round', "state.role='admin';state.page='interview';render();openDrawer('round','r12')"),
      ('hrReport', "state.role='admin';state.page='hr-report';render();openDrawer('hrReport','a1')"),
      ('candidateOwn', "state.role='candidate';state.page='candidate-applications';render();openDrawer('candidateOwn','c1')"),
    ]
    for label,expr in overlay_cases:
        page.evaluate(expr);page.wait_for_timeout(20)
        unwired=page.locator('#portal button:not([onclick]):not([data-prototype-wired="true"])').evaluate_all("els=>els.filter(e=>!(e.type==='submit'&&e.closest('form'))).map(e=>e.innerText.trim())")
        check(f'No dead buttons overlay/{label}',len(unwired)==0,str(unwired))
        page.keyboard.press('Escape');page.wait_for_timeout(10)

    # No dead visible buttons in core routes
    routes=[('admin','applications'),('admin','interview'),('admin','hr-report'),('admin','permissions'),('candidate','candidate-applications'),('candidate','candidate-form'),('interviewer','interviewer-report')]
    for role,route in routes:
        page.evaluate("([r,p])=>{state.role=r;state.lang='vi';state.page=p;state.selectedIds.clear();render()}",[role,route]);page.wait_for_timeout(15)
        unwired=page.locator('button:not([onclick]):not([data-prototype-wired="true"])').evaluate_all("els=>els.filter(e=>!(e.type==='submit'&&e.closest('form'))).map(e=>e.innerText.trim())")
        check(f'No dead buttons {role}/{route}',len(unwired)==0,str(unwired))

    check('No JS/console errors',len(errors)==0,str(errors))
    browser.close()

(root/'RESPONSIVE_QA_RESULTS_v1.4.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
fail=[r for r in results if not r['pass']]
print('TOTAL',len(results),'PASS',len(results)-len(fail),'FAIL',len(fail))
if fail:
    raise SystemExit(1)
