#!/usr/bin/env python3
"""Local first-run preflight for subscription-only software factory operation.

Checks local executable availability and environment hazards without making
network calls or reading / exporting the providers' authentication tokens.
Authentication must be verified by the operator in each official application.

Usage: python scripts/factory-doctor.py [--subscription-only] [--require-codex]
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inspect(root=ROOT, env=None, which=None, subscription_only=False, require_codex=False):
    """Return deterministic (errors, warnings, notes) without side effects."""
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    errors, warnings, notes = [], [], []
    for program in ("git", "gh", "python"):
        if not which(program):
            errors.append(f"{program} is missing from PATH")
    if not which("claude"):
        warnings.append("Claude CLI not on PATH; Claude Desktop Code tab may still work")
    if not which("codex"):
        (errors if require_codex else warnings).append(
            "Codex CLI is missing; optional until a Codex adapter is built")
    if subscription_only:
        for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
            if env.get(key):
                errors.append(
                    f"{key} is set; remove it from this shell for subscription-only operation")
        notes.append("Confirm Claude Code is signed into Claude Ultra using /status")
        notes.append("Confirm Codex is signed in with ChatGPT using the official Codex CLI/app")
    if not (root / ".claude" / "skills" / "factory" / "SKILL.md").exists():
        warnings.append("The /factory Claude Code skill is not installed in this checkout")
    cfg = root / "factory" / "config.json"
    if cfg.exists():
        try:
            policy = json.loads(cfg.read_text(encoding="utf-8")).get("merge_policy", {})
            if policy.get("allow_unattended", False):
                warnings.append("Unattended merging is ENABLED; supervised pilot should keep it disabled")
        except (ValueError, OSError):
            errors.append("factory/config.json cannot be parsed")
    else:
        warnings.append("factory/config.json not found in this checkout")
    notes.append("Subscription allowances are provider-managed, not unlimited or dollar budgets")
    notes.append("This check cannot verify sign-in, plan entitlement, quota or paid API billing")
    return errors, warnings, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subscription-only", action="store_true", help="reject API key environment variables")
    parser.add_argument("--require-codex", action="store_true", help="require an installed Codex CLI")
    args = parser.parse_args(argv)
    errors, warnings, notes = inspect(subscription_only=args.subscription_only, require_codex=args.require_codex)
    for prefix, items in (("ERROR", errors), ("WARN", warnings), ("INFO", notes)):
        for msg in items:
            print(f"{prefix}: {msg}")
    print("Result: FAIL" if errors else "Result: PASS (local checks only)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
