"""End-to-end check of the central layout: `factory onboard`, then `factory run`,
with stand-ins for gh and claude and a local bare repo as origin.

Run from anywhere: python factory/test_run.py
Needs git and bash. No GitHub access and no model calls. About a minute.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BIN = Path(__file__).resolve().parent / "bin"
TMP = Path(tempfile.mkdtemp(prefix="factory-run-test-"))
HOME = TMP / "home"
PY = Path(sys.executable).as_posix()

FAKE_GH = r'''
import json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
path = Path(__file__).with_name("gh-state.json")
s = json.loads(path.read_text())
a = sys.argv[1:]
opt = lambda name: a[a.index(name) + 1] if name in a else None
issue = lambda: next(i for i in s["issues"] if i["number"] == int(a[2]))
pr = lambda n=None: next(p for p in s["prs"] if p["number"] == int(n or a[2]))
out = lambda x: print(x if isinstance(x, str) else json.dumps(x))
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
if a[:2] == ["api", "user"]:
    out("operator")
elif a[0] == "api" and "/actions/jobs/" in a[1]:
    ran = not a[1].endswith("/901")  # job 901 is the one GitHub never started
    out({"conclusion": "failure", "steps": [{"name": "test"}] if ran else [], "runner_name": "runner-1" if ran else ""})
elif a[:2] == ["run", "rerun"]:
    if not os.environ.get("FAKE_CHECKS"):  # the account is fixed: the re-run passes
        for p in s["prs"]:
            p["checks"] = []
elif a[:2] == ["pr", "merge"]:
    pr()["state"] = "MERGED"
elif a[0] == "api" and a[1].endswith("/comments"):
    out(pr(re.search(r"/pulls/(\d+)/", a[1]).group(1)).get("inline", []))
elif a[:2] == ["issue", "list"]:
    out([{"number": i["number"], "title": i["title"]} for i in s["issues"] if opt("--label") in i["labels"] and i["state"] == "OPEN"])
elif a[:2] == ["issue", "view"]:
    i = issue()
    out({"number": i["number"], "title": i["title"], "body": i["body"], "author": {"login": "author"}, "state": i["state"],
         "labels": [{"name": l} for l in i["labels"]], "url": "https://example.test/issues/%d" % i["number"],
         "comments": [{"author": {"login": "operator"}, "body": c, "createdAt": "2026-01-01T00:00:00Z"} for c in i["comments"]]})
elif a[:2] == ["issue", "create"]:
    n = len(s["issues"]) + 1
    s["issues"].append({"number": n, "title": opt("--title"), "body": opt("--body"), "labels": [], "state": "OPEN", "comments": []})
    out("https://example.test/issues/%d" % n)
elif a[:2] == ["issue", "comment"]:
    issue()["comments"].append(opt("--body"))
elif a[:2] == ["issue", "edit"]:
    i = issue()
    i["labels"] = sorted((set(i["labels"]) | set((opt("--add-label") or "").split(","))) - set((opt("--remove-label") or "").split(",")) - {""})
elif a[:2] == ["pr", "list"]:
    out([{"number": p["number"], "url": p["url"]} for p in s["prs"] if p["head"] == opt("--head") and p["state"] == "OPEN"])
elif a[:2] == ["pr", "create"]:
    n = 10 + len(s["prs"])
    s["prs"].append({"number": n, "url": "https://example.test/pull/%d" % n, "head": opt("--head"), "title": opt("--title"),
                     "body": opt("--body"), "isDraft": "--draft" in a, "state": "OPEN", "comments": []})
    out(s["prs"][-1]["url"])
elif a[:2] == ["pr", "view"]:
    p = pr()
    out({"isDraft": p["isDraft"], "state": p["state"], "comments": p["comments"], "reviews": p.get("reviews", []),
         "mergeable": os.environ.get("FAKE_MERGEABLE") or p.get("mergeable", "MERGEABLE"),
         "headRefOid": p.get("headRefOid", "sha0")})
elif a[:2] == ["pr", "checks"]:
    if os.environ.get("FAKE_CHECKS"):  # they stay on the PR until a re-run, as on GitHub
        pr()["checks"] = json.loads(os.environ["FAKE_CHECKS"])
        path.write_text(json.dumps(s, indent=1))
    checks = pr().get("checks", [])
    out(checks)
    if "--watch" in a and any(c["bucket"] == "fail" for c in checks):
        sys.exit(1)
elif a[:2] == ["pr", "ready"]:
    pr()["isDraft"] = False
elif a[:2] == ["pr", "comment"]:
    pr()["comments"].append({"author": {"login": "operator"}, "body": opt("--body"), "createdAt": now})
else:
    sys.exit("fake gh: unhandled " + " ".join(a))
path.write_text(json.dumps(s, indent=1))
'''

FAKE_CLAUDE = r'''
import json, os, re, subprocess, sys, time
from pathlib import Path
a = sys.argv[1:]
agent = Path(a[a.index("--append-system-prompt-file") + 1]).stem.removeprefix("agent-")
prompt = a[a.index("-p") + 1]
# One file per call: parallel reviewers appending to one file garble it on Windows.
log = Path(__file__).with_name("claude-calls")
log.mkdir(exist_ok=True)
(log / ("%020d-%d.json" % (time.time_ns(), os.getpid()))).write_text(json.dumps(
    {"agent": agent, "cwd": Path.cwd().as_posix(), "args": a,
     "token": bool(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))}))
folder = Path(re.search(r"Job folder: (.+?)/\. ", prompt).group(1))
worktree = Path(re.search(r"Worktree: (.+?)\. Branch", prompt).group(1))
print(json.dumps({"type": "system", "subtype": "init"}), flush=True)
if os.environ.get("FAKE_FAIL") == agent:
    print(json.dumps({"type": "result", "is_error": True, "result": "boom"}))
    sys.exit(1)
if os.environ.get("FAKE_STALL") == agent:
    time.sleep(120)
if os.environ.get("FAKE_FLAKY") == agent and not (folder / "flaky-done").exists():
    (folder / "flaky-done").write_text("")
    print(json.dumps({"type": "result", "is_error": True, "result": "API Error: 429 rate limit exceeded", "session_id": "s-flaky"}))
    sys.exit(1)
job = json.loads((folder / "job.json").read_text())
rd = folder / ("round-%d" % job["round"])
if agent == "intake":
    (folder / "intake.md").write_text("DECISION: ACCEPT\nRISK: low\nSURFACES: none\nRESCOPED: no\n\n## Summary\n- small and clear\n\n## Scope\nAdd the file.\n")
elif agent == "spec-writer" and os.environ.get("FAKE_SPEC"):
    (folder / "spec.md").write_text(os.environ["FAKE_SPEC"] + "\n\n## Why\nThree features in one issue: split it into three.\n")
elif agent == "spec-writer":
    (folder / "spec.md").write_text("# Add a file\n\n## Acceptance criteria\n1. feature.txt exists\n")
elif agent == "builder":
    (worktree / "feature.txt").write_text("issue %d round %d\n" % (job["issue"], job["round"]))
    if os.environ.get("FAKE_TOUCH"):
        (worktree / os.environ["FAKE_TOUCH"]).write_text("{}\n")
    git = ["git", "-C", str(worktree), "-c", "user.email=b@example.test", "-c", "user.name=builder"]
    for args in (["add", "-A"], ["commit", "-q", "-m", "Add feature"]):
        for attempt in range(5):  # on Windows, writing an object can fail while a scanner holds its folder
            done = subprocess.run(git + args, capture_output=True, text=True)
            if done.returncode == 0:
                break
            time.sleep(0.3)
        else:
            sys.exit("fake builder: git %s: %s" % (args[0], done.stderr))
    (folder / "build.md").write_text("STATUS: READY\n\n## Summary\n- added feature.txt\n")
elif agent.startswith("reviewer-"):
    if os.environ.get("FAKE_SILENT") == agent and not (folder / "silent-done").exists():
        (folder / "silent-done").write_text("")  # replies with its verdict, writes no review file
    else:
        (rd / ("review-%s.md" % agent.split("-", 1)[1])).write_text(
            "VERDICT: PASS\n\n## Summary\n- fine, ask @someone\n\n## Evidence\n- feature.txt:1: read it\n\n## Findings\nNone.\n"
            "\n## Notes\n- feature.txt could have a newline\n")
    if os.environ.get("FAKE_EDIT") == agent:  # a reviewer that commits to the branch it reviews
        (worktree / "feature.txt").write_text("edited by a reviewer\n")
        subprocess.run(["git", "-C", str(worktree), "-c", "user.email=r@example.test", "-c", "user.name=reviewer",
                        "commit", "-q", "-am", "Reviewer edit"], check=True)
elif agent == "approver":
    (folder / "decision.md").write_text("APPROVE\n\n## Why\nMeets the spec.\n")
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": "done", "total_cost_usd": 0.01, "session_id": "s-" + agent}))
'''

CONF = HOME / "projects" / "demo"
JOBS = HOME / "work" / "demo" / "jobs"


def env(**extra):
    return {**os.environ, "FACTORY_HOME": str(HOME), "GH_TOKEN": "secret", "FAKE_FAIL": "", "FAKE_STALL": "", "FAKE_FLAKY": "", "FAKE_TOUCH": "", "FAKE_SILENT": "", "FAKE_EDIT": "", "FAKE_SPEC": "", "FAKE_CHECKS": "", "FAKE_MERGEABLE": "",
            "FACTORY_GH": f"{PY} {(TMP / 'fake_gh.py').as_posix()}", "FACTORY_CLAUDE": f"{PY} {(TMP / 'fake_claude.py').as_posix()}", **extra}


def git(*args, cwd=None):
    subprocess.run(["git", "-c", "user.email=t@example.test", "-c", "user.name=t", *args], cwd=cwd, check=True, capture_output=True)


def factory(*args, **extra):
    return subprocess.run([sys.executable, str(BIN / "factory"), *args], env=env(**extra), capture_output=True, text=True)


def job_cmd(*args):
    res = subprocess.run([sys.executable, str(BIN / "job"), *args], env=env(FACTORY_PROJECT="demo"), capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    return res.stdout


def gh_state(change=None):
    state = json.loads((TMP / "gh-state.json").read_text())
    if change:
        change(state)
        (TMP / "gh-state.json").write_text(json.dumps(state))
    return state


def config(**changes):
    c = json.loads((CONF / "config.json").read_text())
    c.update(changes)
    (CONF / "config.json").write_text(json.dumps(c))
    return c


def label(n, *more):
    gh_state(lambda s: s["issues"][n - 1].update(labels=["factory", *more]))


def stages_run(n):
    """The agents that ran for issue n, in order."""
    return [c["agent"] for c in calls() if f"Issue: #{n}." in c["args"][c["args"].index("-p") + 1]]


def events(n):
    return [e for e in map(json.loads, (JOBS / "events.jsonl").read_text().splitlines()) if e["issue"] == n]


def job(n):
    return json.loads(next(JOBS.glob(f"{n:03d}-*/job.json")).read_text())


def folder(n):
    return next(JOBS.glob(f"{n:03d}-*"))


def calls():
    return [json.loads(f.read_text()) for f in sorted((TMP / "claude-calls").glob("*.json"))]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def set_up():
    (TMP / "fake_gh.py").write_text(FAKE_GH)
    (TMP / "fake_claude.py").write_text(FAKE_CLAUDE)
    issues = [{"number": n, "title": f"Add feature {n}", "body": "Please add feature.txt", "labels": [],
               "state": "OPEN", "comments": []} for n in range(1, 18)]
    (TMP / "gh-state.json").write_text(json.dumps({"issues": issues, "prs": []}))
    label(1)  # the other issues join the queue one test at a time
    git("init", "-q", "--bare", "-b", "main", str(TMP / "origin.git"))
    git("clone", "-q", str(TMP / "origin.git"), str(TMP / "seed"))
    (TMP / "seed" / "AGENTS.md").write_text("# Demo project\n")
    git("add", "-A", cwd=TMP / "seed")
    git("commit", "-q", "-m", "seed", cwd=TMP / "seed")
    git("push", "-q", "origin", "HEAD:main", cwd=TMP / "seed")
    git("--git-dir", str(TMP / "origin.git"), "symbolic-ref", "HEAD", "refs/heads/main")


def test_onboard_registers_clones_and_reports():
    res = factory("onboard", (TMP / "origin.git").as_posix(), "--name", "demo")
    assert res.returncode == 0, res.stderr
    assert (HOME / "work" / "demo" / "repo" / "AGENTS.md").exists(), "the repo was not cloned"
    c = config()
    assert c["base_branch"] == "main" and c["unattended_merge"] is False and c["job_budget_usd"] == 15
    assert "NO   checks.sh written" in res.stdout and "yes  AGENTS.md or CLAUDE.md" in res.stdout, res.stdout
    assert "NO   CONTEXT.md" in res.stdout, res.stdout
    # The operator's part of onboarding: the project's checks, an optional setup script, no pages to review.
    (CONF / "checks.sh").write_text("#!/usr/bin/env bash\ntest -f feature.txt\n")
    (CONF / "setup.sh").write_text('#!/usr/bin/env bash\necho ran >> "$FACTORY_HOME/setup-ran.txt"\n')
    c.pop("dev_server")
    (CONF / "config.json").write_text(json.dumps(c))
    config(stage_timeout_minutes=2, retry_waits_seconds=[0])  # quick limits for the tests
    assert "yes  checks.sh written" in factory("onboard", (TMP / "origin.git").as_posix(), "--name", "demo").stdout


def test_run_takes_an_issue_to_a_pr_waiting_for_the_operator():
    res = factory("run", "demo")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(1)
    assert j["stage"] == "needs-human" and j["pr"] == 10, j
    assert j["cost_usd"] == 0.05, j["cost_usd"]  # five headless stages, from usage.jsonl
    state = gh_state()
    pr, issue = state["prs"][0], state["issues"][0]
    assert pr["isDraft"] is False and pr["body"] == "Closes #1", pr
    assert "approved, waiting for you to merge" in pr["comments"][-1]["body"], pr["comments"]
    evidence = pr["comments"][-2]["body"]
    assert "round 1 evidence" in evidence and "feature.txt:1: read it" in evidence and "checks: PASS" in evidence, evidence
    assert "@someone" not in evidence, "a review must not notify people"
    follow = state["issues"][-1]
    assert follow["title"] == "Follow-ups from #1: Add feature 1" and follow["labels"] == [], follow  # not queued
    assert "could have a newline" in follow["body"] and j["followup_issue"].endswith(f"/{follow['number']}"), follow
    assert "factory:needs-human" in issue["labels"], issue
    git("--git-dir", str(TMP / "origin.git"), "rev-parse", "--verify", j["branch"])  # the factory pushed the branch
    made = calls()
    assert [c["agent"] for c in made] == ["intake", "spec-writer", "builder", "reviewer-code", "approver"], made
    assert not any(c["token"] for c in made), "an agent stage saw the GitHub token"
    assert made[0]["cwd"].endswith("/work/demo/repo") and made[2]["cwd"] == j["worktree"], (made[0]["cwd"], made[2]["cwd"])
    reviewer = made[3]["args"]
    assert reviewer[reviewer.index("--model") + 1] == "sonnet"  # intake said low, but no path rule matched: medium
    tools = reviewer[reviewer.index("--tools") + 1:reviewer.index("--allowedTools")]
    assert tools == ["Read", "Grep", "Glob", "Write"], tools  # the reviewer's own tools less its shell, and no others
    assert reviewer[reviewer.index("--max-turns") + 1] == "300" and reviewer[reviewer.index("--max-budget-usd") + 1] == "5"
    assert (HOME / "setup-ran.txt").read_text().split() == ["ran"], "setup.sh should run once per worktree"
    assert not (HOME / "work" / "demo" / "repo" / "factory").exists(), "nothing of the factory belongs in the project's repo"


def test_reviewers_get_read_only_tools():
    allowed = lambda a: a[a.index("--allowedTools") + 1:a.index("--add-dir")]
    builder, reviewer = (allowed(c["args"]) for c in calls()[2:4])
    own_file = reviewer[3]  # all a reviewer may write: its review file for this round
    assert own_file.startswith("Edit(//") and own_file.endswith("/001-add-feature-1/round-1/review-code.md)"), own_file
    assert reviewer == ["Read", "Grep", "Glob", own_file], reviewer
    args = calls()[3]["args"]
    assert "Bash" not in args[args.index("--tools") + 1:args.index("--allowedTools")], args  # no shell at all
    assert "+++ b/feature.txt" in (folder(1) / "round-1" / "changes.diff").read_text()
    assert "--setting-sources=" in args and "--strict-mcp-config" in args, args  # the branch cannot widen its review
    assert "--setting-sources=" not in calls()[2]["args"], "the builder still loads the project's settings"
    assert builder == ["Read", "Grep", "Glob", "Bash", "Edit", "Write"], builder  # other stages keep their own tools


def test_every_stage_change_is_in_the_event_log():
    rows = [json.loads(line) for line in (JOBS / "events.jsonl").read_text().splitlines()]
    assert [r["to"] for r in rows] == ["intake", "spec", "build", "gate", "review", "approve", "needs-human"], rows
    assert rows[0]["from"] is None and rows[-1]["from"] == "approve"
    last = rows[-1]
    assert last["decision"] == "APPROVE" and last["cost_usd"] == 0.05 and last["pr"] == 10 and last["risk"] == "medium", last
    assert last["gate"] == "PASS" and last["reviews"] == {"code": "PASS"}, last


def test_a_failed_stage_leaves_the_job_for_the_next_run():
    label(2)
    res = factory("run", "demo", FAKE_FAIL="builder")
    assert res.returncode == 1 and "builder failed" in res.stdout, res.stdout + res.stderr
    assert job(2)["stage"] == "build"
    res = factory("run", "demo")  # a new run picks the job up where it stopped
    assert res.returncode == 0, res.stdout + res.stderr
    assert job(2)["stage"] == "needs-human" and job(2)["pr"] == 11
    assert [c["agent"] for c in calls()].count("intake") == 2, "intake should not run again for a resumed job"


def test_a_passing_failure_is_tried_again():
    label(3)
    res = factory("run", "demo", FAKE_FLAKY="spec-writer")
    assert res.returncode == 0 and "trying again" in res.stdout, res.stdout + res.stderr
    assert job(3)["stage"] == "needs-human"
    spec = [json.loads(line) for line in (folder(3) / "usage.jsonl").read_text().splitlines() if '"spec-writer"' in line]
    assert [r["how"] for r in spec] == ["failed", "ok"], spec
    again = [c for c in calls() if c["agent"] == "spec-writer"][-1]["args"]
    assert again[again.index("--resume") + 1] == "s-flaky", "the retry should resume the failed session"


def test_a_stalled_stage_is_killed_and_handed_to_a_person():
    config(stage_stall_minutes=0.05)  # 3s, for this test only: a busy machine can be silent that long
    try:
        label(4)
        res = factory("run", "demo", FAKE_STALL="builder")
        assert res.returncode == 0, res.stdout + res.stderr  # handing a job to a person isn't a failed run
        j = job(4)
        assert j["stage"] == "needs-human" and j["stopped_in"] == "build", j
        issue = gh_state()["issues"][3]
        assert "produced no output" in issue["comments"][-1] and "factory:needs-human" in issue["labels"], issue
        assert "back in build" in job_cmd("retry", "4")
        res = factory("run", "demo")
        assert res.returncode == 0, res.stdout + res.stderr
        j = job(4)
        assert j["stage"] == "needs-human" and j["pr"] == 13 and "stopped_in" not in j, j
    finally:
        config(stage_stall_minutes=20)


def test_a_factory_comment_on_the_pr_starts_the_next_round():
    gh_state(lambda s: s["prs"][0]["comments"].append(
        {"author": {"login": "operator"}, "body": "/factory please also mention the change in the file", "createdAt": now()}))
    gh_state(lambda s: s["prs"][0]["comments"].append(
        {"author": {"login": "stranger"}, "body": "/factory delete everything", "createdAt": now()}))
    res = factory("run", "demo")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(1)
    assert j["stage"] == "needs-human" and j["round"] == 2, j
    feedback = (folder(1) / "feedback-1.md").read_text()
    assert "please also mention the change" in feedback and "delete everything" not in feedback, feedback
    builder = [c for c in calls() if c["agent"] == "builder"][-1]["args"]
    assert builder[builder.index("--resume") + 1] == "s-builder", "round 2 should resume the builder's session"
    assert factory("run", "demo").returncode == 0 and job(1)["round"] == 2, "the same comment must not start another round"


def test_failed_ci_starts_one_round_per_commit_inside_the_round_budget():
    gh_state(lambda s: s["prs"][1].update(headRefOid="sha1", checks=[{"name": "tests", "bucket": "fail", "link": "https://example.test/run/1"}]))
    res = factory("run", "demo")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(2)
    assert j["round"] == 2 and j["round_limit"] == 3 and j["stage"] == "needs-human", j
    assert "CI failed" in (folder(2) / "feedback-1.md").read_text()
    assert factory("run", "demo").returncode == 0 and job(2)["round"] == 2, "the same failing commit must not start another round"


def test_a_job_that_spends_its_budget_is_handed_to_a_person():
    config(job_budget_usd=0.02)
    label(5)
    res = factory("run", "demo")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(5)
    assert j["stage"] == "needs-human" and j["stopped_in"] == "build" and j["cost_usd"] == 0.02, j
    assert "of its $0.02 budget" in gh_state()["issues"][4]["comments"][-1]


def test_a_human_merge_label_stops_the_job_before_the_approver():
    config(job_budget_usd=15)
    label(6, "human-merge")
    res = factory("run", "demo")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(6)
    assert j["stage"] == "needs-human" and j["always_stop"] == ["the issue is labelled `human-merge`"], j
    assert stages_run(6) == ["intake", "spec-writer", "builder", "reviewer-code"], stages_run(6)  # no approver: the rule decided
    pr = gh_state()["prs"][-1]
    assert "always-stop rule" in pr["comments"][-1]["body"] and pr["isDraft"] is False, pr
    last = events(6)[-1]
    assert last["to"] == "needs-human" and last["always_stop"] and last["decision"] == "ESCALATE", last


def test_a_sensitive_path_raises_the_risk_and_stops_the_job():
    label(7)
    res = factory("run", "demo", FAKE_TOUCH="package.json")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(7)
    assert j["risk"] == "high" and j["intake"]["risk"] == "low", j  # the paths raise the tier; intake cannot lower it
    assert j["agents"]["reviewers"] == {"code": "sonnet", "security": "opus"}, j["agents"]
    assert j["stage"] == "needs-human" and "package.json" in j["always_stop"][0], j
    assert "approver" not in stages_run(7)


def test_low_risk_paths_and_the_council_slot():
    config(risk_paths={"low": ["*.txt"], "high": []}, council={})
    label(8)
    res = factory("run", "demo")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(8)
    assert j["risk"] == "low" and j["agents"]["reviewers"] == {"code": "haiku"}, j  # every changed file is on a low path
    assert [e["to"] for e in events(8)][-3:] == ["approve", "council", "needs-human"]  # the Dev council's slot, empty for now
    assert j["stage"] == "needs-human" and "approver" in stages_run(8)


def test_the_gate_runs_the_checks_with_the_build_cache_off():
    # A cached PASS is not evidence (build plan learning 8): the gate's run turns the build caches off.
    checks = (CONF / "checks.sh").read_text()
    (CONF / "checks.sh").write_text('#!/usr/bin/env bash\ntest -f feature.txt\necho "cache: $FACTORY_GATE $TURBO_FORCE $NX_SKIP_NX_CACHE $MY_CACHE"\n'
                                    'test "$FACTORY_GATE$TURBO_FORCE$NX_SKIP_NX_CACHE$MY_CACHE" = 1truetrueoff\n')
    config(gate_env={"MY_CACHE": "off"})  # a project adds the switch for its own cache
    label(9)
    try:
        res = factory("run", "demo")
        assert res.returncode == 0, res.stdout + res.stderr
    finally:
        (CONF / "checks.sh").write_text(checks)
    j = job(9)
    assert j["stage"] == "needs-human" and [e["gate"] for e in events(9) if e["to"] == "review"] == ["PASS"], j
    assert "cache: 1 true true off" in (folder(9) / "round-1" / "checks.log").read_text()


def test_the_daily_budget_pauses_the_run_and_the_job_waits():
    spent = sum(json.loads(r)["cost_usd"] for f in JOBS.glob("*/usage.jsonl") for r in f.read_text().splitlines())
    config(daily_budget_usd=round(spent + 0.02, 2))  # room for two more stages today
    label(10)
    res = factory("run", "demo")
    assert res.returncode == 0 and "daily budget" in res.stdout, res.stdout + res.stderr
    j = job(10)
    assert j["stage"] == "build" and stages_run(10) == ["intake", "spec-writer"], j  # paused, not handed to a person
    config(daily_budget_usd=100)
    assert factory("run", "demo").returncode == 0 and job(10)["stage"] == "needs-human", job(10)


def test_the_spec_writer_can_hand_a_job_to_a_person():
    label(11)
    assert factory("run", "demo", FAKE_SPEC="STATUS: NEEDS-SPLIT").returncode == 0
    j = job(11)
    assert j["stage"] == "needs-human" and j["stopped_in"] == "spec" and stages_run(11) == ["intake", "spec-writer"], j
    assert "split it into three" in gh_state()["issues"][10]["comments"][-1], "the reason goes on the issue"
    job_cmd("retry", j["id"])  # the operator split the issue: try the spec again
    assert factory("run", "demo").returncode == 0 and job(11)["stage"] == "needs-human" and "builder" in stages_run(11), job(11)


def test_a_reviewer_that_writes_no_review_file_is_sent_back_once():
    label(12)
    res = factory("run", "demo", FAKE_SILENT="reviewer-code")
    assert res.returncode == 0, res.stdout + res.stderr
    assert job(12)["stage"] == "needs-human" and "stopped_in" not in job(12), job(12)  # in the same run
    assert stages_run(12).count("reviewer-code") == 2, stages_run(12)
    again = [c for c in calls() if c["agent"] == "reviewer-code"][-1]["args"]
    assert "Write review-code.md" in again[again.index("-p") + 1], again
    assert again[again.index("--resume") + 1] == "s-reviewer-code", "the reviewer's own session should be sent back"


def test_a_reviewer_that_changes_the_branch_stops_the_job():
    label(13)
    assert factory("run", "demo", FAKE_EDIT="reviewer-code").returncode == 0
    j = job(13)
    assert j["stage"] == "needs-human" and j["stopped_in"] == "review", j
    assert "changed during review round 1" in gh_state()["prs"][-1]["comments"][-1]["body"]
    gated = (folder(13) / "round-1" / "checks.md").read_text().splitlines()[1]
    review = (folder(13) / "round-1" / "review-code.md").read_text().splitlines()
    assert gated.startswith("COMMIT: ") and review[:2] == ["VERDICT: PASS", gated], review  # the commit it read
    job_cmd("retry", "13")  # by hand, past the engine's check: `job` won't apply the verdict to the later commit
    res = subprocess.run([sys.executable, str(BIN / "job"), "advance", "13", "approve"],
                         env=env(FACTORY_PROJECT="demo"), capture_output=True, text=True)
    assert res.returncode != 0 and "written for another commit" in res.stdout + res.stderr, res.stdout + res.stderr
NOT_STARTED = [{"name": "tests", "bucket": "fail", "link": "https://example.test/o/r/actions/runs/9/job/901"}]


def test_ci_that_never_started_is_not_a_failed_check():
    before = job(1)["round"], len(list(folder(1).glob("feedback-*.md")))
    gh_state(lambda s: s["prs"][0].update(headRefOid="sha9", checks=NOT_STARTED))
    res = factory("run", "demo")
    assert res.returncode == 0 and "CI never started" in res.stdout, res.stdout + res.stderr
    assert (job(1)["round"], len(list(folder(1).glob("feedback-*.md")))) == before, "no build round for CI that never ran"


def test_an_unattended_merge_stops_the_run_when_ci_never_starts():
    config(unattended_merge=True)
    label(14)
    label(15)
    try:
        res = factory("run", "demo", FAKE_CHECKS=json.dumps(NOT_STARTED))
    finally:
        config(unattended_merge=False)
    assert res.returncode == 0 and "CI never started" in res.stdout, res.stdout + res.stderr
    j = job(14)
    assert j["stage"] == "needs-human" and j["stopped_in"] == "merging", j  # `job retry` merges it once CI runs
    assert "billing or quota" in gh_state()["prs"][-1]["comments"][-1]["body"]
    assert not list(JOBS.glob("015-*")), "the run must stop, not start the next job"
    # The account is fixed: retry re-runs the jobs GitHub never started, and merges.
    gh_state(lambda s: s["issues"][14].update(labels=[]))
    job_cmd("retry", j["id"])
    config(unattended_merge=True)
    try:
        res = factory("run", "demo")
    finally:
        config(unattended_merge=False)
    assert res.returncode == 0 and job(14)["stage"] == "merged", res.stdout + res.stderr


def test_a_waiting_pr_that_conflicts_gets_one_merge_main_round():
    pr = job(6)["pr"]
    before = job(6)["round"]
    conflict = lambda value: gh_state(lambda s: next(p for p in s["prs"] if p["number"] == pr).update(mergeable=value))
    conflict("CONFLICTING")
    res = factory("run", "demo")
    assert res.returncode == 0 and "merge-main round" in res.stdout, res.stdout + res.stderr
    j = job(6)
    assert j["round"] == before + 1 and j["stage"] == "needs-human" and j["round_limit"] == 3, j  # the budget is not renewed
    assert j["held"], "a job that was waiting for a person still waits after merging the base"
    assert "git merge origin/main" in sorted(folder(6).glob("feedback-*.md"))[-1].read_text()
    res = factory("run", "demo")
    assert res.returncode == 0 and job(6)["round"] == before + 1, "the same commit must not start another round"
    conflict("MERGEABLE")


def test_a_conflict_during_review_goes_back_to_the_builder_before_reviewers_run():
    label(16)
    res = factory("run", "demo", FAKE_MERGEABLE="CONFLICTING")
    assert res.returncode == 0, res.stdout + res.stderr
    j = job(15)  # job ids follow creation order, and issue 15 never became a job
    assert j["stage"] == "needs-human" and j["round"] == 2, j
    ran = stages_run(16)
    assert ran[2:5] == ["builder", "builder", "reviewer-code"], ran  # round 1's reviewers were never started


def job_for_issue(n):
    """The job made from issue n. Job ids follow creation order, so they are not issue numbers."""
    for f in JOBS.glob("*/job.json"):
        j = json.loads(f.read_text())
        if j["issue"] == n:
            return j
    raise AssertionError(f"no job was made from issue {n}")


def test_an_unattended_merge_fails_closed_unless_set_to_true():
    config(unattended_merge="yes")  # not the boolean true: a person merges, not the factory
    label(17)
    try:
        res = factory("run", "demo")
    finally:
        config(unattended_merge=False)
    assert res.returncode == 0, res.stdout + res.stderr
    assert job_for_issue(17)["stage"] == "needs-human", job_for_issue(17)


def test_status_lists_every_job():
    out = factory("status").stdout
    assert "== demo" in out and "001-add-feature-1" in out and "005-add-feature-5" in out, out


if __name__ == "__main__":
    set_up()
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"ok  {name}", flush=True)
    print("all passed")
