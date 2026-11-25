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
REAL_RUN = job.run  # tests that fake git replace job.run, then restore this


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


def test_rejection_clears_ready_for_agent():  # frontier must not re-release a rejected issue
    d = TMP / "005-rejected"
    d.mkdir()
    (d / "intake.md").write_text("DECISION: REJECT\nRISK: low\nSURFACES: none\nRESCOPED: no\n\n## Summary\n- no\n")
    edits = []

    def fake_gh(*args):
        if args[1] == "view":
            return json.dumps({"comments": []})
        if args[1] == "edit":
            edits.append(args)
        return ""

    job.gh = fake_gh
    job.run = lambda cmd, cwd=None, check=True: subprocess.CompletedProcess(cmd, 0, "", "")  # no real git
    j = {"id": "005-rejected", "issue": 5, "stage": "intake", "round": 0, "pr": None, "branch": "factory/005-rejected",
         "worktree": str(TMP / "wt" / "005-rejected"), "intake": None, "agents": None}
    assert job.advance(j, "rejected")["stage"] == "rejected"
    removed = edits[0][edits[0].index("--remove-label") + 1].split(",")
    assert {"factory", "ready-for-agent"} <= set(removed), removed


def test_worktree_cleanup_can_be_repeated():  # the trial-1 leftover that blocked the queue
    repo = TMP / "repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                    "--allow-empty", "-m", "x"], check=True)
    wt = repo / ".worktrees" / "006-cleanup"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "-b", "factory/006-cleanup", str(wt)], check=True)
    (wt / "big.txt").write_text("x")
    j = {"id": "006-cleanup", "worktree": str(wt), "branch": "factory/006-cleanup"}
    job.run = lambda cmd, cwd=None, check=True: REAL_RUN(cmd, cwd=repo, check=check)
    try:
        # The half-done state from the trial: git has forgotten the worktree, the folder is still there.
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)], capture_output=True)
        wt.mkdir(parents=True, exist_ok=True)
        (wt / "leftover.txt").write_text("x")
        job.remove_worktree(j)
        job.remove_worktree(j)  # and again: no error
    finally:
        job.run = REAL_RUN
    assert not wt.exists(), "the leftover folder is still there"
    branches = subprocess.run(["git", "-C", str(repo), "branch", "--list", "factory/*"], capture_output=True, text=True).stdout
    assert not branches.strip(), branches


def test_review_without_evidence_is_refused():  # hardening: no 8-second reviews
    d = TMP / "007-evidence"
    (d / "round-1").mkdir(parents=True)
    review = d / "round-1" / "review-code.md"
    review.write_text("VERDICT: PASS\n\n## Summary\n- looks fine\n\n## Findings\nNone.\n")
    j = {"id": "007-evidence", "issue": 7, "stage": "review", "round": 1, "round_limit": 3, "pr": 1,
         "worktree": str(TMP), "intake": None, "gate": None, "agents": {"reviewers": {"code": "haiku"}}, "reviews": {}}
    job.cost_usd = lambda j: 0.0
    job.always_stop = lambda j: []  # no GitHub or git here; the always-stop rules have their own test in test_run.py
    assert job.sync(dict(j))["reviews"] == {"code": "no-evidence"}
    try:
        job.advance(job.sync(dict(j)), "approve")
        raise AssertionError("a review with no evidence went to approve")
    except job.Refused as e:
        assert "Evidence" in str(e), e
    review.write_text("VERDICT: PASS\n\n## Summary\n- fine\n\n## Evidence\n- src/lib/payments.ts:65: new pattern\n\n## Findings\nNone.\n")
    assert job.advance(job.sync(dict(j)), "approve")["stage"] == "approve"


def test_sensitive_path_adds_security_review():  # hardening: risk by path, not intake's rating
    d = TMP / "008-sensitive"
    (d / "round-1").mkdir(parents=True)
    (d / "round-1" / "checks.md").write_text("GATE: PASS\nCOMMIT: abc123\n\n## Summary\n- ok\n")

    def fake_run(cmd, cwd=None, check=True):
        out = {"rev-parse": "abc123\n", "diff": "README.md\nsrc/lib/payments.ts\n"}.get(cmd[1], "")
        return subprocess.CompletedProcess(cmd, 0, out, "")

    saved = {k: job.CONFIG.get(k) for k in ("sensitive_paths", "sensitive_reviewers")}
    job.CONFIG.update(sensitive_paths=["src/lib/payments.ts"], sensitive_reviewers={"code": "sonnet", "security": "opus"})
    job.run = fake_run
    try:
        j = {"id": "008-sensitive", "issue": 8, "stage": "gate", "round": 1, "round_limit": 3, "pr": 1,
             "worktree": str(TMP), "agents": {"reviewers": {"code": "haiku"}}, "reviews": {}}
        j = job.advance(j, "review")
    finally:
        job.run = REAL_RUN
        job.CONFIG.update(saved)
    assert j["agents"]["reviewers"] == {"code": "sonnet", "security": "opus"}, j["agents"]
    assert set(j["reviews"]) == {"code", "security"}


def test_template_sensitive_paths():  # the shipped defaults catch manifests, lockfiles and env files at any depth
    import fnmatch
    for path, hit in (("package.json", True), ("apps/web/package.json", True), ("pnpm-lock.yaml", True),
                      (".env.local", True), ("src/app/page.tsx", False), ("src/lib/clock.ts", False)):
        assert any(fnmatch.fnmatch(path, p) for p in job.CONFIG["sensitive_paths"]) == hit, path


def test_gate_rejects_new_and_renamed_in_protected_files():  # S1.9: a new CI workflow used to pass
    gate = load_script("gate")
    repo = TMP / "protectedrepo"

    def g(*args):
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                       check=True, capture_output=True)

    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "deploy.yml").write_text("on: push\n")
    (repo / "README.md").write_text("x\n")
    g("add", "-A")
    g("commit", "-q", "-m", "base")
    g("update-ref", f"refs/remotes/origin/{gate.CONFIG['base_branch']}", "HEAD")
    assert gate.protected_changes(repo) == []
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "new.yml").write_text("on: pull_request\n")  # added
    g("mv", "docs/deploy.yml", ".github/workflows/deploy.yml")  # renamed in
    (repo / "README.md").write_text("y\n")  # not protected
    g("add", "-A")
    g("commit", "-q", "-m", "branch")
    hits = gate.protected_changes(repo)
    assert any(h.endswith(".github/workflows/new.yml") for h in hits), hits
    assert any(h.endswith(".github/workflows/deploy.yml") for h in hits), hits
    assert not any("README.md" in h for h in hits), hits


def test_hook_skips_checks_after_a_clean_pass():  # hardening: the Stop hook doesn't repeat a passed run
    gate = load_script("gate")
    repo = TMP / "hookrepo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                    "--allow-empty", "-m", "x"], check=True)
    assert not gate.passed_on_head(repo)  # no marker yet
    head = gate.clean_head(repo)
    (gate.git_dir(repo) / "factory-checks-passed").write_text(head)
    assert gate.passed_on_head(repo)
    (repo / "new.txt").write_text("uncommitted")
    assert not gate.passed_on_head(repo), "a dirty tree must run the checks again"
    (repo / "new.txt").unlink()
    (gate.git_dir(repo) / "factory-checks-passed").write_text("0" * 40)
    assert not gate.passed_on_head(repo), "a pass on another commit doesn't count"


def test_merge_waits_for_ci():  # main requires CI, so job merge must wait for it
    j = {"id": "009-ci", "pr": 9}
    calls = []

    def fake_run(code, out):
        def run(cmd, cwd=None, check=True):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, code, out, "")
        return run

    try:
        job.run = fake_run(0, "checks\tpass\nsemgrep\tpass\n")
        assert job.wait_for_ci(j, settle=0) is None
        watched = [c for c in calls if "--watch" in c]
        assert watched and watched[-1][-6:-3] == ["checks", "9", "--watch"], calls
        job.run = fake_run(0, '[{"name": "tests", "bucket": "cancel", "link": ""}]')
        assert "CI was cancelled on PR #9" in job.wait_for_ci(j, settle=0)
        job.run = fake_run(1, "checks\tfail\n")
        assert "CI didn't pass on PR #9" in job.wait_for_ci(j, settle=0)
        job.run = fake_run(1, "no checks reported on the 'factory/009-ci' branch")
        assert job.wait_for_ci(j, settle=0) is None  # a repo or branch without CI isn't blocked

        tries = []

        def flaky_gh(*args):
            tries.append(args)
            if len(tries) < 3:
                raise job.Refused("Required status check \"checks\" is expected")
            return ""

        job.gh = flaky_gh
        job.merge_when_allowed(j, pause=0)
        assert len(tries) == 3, "merge should retry while a required check is pending"

        def broken_gh(*args):
            raise job.Refused("Pull request is not mergeable: conflicts")

        job.gh = broken_gh
        try:
            job.merge_when_allowed(j, pause=0)
            raise AssertionError("a non-CI merge failure must not be retried")
        except job.Refused:
            pass
    finally:
        job.run = REAL_RUN


def test_no_hand_merge_hook():
    hook = ROOT / ".claude" / "hooks" / "no-hand-merge.py"

    def blocked(command):
        res = subprocess.run([sys.executable, str(hook)], input=json.dumps({"tool_input": {"command": command}}),
                             capture_output=True, text=True)
        return res.returncode == 2

    for command in ("gh pr merge 27 --merge", "gh pr view 27 && gh pr merge 27", "gh  pr   merge 3",
                    "gh.exe pr merge 3", "python -c \"run(['gh', 'pr', 'merge', '3'])\"",
                    "gh api -X PUT repos/o/r/pulls/27/merge"):
        assert blocked(command), command
    for command in ("factory/bin/job merge 004-x", "gh pr view 27", "git merge --no-edit origin/main",
                    "gh pr list --search merged"):
        assert not blocked(command), command


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
