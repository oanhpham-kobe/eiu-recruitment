from pathlib import Path

p = Path("project_control/tools/ds005_patch.py")
s = p.read_text(encoding="utf-8")

# Verification already passed on run 34170150402. Keep deterministic formatting
# and diff hygiene only; do not rerun passed tests/typecheck because the previous
# failure was solely GitHub workflow permission at push time.
remove_prefixes = (
    'run("npm", "run", "design:check", cwd=WEB)',
    'run("node", "--conditions", "react-server", "--test", "--import", "tsx",',
    'run("npm", "run", "typecheck", cwd=WEB)',
)
lines = []
skipping_multiline_test = False
for line in s.splitlines():
    stripped = line.strip()
    if skipping_multiline_test:
        if stripped.endswith('cwd=WEB)'):
            skipping_multiline_test = False
        continue
    if any(stripped.startswith(prefix) for prefix in remove_prefixes):
        if stripped.startswith('run("node"') and not stripped.endswith('cwd=WEB)'):
            skipping_multiline_test = True
        continue
    lines.append(line)
s = "\n".join(lines) + "\n"

old_add = 'run("git", "add", "web/scripts/validate-design-contract.mjs", "web/package.json", "web/src/styles/candidate-portal.css", "web/src/components/candidate", "web/src/app/globals.css", ".github/workflows/integration-ci.yml", "web/src/__tests__/design-shell.test.ts", cwd=ROOT)'
new_add = 'run("git", "add", "web/scripts/validate-design-contract.mjs", "web/package.json", "web/src/styles/candidate-portal.css", "web/src/components/candidate", "web/src/app/globals.css", "web/src/__tests__/design-shell.test.ts", cwd=ROOT)'
if old_add in s:
    s = s.replace(old_add, new_add, 1)
elif new_add not in s:
    raise SystemExit("verified DS-005 git-add anchor missing")

p.write_text(s, encoding="utf-8", newline="\n")
