"""Portable, offline regression tests for the factory's assurance boundaries.

Run with: python -m unittest discover -s factory -p test_assurance.py -v
Tests use temporary Git repositories; no GitHub credentials or Node required.
"""
import importlib.machinery
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent / "bin"
sys.path.insert(0, str(BIN))


def load_script(name):
    module_name = "factory_assurance_" + name
    loader = importlib.machinery.SourceFileLoader(module_name, str(BIN / name))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(module_name, loader))
    loader.exec_module(module)
    return module


gate = load_script("gate")
job = load_script("job")


class TemporaryGitRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "factory-test@example.invalid")
        self.git("config", "user.name", "Factory Test")
        (self.root / "README.md").write_text("Initial.\n")
        (self.root / "src").mkdir()
        (self.root / "src" / "keep.py").write_text("value = 1\n")
        self.commit("initial")
        self.git("update-ref", "refs/remotes/origin/main", self.git("rev-parse", "HEAD"))
        self.git("checkout", "-b", "feature")

    def git(self, *args):
        res = subprocess.run(["git", *args], cwd=self.root,
                             capture_output=True, text=True, check=True)
        return res.stdout.strip()

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-m", message)


class ProtectedPathsTests(TemporaryGitRepo):
    def test_new_workflow_is_protected(self):
        p = self.root / ".github" / "workflows" / "ci.yml"
        p.parent.mkdir(parents=True)
        p.write_text("name: test\n")
        self.commit("add workflow")
        self.assertIn("A .github/workflows/ci.yml", gate.protected_changes(self.root))

    def test_renamed_destination_is_protected(self):
        p = self.root / "src" / "new.yml"
        p.write_text("value\n")
        self.commit("add ordinary file")
        self.git("update-ref", "refs/remotes/origin/main", self.git("rev-parse", "HEAD"))
        dest = self.root / ".github" / "workflows" / "new.yml"
        dest.parent.mkdir(parents=True)
        self.git("mv", "src/new.yml", ".github/workflows/new.yml")
        self.commit("rename into protected path")
        self.assertIn("A .github/workflows/new.yml", gate.protected_changes(self.root))

    def test_existing_protected_file_is_blocked(self):
        p = self.root / "factory" / "config.json"
        p.parent.mkdir(parents=True)
        p.write_text("{}\n")
        self.commit("add config")
        self.git("update-ref", "refs/remotes/origin/main", self.git("rev-parse", "HEAD"))
        p.write_text('{"changed":true}\n')
        self.commit("edit config")
        self.assertIn("M factory/config.json", gate.protected_changes(self.root))

    def test_unprotected_change_passes(self):
        (self.root / "src" / "keep.py").write_text("value = 2\n")
        self.commit("edit source")
        self.assertEqual([], gate.protected_changes(self.root))


class ReviewBindingTests(TemporaryGitRepo):
    def setUp(self):
        super().setUp()
        self.saved_jobs = job.JOBS
        self.addCleanup(lambda: setattr(job, "JOBS", self.saved_jobs))
        job.JOBS = self.root / "jobs"
        self.d = job.JOBS / "001-test"
        rd = self.d / "round-1"
        rd.mkdir(parents=True)
        (self.d / "issue.md").write_text("Original requirement\n")
        (self.d / "spec.md").write_text(
            "SCOPE_CHANGE: no\n\n# Test\n\n"
            "## Acceptance criteria traceability\n1. Original -> 1 retained\n")
        (self.root / "src" / "keep.py").write_text("value = 3\n")
        self.commit("feature")
        self.j = {
            "id": "001-test", "worktree": str(self.root), "round": 1, "stage": "review",
            "intake": {"risk": "low", "rescoped": False},
            "agents": {"reviewers": {"code": "haiku"}}, "reviews": {},
        }
        self.j["review_binding"] = job.current_review_binding(self.j)
        (rd / "checks.md").write_text(
            "GATE: PASS\nCOMMIT: " + self.j["review_binding"]["head"] + "\n")
        (rd / "review-code.md").write_text(
            "VERDICT: PASS\nCOMMIT: " + self.j["review_binding"]["head"] + "\n")

    def test_review_is_bound_to_head_and_requirements(self):
        job.require_review_binding(self.j)
        (self.d / "spec.md").write_text("SCOPE_CHANGE: yes\n")
        with self.assertRaises(job.Refused):
            job.require_review_binding(self.j)

    def test_review_refuses_changed_head(self):
        (self.root / "src" / "keep.py").write_text("value = 4\n")
        self.commit("after review")
        with self.assertRaises(job.Refused):
            job.require_review_binding(self.j)

    def test_review_refuses_moved_base(self):
        self.git("update-ref", "refs/remotes/origin/main", self.git("rev-parse", "HEAD"))
        with self.assertRaises(job.Refused):
            job.require_review_binding(self.j)

    def test_invalid_reviewer_commit_is_not_pass(self):
        (self.d / "round-1" / "review-code.md").write_text(
            "VERDICT: PASS\nCOMMIT: wrong-commit\n")
        saved = job.cost_usd
        self.addCleanup(lambda: setattr(job, "cost_usd", saved))
        job.cost_usd = lambda _: 0.0
        self.assertEqual("invalid", job.sync(self.j)["reviews"]["code"])

    def test_unattended_merge_disabled_by_default(self):
        self.assertIn("disabled", job.unattended_merge_blocker(self.j))

    def test_high_risk_path_cannot_be_downgraded(self):
        p = self.root / ".github" / "workflows" / "new.yml"
        p.parent.mkdir(parents=True)
        p.write_text("name: unsafe\n")
        self.commit("workflow")
        self.assertEqual("high", job.effective_risk(self.j))

    def test_mixed_low_and_unknown_paths_remain_medium(self):
        (self.root / "README.md").write_text("Updated docs\n")
        (self.root / "src" / "keep.py").write_text("value = 9\n")
        self.commit("docs plus unclassified code")
        self.assertEqual("medium", job.effective_risk(self.j))

    def test_documentation_only_remains_low(self):
        (self.root / "README.md").write_text("Updated docs\n")
        self.commit("docs only")
        self.assertEqual("low", job.effective_risk(self.j))


if __name__ == "__main__":
    unittest.main()
