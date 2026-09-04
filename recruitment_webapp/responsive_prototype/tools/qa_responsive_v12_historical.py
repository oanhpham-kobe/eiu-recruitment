from pathlib import Path
import re, base64, json, sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'screenshots'
OUT.mkdir(exist_ok=True)

def build_inline_html():
    html = (ROOT/'index.html').read_text(encoding='utf-8')
    html = re.sub(r'<link rel="preconnect"[^>]*>', '', html)
    html = re.sub(r'<link href="https://fonts.googleapis.com[^>]*>', '', html)
    styles = (ROOT/'styles.css').read_text(encoding='utf-8') + '\n' + (ROOT/'responsive-v12.css').read_text(encoding='utf-8')
    img = base64.b64encode((ROOT/'assets/eiu-campus-login.png').read_bytes()).decode()
    styles = styles.replace("url('assets/eiu-campus-login.png')", f"url('data:image/png;base64,{img}')")
    html = html.replace('<link rel="stylesheet" href="styles.css" />\n  <link rel="stylesheet" href="responsive-v12.css" />', f'<style>{styles}</style>')
    # about:blank in QA has no localStorage. This patch only changes the QA harness, never production prototype files.
    v11 = (ROOT/'v11-overrides.js').read_text(encoding='utf-8').replace("localStorage.getItem('eiuRecruitmentLang') || 'vi'", "'vi'").replace("localStorage.setItem('eiuRecruitmentLang',lang);", '')
    r12 = (ROOT/'responsive-v12.js').read_text(encoding='utf-8').replace("localStorage.setItem('eiuRecruitmentLang',lang);", '')
    scripts = {'app.js': (ROOT/'app.js').read_text(encoding='utf-8'), 'v11-overrides.js':v11, 'responsive-v12.js':r12}
    for fn, js in scripts.items():
        html = html.replace(f'<script src="{fn}"></script>', f'<script>\n{js}\n</script>')
    return html

CASES = [
    ('login_mobile',375,812,None,None),
    ('candidate_form_mobile',375,812,'candidate','candidate-form'),
    ('candidate_apps_mobile',390,844,'candidate','candidate-applications'),
    ('hr_inbox_mobile',390,844,'hr','applications'),
    ('permissions_mobile',390,844,'admin','permissions'),
    ('interview_tablet_portrait',768,1024,'hr','interview'),
    ('hr_report_tablet_portrait',768,1024,'hr','hr-report'),
    ('hr_inbox_tablet_landscape',1024,768,'hr','applications'),
    ('hr_inbox_desktop',1280,800,'hr','applications'),
]

def main():
    html = build_inline_html()
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
        for name,w,h,role,page_name in CASES:
            page=browser.new_page(viewport={'width':w,'height':h}, device_scale_factor=1)
            errors=[]; page.on('pageerror', lambda e,errors=errors: errors.append(str(e)))
            page.set_content(html, wait_until='load', timeout=20000)
            if role:
                page.evaluate("([r,p])=>{state.role=r;state.page=p;render()}",[role,page_name])
            page.wait_for_timeout(100)
            metrics=page.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,sh:document.documentElement.scrollHeight,ch:document.documentElement.clientHeight})")
            checks=[]
            checks.append(('no_page_horizontal_overflow', metrics['sw'] <= metrics['cw']+1))
            checks.append(('no_js_errors', not errors))
            if name=='candidate_form_mobile':
                checks += [
                    ('candidate_form_one_column', page.locator('.candidate-form .form-grid').first.evaluate("e=>getComputedStyle(e).gridTemplateColumns.split(' ').length===1")),
                    ('privacy_present', page.locator('.privacy-section').count()==1),
                    ('sticky_actions_present', page.locator('.candidate-form-actions').count()==1),
                ]
            if name=='candidate_apps_mobile':
                checks += [('candidate_mobile_cards_visible', page.locator('.candidate-mobile-list').evaluate("e=>getComputedStyle(e).display!=='none'")),('candidate_desktop_table_hidden', page.locator('.candidate-desktop-table').evaluate("e=>getComputedStyle(e).display==='none'"))]
            if name in ('hr_inbox_mobile','permissions_mobile'):
                checks += [('structured_rows_mobile', page.locator('.main .responsive-table-shell>.data-table thead').evaluate("e=>getComputedStyle(e).display==='none'"))]
                page.locator('.hamb').click(); page.wait_for_timeout(60)
                checks += [('mobile_nav_opens',page.locator('.responsive-sidebar.open').count()==1)]
                page.evaluate('closeMobileNav()')
            if name=='hr_inbox_mobile':
                page.locator('.responsive-filter-btn').click(); page.wait_for_timeout(60)
                checks += [('filter_sheet_opens',page.locator('.modal').count()==1)]
                page.evaluate('closeModal()')
                page.locator('.action-cell .row-btn').first.click(); page.wait_for_timeout(250)
                box=page.locator('.drawer').bounding_box(); checks += [('drawer_full_screen_mobile', bool(box and abs(box['width']-w)<2 and abs(box['height']-h)<2))]
            if 'tablet' in name:
                checks += [('table_header_visible_tablet', page.locator('.main .data-table thead').evaluate("e=>getComputedStyle(e).display!=='none'")),('table_scroll_container', page.locator('.desktop-table-scroll').count()>=1)]
            if name=='hr_inbox_desktop':
                checks += [('sidebar_visible_desktop', page.locator('.sidebar').evaluate("e=>getComputedStyle(e).transform==='none'")),('hamb_hidden_desktop', page.locator('.hamb').evaluate("e=>getComputedStyle(e).display==='none'"))]
            if w<=640 and role:
                # core touch controls should be at least 44 high when visible
                vals=page.locator('.hamb,.lang-btn,.toolbar .btn,.row-btn').evaluate_all("els=>els.filter(e=>e.getClientRects().length>0 && getComputedStyle(e).visibility!=='hidden').map(e=>({tag:e.className,h:e.getBoundingClientRect().height,w:e.getBoundingClientRect().width}))")
                bad=[v for v in vals if v['h']<43.5]
                checks += [('core_touch_height_44', not bad)]
            page.screenshot(path=str(OUT/f'{name}.png'), full_page=False)
            ok=all(v for _,v in checks)
            results.append({'case':name,'viewport':f'{w}x{h}','ok':ok,'errors':errors,'checks':checks})
            page.close()
        browser.close()
    (ROOT/'RESPONSIVE_QA_RESULTS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Responsive Browser QA — v1.2','','Baseline: Full Handover v1.8 + Design System v1.7.','', '| Case | Viewport | Result |','|---|---:|---|']
    for r in results: lines.append(f"| {r['case']} | {r['viewport']} | {'PASS' if r['ok'] else 'FAIL'} |")
    lines += ['', '## Checks']
    for r in results:
        lines.append(f"\n### {r['case']} — {'PASS' if r['ok'] else 'FAIL'}")
        for k,v in r['checks']: lines.append(f"- {'PASS' if v else 'FAIL'} — {k}")
        if r['errors']: lines.append('- JS errors: '+ '; '.join(r['errors']))
    lines += ['', '## Notes','- Screenshots are in `screenshots/`.','- This is prototype/browser evidence only; it is not production UAT or backend validation.','- Candidate mobile is a go-live UX target. Internal HR remains desktop-first; tablet keeps wide tables and mobile uses structured rows for UX-UAT.']
    (ROOT/'RESPONSIVE_BROWSER_QA_v1.2.md').write_text('\n'.join(lines),encoding='utf-8')
    failed=[r for r in results if not r['ok']]
    print(f"RESPONSIVE_QA total={len(results)} pass={len(results)-len(failed)} fail={len(failed)}")
    if failed:
        for r in failed: print('FAIL',r['case'],[x for x in r['checks'] if not x[1]],r['errors'])
        return 1
    return 0

if __name__=='__main__': sys.exit(main())
