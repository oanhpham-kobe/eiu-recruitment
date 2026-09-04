from pathlib import Path
import re, base64, json, sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'screenshots_v13'
OUT.mkdir(exist_ok=True)


def build_inline_html():
    html = (ROOT/'index.html').read_text(encoding='utf-8')
    html = re.sub(r'<link rel="preconnect"[^>]*>', '', html)
    html = re.sub(r'<link href="https://fonts.googleapis.com[^>]*>', '', html)
    styles = '\n'.join((ROOT/f).read_text(encoding='utf-8') for f in ['styles.css','responsive-v12.css','responsive-v13.css'])
    img = base64.b64encode((ROOT/'assets/eiu-campus-login.png').read_bytes()).decode()
    styles = styles.replace("url('assets/eiu-campus-login.png')", f"url('data:image/png;base64,{img}')")
    for f in ['styles.css','responsive-v12.css','responsive-v13.css']:
        html = html.replace(f'<link rel="stylesheet" href="{f}" />', '')
    html = html.replace('</head>', f'<style>{styles}</style></head>')
    v11 = (ROOT/'v11-overrides.js').read_text(encoding='utf-8').replace("localStorage.getItem('eiuRecruitmentLang') || 'vi'", "'vi'").replace("localStorage.setItem('eiuRecruitmentLang',lang);", '')
    r12 = (ROOT/'responsive-v12.js').read_text(encoding='utf-8').replace("localStorage.setItem('eiuRecruitmentLang',lang);", '')
    scripts = {
        'app.js': (ROOT/'app.js').read_text(encoding='utf-8'),
        'v11-overrides.js': v11,
        'responsive-v12.js': r12,
        'responsive-v13.js': (ROOT/'responsive-v13.js').read_text(encoding='utf-8'),
    }
    for fn, js in scripts.items():
        html = html.replace(f'<script src="{fn}"></script>', f'<script>\n{js}\n</script>')
    return html

CASES = [
    ('login_360',360,800,None,None),
    ('candidate_form_360',360,800,'candidate','candidate-form'),
    ('candidate_apps_390',390,844,'candidate','candidate-applications'),
    ('hr_inbox_390',390,844,'hr','applications'),
    ('hr_inbox_430',430,932,'hr','applications'),
    ('hr_overlay_short',390,600,'hr','applications'),
    ('permissions_430',430,932,'admin','permissions'),
    ('interview_tablet_portrait',768,1024,'hr','interview'),
    ('hr_report_tablet_landscape',1024,768,'hr','hr-report'),
    ('hr_inbox_desktop',1280,800,'hr','applications'),
]


def bool_eval(page, expr, arg=None):
    return bool(page.evaluate(expr, arg) if arg is not None else page.evaluate(expr))


def main():
    html=build_inline_html(); results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
        for name,w,h,role,page_name in CASES:
            print('CASE',name,flush=True)
            page=browser.new_page(viewport={'width':w,'height':h}, device_scale_factor=1)
            page.set_default_timeout(2500)
            errors=[]; console_errors=[]
            page.on('pageerror', lambda e, errors=errors: errors.append(str(e)))
            page.on('console', lambda m, console_errors=console_errors: console_errors.append(m.text) if m.type=='error' else None)
            page.set_content(html, wait_until='load', timeout=20000)
            if role:
                page.evaluate("([r,p])=>{state.role=r;state.page=p;render()}",[role,page_name])
            page.wait_for_timeout(120)
            metrics=page.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
            checks=[('no_page_horizontal_overflow',metrics['sw']<=metrics['cw']+1),('no_js_errors',not errors),('no_console_errors',not console_errors),('document_lang',page.locator('html').get_attribute('lang') in ('vi','en')),('no_duplicate_ids',page.evaluate("(()=>{const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return new Set(ids).size===ids.length})()")),('visible_buttons_have_names',page.evaluate("[...document.querySelectorAll('button')].filter(b=>b.getClientRects().length&&getComputedStyle(b).visibility!=='hidden').every(b=>Boolean((b.innerText||'').trim()||b.getAttribute('aria-label')||b.getAttribute('title')))"))]

            if role and w<1280:
                checks += [
                    ('closed_sidebar_hidden_from_at', page.locator('.responsive-sidebar').get_attribute('aria-hidden')=='true'),
                    ('closed_sidebar_inert', page.locator('.responsive-sidebar').get_attribute('inert') is not None),
                ]
                hamb=page.locator('.hamb').first
                hamb.focus(); hamb.click(); page.wait_for_timeout(80)
                checks += [
                    ('mobile_nav_opens',page.locator('.responsive-sidebar.open').count()==1),
                    ('mobile_nav_dialog_semantics',page.locator('.responsive-sidebar.open').get_attribute('aria-modal')=='true'),
                    ('nav_focus_moves_to_close',page.evaluate("document.activeElement?.classList.contains('mobile-nav-close')") is True),
                    ('background_inert_while_nav_open',page.locator('.main,.candidate-content').first.get_attribute('inert') is not None),
                    ('mobile_signout_available',page.locator('.responsive-sidebar.open .mobile-sidebar-signout').count()==1),
                ]
                page.keyboard.press('Escape'); page.wait_for_timeout(80)
                checks += [
                    ('escape_closes_nav',page.locator('.responsive-sidebar.open').count()==0),
                    ('focus_restores_to_hamburger',page.evaluate("document.activeElement?.classList.contains('hamb')") is True),
                ]

            if name=='candidate_form_360':
                checks += [
                    ('one_column_form', page.locator('.candidate-form .form-grid').first.evaluate("e=>getComputedStyle(e).gridTemplateColumns.split(' ').length===1")),
                    ('language_switch_visible', page.locator('.responsive-candidate-head .language-switcher').evaluate("e=>getComputedStyle(e).display!=='none'")),
                    ('privacy_present',page.locator('.privacy-section').count()==1),
                    ('sticky_actions_present',page.locator('.candidate-form-actions').count()==1),
                    ('labels_bound',page.evaluate("[...document.querySelectorAll('.candidate-form .field')].every(g=>{const l=g.querySelector(':scope > label');const c=g.querySelector(':scope > input,:scope > select,:scope > textarea,:scope > .input,:scope > .select,:scope > .textarea');return !l||!c||l.contains(c)||Boolean(c.id&&l.htmlFor===c.id)})")),
                ]
                ack=page.locator('#privacyAck'); ack.uncheck()
                page.locator('.candidate-form-actions button[type="submit"]').click(); page.wait_for_timeout(60)
                checks += [
                    ('privacy_error_visible',page.locator('#privacyError').is_visible()),
                    ('privacy_invalid_focus',page.evaluate("document.activeElement?.id==='privacyAck'")),
                ]
            if name=='candidate_apps_390':
                checks += [
                    ('mobile_cards_visible',page.locator('.candidate-mobile-list').evaluate("e=>getComputedStyle(e).display!=='none'")),
                    ('desktop_candidate_table_hidden',page.locator('.candidate-desktop-table').evaluate("e=>getComputedStyle(e).display==='none'")),
                    ('language_switch_visible',page.locator('.responsive-candidate-head .language-switcher').evaluate("e=>getComputedStyle(e).display!=='none'")),
                ]
            if name.startswith('hr_inbox_') and w<=640:
                checks += [('structured_rows_on_phone',page.locator('.main .responsive-table-shell>.data-table thead').evaluate("e=>getComputedStyle(e).display==='none'"))]
                # Filter dialog focus/escape/restore.
                trigger=page.locator('.responsive-filter-btn')
                trigger.focus(); trigger.click(); page.wait_for_timeout(80)
                checks += [
                    ('filter_has_dialog_semantics',page.locator('.modal').get_attribute('role')=='dialog' and page.locator('.modal').get_attribute('aria-modal')=='true'),
                    ('app_inert_for_modal',page.locator('#app').get_attribute('inert') is not None),
                    ('modal_focus_inside',page.evaluate("Boolean(document.activeElement?.closest('.modal'))")),
                ]
                page.keyboard.press('Escape'); page.wait_for_timeout(60)
                checks += [('filter_escape_closes',page.locator('.modal').count()==0),('filter_focus_restored',page.evaluate("document.activeElement?.classList.contains('responsive-filter-btn')"))]
            if name=='hr_overlay_short':
                # Open drawer and verify short-height usability + dialog semantics.
                page.locator('.action-cell .row-btn').first.focus(); page.locator('.action-cell .row-btn').first.click(); page.wait_for_timeout(100)
                box=page.locator('.drawer').bounding_box(); head=page.locator('.drawer-head').bounding_box(); body=page.locator('.drawer-body')
                checks += [
                    ('drawer_full_width_mobile',bool(box and abs(box['width']-w)<2)),
                    ('drawer_dialog_semantics',page.locator('.drawer').get_attribute('role')=='dialog'),
                    ('drawer_header_visible_short_height',bool(head and head['y'] >= -1 and head['y'] < h)),
                    ('drawer_body_scrollable_short_height',body.evaluate("e=>e.scrollHeight>=e.clientHeight")),
                    ('drawer_focus_inside',page.evaluate("Boolean(document.activeElement?.closest('.drawer'))")),
                ]
                page.keyboard.press('Escape'); page.wait_for_timeout(60)
                checks += [('drawer_escape_closes',page.locator('.drawer').count()==0)]
            if 'tablet' in name:
                checks += [
                    ('table_header_visible_tablet',page.locator('.main .data-table thead').evaluate("e=>getComputedStyle(e).display!=='none'")),
                    ('table_scroller_present',page.locator('.desktop-table-scroll').count()>=1),
                    ('wide_scroller_keyboard_reachable',page.locator('.desktop-table-scroll').first.get_attribute('tabindex')=='0'),
                ]
            if name=='permissions_430':
                checks += [('root_permissions_visible',page.get_by_text('Tất cả quyền Root').count()==1)]
            if name=='hr_inbox_desktop':
                checks += [
                    ('sidebar_visible_desktop',page.locator('.sidebar').get_attribute('aria-hidden')=='false'),
                    ('hamb_hidden_desktop',page.locator('.hamb').evaluate("e=>getComputedStyle(e).display==='none'")),
                    ('sidebar_not_dialog_desktop',page.locator('.sidebar').get_attribute('role') is None),
                ]

            if w<=430 and role:
                vals=page.locator('.hamb,.lang-btn,.toolbar .btn,.row-btn,.mobile-sidebar-signout').evaluate_all("els=>els.filter(e=>e.getClientRects().length>0 && getComputedStyle(e).visibility!=='hidden').map(e=>({h:e.getBoundingClientRect().height,w:e.getBoundingClientRect().width,cls:e.className}))")
                bad=[v for v in vals if v['h']<43.5 or v['w']<43.5]
                if bad: print('BAD_TOUCH',name,bad,flush=True)
                checks += [('core_touch_targets_44',not bad)]

            page.screenshot(path=str(OUT/f'{name}.png'), full_page=False)
            ok=all(v for _,v in checks)
            results.append({'case':name,'viewport':f'{w}x{h}','ok':ok,'checks':checks,'page_errors':errors,'console_errors':console_errors})
            page.close()
        browser.close()

    (ROOT/'RESPONSIVE_QA_RESULTS_v1.3.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Responsive Browser QA — v1.3','', 'Baseline: Full Handover **v1.8** + Design System **v1.7**.','', '> Fresh Playwright/Chromium evidence for the rebuilt responsive layer. This is prototype evidence, not production UAT.','', '| Case | Viewport | Result |','|---|---:|---|']
    for r in results: lines.append(f"| {r['case']} | {r['viewport']} | {'PASS' if r['ok'] else 'FAIL'} |")
    lines += ['', '## Checks']
    for r in results:
        lines += ['', f"### {r['case']} — {'PASS' if r['ok'] else 'FAIL'}"]
        lines += [f"- {'PASS' if v else 'FAIL'} — {k}" for k,v in r['checks']]
        if r['page_errors']: lines.append('- Page errors: '+'; '.join(r['page_errors']))
        if r['console_errors']: lines.append('- Console errors: '+'; '.join(r['console_errors']))
    lines += ['', '## Evidence boundaries', '- Viewports include 360, 390, 430, 768, 1024 and 1280 widths plus a constrained 390×600 overlay case.', '- Keyboard evidence covers mobile navigation and Modal/Drawer Escape/focus restoration.', '- Candidate Form checks one-column layout, visible VI|EN, associated labels and privacy-error focus.', '- No axe package was added to this static prototype. Production implementation still requires axe plus manual keyboard/screen-reader sanity evidence.', '- Screenshots are in `screenshots_v13/`.']
    (ROOT/'RESPONSIVE_BROWSER_QA_v1.3.md').write_text('\n'.join(lines),encoding='utf-8')
    failed=[r for r in results if not r['ok']]
    print(f"RESPONSIVE_QA_V13 total={len(results)} pass={len(results)-len(failed)} fail={len(failed)}")
    if failed:
        for r in failed: print('FAIL',r['case'],[x for x in r['checks'] if not x[1]],r['page_errors'],r['console_errors'])
        return 1
    return 0

if __name__=='__main__': sys.exit(main())
