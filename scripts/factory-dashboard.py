#!/usr/bin/env python3
"""One dashboard, a board per project in config/projects.yaml.

Usage:
    python scripts/factory-dashboard.py [port]      (default 8020)

Serves factory/dashboard.html with a tab per registered project. A project's
board reads <path>/factory/jobs/, where `path` is the project's local checkout.
A project with no `path` gets a tab that says so. Projects onboarded into the factory
home ($FACTORY_HOME, default ~/factory-home) get a tab too, reading work/<project>/jobs/.

Each tab lists the repo's pull requests, read with the GitHub CLI (`gh`, signed in).

config/projects.yaml is gitignored: this repo is public, and the registry names
real projects and paths on your machine. config/projects.example.yaml shows its shape.

Requires PyYAML (pip install -r requirements.txt). Listens on localhost only.
"""
import json, os, shlex, subprocess, sys, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import yaml

FACTORY_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = FACTORY_ROOT / "config" / "projects.yaml"
HOME = Path(os.environ.get("FACTORY_HOME") or Path.home() / "factory-home")
GH = shlex.split(os.environ.get("FACTORY_GH", "gh"))
PR_TTL = 60  # seconds; the page polls every 2s and GitHub rate-limits
pr_cache = {}  # repo -> (fetched at, payload)


def load_projects():
    """slug -> {"name", "repo", "jobs": Path to the project's jobs, or None}."""
    config = {}
    if CONFIG_PATH.exists():
        config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    out = {}
    for slug, p in (config.get("projects") or {}).items():
        factory = Path(p["path"]).expanduser() / "factory" if p.get("path") else None
        out[slug] = {"name": p.get("name") or slug, "repo": p.get("repo"),
                     "jobs": factory / "jobs" if factory and factory.is_dir() else None}
    for conf in sorted(HOME.glob("projects/*/config.json")):
        slug = conf.parent.name
        known = out.get(slug, {})
        out[slug] = {"name": known.get("name") or slug,
                     "repo": json.loads(conf.read_text(encoding="utf-8")).get("repo") or known.get("repo"),
                     "jobs": HOME / "work" / slug / "jobs"}
    return out


def check_state(rollup):
    """One word for a PR's checks: fail, pending, pass, or none."""
    states = [c.get("conclusion") or c.get("state") or "PENDING" for c in rollup or []]
    if any(s in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE") for s in states):
        return "fail"
    if any(s in ("PENDING", "EXPECTED") for s in states):
        return "pending"
    return "pass" if states else "none"


def pull_requests(repo):
    at, payload = pr_cache.get(repo, (0, None))
    if time.time() - at < PR_TTL:
        return payload
    # ponytail: the newest 50 PRs in any state; page through them when a repo outgrows that
    cmd = [*GH, "pr", "list", "--repo", repo, "--state", "all", "--limit", "50", "--json",
           "number,title,url,state,isDraft,reviewDecision,mergeable,updatedAt,statusCheckRollup"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=30)
        if r.returncode:
            payload = {"error": r.stderr.strip() or f"gh exited {r.returncode}"}
        else:
            prs = json.loads(r.stdout)
            for pr in prs:
                pr["checks"] = check_state(pr.pop("statusCheckRollup", None))
            payload = {"prs": prs}
    except (OSError, subprocess.TimeoutExpired, ValueError) as e:
        payload = {"error": str(e)}
    pr_cache[repo] = (time.time(), payload)
    return payload


class Handler(SimpleHTTPRequestHandler):
    projects = {}

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Private PR titles are served here: refuse a web page that rebinds its name to 127.0.0.1.
        if urlsplit("//" + self.headers.get("Host", "")).hostname not in ("localhost", "127.0.0.1"):
            return self.send_error(403)
        path = urlsplit(self.path).path
        if path == "/projects.json":
            return self.send_json([{"slug": s, "name": p["name"], "installed": p["jobs"] is not None,
                                    "repo": p["repo"]} for s, p in self.projects.items()])
        slug, _, leaf = path.lstrip("/").partition("/")
        if leaf == "prs.json" and self.projects.get(slug, {}).get("repo"):
            return self.send_json(pull_requests(self.projects[slug]["repo"]))
        if path == "/":
            self.path = "/dashboard.html"
        super().do_GET()

    def translate_path(self, path):
        # /<slug>/jobs/... is that project's factory/jobs/; all else is this repo's factory/.
        # The parent drops ".." parts, so a request cannot leave the directory set here.
        slug, jobs, rest = (urlsplit(path).path.lstrip("/").split("/", 2) + ["", ""])[:3]
        root = self.projects.get(slug, {}).get("jobs")
        if root and jobs == "jobs":
            self.directory = str(root)
            return super().translate_path("/" + rest)
        self.directory = str(FACTORY_ROOT / "factory")
        return super().translate_path(path)

    def log_message(self, *args):  # the dashboard polls every 2s
        pass


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8020
    Handler.projects = load_projects()
    if not Handler.projects:
        print(f"  no projects: create {CONFIG_PATH} (see projects.example.yaml)")
    for slug, p in Handler.projects.items():
        print(f"  {slug:<12} {p['jobs'] or 'no local checkout: set `path` in config/projects.yaml'}")
    print(f"http://localhost:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
