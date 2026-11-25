"""Self-check for factory-dashboard.py. Run: python scripts/test_factory_dashboard.py"""
import importlib.util, json, sys, tempfile, threading, urllib.error, urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

spec = importlib.util.spec_from_file_location("dash", Path(__file__).with_name("factory-dashboard.py"))
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    job = tmp / "alpha" / "factory" / "jobs" / "001-x"
    job.mkdir(parents=True)
    (job / "job.json").write_text('{"id": "001-x"}')
    (tmp / "alpha" / "factory" / "config.json").write_text("private")
    (tmp / "alpha" / "secret.txt").write_text("private")
    fd.CONFIG_PATH = tmp / "projects.yaml"
    fd.HOME = tmp / "home"
    assert fd.load_projects() == {}, "no registry yet is not an error"
    fd.CONFIG_PATH.write_text(
        f"projects:\n  alpha:\n    name: Alpha\n    path: '{tmp / 'alpha'}'\n  beta:\n    repo: o/beta\n")

    conf = fd.HOME / "projects" / "gamma"
    conf.mkdir(parents=True)
    (conf / "config.json").write_text('{"repo": "o/gamma"}')
    gh = tmp / "gh.py"
    gh.write_text("""print('[{"number": 7, "statusCheckRollup": [{"conclusion": "SUCCESS"}, {"state": "FAILURE"}]}]')""")
    fd.GH = [sys.executable, str(gh)]
    assert fd.check_state([]) == "none" and fd.check_state([{"status": "IN_PROGRESS", "conclusion": ""}]) == "pending"
    assert fd.check_state([{"conclusion": "SUCCESS"}, {"conclusion": "SKIPPED"}]) == "pass"

    fd.Handler.projects = fd.load_projects()
    server = ThreadingHTTPServer(("127.0.0.1", 0), fd.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"

    def get(path):
        try:
            with urllib.request.urlopen(base + path) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, ""

    assert json.loads(get("/projects.json")[1]) == [
        {"slug": "alpha", "name": "Alpha", "installed": True, "repo": None},
        {"slug": "beta", "name": "beta", "installed": False, "repo": "o/beta"},
        {"slug": "gamma", "name": "gamma", "installed": True, "repo": "o/gamma"},
    ]
    assert json.loads(get("/gamma/prs.json")[1]) == {"prs": [{"number": 7, "checks": "fail"}]}
    assert get("/alpha/prs.json")[0] == 404, "no repo, no PRs"
    try:
        urllib.request.urlopen(urllib.request.Request(base + "/gamma/prs.json", headers={"Host": "evil.example"}))
        raise AssertionError("a foreign Host header was served")
    except urllib.error.HTTPError as e:
        assert e.code == 403
    assert get("/alpha/jobs/001-x/job.json") == (200, '{"id": "001-x"}')
    assert "001-x/" in get("/alpha/jobs/")[1], "the board reads the directory listing"
    assert get("/")[0] == 200 and get("/dashboard.html")[0] == 200
    assert get("/beta/jobs/")[0] == 404, "no checkout, no board"
    for escape in ("/alpha/jobs/../config.json", "/alpha/jobs/%2e%2e/config.json",
                   "/alpha/jobs/../../secret.txt", "/alpha/jobs/..%5c..%5csecret.txt"):
        assert "private" not in get(escape)[1], f"{escape} left the jobs directory"
    server.shutdown()

print("ok")
