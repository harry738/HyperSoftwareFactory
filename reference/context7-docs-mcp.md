# Context7 — Up-to-Date Docs for AI Coding Agents

**Source:** Upstash (2026)
**URL:** https://context7.com
**License:** Freemium (free tier: 1,000 API calls/month)
**Integration:** MCP server

---

## What It Is

Context7 is an MCP server that injects current, version-specific library documentation directly into AI coding agents (Claude Code, Cursor, Windsurf). Instead of an agent guessing a library's API from training data (which may be months out of date), it fetches the actual current docs at request time.

**Key problem solved:** LLMs hallucinate deprecated library methods because their training data is stale. Context7 replaces that with live, version-pinned documentation.

## How It Works

```
Agent needs to use an API → Context7 resolve-library-id → Context7 query-docs
                              ↓
                    Returns version-specific code snippets
                    from official documentation
```

**Two tool calls:**
1. `resolve-library-id` — identify the library (e.g., `next.js`, `drizzle-orm`)
2. `query-docs` — get relevant documentation and code examples for a specific version

## Integration into the Software Factory

### Installation

```bash
# Install Context7 CLI
npm install -g ctx7

# Setup in project
cd ~/your-project
ctx7 setup

# Adds Context7 rules and skills to Claude Code
```

### MCP Server Config

```json
{
  "mcpServers": {
    "context7": {
      "command": "ctx7",
      "args": ["mcp"]
    }
  }
}
```

### Factory Usage

In the Build Floor: every Claude Code subagent loads Context7 before writing implementation code. The build spec includes a step: "Before implementing any library call, resolve its current API via Context7."

## What It Covers

Context7 indexes documentation for hundreds of libraries and frameworks. Popular indexed libraries include:
- Next.js, React, Vue, Svelte, Angular
- Drizzle ORM, Prisma, TypeORM
- Tailwind CSS, shadcn/ui
- tRPC, TanStack Query, Zustand
- Clerk, Auth.js, Lucia
- And many more

## Limitations

- **Not a general web search** — only indexed library/framework docs. Still need Crawl4AI for general web content.
- **Library must be indexed** — private/internal libraries need the paid enterprise tier.
- **Rate-limited** — free tier: 1,000 calls/month, +20 bonus calls/day after hitting the cap.

## Factory Impact

| Before Context7 | After Context7 |
|---|---|
| Agent writes code against outdated APIs | Agent writes code against current, version-specific docs |
| Build fails when CI runs against real packages | Build succeeds — code matches what's actually published |
| Human must verify library calls manually | Human verifies less — Context7 has already resolved the API |