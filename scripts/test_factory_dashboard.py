"""Self-check for factory-dashboard.py. Run: python scripts/test_factory_dashboard.py"""
import importlib.util, json, tempfile, threading, urllib.error, urllib.request
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
    fd.HOME = tmp / "home"  # never the real factory home
    assert fd.load_projects() == {}, "no registry yet is not an error"
    fd.CONFIG_PATH.write_text(
        f"projects:\n  alpha:\n    name: Alpha\n    path: '{tmp / 'alpha'}'\n  beta:\n    repo: o/beta\n")

    # Central layout: gamma has a job, delta none yet, "half" was never given a config.
    # alpha is installed both ways; beta is in the registry without a checkout.
    for name in ("alpha", "beta", "gamma", "delta"):
        (fd.HOME / "projects" / name).mkdir(parents=True)
        (fd.HOME / "projects" / name / "config.json").write_text("private")
    (fd.HOME / "projects" / "half").mkdir()
    central = fd.HOME / "work" / "gamma" / "jobs" / "002-y"
    central.mkdir(parents=True)
    (central / "job.json").write_text('{"id": "002-y"}')

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
        {"slug": "alpha", "name": "Alpha", "installed": True, "project": None},
        {"slug": "beta", "name": "beta", "installed": True, "project": "beta"},
        {"slug": "alpha-central", "name": "Alpha (central)", "installed": True, "project": "alpha"},
        {"slug": "delta", "name": "delta", "installed": True, "project": "delta"},
        {"slug": "gamma", "name": "gamma", "installed": True, "project": "gamma"},
    ]
    assert get("/gamma/jobs/002-y/job.json") == (200, '{"id": "002-y"}')
    assert "002-y/" in get("/gamma/jobs/")[1]
    assert get("/delta/jobs/")[0] == 404, "no job yet: the page shows an empty board"
    for escape in ("/gamma/jobs/../../../projects/gamma/config.json",
                   "/gamma/jobs/%2e%2e/%2e%2e/%2e%2e/projects/gamma/config.json"):
        assert "private" not in get(escape)[1], f"{escape} left the jobs directory"
    assert get("/alpha/jobs/001-x/job.json") == (200, '{"id": "001-x"}')
    assert "001-x/" in get("/alpha/jobs/")[1], "the board reads the directory listing"
    assert get("/")[0] == 200 and get("/dashboard.html")[0] == 200
    fd.HOME = tmp / "none"
    assert fd.load_projects()["beta"]["jobs"] is None, "no checkout, no board"
    for escape in ("/alpha/jobs/../config.json", "/alpha/jobs/%2e%2e/config.json",
                   "/alpha/jobs/../../secret.txt", "/alpha/jobs/..%5c..%5csecret.txt"):
        assert "private" not in get(escape)[1], f"{escape} left the jobs directory"
    server.shutdown()

print("ok")
