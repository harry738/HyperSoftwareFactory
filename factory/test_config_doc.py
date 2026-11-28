"""Check that reference/config.md documents every top-level key of the
config.json template, plus `repo` and `council`, which onboard and the
council stage use but the template leaves out.

Run from anywhere: python factory/test_config_doc.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_every_key_is_documented():
    keys = [*json.loads((ROOT / "factory" / "config.json").read_text(encoding="utf-8")), "repo", "council"]
    doc = (ROOT / "reference" / "config.md").read_text(encoding="utf-8")
    missing = [k for k in keys if f"`{k}`" not in doc]
    assert not missing, f"reference/config.md has no `key` entry for: {', '.join(missing)}"


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"ok  {name}", flush=True)
    print("all passed")
