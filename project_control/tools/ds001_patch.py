from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
TOKENS = WEB / "src/styles/tokens.css"
GLOBALS = WEB / "src/app/globals.css"
TOKEN_TEST = WEB / "src/__tests__/tokens.test.ts"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected one match, got {n}")
    return text.replace(old, new, 1)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")

# 1) Runtime token semantics: preserve generic 112; add scoped operational 144.
tokens = TOKENS.read_text(encoding="utf-8")
tokens = replace_once(
    tokens,
    "  --badge-width-interview: 112px;\n  --badge-width-candidate: 128px;",
    "  --badge-width-interview: 112px;\n  /* Current Interview / HR Report operational page benchmark.\n     Scoped page consumers use this instead of reinterpreting the initial generic token. */\n  --badge-width-interview-operational: 144px;\n  --badge-width-candidate: 128px;",
    "operational interview badge token",
)
write(TOKENS, tokens)

# 2) Known invalid token consumer.
globals_css = GLOBALS.read_text(encoding="utf-8")
globals_css = replace_once(
    globals_css,
    "var(--font-size-title-page)",
    "var(--font-size-page-title)",
    "page-title token typo",
)
write(GLOBALS, globals_css)

# 3) Collapse non-authoritative aliases to v1.8 runtime tokens.
# These replacements intentionally keep presentation semantics simple and avoid a second Slate-like palette.
replacements = {
    "--font-stack": "--font-sans",
    "--surface-muted": "--eiu-cream",
    "--surface-hover": "--eiu-cream",
    "--ink-900": "--ink-950",
    "--ink-800": "--ink-950",
    "--ink-700": "--ink-950",
    "--ink-500": "--ink-600",
    "--accent": "--eiu-blue",
    "--radius-pill": "--radius-badge",
    "--status-danger-border": "--status-danger-text",
    "--status-warning-border": "--status-warning-text",
}
for css_path in sorted((WEB / "src").rglob("*.css")):
    css = css_path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        css = css.replace(f"var({old},", f"var({new},")
        css = css.replace(f"var({old})", f"var({new})")
    write(css_path, css)

# 4) Strip fallbacks from variables that are actually declared by tokens.css.
# This makes future missing-token drift fail visibly instead of silently switching to a feature palette.
tokens = TOKENS.read_text(encoding="utf-8")
declared = set(re.findall(r"(--[A-Za-z0-9_-]+)\s*:", tokens))
var_with_simple_fallback = re.compile(r"var\((--[A-Za-z0-9_-]+)\s*,\s*([^()]+?)\)")
for css_path in sorted((WEB / "src").rglob("*.css")):
    css = css_path.read_text(encoding="utf-8")
    def strip(match: re.Match[str]) -> str:
        name = match.group(1)
        return f"var({name})" if name in declared else match.group(0)
    previous = None
    while css != previous:
        previous = css
        css = var_with_simple_fallback.sub(strip, css)
    write(css_path, css)

# 5) Focused token test asserts both generic and scoped meanings.
test = TOKEN_TEST.read_text(encoding="utf-8")
test = replace_once(
    test,
    '  assert.match(tokensCss, /--badge-width-interview:\\s*112px/);\n  assert.match(tokensCss, /--badge-width-report:\\s*168px/);',
    '  assert.match(tokensCss, /--badge-width-interview:\\s*112px/);\n  assert.match(tokensCss, /--badge-width-interview-operational:\\s*144px/);\n  assert.match(tokensCss, /--badge-width-report:\\s*168px/);',
    "token test operational badge",
)
write(TOKEN_TEST, test)

# 6) Fail closed if any CSS var consumer remains undeclared after the convergence pass.
tokens = TOKENS.read_text(encoding="utf-8")
declared = set(re.findall(r"(--[A-Za-z0-9_-]+)\s*:", tokens))
undefined: dict[str, list[str]] = {}
for css_path in sorted((WEB / "src").rglob("*.css")):
    css = css_path.read_text(encoding="utf-8")
    for name in sorted(set(re.findall(r"var\((--[A-Za-z0-9_-]+)", css)) - declared):
        undefined.setdefault(name, []).append(str(css_path.relative_to(ROOT)))
if undefined:
    for name, paths in undefined.items():
        print(f"UNDEFINED {name}: {', '.join(paths)}")
    raise SystemExit("DS-001 undefined CSS custom properties remain")

# Focused verification only.
subprocess.run(
    ["node", "--conditions", "react-server", "--test", "--import", "tsx", "src/__tests__/tokens.test.ts"],
    cwd=WEB,
    check=True,
)
subprocess.run(
    ["npx", "biome", "check", "src/styles/tokens.css", "src/styles/login.css", "src/styles/candidate-portal.css", "src/app/globals.css", "src/__tests__/tokens.test.ts"],
    cwd=WEB,
    check=True,
)
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)

subprocess.run(["git", "add", "web/src/styles", "web/src/app/globals.css", "web/src/__tests__/tokens.test.ts"], cwd=ROOT, check=True)
subprocess.run(["git", "commit", "-m", "feat(ds): converge production design tokens"], cwd=ROOT, check=True)
subprocess.run(["git", "push", "origin", "HEAD:oanhpham-kobe/DESIGN-SYSTEM-HARDENING-001"], cwd=ROOT, check=True)
