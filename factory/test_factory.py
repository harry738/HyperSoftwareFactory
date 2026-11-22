"""Checks for the factory's Windows fixes. binley: not upstream.

Run from the repo root: python factory/test_factory.py
Needs `npm ci` done (for the dev server check) and no GitHub access. About a minute.
"""

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "factory" / "bin"
sys.path.insert(0, str(BIN))
import proc  # noqa: E402

proc.setup()
TMP = Path(tempfile.mkdtemp(prefix="factory-test-"))


def load_script(name):
    loader = importlib.machinery.SourceFileLoader(name, str(BIN / name))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(module)
    return module


job = load_script("job")
job.JOBS = TMP  # job folders go here, not in factory/jobs


def python(code):
    """A Python child that has run proc.setup(), like every factory script."""
    head = f"import sys, time, subprocess; sys.path.insert(0, {str(BIN)!r}); import proc; proc.setup()\n"
    return subprocess.Popen([sys.executable, "-X", "utf8", "-c", head + code], stdout=subprocess.PIPE, text=True)


def alive(pid):
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
    return str(pid) in out.split()


def test_git_never_prompts():  # fix 2
    child = python("import os; print(os.environ['GIT_TERMINAL_PROMPT'], os.environ['GCM_INTERACTIVE'])")
    assert child.stdout.read().split() == ["0", "never"]


def test_job_lock_waits():  # fix 5
    (TMP / "001-lock").mkdir()
    (TMP / "001-lock" / "job.json").write_text('{"id": "001-lock"}')
    holder = python(f"f = open({str(TMP / '001-lock' / '.lock')!r}, 'w'); proc.lock(f); print('held', flush=True); time.sleep(13)")
    assert holder.stdout.readline().strip() == "held"
    start = time.monotonic()
    assert job.load("001-lock")["id"] == "001-lock"  # msvcrt's own lock raised after ~10s here
    waited = time.monotonic() - start
    assert waited > 11, f"load returned after {waited:.1f}s, while the lock was still held"
    holder.wait()


def test_children_die_with_the_script():  # fix 6
    parent = python(
        "c = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
        "d = proc.spawn_detached([sys.executable, '-c', 'import time; time.sleep(120)'], '.', 'NUL')\n"
        "print(c.pid, d, flush=True); time.sleep(120)")
    child, detached = map(int, parent.stdout.readline().split())
    assert alive(child) and alive(detached)
    parent.kill()  # TerminateProcess: no cleanup runs, as when a hung script is stopped
    parent.wait()
    time.sleep(1)
    assert not alive(child), "the child outlived its script"
    assert alive(detached), "spawn_detached's process died with its script"
    subprocess.run(["taskkill", "/F", "/PID", str(detached)], capture_output=True)


def test_advance_can_be_rerun():  # fix 8
    d = TMP / "002-rerun"
    d.mkdir()
    (d / "intake.md").write_text("DECISION: ACCEPT\nRISK: low\nSURFACES: none\nRESCOPED: no\n\n## Summary\n- ok\n")
    start = {"id": "002-rerun", "issue": 2, "stage": "intake", "round": 0, "pr": None, "branch": "factory/002-rerun",
             "worktree": str(TMP / "wt" / "002-rerun"), "intake": {"risk": "low", "surfaces": []},
             "agents": {"reviewers": {"code": "haiku"}}}
    comments, worktree_adds, fetch_fails = [], [], [True]

    def fake_gh(*args):
        if args[1] == "view":
            return json.dumps({"comments": [{"body": b} for b in comments]})
        if args[1] == "comment":
            comments.append(args[args.index("--body") + 1])
            return ""
        raise AssertionError(args)

    def fake_run(cmd, cwd=None, check=True):
        if cmd[:2] == ["git", "fetch"] and fetch_fails.pop():
            raise job.Refused("fetch failed")  # the pilot's hung sign-in, after the comment was posted
        if cmd[:3] == ["git", "worktree", "add"]:
            worktree_adds.append(cmd)
            Path(cmd[-2]).mkdir(parents=True)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    job.gh, job.run = fake_gh, fake_run
    try:
        job.advance(dict(start), "spec")
        raise AssertionError("the first advance should have failed")
    except job.Refused:
        pass
    fetch_fails.append(False)
    assert job.advance(dict(start), "spec")["stage"] == "spec"
    fetch_fails.append(False)
    job.advance(dict(start), "spec")  # once more, as if the save after it had failed
    assert len(comments) == 1, f"posted the intake comment {len(comments)} times"
    assert len(worktree_adds) == 1


def test_blocked_review_goes_to_a_human():  # fix 3
    d = TMP / "003-blocked"
    (d / "round-1").mkdir(parents=True)
    (d / "round-1" / "review-code.md").write_text("VERDICT: PASS\n")
    (d / "round-1" / "review-ux.md").write_text("VERDICT: BLOCKED\n\n## Blocked\nThe dev server didn't answer.\n")
    j = {"id": "003-blocked", "issue": 3, "stage": "review", "round": 1, "round_limit": 3, "pr": None,
         "worktree": str(TMP / "wt" / "003-blocked"), "agents": {"reviewers": {"code": "haiku", "ux": "sonnet"}},
         "reviews": {"code": "PASS", "ux": "BLOCKED"}}
    job.gh = lambda *args: json.dumps({"comments": []}) if args[1] == "view" else ""
    for stage in ("approve", "build"):
        try:
            job.advance(dict(j), stage)
            raise AssertionError(f"a BLOCKED review went to {stage}")
        except job.Refused:
            pass
    assert job.advance(dict(j), "needs-human")["stage"] == "needs-human"
    assert "The dev server didn't answer." in (d / "decision.md").read_text()


def test_frontier_releases_only_unblocked_issues():  # P1-08
    frontier = load_script("frontier")
    issues = [{"number": 10, "title": "free", "labels": [{"name": "ready-for-agent"}]},
              {"number": 11, "title": "blocked", "labels": [{"name": "ready-for-agent"}]},
              {"number": 12, "title": "queued", "labels": [{"name": "ready-for-agent"}, {"name": "factory"}]}]
    open_blockers = {10: "", 11: "10\n"}  # what `gh api ... --jq` prints: open blocker numbers
    asked, labelled = [], []

    def fake_gh(*args):
        if args[:2] == ("issue", "list"):
            return json.dumps(issues)
        if args[0] == "api":
            n = int(args[2].split("/")[4])
            asked.append(n)
            return open_blockers[n]
        if args[:2] == ("issue", "edit"):
            labelled.append((int(args[2]), args[4]))
            return ""
        raise AssertionError(args)

    frontier.gh = fake_gh
    frontier.main([])
    assert labelled == [(10, "factory")], labelled
    assert asked == [10, 11], "an issue already labelled factory needs no blocker lookup"


def test_one_dev_server_per_review():  # fix 7: one shared server, stopped with its children
    j = {"id": "990-devserver", "worktree": str(TMP), "agents": {"reviewers": {"code": "haiku", "ux": "sonnet", "ui": "haiku"}}}
    (TMP / j["id"]).mkdir()
    port = job.port(j, 1)
    assert not proc.listening(port), f"something already listens on {port}"
    saved = job.CONFIG.get("dev_server")
    job.CONFIG["dev_server"] = [sys.executable, "-m", "http.server", "{port}"]  # stands in for the project's server
    try:
        job.start_dev_server(j)
        first = proc.listening(port)
        assert first, "no dev server after start_dev_server"
        job.start_dev_server(j)  # the second reviewer, or a resume: no second server
        assert proc.listening(port) == first
    finally:
        job.CONFIG["dev_server"] = saved
    stopped = proc.stop_port(port)
    time.sleep(2)
    assert not proc.listening(port), "the dev server is still listening after stop_port"
    assert not any(alive(p) for p in stopped)


def test_no_dev_server_without_config():
    j = {"id": "991-nodev", "worktree": str(TMP), "agents": {"reviewers": {"ui": "haiku"}}}
    saved = job.CONFIG.pop("dev_server", None)
    try:
        job.start_dev_server(j)  # returns at once, starts nothing
        assert not proc.listening(job.port(j, 1))
    finally:
        if saved is not None:
            job.CONFIG["dev_server"] = saved


if __name__ == "__main__":
    if not proc.WINDOWS:
        sys.exit("These checks are for the Windows patches; run them on Windows.")
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            start = time.monotonic()
            test()
            print(f"ok  {name}  ({time.monotonic() - start:.0f}s)")
    print("all passed")
