from pathlib import Path

p = Path("project_control/tools/ds005_patch.py")
s = p.read_text(encoding="utf-8")
anchor = "# Durable production validator. It checks statically provable contracts only.\n"
repair = r'''# Repair DS-005 findings exposed by the first validator run.
globals = globals_path.read_text(encoding="utf-8")
globals, small_button_count = re.subn(
    r"(\.btn-sm\s*\{[^}]*?min-height:\s*)36px",
    r"\g<1>44px",
    globals,
    flags=re.S,
)
if small_button_count != 2:
    raise RuntimeError(f"expected two 36px global btn-sm contracts, got {small_button_count}")
write(globals_path, globals)

login_path = SRC / "styles/login.css"
login = login_path.read_text(encoding="utf-8")
login, font_alias_count = re.subn(
    r"font-family:\s*var\(\s*--font-stack,.*?\);",
    "font-family: var(--font-sans);",
    login,
    count=1,
    flags=re.S,
)
if font_alias_count != 1:
    raise RuntimeError(f"expected one login --font-stack alias, got {font_alias_count}")
login = login.replace("font-size: 15px;", "font-size: 16px;")
write(login_path, login)

'''
if repair not in s:
    if anchor not in s:
        raise SystemExit("DS-005 validator anchor missing")
    s = s.replace(anchor, repair + anchor, 1)
p.write_text(s, encoding="utf-8", newline="\n")
