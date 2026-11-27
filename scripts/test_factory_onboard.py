"""Self-check for factory-onboard.py. Run: python scripts/test_factory_onboard.py"""
import importlib.util, tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("onboard", Path(__file__).with_name("factory-onboard.py"))
fo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fo)


def rejects(**kw):
    try:
        fo.onboard(**kw)
    except ValueError:
        return True
    return False


with tempfile.TemporaryDirectory() as tmp:
    fo.FACTORY_ROOT = Path(tmp)
    fo.CONFIG_PATH = Path(tmp) / "config" / "projects.yaml"
    # README_TEMPLATE keeps pointing at the real config/README.template.md

    out = fo.onboard("demo", "owner/demo", council="fast")
    text = fo.CONFIG_PATH.read_text(encoding="utf-8")
    entry = fo.load_config()["projects"]["demo"]
    assert text.startswith("# Software Factory"), "header comment lost"
    assert entry["name"] == "demo", "name must default to slug, not null"
    assert entry["council_enabled"] is False
    assert "alert_channel" not in entry, "no placeholder alert channel"
    assert (out / "roadmap.yaml").exists() and (out / ".factory.md").exists()
    readme = (out / "README.md").read_text(encoding="utf-8")
    assert "# demo" in readme and "owner/demo" in readme and "$" not in readme, "README template not filled"

    assert rejects(slug="demo", repo="owner/demo"), "duplicate slug must be rejected"
    assert rejects(slug="Bad Slug", repo="owner/x")
    assert rejects(slug="ok", repo="https://github.com/owner/x")
    assert list(fo.load_config()["projects"]) == ["demo"], "rejected input must not be saved"

for empty_projects in ("projects:\n", "projects: null\n", "projects: ~\n"):
    with tempfile.TemporaryDirectory() as tmp:
        fo.FACTORY_ROOT = Path(tmp)
        fo.CONFIG_PATH = Path(tmp) / "projects.yaml"
        fo.CONFIG_PATH.write_text(empty_projects, encoding="utf-8")

        out = fo.onboard("first", "owner/first")
        assert fo.load_config()["projects"]["first"]["repo"] == "owner/first"
        assert (out / "README.md").exists(), "first project drafts must be written"

print("ok")
