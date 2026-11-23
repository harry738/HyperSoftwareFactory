#!/usr/bin/env python3
"""One dashboard, a board per project in config/projects.yaml.

Usage:
    python scripts/factory-dashboard.py [port]      (default 8020)

Serves factory/dashboard.html with a tab per registered project. A project's
board reads <path>/factory/jobs/, where `path` is the project's local checkout.
A project with no `path` gets a tab that says so.

config/projects.yaml is gitignored: this repo is public, and the registry names
real projects and paths on your machine. config/projects.example.yaml shows its shape.

Requires PyYAML (pip install -r requirements.txt). Listens on localhost only.
"""
import json, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import yaml

FACTORY_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = FACTORY_ROOT / "config" / "projects.yaml"


def load_projects():
    """slug -> {"name", "jobs": Path to the checkout's factory/jobs, or None}."""
    config = {}
    if CONFIG_PATH.exists():
        config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    out = {}
    for slug, p in (config.get("projects") or {}).items():
        factory = Path(p["path"]).expanduser() / "factory" if p.get("path") else None
        out[slug] = {"name": p.get("name") or slug,
                     "jobs": factory / "jobs" if factory and factory.is_dir() else None}
    return out


class Handler(SimpleHTTPRequestHandler):
    projects = {}

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/projects.json":
            body = json.dumps([{"slug": s, "name": p["name"], "installed": p["jobs"] is not None}
                               for s, p in self.projects.items()]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
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
