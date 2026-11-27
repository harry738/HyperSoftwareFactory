"""Browser check of the pixel dashboard's keyboard behaviour, in a real Chromium.

Runs only when FACTORY_BROWSER_TESTS=1, because it needs Playwright and a browser:

    pip install playwright && python -m playwright install chromium
    FACTORY_BROWSER_TESTS=1 python scripts/test_dashboard_browser.py

Without the variable it prints a skip line and exits 0, so CI is unaffected.
It serves factory/dashboard-pixel.html from a temporary folder with three made-up
jobs, then checks focus on open, the Tab trap, and focus on close.
"""

import json
import os
import shutil
import sys
import tempfile
import threading
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "factory" / "dashboard-pixel.html"


def make_site(site: Path) -> None:
    shutil.copy(PAGE, site / "dashboard.html")
    (site / "VERSION").write_text("0.0.0-test\n", encoding="utf-8")
    jobs = {
        "001-add-export": {"title": "Add CSV export to the orders page", "stage": "needs-human", "round": 1,
                           "cost_usd": 1.42, "started": "2026-11-27T09:00:00Z", "issue": 14,
                           "issue_url": "https://example.invalid/issues/14", "pr": 21,
                           "pr_url": "https://example.invalid/pull/21", "agents": {"reviewers": {"code": "sonnet"}}},
        "002-fix-login": {"title": "Fix login redirect loop", "stage": "build", "round": 1,
                          "cost_usd": 0.37, "started": "2026-11-27T10:00:00Z", "issue": 15,
                          "issue_url": "https://example.invalid/issues/15"},
        "003-dark-mode": {"title": "Add dark mode toggle", "stage": "merged", "round": 1,
                          "cost_usd": 2.10, "started": "2026-11-26T08:00:00Z", "ended": "2026-11-26T11:00:00Z",
                          "issue": 9, "issue_url": "https://example.invalid/issues/9", "pr": 18,
                          "pr_url": "https://example.invalid/pull/18", "agents": {"reviewers": {"code": "sonnet"}}},
    }
    for job_id, job in jobs.items():
        folder = site / "jobs" / job_id
        folder.mkdir(parents=True)
        (folder / "job.json").write_text(json.dumps({"id": job_id, **job}), encoding="utf-8")
    (site / "jobs" / "001-add-export" / "spec.md").write_text("## Summary\n- Adds CSV export\n", encoding="utf-8")
    (site / "jobs" / "001-add-export" / "round-1").mkdir()
    (site / "jobs" / "001-add-export" / "round-1" / "checks.md").write_text("PASS\n", encoding="utf-8")


def serve(site: Path) -> ThreadingHTTPServer:
    handler = partial(SimpleHTTPRequestHandler, directory=str(site))
    handler.log_message = lambda *args, **kwargs: None  # keep the test output readable
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> int:
    if os.environ.get("FACTORY_BROWSER_TESTS") != "1":
        print("skipped: set FACTORY_BROWSER_TESTS=1 to run the browser check")
        return 0
    from playwright.sync_api import sync_playwright

    site = Path(tempfile.mkdtemp(prefix="dash-browser-"))
    make_site(site)
    server = serve(site)
    url = f"http://127.0.0.1:{server.server_address[1]}/dashboard.html"

    def state(page):
        return page.evaluate("""() => {
            const a = document.activeElement;
            return {
                inDrawer: !!a.closest('.drawer'),
                isCard: !!a.closest('[data-job]') && !a.closest('.drawer'),
                bodyOpen: document.body.classList.contains('open'),
                inert: [...document.body.children].filter(e => e.inert).map(e => e.id || e.tagName),
            };
        }""")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector("[data-job]")
            page.wait_for_timeout(1200)  # let the first poll finish

            card = page.locator("[data-job='002-fix-login']")
            card.click()
            page.wait_for_timeout(600)  # the drawer slides in over .25s, then takes focus

            opened = state(page)
            assert opened["bodyOpen"], opened
            assert opened["inDrawer"], f"focus did not move into the drawer on open: {opened}"
            assert sorted(opened["inert"]) == ["FOOTER", "HEADER", "MAIN", "SCRIPT"], opened

            for i in range(15):
                page.keyboard.press("Tab")
                s = state(page)
                assert s["inDrawer"], f"Tab left the drawer on press {i + 1}: {s}"
            for i in range(4):
                page.keyboard.press("Shift+Tab")
                s = state(page)
                assert s["inDrawer"], f"Shift+Tab left the drawer on press {i + 1}: {s}"

            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
            closed = state(page)
            assert not closed["bodyOpen"] and closed["inert"] == [], closed
            assert closed["isCard"], f"focus did not return to the card that opened the drawer: {closed}"

            browser.close()
    finally:
        server.shutdown()
        shutil.rmtree(site, ignore_errors=True)
    print("ok  browser: focus on open, Tab trap, focus back on close")
    return 0


if __name__ == "__main__":
    sys.exit(main())
