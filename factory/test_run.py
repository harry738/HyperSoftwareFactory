"""End-to-end check of the central layout: `factory onboard`, then `factory run`,
with stand-ins for gh and claude and a local bare repo as origin.

Run from anywhere: python factory/test_run.py
Needs git and bash. No GitHub access and no model calls. Under a minute.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parent / "bin"
TMP = Path(tempfile.mkdtemp(prefix="factory-run-test-"))
HOME = TMP / "home"
PY = Path(sys.executable).as_posix()

FAKE_GH = r'''
import json, sys
from pathlib import Path
path = Path(__file__).with_name("gh-state.json")
s = json.loads(path.read_text())
a = sys.argv[1:]
opt = lambda name: a[a.index(name) + 1] if name in a else None
issue = lambda: next(i for i in s["issues"] if i["number"] == int(a[2]))
pr = lambda: next(p for p in s["prs"] if p["number"] == int(a[2]))
out = lambda x: print(x if isinstance(x, str) else json.dumps(x))
if a[:2] == ["api", "user"]:
    out("operator")
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
    out({"isDraft": p["isDraft"], "state": p["state"], "comments": [{"body": c} for c in p["comments"]]})
elif a[:2] == ["pr", "ready"]:
    pr()["isDraft"] = False
elif a[:2] == ["pr", "comment"]:
    pr()["comments"].append(opt("--body"))
else:
    sys.exit("fake gh: unhandled " + " ".join(a))
path.write_text(json.dumps(s, indent=1))
'''

FAKE_CLAUDE = r'''
import json, os, re, subprocess, sys
from pathlib import Path
a = sys.argv[1:]
agent = Path(a[a.index("--append-system-prompt-file") + 1]).stem.removeprefix("agent-")
prompt = a[a.index("-p") + 1]
with Path(__file__).with_name("claude-calls.jsonl").open("a") as f:
    f.write(json.dumps({"agent": agent, "cwd": Path.cwd().as_posix(), "args": a,
                        "token": bool(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))}) + "\n")
if os.environ.get("FAKE_FAIL") == agent:
    print(json.dumps({"is_error": True, "result": "boom"}))
    sys.exit(1)
folder = Path(re.search(r"Job folder: (.+?)/\. ", prompt).group(1))
worktree = Path(re.search(r"Worktree: (.+?)\. Branch", prompt).group(1))
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
print(json.dumps({"is_error": False, "result": "done", "total_cost_usd": 0.01, "session_id": "s-" + agent}))
'''


def git(*args, cwd=None):
    subprocess.run(["git", "-c", "user.email=t@example.test", "-c", "user.name=t", *args], cwd=cwd, check=True, capture_output=True)


def factory(*args, **extra):
    env = {**os.environ, "FACTORY_HOME": str(HOME), "GH_TOKEN": "secret", "FAKE_FAIL": "",
           "FACTORY_GH": f"{PY} {(TMP / 'fake_gh.py').as_posix()}", "FACTORY_CLAUDE": f"{PY} {(TMP / 'fake_claude.py').as_posix()}", **extra}
    return subprocess.run([sys.executable, str(BIN / "factory"), *args], env=env, capture_output=True, text=True)


def gh_state():
    return json.loads((TMP / "gh-state.json").read_text())


def job(n):
    return json.loads(next((HOME / "work" / "demo" / "jobs").glob(f"{n:03d}-*/job.json")).read_text())


def calls():
    return [json.loads(line) for line in (TMP / "claude-calls.jsonl").read_text().splitlines()]


def set_up():
    (TMP / "fake_gh.py").write_text(FAKE_GH)
    (TMP / "fake_claude.py").write_text(FAKE_CLAUDE)
    issues = [{"number": n, "title": f"Add feature {n}", "body": "Please add feature.txt", "labels": ["factory"],
               "state": "OPEN", "comments": []} for n in (1, 2)]
    issues[1]["labels"] = []  # the second issue joins the queue later
    (TMP / "gh-state.json").write_text(json.dumps({"issues": issues, "prs": []}))
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
    conf = HOME / "projects" / "demo"
    assert (HOME / "work" / "demo" / "repo" / "AGENTS.md").exists(), "the repo was not cloned"
    config = json.loads((conf / "config.json").read_text())
    assert config["base_branch"] == "main" and config["unattended_merge"] is False
    assert "NO   checks.sh written" in res.stdout and "yes  AGENTS.md or CLAUDE.md" in res.stdout, res.stdout
    assert "NO   CONTEXT.md" in res.stdout, res.stdout
    # The operator's part of onboarding: the project's checks, an optional setup script, no pages to review.
    (conf / "checks.sh").write_text("#!/usr/bin/env bash\ntest -f feature.txt\n")
    (conf / "setup.sh").write_text('#!/usr/bin/env bash\necho ran >> "$FACTORY_HOME/setup-ran.txt"\n')
    config.pop("dev_server")
    (conf / "config.json").write_text(json.dumps(config))
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
    assert "approved, waiting for you to merge" in pr["comments"][-1], pr["comments"]
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
    assert (HOME / "setup-ran.txt").read_text().split() == ["ran"], "setup.sh should run once per worktree"
    assert not (HOME / "work" / "demo" / "repo" / "factory").exists(), "nothing of the factory belongs in the project's repo"


def test_a_failed_stage_leaves_the_job_for_the_next_run():
    state = gh_state()
    state["issues"][1]["labels"] = ["factory"]
    (TMP / "gh-state.json").write_text(json.dumps(state))
    res = factory("run", "demo", FAKE_FAIL="builder")
    assert res.returncode == 1 and "builder failed" in res.stdout, res.stdout + res.stderr
    assert job(2)["stage"] == "build"
    res = factory("run", "demo")  # a new run picks the job up where it stopped
    assert res.returncode == 0, res.stdout + res.stderr
    assert job(2)["stage"] == "needs-human" and job(2)["pr"] == 11
    assert [c["agent"] for c in calls()].count("intake") == 2, "intake should not run again for a resumed job"


def test_status_lists_every_job():
    out = factory("status").stdout
    assert "== demo" in out and "001-add-feature-1" in out and "002-add-feature-2" in out, out


if __name__ == "__main__":
    set_up()
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"ok  {name}", flush=True)
    print("all passed")
