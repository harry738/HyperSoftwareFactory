"""The factory's only way out: an HTTPS (CONNECT, port 443) proxy for listed hosts.

Rules are one host per line in $ALLOW_DIR/*.txt; ".example.com" matches its
subdomains. The files are read on every request, so a change needs no restart.
"""

import asyncio
import ipaddress
import os
import re
import socket
from pathlib import Path

ALLOW = Path(os.environ.get("ALLOW_DIR", "/allow"))
HOST = re.compile(r"[a-z0-9-]+(\.[a-z0-9-]+)+")


def allowed(host):
    # base.txt first: a project's broken file must not take the base hosts with it.
    for f in sorted(ALLOW.glob("*.txt"), key=lambda f: (f.name != "base.txt", f.name)):
        try:
            lines = f.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError) as e:  # PowerShell's `>` writes UTF-16
            print(f"SKIPPED {f.name}: save it as UTF-8 ({e})", flush=True)
            continue
        for line in lines:
            rule = line.split("#", 1)[0].strip().lower()
            if rule and (host == rule or (rule.startswith(".") and host.endswith(rule))):
                return True
    return False


async def connect(host):
    """Resolve here and refuse private, loopback and link-local addresses, so no
    listed name can be pointed at the Docker host or the local network."""
    for *_, addr in await asyncio.get_running_loop().getaddrinfo(host, 443, type=socket.SOCK_STREAM):
        if ipaddress.ip_address(addr[0]).is_global:
            try:
                return await asyncio.wait_for(asyncio.open_connection(addr[0], 443), 10)
            except (OSError, asyncio.TimeoutError):
                continue
    raise OSError(f"no usable address for {host}")


async def pipe(reader, writer):
    try:
        while data := await reader.read(65536):
            writer.write(data)
            await writer.drain()
        writer.write_eof()
    except OSError:
        writer.close()


def refuse(writer, status):
    writer.write(f"HTTP/1.1 {status}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode())


async def handle(reader, writer):
    upstream = None
    try:
        head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 30)
        method, target = head.split(b"\r\n", 1)[0].decode("ascii").split(" ")[:2]
        host, _, port = target.rpartition(":")
        host = host.lower().rstrip(".")
        if method != "CONNECT" or port != "443" or not HOST.fullmatch(host) or not allowed(host):
            print(f"DENY {method[:20]!r} {target[:200]!r}", flush=True)
            return refuse(writer, "403 Forbidden")
        try:
            up_reader, upstream = await connect(host)
        except OSError as e:
            print(f"FAIL {host}: {e}", flush=True)
            return refuse(writer, "502 Bad Gateway")
        print(f"ALLOW {host}", flush=True)
        writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
        await asyncio.gather(pipe(reader, upstream), pipe(up_reader, writer))
    except (OSError, ValueError, EOFError, asyncio.TimeoutError, asyncio.LimitOverrunError):
        pass
    finally:
        writer.close()
        if upstream:
            upstream.close()


async def main():
    async with await asyncio.start_server(handle, "0.0.0.0", 3128) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
