"""The container's egress proxy: which hosts it lets through. No network needed."""

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "deploy"))
import proxy  # noqa: E402

proxy.ALLOW = Path(tempfile.mkdtemp())
(proxy.ALLOW / "base.txt").write_text("# comment\ngithub.com\n.example.org  # subdomains only\n")
(proxy.ALLOW / "a-project.txt").write_text("registry.example.net\n", encoding="utf-16")  # as PowerShell 5.1 writes it


async def status(request, port):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"{request} HTTP/1.1\r\nHost: x\r\n\r\n".encode())
    line = await reader.readline()
    writer.close()
    return line.split()[1].decode()


async def main():
    assert proxy.allowed("github.com") and proxy.allowed("a.example.org")
    for host in ["example.org", "github.com.evil.test", "evilgithub.com", "api.github.com"]:
        assert not proxy.allowed(host), host

    assert not proxy.allowed("registry.example.net")  # skipped with a message, and the base hosts still work

    async with await asyncio.start_server(proxy.handle, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        for request in ["CONNECT example.com:443", "CONNECT github.com:22", "GET http://github.com/",
                        "CONNECT 127.0.0.1:443"]:
            assert await status(request, port) == "403", request

    try:  # a listed name that points at this machine or the local network is refused
        await proxy.connect("localhost")
        raise AssertionError("connected to a loopback address")
    except OSError:
        pass


asyncio.run(main())
print("all passed")
