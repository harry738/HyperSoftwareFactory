"""Offline tests for subscription-only first-run preflight."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("factory_doctor", ROOT / "scripts" / "factory-doctor.py")
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / ".claude" / "skills" / "factory").mkdir(parents=True)
        (self.root / ".claude" / "skills" / "factory" / "SKILL.md").write_text("test\n")
        (self.root / "factory").mkdir()
        (self.root / "factory" / "config.json").write_text('{"merge_policy":{"allow_unattended":false}}\n')
        self.tools = lambda name: "/fake/bin/" + name

    def test_subscription_only_rejects_api_credentials(self):
        errors, _, notes = doctor.inspect(
            root=self.root, env={"ANTHROPIC_API_KEY": "dummy", "OPENAI_API_KEY": "dummy"},
            which=self.tools, subscription_only=True)
        self.assertTrue(any("ANTHROPIC_API_KEY" in e for e in errors))
        self.assertTrue(any("OPENAI_API_KEY" in e for e in errors))
        self.assertTrue(any("cannot verify" in n.lower() for n in notes))

    def test_subscription_only_passes_without_api_credentials(self):
        errors, _, _ = doctor.inspect(
            root=self.root, env={}, which=self.tools, subscription_only=True)
        self.assertEqual(errors, [])

    def test_missing_codex_is_warning_by_default(self):
        available = lambda name: None if name == "codex" else "/fake/" + name
        errors, warnings, _ = doctor.inspect(root=self.root, env={}, which=available)
        self.assertEqual(errors, [])
        self.assertTrue(any("Codex" in w for w in warnings))

    def test_can_require_codex(self):
        available = lambda name: None if name == "codex" else "/fake/" + name
        errors, _, _ = doctor.inspect(root=self.root, env={}, which=available, require_codex=True)
        self.assertTrue(any("Codex" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
