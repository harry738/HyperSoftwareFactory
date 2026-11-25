# One image for both services: the factory and its egress proxy.
# Build context is the repo root; Dockerfile.dockerignore limits what goes in.
FROM node:24-bookworm-slim AS node

FROM python:3.14-slim-bookworm

# Node and npm for the projects the factory builds.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# git, lsof (proc.py), and gh and Claude Code from their signed apt repositories.
# Empty CLAUDE_VERSION takes the current stable release; to pin, give the apt version (e.g. 2.1.323-1).
ARG CLAUDE_VERSION=
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg git lsof; \
    install -d -m 0755 /etc/apt/keyrings; \
    curl -fsSL https://downloads.claude.ai/keys/claude-code.asc -o /etc/apt/keyrings/claude-code.asc; \
    gpg --show-keys --with-colons /etc/apt/keyrings/claude-code.asc \
      | grep -q '^fpr:::::::::31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE:'; \
    echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] https://downloads.claude.ai/claude-code/apt/stable stable main" \
      > /etc/apt/sources.list.d/claude-code.list; \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /etc/apt/keyrings/githubcli.gpg; \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends gh "claude-code${CLAUDE_VERSION:+=$CLAUDE_VERSION}"; \
    rm -rf /var/lib/apt/lists/*; \
    claude --version; gh --version

# Chromium, for projects with pages. Must match the project's @playwright/test version.
ARG PLAYWRIGHT_VERSION=
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN if [ -n "$PLAYWRIGHT_VERSION" ]; then \
      npx -y "playwright@$PLAYWRIGHT_VERSION" install --with-deps chromium && chmod -R a+rX /ms-playwright; \
    fi

# git: commit identity, and HTTPS auth from GH_TOKEN with nothing written to disk.
RUN git config --system user.name "Software Factory" \
 && git config --system user.email "factory@localhost" \
 && git config --system credential.https://github.com.helper '!gh auth git-credential'

RUN groupadd -g 10001 factory \
 && useradd -u 10001 -g 10001 -m -s /bin/bash factory \
 && install -d -o factory -g factory /home/factory/factory-home /home/factory/.claude

# The engine: root-owned, so the factory user cannot change it.
# factory/ and .claude/agents/ must stay siblings.
COPY factory /opt/factory/factory
COPY .claude/agents /opt/factory/.claude/agents
COPY deploy /opt/factory/deploy
RUN chmod -R u=rwX,go=rX /opt/factory \
 && chmod a+x /opt/factory/factory/bin/* \
 && ln -s /opt/factory/factory/bin/factory /usr/local/bin/factory

ENV FACTORY_HOME=/home/factory/factory-home \
    CLAUDE_CONFIG_DIR=/home/factory/.claude \
    LANG=C.UTF-8 \
    PYTHONUTF8=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DISABLE_UPDATES=1 \
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
    NEXT_TELEMETRY_DISABLED=1
# pip installs a project's tools here (the system is read-only). Appended, so they cannot shadow git or gh.
ENV PATH=$PATH:/home/factory/.local/bin

USER factory
WORKDIR /home/factory
CMD ["sleep", "infinity"]
