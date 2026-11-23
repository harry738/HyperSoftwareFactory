#!/usr/bin/env python3
"""
Factory Onboarding Wizard — register a project with the Software Factory.

Usage:
    python scripts/factory-onboard.py --interactive
    python scripts/factory-onboard.py --name myproject --repo your-org/myproject --council fast

What it does:
    1. Adds the project to config/projects.yaml (gitignored: it stays on this machine).
    2. Writes draft roadmap and README files to onboarding/<slug>/ for you to review
       and push to the project repo. It does NOT push anything itself.

Requires PyYAML (pip install -r requirements.txt) and, for the repo check,
an authenticated GitHub CLI (`gh auth login`).
"""
import argparse, re, subprocess, sys
from string import Template
from datetime import date
from pathlib import Path

import yaml

FACTORY_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = FACTORY_ROOT / "config" / "projects.yaml"
CONFIG_HEADER = (
    "# Software Factory — Project Configuration\n"
    "# Add projects with `python scripts/factory-onboard.py --interactive`\n"
    "# Or edit this file directly.\n\n"
)
README_TEMPLATE = FACTORY_ROOT / "config" / "README.template.md"
ROADMAP_PATH = "docs/product/roadmap.yaml"
INBOX_PATH = "docs/product/roadmap-inbox/"
SLUG_RE = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
CADENCES = ("weekly", "biweekly", "monthly", "none")

# ── GitHub (via gh CLI: handles auth on every platform) ─────────────────

def repo_status(repo):
    """Return 'exists', 'missing', or 'unknown' (auth, network, gh not installed)."""
    try:
        r = subprocess.run(["gh", "api", f"repos/{repo}", "--silent"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"  ⚠️  Could not run gh: {e}")
        return "unknown"
    if r.returncode == 0:
        return "exists"
    if "404" in r.stderr:
        return "missing"
    print(f"  ⚠️  GitHub check failed: {r.stderr.strip()[:200]}")
    return "unknown"

def create_repo(repo, description):
    """Create a PRIVATE repo. Make it public yourself if you mean to."""
    r = subprocess.run(["gh", "repo", "create", repo, "--private", "--description", description],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"  ❌ Repo creation failed: {r.stderr.strip()[:200]}")
    return r.returncode == 0

# ── Config ──────────────────────────────────────────────────────────────

def load_config():
    if CONFIG_PATH.exists():
        config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    else:
        config = {}
    config.setdefault("projects", {})
    return config

def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
    CONFIG_PATH.write_text(CONFIG_HEADER + body, encoding="utf-8")

# ── Core ────────────────────────────────────────────────────────────────

def onboard(slug, repo, name=None, council="full", cadence="weekly", alert=None):
    """Validate, add to config, write draft files. Returns the draft directory."""
    if not SLUG_RE.match(slug):
        raise ValueError("Slug must be 2-32 chars: lowercase letter first, then a-z 0-9 _ -")
    if not REPO_RE.match(repo):
        raise ValueError("Repo must be 'owner/repo' — not a URL")
    if council not in ("full", "fast"):
        raise ValueError("Council must be 'full' or 'fast'")
    if cadence not in CADENCES:
        raise ValueError(f"Cadence must be one of: {', '.join(CADENCES)}")
    config = load_config()
    if slug in config["projects"]:
        raise ValueError(f"Project '{slug}' already exists in {CONFIG_PATH.name}")

    name = name or slug
    today = date.today().isoformat()
    entry = {
        "name": name,
        "repo": repo,
        "roadmap": ROADMAP_PATH,
        "inbox": INBOX_PATH,
        # true = Full Council at Gate 2/3; false = Chair-only Fast Council everywhere
        "council_enabled": council == "full",
        "sprint_cadence": cadence,
        "onboarded": today,
    }
    if alert:
        entry["alert_channel"] = f"telegram:{alert}"
    config["projects"][slug] = entry
    save_config(config)

    out = FACTORY_ROOT / "onboarding" / slug
    (out / "roadmap-inbox").mkdir(parents=True, exist_ok=True)
    (out / "roadmap-inbox" / ".gitkeep").touch()
    roadmap = {
        "meta": {"project": slug, "created": today, "last_updated": today, "rm_counter": 1},
        "backlog": [], "in_progress": [], "staging": [],
        "done": [{"rm": "RM-0001", "title": "Project setup — factory onboarding",
                  "status": "done", "tier": 0, "effort": 1, "confidence": 1.0, "created": today}],
    }
    (out / "roadmap.yaml").write_text(
        yaml.safe_dump(roadmap, default_flow_style=False, sort_keys=False), encoding="utf-8")
    (out / ".factory.md").write_text(f"""# Project: {name}

**Slug:** {slug}
**Repo:** {repo}
**Onboarded:** {today}

Factory settings for this project live in `config/projects.yaml` in the
HyperSoftwareFactory repo.

- Roadmap: `{ROADMAP_PATH}` — managed by the factory pipeline.
- Inbox: `{INBOX_PATH}` — build specs land here from the factory.
""", encoding="utf-8")
    # ponytail: safe_substitute leaves any unknown $word alone instead of raising
    (out / "README.md").write_text(Template(README_TEMPLATE.read_text(encoding="utf-8")).safe_substitute(
        name=name, slug=slug, repo=repo, onboarded=today), encoding="utf-8")
    return out

def print_next_steps(slug, repo, out):
    print(f"\n  ✅ '{slug}' added to {CONFIG_PATH}")
    print(f"  ✅ Draft files written to {out}")
    print(f"\n  Next steps (nothing has been pushed):")
    print(f"  1. Review the drafts, then copy them into {repo}:")
    print(f"       roadmap.yaml   → {ROADMAP_PATH}")
    print(f"       roadmap-inbox/ → {INBOX_PATH}")
    print(f"       .factory.md    → .factory.md")
    print(f"       README.md      → README.md (merge with any existing one; fill or delete each section)")
    print(f"  2. Nothing to commit here: config/projects.yaml is gitignored.\n")

# ── Interactive wizard ──────────────────────────────────────────────────

def ask(prompt, valid, error):
    while True:
        value = input(prompt).strip()
        if valid(value):
            return value
        print(f"  ❌ {error}")

def interactive_wizard():
    print("\n" + "=" * 60 + "\n  FACTORY ONBOARDING WIZARD\n" + "=" * 60 + "\n")
    existing = load_config()["projects"]
    slug = ask("  Project slug (e.g. 'myproject'): ",
               lambda s: SLUG_RE.match(s) and s not in existing,
               "2-32 chars, lowercase, no spaces, and not already registered.")
    name = input(f"  Full project name (default: {slug}): ").strip() or slug
    repo = ask(f"  GitHub repo (e.g. 'your-org/{slug}'): ", REPO_RE.match,
               "Format: 'owner/repo' — no full URL.")

    print(f"\n  Checking {repo}...")
    status = repo_status(repo)
    if status == "exists":
        print("  ✅ Repo found")
    elif status == "missing":
        if input("  Repo not found. Create it as a PRIVATE repo? (y/n): ").strip().lower() == "y":
            if create_repo(repo, name):
                print(f"  ✅ Private repo created: https://github.com/{repo}")
    else:
        print("  ⚠️  Could not verify the repo. Continuing; drafts are local only.")

    council = "full" if input(
        "\n  Council: 1 = Full (4-model), 2 = Fast (Chair-only). Choice (1/2): ").strip() == "1" else "fast"
    choice = input("  Sprint cadence: 1 weekly, 2 biweekly, 3 monthly, 4 none. Choice: ").strip()
    cadence = dict(zip("1234", CADENCES)).get(choice, "none")
    alert = input("  Telegram chat ID for alerts (blank = none): ").strip() or None

    print("\n" + "=" * 60 + "\n  SUMMARY\n" + "=" * 60)
    for k, v in [("slug", slug), ("name", name), ("repo", repo), ("council", council),
                 ("cadence", cadence), ("alert", alert or "none")]:
        print(f"  {k}: {v}")
    if input("\n  Onboard this project? (y/n): ").strip().lower() != "y":
        print("  ❌ Cancelled. Nothing written.")
        return
    print_next_steps(slug, repo, onboard(slug, repo, name, council, cadence, alert))

# ── Main ────────────────────────────────────────────────────────────────

def main():
    sys.stdout.reconfigure(encoding="utf-8")  # emoji output on Windows consoles
    parser = argparse.ArgumentParser(description="Factory Onboarding Wizard")
    parser.add_argument("--interactive", action="store_true", help="Interactive wizard")
    parser.add_argument("--name", help="Project slug")
    parser.add_argument("--repo", help="GitHub repo (owner/repo)")
    parser.add_argument("--council", default="full", choices=("full", "fast"), help="Council mode")
    parser.add_argument("--cadence", default="weekly", choices=CADENCES, help="Sprint cadence")
    parser.add_argument("--full-name", help="Full project name (default: slug)")
    parser.add_argument("--alert", help="Telegram chat ID for alerts")
    args = parser.parse_args()

    if args.interactive or len(sys.argv) == 1:
        interactive_wizard()
    elif args.name and args.repo:
        try:
            out = onboard(args.name, args.repo, args.full_name, args.council, args.cadence, args.alert)
        except ValueError as e:
            sys.exit(f"❌ {e}")
        if repo_status(args.repo) == "missing":
            print(f"  ⚠️  {args.repo} does not exist on GitHub yet.")
        print_next_steps(args.name, args.repo, out)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
