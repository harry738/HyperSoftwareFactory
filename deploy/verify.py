"""Run inside the factory container: prove there is no way out except to listed hosts.

  python /opt/factory/deploy/verify.py [extra-allowed-host ...]

Needs no token. Exits 1 if any check fails.
"""

import os
import socket
import ssl
import sys
import time
from pathlib import Path

PROXY = ("egress", 3128)
ALLOWED = ["github.com", "api.github.com", "api.anthropic.com", "platform.claude.com"]
failed = []


def check(name, ok):
    print(("ok    " if ok else "FAIL  ") + name)
    if not ok:
        failed.append(name)


def reaches(host, port, family=socket.AF_INET):
    try:
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((host, port))
        return True
    except OSError:
        return False


def resolves(name):
    try:
        socket.getaddrinfo(name, 443)
        return True
    except OSError:
        return False


def udp_dns(server):
    """True when a DNS server outside answers a query for example.com."""
    query = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(3)
            s.sendto(query, (server, 53))
            return bool(s.recv(512))
    except OSError:
        return False


def proxy(request, tls=None):
    """The proxy's status code for a request; with tls, also complete a handshake through the tunnel."""
    try:
        with socket.create_connection(PROXY, timeout=20) as s:
            s.sendall(f"{request} HTTP/1.1\r\nHost: x\r\n\r\n".encode())
            head = b""
            while b"\r\n\r\n" not in head:
                data = s.recv(1)
                if not data:
                    break
                head += data
            status = head.split()[1].decode() if len(head.split()) > 1 else "none"
            if tls and status == "200":
                ssl.create_default_context().wrap_socket(s, server_hostname=tls).close()
            return status
    except OSError as e:
        return type(e).__name__


for _ in range(50):  # the proxy may still be starting
    if reaches(*PROXY):
        break
    time.sleep(0.2)
check("the proxy is reachable (so the refusals below mean something)", reaches(*PROXY))

print("-- no direct route")
routes = Path("/proc/net/route").read_text().splitlines()[1:]
check("no default IPv4 route", not any(line.split()[1] == "00000000" for line in routes))
check("TCP 443 to 1.1.1.1", not reaches("1.1.1.1", 443))
check("TCP 22 to a public address", not reaches("140.82.112.3", 22))
check("IPv6 to a public address", not reaches("2606:4700:4700::1111", 443, socket.AF_INET6))
check("DNS: an external name does not resolve", not resolves("example.com"))
check("DNS: no answer from 1.1.1.1 on UDP 53", not udp_dns("1.1.1.1"))
check("host.docker.internal does not resolve", not resolves("host.docker.internal"))

print("-- the proxy refuses")
for request in ["CONNECT example.com:443", "CONNECT raw.githubusercontent.com:443", "CONNECT github.com:22",
                "CONNECT 1.1.1.1:443", "CONNECT host.docker.internal:443", "CONNECT github.com.example.com:443",
                "GET http://example.com/"]:
    check(request, proxy(request) == "403")

print("-- the proxy allows (TLS handshake through the tunnel)")
for host in ALLOWED + sys.argv[1:]:
    status = proxy(f"CONNECT {host}:443", tls=host)
    check(f"{host} ({status})", status == "200")

print("-- the process")
status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
check("not root", os.getuid() != 0)
check("no capabilities", int(status["CapEff"], 16) == 0 and int(status["CapBnd"], 16) == 0)
check("no-new-privileges", status["NoNewPrivs"].strip() == "1")
check("engine directory is not writable", not os.access("/opt/factory", os.W_OK))

sys.exit(f"{len(failed)} check(s) failed" if failed else 0)
