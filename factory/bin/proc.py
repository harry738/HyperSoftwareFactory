"""Process helpers shared by the factory scripts. binley: added for Windows; none of this is upstream.

  setup()                 call first in every script: UTF-8, no git prompts, children die with the script
  layout(script)          where the project's repo, jobs, worktrees and config are
  bash()                  the bash to run checks.sh and setup.sh with
  lock(f)                 wait for an exclusive lock on an open file, as flock does
  spawn_detached(...)     start a process that outlives the script (the review dev server)
  listening(port)         PIDs listening on a TCP port
  stop_port(port)         stop whatever listens on a port, with its child processes
  kill_tree(pid)          stop a process and everything it started

As a script: `python factory/bin/proc.py stop-port <port>`, for agents stopping their dev server.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

WINDOWS = sys.platform == "win32"


def setup():
    # Before the UTF-8 re-exec, so the re-exec'd copy is also killed if this one is stopped.
    if WINDOWS:
        _kill_children_with_this_process()
        if not sys.flags.utf8_mode:  # Windows defaults to cp1252
            sys.exit(subprocess.call([sys.executable, "-X", "utf8", *sys.argv]))
    # A git that needs a sign-in fails at once instead of opening a dialog nobody sees.
    os.environ["GIT_TERMINAL_PROMPT"] = "0"
    os.environ["GCM_INTERACTIVE"] = "never"


def layout(script):
    """Where the factory's files are.

    Central: FACTORY_HOME and FACTORY_PROJECT are set. The engine stays where it
    is installed. A project's config is in <home>/projects/<project>/, and its
    clone, worktrees and jobs are in <home>/work/<project>/, so nothing of the
    factory's is inside the project's repo.
    Legacy: the factory was copied into the project's repo, at <repo>/factory/.
    """
    home, project = os.environ.get("FACTORY_HOME"), os.environ.get("FACTORY_PROJECT")
    if home and project:
        conf, work = Path(home) / "projects" / project, Path(home) / "work" / project
        return {"repo": work / "repo", "jobs": work / "jobs", "worktrees": work / "worktrees",
                "config": conf / "config.json", "checks": conf / "checks.sh", "setup": conf / "setup.sh"}
    repo = Path(script).resolve().parents[2]
    f = repo / "factory"
    return {"repo": repo, "jobs": f / "jobs", "worktrees": repo / ".worktrees",
            "config": f / "config.json", "checks": f / "checks.sh", "setup": f / "setup.sh"}


def bash():  # binley: outside Git Bash, "bash" on PATH is WSL, which can't read E:/ paths
    git = shutil.which("git") if WINDOWS else None
    for root in (Path(git).resolve().parents[1:3] if git else ()):
        if (root / "bin" / "bash.exe").exists():
            return str(root / "bin" / "bash.exe")
    return shutil.which("bash") or "bash"


def _kill_children_with_this_process():
    """Put this process in a Windows job object that kills every process in it
    when the last handle closes, which is when this process ends, however it ends.
    Children join the job automatically; spawn_detached breaks away from it."""
    import ctypes
    from ctypes import wintypes

    class Basic(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class Extended(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", ctypes.c_ulonglong * 6),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kill_on_close, breakaway_ok, extended_limits = 0x2000, 0x800, 9
    job = kernel32.CreateJobObjectW(None, None)
    info = Extended()
    info.BasicLimitInformation.LimitFlags = kill_on_close | breakaway_ok
    ok = job and kernel32.SetInformationJobObject(
        wintypes.HANDLE(job), extended_limits, ctypes.byref(info), ctypes.sizeof(info)
    ) and kernel32.AssignProcessToJobObject(wintypes.HANDLE(job), wintypes.HANDLE(kernel32.GetCurrentProcess()))
    if not ok:
        print(f"factory: warning: child processes won't be stopped with this script "
              f"(Windows error {ctypes.get_last_error()})", file=sys.stderr)
    # The handle is never closed: it closes when this process ends, and the job's processes go with it.


def lock(f):
    """Block until this process holds an exclusive lock on the open file f."""
    if WINDOWS:
        import msvcrt
        while True:  # msvcrt's own blocking lock gives up after about 10 seconds
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                time.sleep(0.2)
    else:
        import fcntl
        fcntl.flock(f, fcntl.LOCK_EX)


def spawn_detached(cmd, cwd, log_path):
    """Start cmd in the background, outside this script's job object, logging to log_path."""
    flags = 0x01000000 | 0x00000200 | 0x08000000 if WINDOWS else 0  # breakaway, new group, no window
    with open(log_path, "ab") as log:
        p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                             creationflags=flags, start_new_session=not WINDOWS)
    return p.pid


def listening(port):
    if not WINDOWS:
        res = subprocess.run(["lsof", f"-tiTCP:{port}", "-sTCP:LISTEN"], capture_output=True, text=True)
        return {int(p) for p in res.stdout.split()}
    res = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True).stdout
    res += subprocess.run(["netstat", "-ano", "-p", "TCPv6"], capture_output=True, text=True).stdout
    pids = set()
    for line in res.splitlines():
        cols = line.split()
        if len(cols) == 5 and cols[3] == "LISTENING" and cols[1].rsplit(":", 1)[-1] == str(port):
            pids.add(int(cols[4]))
    return pids


def kill_tree(pid):
    """Stop a process and everything it started. On POSIX the process must have
    been started in its own session (start_new_session=True)."""
    if WINDOWS:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)
    else:
        try:
            os.killpg(pid, 9)
        except ProcessLookupError:
            pass


def stop_port(port):
    """Stop every process listening on port and its children. Returns the PIDs stopped."""
    pids = listening(port)
    for pid in pids:
        if WINDOWS:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, 15)
    return pids


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "stop-port" and sys.argv[2].isdigit():
        stopped = stop_port(int(sys.argv[2]))
        print(f"port {sys.argv[2]}: " + (f"stopped {', '.join(map(str, sorted(stopped)))}" if stopped else "nothing listening"))
    else:
        sys.exit(__doc__.strip())
