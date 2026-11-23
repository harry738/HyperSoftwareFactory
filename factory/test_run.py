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
import json, re, sys
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
elif a[0] == "api" and a[1].endswith("/comments"):
    out(pr(re.search(r"/pulls/(\d+)/", a[1]).group(1)).get("inline", []))
elif a[:2] == ["issue", "list"]:
    out([{"number": i["number"], "title": i["title"]} for i in s["issues"] if opt("--label") in i["labels"] and i["state"] == "OPEN"])
elif a[:2] == ["issue", "view"]:
    i = issue()
    out({"number": i["number"], "title": i["title"], "body": i["body"], "author": {"login": "author"}, "state": i["state"],
         "labels": [{"name": l} for l in i["labels"]], "url": "https://example.test/issues/%d" % i["number"],
         "comments": [{"author": {"login": "operator"}, "body": c, "createdAt": "2026-01-01T00:00:00Z"} for c in i["comments"]]})
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
         "headRefOid": p.get("headRefOid", "sha0")})
elif a[:2] == ["pr", "checks"]:
    out(pr().get("checks", []))
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
with Path(__file__).with_name("claude-calls.jsonl").open("a") as f:
    f.write(json.dumps({"agent": agent, "cwd": Path.cwd().as_posix(), "args": a,
                        "token": bool(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))}) + "\n")
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
elif agent == "spec-writer":
    (folder / "spec.md").write_text("# Add a file\n\n## Acceptance criteria\n1. feature.txt exists\n")
elif agent == "builder":
    (worktree / "feature.txt").write_text("issue %d round %d\n" % (job["issue"], job["round"]))
    git = ["git", "-C", str(worktree), "-c", "user.email=b@example.test", "-c", "user.name=builder"]
    subprocess.run(git + ["add", "-A"], check=True)
    subprocess.run(git + ["commit", "-q", "-m", "Add feature"], check=True)
    (folder / "build.md").write_text("STATUS: READY\n\n## Summary\n- added feature.txt\n")
elif agent.startswith("reviewer-"):
    (rd / ("review-%s.md" % agent.split("-", 1)[1])).write_text(
        "VERDICT: PASS\n\n## Summary\n- fine\n\n## Evidence\n- feature.txt:1: read it\n\n## Findings\nNone.\n")
elif agent == "approver":
    (folder / "decision.md").write_text("APPROVE\n\n## Why\nMeets the spec.\n")
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": "done", "total_cost_usd": 0.01, "session_id": "s-" + agent}))
'''

CONF = HOME / "projects" / "demo"
JOBS = HOME / "work" / "demo" / "jobs"


def env(**extra):
    return {**os.environ, "FACTORY_HOME": str(HOME), "GH_TOKEN": "secret", "FAKE_FAIL": "", "FAKE_STALL": "", "FAKE_FLAKY": "",
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


def label(n):
    gh_state(lambda s: s["issues"][n - 1].update(labels=["factory"]))


def job(n):
    return json.loads(next(JOBS.glob(f"{n:03d}-*/job.json")).read_text())


def folder(n):
    return next(JOBS.glob(f"{n:03d}-*"))


def calls():
    return [json.loads(line) for line in (TMP / "claude-calls.jsonl").read_text().splitlines()]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def set_up():
    (TMP / "fake_gh.py").write_text(FAKE_GH)
    (TMP / "fake_claude.py").write_text(FAKE_CLAUDE)
    issues = [{"number": n, "title": f"Add feature {n}", "body": "Please add feature.txt", "labels": [],
               "state": "OPEN", "comments": []} for n in range(1, 6)]
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
    config(stage_stall_minutes=0.05, stage_timeout_minutes=2, retry_waits_seconds=[0])  # quick limits for the tests
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
    assert "factory:needs-human" in issue["labels"], issue
    git("--git-dir", str(TMP / "origin.git"), "rev-parse", "--verify", j["branch"])  # the factory pushed the branch
    made = calls()
    assert [c["agent"] for c in made] == ["intake", "spec-writer", "builder", "reviewer-code", "approver"], made
    assert not any(c["token"] for c in made), "an agent stage saw the GitHub token"
    assert made[0]["cwd"].endswith("/work/demo/repo") and made[2]["cwd"] == j["worktree"], (made[0]["cwd"], made[2]["cwd"])
    reviewer = made[3]["args"]
    assert reviewer[reviewer.index("--model") + 1] == "haiku"
    tools = reviewer[reviewer.index("--tools") + 1:reviewer.index("--allowedTools")]
    assert tools == ["Read", "Grep", "Glob", "Bash", "Write"], tools  # the reviewer's own tools and no others
    assert reviewer[reviewer.index("--max-turns") + 1] == "300" and reviewer[reviewer.index("--max-budget-usd") + 1] == "5"
    assert (HOME / "setup-ran.txt").read_text().split() == ["ran"], "setup.sh should run once per worktree"
    assert not (HOME / "work" / "demo" / "repo" / "factory").exists(), "nothing of the factory belongs in the project's repo"


def test_every_stage_change_is_in_the_event_log():
    rows = [json.loads(line) for line in (JOBS / "events.jsonl").read_text().splitlines()]
    assert [r["to"] for r in rows] == ["intake", "spec", "build", "gate", "review", "approve", "needs-human"], rows
    assert rows[0]["from"] is None and rows[-1]["from"] == "approve"
    last = rows[-1]
    assert last["decision"] == "APPROVE" and last["cost_usd"] == 0.05 and last["pr"] == 10 and last["risk"] == "low", last
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
    label(4)
    res = factory("run", "demo", FAKE_STALL="builder")
    assert res.returncode == 0, res.stdout + res.stderr  # handing a job to a person isn't a failed run
    j = job(4)
    assert j["stage"] == "needs-human" and j["stopped_in"] == "build", j
    issue = gh_state()["issues"][3]
    assert "produced no output" in issue["comments"][-1] and "factory:needs-human" in issue["labels"], issue
    assert "back in build" in job_cmd("retry", "4")
    assert factory("run", "demo").returncode == 0
    j = job(4)
    assert j["stage"] == "needs-human" and j["pr"] == 13 and "stopped_in" not in j, j


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
    assert factory("run", "demo").returncode == 0
    j = job(2)
    assert j["round"] == 2 and j["round_limit"] == 3 and j["stage"] == "needs-human", j
    assert "CI failed" in (folder(2) / "feedback-1.md").read_text()
    assert factory("run", "demo").returncode == 0 and job(2)["round"] == 2, "the same failing commit must not start another round"


def test_a_job_that_spends_its_budget_is_handed_to_a_person():
    config(job_budget_usd=0.02)
    label(5)
    assert factory("run", "demo").returncode == 0
    j = job(5)
    assert j["stage"] == "needs-human" and j["stopped_in"] == "build" and j["cost_usd"] == 0.02, j
    assert "of its $0.02 budget" in gh_state()["issues"][4]["comments"][-1]


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
