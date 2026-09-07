from pathlib import Path

p = Path('project_control/tools/ds002_003_patch.py')
s = p.read_text(encoding='utf-8')

regex_line = '  assert.match(layout, /pathname === "\\\\/candidate"/);'
fixed_line = '  assert.ok(layout.includes(\'pathname === "/candidate"\'));'
if regex_line in s:
    s = s.replace(regex_line, fixed_line, 1)
elif fixed_line not in s:
    raise SystemExit('design-shell test anchor missing')

old_switcher = '''        <div className="language-switcher" role="group" aria-label="Chọn ngôn ngữ / Choose language">
          <button type="button" className="lang-btn active" aria-pressed="true" aria-label="Tiếng Việt (Đang chọn / Selected)">VI</button>
          <span className="lang-divider" aria-hidden="true">|</span>
          <button type="button" className="lang-btn" aria-pressed="false" aria-label="English">EN</button>
        </div>'''
new_switcher = '''        <fieldset className="language-switcher">
          <legend className="sr-only">Chọn ngôn ngữ / Choose language</legend>
          <button type="button" className="lang-btn active" aria-pressed="true" aria-label="Tiếng Việt (Đang chọn / Selected)">VI</button>
          <span className="lang-divider" aria-hidden="true">|</span>
          <button type="button" className="lang-btn" aria-pressed="false" aria-label="English">EN</button>
        </fieldset>'''
if old_switcher in s:
    s = s.replace(old_switcher, new_switcher, 1)
elif new_switcher not in s:
    raise SystemExit('language switcher anchor missing')

needle = 'run("npx", "biome", "check",'
replacement = 'run("npx", "biome", "check", "--write",'
count = s.count(needle)
if count:
    if count != 2:
        raise SystemExit(f'expected two Biome gates, got {count}')
    s = s.replace(needle, replacement)
elif s.count(replacement) != 2:
    raise SystemExit('Biome write gates missing')

p.write_text(s, encoding='utf-8')
