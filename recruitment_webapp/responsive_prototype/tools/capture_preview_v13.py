from pathlib import Path
from qa_responsive_v13 import build_inline_html
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'screenshots_preview_v13';OUT.mkdir(exist_ok=True)
SCENARIOS=[
 ('candidate_apps_390',390,844,'candidate','candidate-applications',None),
 ('candidate_form_360',360,800,'candidate','candidate-form',None),
 ('hr_inbox_430',430,932,'hr','applications',None),
 ('interview_tablet_768',768,1024,'hr','interview',None),
 ('hr_report_tablet_1024',1024,768,'hr','hr-report',None),
 ('permissions_430',430,932,'admin','permissions',None),
 ('hr_nav_390',390,844,'hr','applications','nav'),
 ('hr_filter_390',390,844,'hr','applications','filter'),
 ('hr_drawer_390',390,844,'hr','applications','drawer'),
]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 html=build_inline_html()
 for name,w,h,role,page_name,action in SCENARIOS:
  pg=b.new_page(viewport={'width':w,'height':h});pg.set_content(html,wait_until='load');pg.evaluate("([r,p])=>{state.role=r;state.page=p;render()}",[role,page_name]);pg.wait_for_timeout(80)
  if action=='nav': pg.evaluate('toggleMobileNav()');pg.wait_for_timeout(50);pg.evaluate('document.activeElement&&document.activeElement.blur()')
  if action=='filter': pg.evaluate("openModal('responsiveFilters',{page:'applications'})");pg.wait_for_timeout(50);pg.evaluate('document.activeElement&&document.activeElement.blur()')
  if action=='drawer': pg.evaluate("openDrawer('candidate','c1')");pg.wait_for_timeout(50);pg.evaluate('document.activeElement&&document.activeElement.blur()')
  pg.screenshot(path=str(OUT/f'{name}.png'),full_page=False);pg.close()
 b.close()
print('captured',len(SCENARIOS))
