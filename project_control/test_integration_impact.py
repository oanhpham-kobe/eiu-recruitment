import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml


class IntegrationImpactTests(unittest.TestCase):
    def resolve(self, changed_path, full=False):
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/integration-ci.yml"
        steps = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]["impact"]["steps"]
        script = next(step["run"] for step in steps if step["name"] == "Resolve impacted domains")
        bash = shutil.which("bash")
        if os.name == "nt":
            bash = str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
            git("init", "-q")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "baseline")
            target = root / changed_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("synthetic fixture\n", encoding="utf-8")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "change")
            output = root / "scope-output"
            env = {**os.environ, "BEFORE": "", "AFTER": git("rev-parse", "HEAD"), "FORCE_FULL": str(full).lower(), "COMMIT_MESSAGE": "test", "GITHUB_OUTPUT": output.as_posix()}
            subprocess.run([bash, "-c", script], cwd=root, env=env, check=True, capture_output=True)
            return dict(line.split("=", 1) for line in output.read_text().splitlines())

    def test_storage_runtime_requires_real_database_and_storage_gate(self):
        self.assertEqual(self.resolve("web/src/lib/storage/cleanup-runner.ts"), {"web": "true", "db": "true"})

    def test_dependencies_require_both_domains(self):
        self.assertEqual(self.resolve("web/package-lock.json"), {"web": "true", "db": "true"})

    def test_ordinary_ui_keeps_focused_web_verification(self):
        self.assertEqual(self.resolve("web/src/components/ui/Button.tsx"), {"web": "true", "db": "false"})

    def test_governance_only_does_not_claim_product_verification(self):
        self.assertEqual(self.resolve("project_control/CURRENT_STATE.md"), {"web": "false", "db": "false"})

    def test_database_changes_select_database(self):
        self.assertEqual(self.resolve("supabase/migrations/test.sql"), {"web": "false", "db": "true"})

    def test_full_request_broadens_governance_change(self):
        self.assertEqual(self.resolve("project_control/CURRENT_STATE.md", full=True), {"web": "true", "db": "true"})


if __name__ == "__main__":
    unittest.main()
