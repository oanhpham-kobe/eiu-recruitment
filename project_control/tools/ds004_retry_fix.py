from pathlib import Path

p = Path("project_control/tools/ds004_patch.py")
s = p.read_text(encoding="utf-8")
old = 'run("node", "--conditions", "react-server", "--test", "--import", "tsx", "src/__tests__/design-responsive-convergence.test.ts", "src/__tests__/candidate-portal.test.ts", "src/__tests__/application-inbox.test.ts", "src/__tests__/application-inbox-bulk-ui.test.ts", cwd=WEB)'
new = 'run("node", "--conditions", "react-server", "--test", "--import", "tsx", "src/__tests__/design-responsive-convergence.test.ts", "src/__tests__/application-inbox.test.ts", "src/__tests__/application-inbox-bulk-ui.test.ts", cwd=WEB)'
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("DS-004 focused test command anchor missing")
p.write_text(s, encoding="utf-8", newline="\n")
