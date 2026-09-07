from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
SRC = WEB / "src"


def run(*args: str, cwd: Path = ROOT) -> None:
    subprocess.run(list(args), cwd=cwd, check=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

# Converge remaining Candidate feature-local primitive collisions into the shared/global layer.
candidate_css_path = SRC / "styles/candidate-portal.css"
candidate_css = candidate_css_path.read_text(encoding="utf-8")
for pattern in (
    r"\n\.btn-primary \{.*?\}\n\n\.btn-primary:hover:not\(:disabled\) \{.*?\}\n\n\.btn-primary:disabled \{.*?\}\n",
    r"\n\.btn-secondary \{.*?\}\n\n\.btn-secondary:hover:not\(:disabled\) \{.*?\}\n",
    r"\n\.status-badge \{.*?\}\n",
):
    candidate_css, count = re.subn(pattern, "\n", candidate_css, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"candidate primitive collision anchor not found: {pattern}")
candidate_css = candidate_css.replace(".btn-danger {", ".candidate-btn-danger {")
candidate_css = candidate_css.replace(".btn-danger:hover {", ".candidate-btn-danger:hover {")
write(candidate_css_path, candidate_css)

# Remove TSX color fallbacks that silently form a second palette when canonical tokens exist.
tokens_css = (SRC / "styles/tokens.css").read_text(encoding="utf-8")
declared = set(re.findall(r"(--[A-Za-z0-9_-]+)\s*:", tokens_css))
var_fallback = re.compile(r"var\((--[A-Za-z0-9_-]+)\s*,\s*#[0-9A-Fa-f]{3,8}\)")
for path in sorted(SRC.rglob("*.tsx")):
    text = path.read_text(encoding="utf-8")
    text = var_fallback.sub(lambda m: f"var({m.group(1)})" if m.group(1) in declared else m.group(0), text)
    write(path, text)

# Known Candidate inline hard-rule violations discovered by the production audit.
uploader_path = SRC / "components/candidate/DocumentUploader.tsx"
uploader = uploader_path.read_text(encoding="utf-8")
uploader = uploader.replace('fontSize: "14px"', 'fontSize: "16px"')
uploader = uploader.replace('fontSize: "12px"', 'fontSize: "14px"')
uploader = uploader.replace('className="btn btn-danger"', 'className="btn candidate-btn-danger"')
uploader = uploader.replace('style={{ minHeight: "36px", padding: "4px 12px" }}', 'style={{ minHeight: "44px", padding: "8px 12px" }}')
write(uploader_path, uploader)

education_path = SRC / "components/candidate/EducationSection.tsx"
education = education_path.read_text(encoding="utf-8").replace('className="btn btn-danger btn-sm"', 'className="btn candidate-btn-danger btn-sm"')
write(education_path, education)

# Central legacy primary button disabled state remains accessible while old consumers converge.
globals_path = SRC / "app/globals.css"
globals = globals_path.read_text(encoding="utf-8")
anchor = ".btn-primary:hover {\n  background-color: #0d3052;\n}\n"
addition = anchor + "\n.btn-primary:disabled {\n  cursor: not-allowed;\n  opacity: 0.55;\n}\n"
if addition not in globals:
    if anchor not in globals:
        raise RuntimeError("global primary button anchor missing")
    globals = globals.replace(anchor, addition, 1)
write(globals_path, globals)

# Durable production validator. It checks statically provable contracts only.
validator = WEB / "scripts/validate-design-contract.mjs"
write(validator, r'''import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const src = path.join(root, "src");
const tokenFile = path.join(src, "styles", "tokens.css");
const tokenText = fs.readFileSync(tokenFile, "utf8");
const declaredTokens = new Set([...tokenText.matchAll(/(--[A-Za-z0-9_-]+)\s*:/g)].map((m) => m[1]));
const failures = [];

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

const files = walk(src).filter((f) => /\.(css|tsx|ts)$/.test(f));
const forbiddenAliases = [
  "--font-stack",
  "--surface-muted",
  "--surface-hover",
  "--ink-900",
  "--ink-800",
  "--ink-700",
  "--ink-500",
  "--accent",
  "--radius-pill",
  "--status-danger-border",
  "--status-warning-border",
  "--font-size-title-page",
];

for (const file of files) {
  const rel = path.relative(root, file).replaceAll(path.sep, "/");
  const text = fs.readFileSync(file, "utf8");

  for (const match of text.matchAll(/var\((--[A-Za-z0-9_-]+)/g)) {
    if (!declaredTokens.has(match[1])) failures.push(`${rel}: undefined design token ${match[1]}`);
  }
  for (const alias of forbiddenAliases) {
    if (text.includes(alias)) failures.push(`${rel}: forbidden legacy design token ${alias}`);
  }
  if (/\.tsx?$/.test(file) && /var\(--[A-Za-z0-9_-]+\s*,/.test(text)) {
    failures.push(`${rel}: TS/TSX token fallback is forbidden; use declared runtime tokens`);
  }

  if (file.endsWith(".css")) {
    const allowedPrimitiveFile = rel === "src/app/globals.css" || rel === "src/styles/ui.css";
    if (!allowedPrimitiveFile) {
      for (const selector of ["btn-primary", "btn-secondary", "status-badge"]) {
        const rx = new RegExp(`(^|[}\\n])\\s*\\.${selector}(?=\\s*[:,{])`, "m");
        if (rx.test(text)) failures.push(`${rel}: feature-local generic primitive .${selector} is forbidden`);
      }
    }

    // Enforce literal sizes only on selectors that clearly represent controls/primary feedback.
    for (const block of text.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
      const selector = block[1].trim();
      const body = block[2];
      const primarySelector = /(^|[\s>+~,.:#])(button|input|select|textarea)([\s>+~,.:#\[]|$)|\.btn(?:[-_\s.:#\[]|$)|close-btn|dismiss-btn|status-menu__trigger|form-server-error|portal-alert/.test(selector);
      if (!primarySelector) continue;
      for (const size of body.matchAll(/font-size:\s*([0-9]+(?:\.[0-9]+)?)px/g)) {
        if (Number(size[1]) < 16) failures.push(`${rel}: ${selector} uses ${size[1]}px primary/control text`);
      }
      for (const height of body.matchAll(/min-height:\s*([0-9]+(?:\.[0-9]+)?)px/g)) {
        if (Number(height[1]) < 44) failures.push(`${rel}: ${selector} uses ${height[1]}px minimum control height`);
      }
    }
  }
}

if (!tokenText.includes("--badge-width-interview-operational: 144px")) {
  failures.push("src/styles/tokens.css: missing 144px operational Interview badge token");
}
for (const required of [
  "components/ui/Button.tsx",
  "components/ui/StatusBadge.tsx",
  "components/ui/StatusMenu.tsx",
  "components/ui/Dialog.tsx",
  "components/ui/Drawer.tsx",
  "components/ui/TableScrollContainer.tsx",
]) {
  if (!fs.existsSync(path.join(src, required))) failures.push(`src/${required}: required production primitive missing`);
}

if (failures.length) {
  console.error("DESIGN CONTRACT VALIDATION: FAIL");
  for (const failure of [...new Set(failures)].sort()) console.error(` - ${failure}`);
  process.exit(1);
}
console.log("DESIGN CONTRACT VALIDATION: PASS");
console.log(` - scanned ${files.length} production CSS/TS/TSX files`);
console.log(` - declared runtime tokens: ${declaredTokens.size}`);
''')

# Package script.
package_path = WEB / "package.json"
package = json.loads(package_path.read_text(encoding="utf-8"))
package["scripts"]["design:check"] = "node scripts/validate-design-contract.mjs"
write(package_path, json.dumps(package, ensure_ascii=False, indent=2) + "\n")

# Integration CI: the design check is cheap and runs only when the impact resolver selects web.
ci_path = ROOT / ".github/workflows/integration-ci.yml"
ci = ci_path.read_text(encoding="utf-8")
anchor_ci = "      - name: Lint\n        run: npm run lint\n"
addition_ci = "      - name: Validate production design contract\n        run: npm run design:check\n\n" + anchor_ci
if "Validate production design contract" not in ci:
    if anchor_ci not in ci:
        raise RuntimeError("integration CI lint anchor missing")
    ci = ci.replace(anchor_ci, addition_ci, 1)
write(ci_path, ci)

# Focused verification only.
run("npm", "run", "design:check", cwd=WEB)
run("node", "--conditions", "react-server", "--test", "--import", "tsx", "src/__tests__/tokens.test.ts", "src/__tests__/design-shell.test.ts", "src/__tests__/design-primitives.test.ts", "src/__tests__/design-responsive-convergence.test.ts", cwd=WEB)
run("npx", "biome", "check", "--write", "scripts/validate-design-contract.mjs", "package.json", "src/styles/candidate-portal.css", "src/components/candidate/DocumentUploader.tsx", "src/components/candidate/EducationSection.tsx", "src/app/globals.css", cwd=WEB)
run("npm", "run", "design:check", cwd=WEB)
run("npm", "run", "typecheck", cwd=WEB)
run("git", "diff", "--check", cwd=ROOT)

run("git", "add", "web/scripts/validate-design-contract.mjs", "web/package.json", "web/src/styles/candidate-portal.css", "web/src/components/candidate", "web/src/app/globals.css", ".github/workflows/integration-ci.yml", cwd=ROOT)
run("git", "commit", "-m", "feat(ds): enforce production design contracts", cwd=ROOT)
run("git", "push", "origin", "HEAD:oanhpham-kobe/DESIGN-SYSTEM-HARDENING-001", cwd=ROOT)
