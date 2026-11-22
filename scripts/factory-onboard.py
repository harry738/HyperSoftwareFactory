#!/usr/bin/env python3
"""
Factory Onboarding Wizard — add a new project to the Software Factory.

Usage:
    python3 scripts/factory-onboard.py --interactive
    python3 scripts/factory-onboard.py --name propinfo --repo harry738/propInfo.co.uk --council false

Walks through project setup, creates config entry, and initialises the repo.
"""
import argparse, json, os, re, sys, urllib.request, urllib.error, yaml
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "projects.yaml"
SCRIPTS_DIR = Path(__file__).resolve().parent
HYPEROS_ROOT = Path(__file__).resolve().parent.parent

# ── GitHub API helpers ──────────────────────────────────────────────────

def gh_token():
    """Read GitHub token from gh config."""
    hosts = Path.home() / ".config" / "gh" / "hosts.yml"
    if hosts.exists():
        for line in hosts.read_text().splitlines():
            if "oauth_token:" in line:
                return line.split(":", 1)[1].strip()
    return os.environ.get("GH_TOKEN", "")

def gh_api(method, path, data=None):
    """Call GitHub API."""
    token = gh_token()
    if not token:
        print("❌ No GitHub token found. Set GH_TOKEN or run `gh auth login`.")
        sys.exit(1)
    url = f"https://api.github.com/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"❌ GitHub API error ({e.code}): {err[:300]}")
        return None

def check_repo(repo_full):
    """Check if a repo exists and is accessible."""
    data = gh_api("GET", f"repos/{repo_full}")
    if data:
        print(f"  ✅ Repo found: {data.get('full_name')} ({data.get('stargazers_count')}⭐)")
        return True
    return False

# ── Config management ───────────────────────────────────────────────────

def load_config():
    """Load existing projects config."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {"projects": {}}
    return {"projects": {}}

def save_config(config):
    """Save projects config."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    print(f"  ✅ Config saved to {CONFIG_PATH}")

# ── Repo initialisation ─────────────────────────────────────────────────

def init_repo_structure(repo_full, project_slug):
    """
    Create initial roadmap files in the target repo via a PR.
    We write files to a local checkout or create a branch via API.
    For now: write a draft to the local filesystem for review.
    """
    output_dir = HYPEROS_ROOT / "onboarding" / project_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    # roadmap.yaml
    roadmap = {
        "meta": {
            "project": project_slug,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "rm_counter": 1,
        },
        "backlog": [],
        "in_progress": [],
        "staging": [],
        "done": [{
            "rm": "RM-0001",
            "title": "Project setup — factory onboarding",
            "status": "done",
            "tier": 0,
            "effort": 1,
            "confidence": 1.0,
            "created": datetime.now().strftime("%Y-%m-%d"),
        }],
    }
    with open(output_dir / "roadmap.yaml", "w") as f:
        yaml.dump(roadmap, f, default_flow_style=False, sort_keys=False)
    
    # roadmap-inbox/
    (output_dir / "roadmap-inbox").mkdir(exist_ok=True)

    # .factory.md — project card
    card = f"""# Project: {project_slug}

**Full name:** {project_slug}
**Repo:** {repo_full}
**Onboarded:** {datetime.now().strftime("%Y-%m-%d")}
**Factory status:** Active

## Configuration in HyperAISystemsOS

See `config/projects.yaml` for this project's factory settings.

## Roadmap

`docs/product/roadmap.yaml` — managed by the factory pipeline.

## Inbox

`docs/product/roadmap-inbox/` — build specs land here from the factory.
"""
    with open(output_dir / ".factory.md", "w") as f:
        f.write(card)

    print(f"  ✅ Draft files created in {output_dir}/")
    print(f"     Review and push to {repo_full}:")
    print(f"     - docs/product/roadmap.yaml")
    print(f"     - docs/product/roadmap-inbox/")
    return output_dir

# ── Interactive wizard ──────────────────────────────────────────────────

def interactive_wizard():
    print("\n" + "=" * 60)
    print("  FACTORY ONBOARDING WIZARD")
    print("=" * 60)
    print()

    # 1. Project name
    while True:
        slug = input("  Project slug (e.g. 'propinfo', 'startup'): ").strip().lower()
        if re.match(r'^[a-z][a-z0-9_-]{1,32}$', slug):
            break
        print("  ❌ Slug must be 2-32 chars, lowercase, no spaces. Try again.")

    # 2. Full name
    full = input(f"  Full project name (e.g. '{slug}.co.uk'): ").strip() or slug

    # 3. GitHub repo
    while True:
        repo = input(f"  GitHub repo (e.g. 'harry738/{slug}'): ").strip()
        if "/" in repo and not repo.startswith("http"):
            break
        print("  ❌ Format: 'owner/repo' — no full URL.")

    # 4. Check repo exists
    print(f"\n  Checking {repo}...")
    exists = check_repo(repo)
    if not exists:
        create = input("  Repo not found. Create it? (y/n): ").strip().lower()
        if create == "y":
            data = gh_api("POST", "user/repos", {
                "name": repo.split("/")[1],
                "description": full,
                "private": False,
            })
            if data:
                print(f"  ✅ Repo created: {data.get('html_url')}")
                exists = True
        if not exists:
            print("  ⚠️  Continuing without repo check. Files will be staged locally.")
    
    # 5. Council mode
    print("\n  Council mode:")
    print("    1. Full (4-model council + Chair synthesis)")
    print("    2. Fast (Chair-only, for smaller projects)")
    council_choice = input("  Choice (1/2): ").strip()
    has_council = council_choice == "1"

    # 6. Sprint cadence
    print("\n  Sprint cadence:")
    print("    1. Weekly (Friday 22:00 kickoff)")
    print("    2. Biweekly")
    print("    3. Monthly")
    print("    4. None (on-demand only)")
    sprint_choice = input("  Choice (1/2/3/4): ").strip()
    cadences = {"1": "weekly", "2": "biweekly", "3": "monthly", "4": "none"}
    sprint_cadence = cadences.get(sprint_choice, "none")

    # 7. Alert channel
    alert = input("  Telegram chat ID for alerts (default: [YOUR_TELEGRAM_CHAT_ID]): ").strip() or "[YOUR_TELEGRAM_CHAT_ID]"

    # ── Summary ──
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    summary = {
        "slug": slug,
        "full_name": full,
        "repo": repo,
        "has_council": has_council,
        "sprint_cadence": sprint_cadence,
        "alert_channel": f"telegram:{alert}",
    }
    for k, v in summary.items():
        print(f"  {k}: {v}")

    confirm = input("\n  Onboard this project? (y/n): ").strip().lower()
    if confirm != "y":
        print("  ❌ Cancelled.")
        return

    # ── Execute ──
    # Add to config
    config = load_config()
    config["projects"][slug] = {
        "name": full,
        "repo": repo,
        "roadmap": "docs/product/roadmap.yaml",
        "inbox": "docs/product/roadmap-inbox/",
        "council_enabled": has_council,
        "sprint_cadence": sprint_cadence,
        "alert_channel": f"telegram:{alert}",
        "onboarded": datetime.now().strftime("%Y-%m-%d"),
    }
    save_config(config)

    # Create draft files
    out = init_repo_structure(repo, slug)

    print(f"\n  ✅ Project '{slug}' onboarded to the factory!")
    print(f"\n  Next steps:")
    print(f"  1. Review files in {out}/")
    print(f"  2. Push to {repo}:")
    print(f"     - docs/product/roadmap.yaml")
    print(f"     - docs/product/roadmap-inbox/")
    print(f"  3. Tell the factory: 'run intake for {slug}'")
    print()

# ── CLI mode ────────────────────────────────────────────────────────────

def cli_onboard(args):
    """Non-interactive onboarding from CLI args."""
    config = load_config()
    
    # Validate slug is free
    slug = args.name
    if slug in config.get("projects", {}):
        print(f"❌ Project '{slug}' already exists in config.")
        sys.exit(1)

    repo = args.repo
    council = args.council.lower() in ("true", "yes", "y", "full")
    cadence = getattr(args, "cadence", "weekly")

    config["projects"][slug] = {
        "name": getattr(args, "full_name", slug),
        "repo": repo,
        "roadmap": "docs/product/roadmap.yaml",
        "inbox": "docs/product/roadmap-inbox/",
        "council_enabled": council,
        "sprint_cadence": cadence,
        "alert_channel": f"telegram:{getattr(args, 'alert', '[YOUR_TELEGRAM_CHAT_ID]')}",
        "onboarded": datetime.now().strftime("%Y-%m-%d"),
    }
    save_config(config)
    init_repo_structure(repo, slug)
    print(f"✅ Project '{slug}' onboarded.")

# ── Main ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Factory Onboarding Wizard")
    parser.add_argument("--interactive", action="store_true", help="Interactive wizard")
    parser.add_argument("--name", help="Project slug")
    parser.add_argument("--repo", help="GitHub repo (owner/repo)")
    parser.add_argument("--council", default="true", help="Full council? (true/false)")
    parser.add_argument("--cadence", default="weekly", help="Sprint cadence")
    parser.add_argument("--full-name", help="Full project name")
    parser.add_argument("--alert", default="[YOUR_TELEGRAM_CHAT_ID]", help="Telegram chat ID")

    args = parser.parse_args()

    if args.interactive or len(sys.argv) == 1:
        interactive_wizard()
    elif args.name and args.repo:
        cli_onboard(args)
    else:
        parser.print_help()