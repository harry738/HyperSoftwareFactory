# The factory container

Two containers from one image. `factory` is on a Docker network with no route out; `egress` (a small proxy, `proxy.py`) forwards HTTPS to listed hosts and nothing else. If the proxy is down, nothing leaves.

From the repo root:

```sh
docker compose -f deploy/compose.yaml up -d --build
docker compose -f deploy/compose.yaml exec factory python /opt/factory/deploy/verify.py   # no token needed; exit 0
docker compose -f deploy/compose.yaml logs egress                                         # ALLOW / DENY lines
```

Then, once per project:

```sh
docker compose -f deploy/compose.yaml exec -e GH_TOKEN factory factory onboard <owner/repo>
docker compose -f deploy/compose.yaml exec -T factory sh -c 'cat > factory-home/projects/<project>/checks.sh' < checks.sh
docker compose -f deploy/compose.yaml exec -e GH_TOKEN factory factory run <project>
```

`setup.sh` and `config.json` in the same folder are written the same way. Save them with LF line endings.

Tokens are passed at run time, from the shell or `deploy/.env` (ignored by git): `CLAUDE_CODE_OAUTH_TOKEN` and the project's `GH_TOKEN`. `CLAUDE_VERSION` pins Claude Code (the apt version, such as `2.1.323-1`); `PLAYWRIGHT_VERSION` adds Chromium for projects with pages.

## Hosts

`allow/base.txt` is always allowed. For a project's registries, create `allow/<project>.txt` (ignored by git), one host per line; `.example.com` matches subdomains only. Save it as UTF-8 (PowerShell's `>` writes UTF-16, which the proxy skips). It takes effect on the next request. The lists are combined, so every project gets every listed host.

- npm: `registry.npmjs.org`
- pip: `pypi.org`, `files.pythonhosted.org`

## What it does not protect against

- **Engine, agents and project code are one user.** Agents can likely read the tokens through `/proc`, and can write review files, project config and job state in the volume. The container limits where traffic can go; it is not a boundary between agent and engine.
- **Allowed hosts can carry data out:** any GitHub repository or gist, the model API with another key, a registry publish.
- **The proxy checks the requested host name only.** It does not read the TLS traffic.
- Image builds and the proxy container have ordinary network access.
