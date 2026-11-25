# LLM provider integration (proposal)

Local only. Not pushed. Not an official revision of `reference/build-plan.md`. The operator remains the only merger, and any paid provider spend needs his yes.

Written 25 November 2026 (Europe/London) from `main` @ `72a982c` (plan v6.4), the local deployable plan (`docs/roadmap/deployable-roadmap.md`, `docs/roadmap/agent-roster.md`, `docs/roadmap/feature-list-by-phase.md`), and the operator's voice request the same evening: make provider integration a first-class factory capability, with three connection types handled uniformly — local models on the same machine, models on the LAN, and OpenRouter as an aggregator.

This would relax a stated v6.4 non-goal ("Other models for the builder or the reviewers. Only council seats use other vendors," in `CONTEXT.md` and `reference/build-plan.md`) **only if the operator agrees**. Until he does, Claude Code remains the default stage harness. The layer is designed so that change is configuration, not a rewrite of agent logic.

## 1. Goal and non-goals

**Goal.** A provider abstraction between the scripted orchestrator / stage runners and the models they call, so the factory can bind each agent role to a model and a connection (local, LAN, or OpenRouter) without changing that role's logic. The same layer owns fallback policy, cost accounting, rate limits, and fail-closed rules.

**Non-goals.**

- Replacing `factory run` with a model that chooses the next stage. The orchestrator stays a script (v6.4).
- Standing up a required extra gateway process (LiteLLM Proxy, Portkey, or similar) inside the factory container.
- Sending prompts or source to a cloud aggregator by default. Leaving the LAN is an explicit project policy, off until the operator turns it on.
- Silently downgrading a security or fresh-context reviewer to a weaker model, or retrying a bad request on another model as if it were a transient failure.
- Putting API keys, OAuth tokens, or model-server secrets in a worktree, in the public repo, or in `config.json` values.
- Claiming a local coding model is a drop-in for the Claude Code agent loop. A raw chat API is not a stage harness.
- Building a new multi-provider SDK from scratch when an existing library can do the HTTP and format translation (see §15).

## 2. How models are chosen today (`72a982c`)

Grounded in the engine on `main`. This is what the new layer has to wrap, not invent around.

- **Every stage is one headless Claude Code CLI run** (`factory/bin/run`). The executable comes from `FACTORY_CLAUDE` (default `claude`). Tests already point that variable at a stand-in (`factory/test_run.py`).
- Agent definitions live in the engine's `.claude/agents/*.md`, not in the project. Front matter sets a default `model` and `tools`: intake / spec-writer / approver use `fable`; builder and `reviewer-security` use `opus`; `reviewer-code` and `reviewer-ui` use `haiku`; `reviewer-ux` uses `sonnet`.
- `factory/bin/route` then overrides reviewer models from `config.json`: `routing.low|medium|high` (template: `haiku` / `sonnet` / `sonnet` for the code reviewer) plus `surface_reviewers` (security → `opus`). Those short names are passed to Claude Code as `--model`.
- **Budgets** are already enforced by the script, in USD: `stage_budget_usd` (also passed as `--max-budget-usd`), `job_budget_usd`, `daily_budget_usd` (UTC day). Hitting a cap stops the job for a person (`job stop`). v6.4 open question 4: it is unverified whether the CLI cost cap applies on a subscription login, so the engine also computes its own cap.
- **Cost** is written per stage to `<job>/usage.jsonl` (`agent`, `model`, `round`, `ok`, `how`, `cost_usd` from the CLI's `total_cost_usd`). Stage changes append to `events.jsonl` with `cost_usd`. A fallback path in `factory/bin/job` prices Claude Code transcripts from `prices_usd_per_mtok` in `config.json` and **dies if a model has no price**.
- Agent stages run with GitHub tokens removed (`GH_TOKEN`, `GITHUB_TOKEN`, `GH_ENTERPRISE_TOKEN`). The Claude login (`CLAUDE_CODE_OAUTH_TOKEN` / `ANTHROPIC_API_KEY`) stays in the stage environment because the harness needs it. `SECRET_ENV` in `job` redacts those values from posted evidence.
- **E6 allowlist** (`deploy/allow/base.txt`): `github.com`, `api.github.com`, `api.anthropic.com`, `platform.claude.com`. The factory container sits on an internal Docker network with no route out; an egress proxy forwards **HTTPS** to listed hosts only. `NO_PROXY` is `localhost,127.0.0.1,::1`. `localhost` inside the container is the container itself, not the Docker host.
- Planned **F1 council** is the one place v6.4 already wants other vendors: "a script in the engine that calls the models directly through one API gateway. Its key lives in the factory's secrets, where no agent can read it."

The important split: **today's stages are a CLI harness, not raw model API calls.** A completion library can serve council seats, health checks, and later raw-API roles. It does not, by itself, run intake, build, or review.

## 3. Architecture

```
config.json  +  env (key *names* only in config)
        │
        ▼
factory run / job / route     (script; holds GitHub token; no model)
        │
        ▼
┌───────────────────────────────────────┐
│  Provider layer (factory-owned)       │
│  resolve role → binding → endpoint    │
│  health, rate limit, budget, fallback │
│  fail-closed and data-residency rules │
│  usage → usage.jsonl / events.jsonl   │
└───────────────┬───────────────────────┘
                │
     ┌──────────┴──────────┐
     ▼                     ▼
 Stage harness         Completion API
 (CLI agent loop)      (chat/completions)
     │                     │
     │                     ├─ LiteLLM SDK (adopted transport)
     │                     │
     ▼                     ▼
 Claude Code CLI      three connection types
 (and later Codex,    (1) local   (2) LAN   (3) OpenRouter
  if the operator agrees)
```

**Two invocation modes**, both behind the same factory facade so role code does not branch:

1. **Stage harness.** Today's path. The adapter starts a CLI (`claude -p … --model …`), enforces tools / timeouts / stall kill, and reads usage from the CLI result. A second harness (for example Codex) would be another adapter with the same `run_stage` shape. This is not a raw `complete()` call.
2. **Completion API.** Messages in, assistant text / tool calls / usage out. Used first for the F1 council, for provider health checks, and for any later role that does not need a worktree agent loop (for example a tool-less F4 summariser). Transport should be an adopted library (see §15), not a hand-rolled HTTP client per vendor.

**Three connection types**, used by the completion mode and, where a harness can be pointed at a base URL, optionally by a harness too:

| Kind | Where the model runs | Typical endpoint | API cost |
|---|---|---|---|
| `local` | Same machine as the factory (host or a compose sidecar) | Ollama native or OpenAI-compatible on localhost / `host.docker.internal` / sidecar hostname | $0 (tokens and latency still recorded) |
| `lan` | Another host on the private network | Same APIs at `host:port` | $0 (same accounting; optional amortised estimate) |
| `openrouter` | OpenRouter's aggregator | `https://openrouter.ai/api/v1` | whatever OpenRouter reports in `usage.cost` |

The factory policy layer — not the upstream vendor — decides whether a role may move between those types. OpenRouter's own model/provider fallback is a sub-policy of the `openrouter` connection, and is tightened for reviewer and security roles (see §8).

## 4. The three connection types

### 4.1 Local (same machine)

**APIs, both first-class:**

- **Ollama native:** typically `http://127.0.0.1:11434/api/chat` (and `/api/generate`, `/api/tags` for health). LiteLLM talks to this as `ollama/<model>` or `ollama_chat/<model>` with `api_base` set to that origin ([LiteLLM Ollama docs](https://docs.litellm.ai/docs/providers/ollama)).
- **OpenAI-compatible:** `http://127.0.0.1:<port>/v1/chat/completions`. Ollama also exposes this at `http://127.0.0.1:11434/v1/` ([Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)). The same shape covers llama.cpp server, vLLM, and LM Studio on localhost. Clients often require an `api_key` field that the server ignores; if a local server does require a token, the value lives in an environment variable named in config, never in the file.

**Docker honesty.** `NO_PROXY` already includes `localhost`, but that address is the *container*, not the host. To use a model that is actually on the operator's machine, pick one of:

- a compose **sidecar** on the `inside` network (preferred: no extra host route, health-checkable by service name), or
- `host.docker.internal` (Docker Desktop) added to `NO_PROXY` and to a private-endpoint allowlist, HTTP only if the destination is loopback or a documented Docker-host name.

**Health.** Before a job binds a role to a local endpoint, `GET /api/tags` (Ollama) or `GET /v1/models` (OpenAI-compatible). A required local binding that is unhealthy fails closed: the job stops for the operator; it does not quietly jump to OpenRouter.

### 4.2 LAN (another host on the private network)

Same APIs as local, at a LAN `host:port` (hostname or RFC1918 / ULA address). Benefits: heavier models can sit on a GPU box; **prompts and source stay on the LAN** when every binding (and every permitted fallback) is `local` or `lan`.

**TLS and auth.**

- HTTPS with a private CA or a pinned certificate is preferred.
- Plain HTTP is allowed only to loopback, RFC1918, link-local, or IPv6 ULA destinations. Public IPs and public DNS names must be HTTPS and go through the existing egress allowlist — never a general HTTP hole to the internet.
- Auth is optional: none, or `Authorization: Bearer` from an environment variable named in config (for example `FACTORY_LAN_LLM_TOKEN`).

**E6 / container path.** This is the hard part, and the spec will not pretend today's compose file already solves it. The factory service has **no route out** except the HTTPS egress proxy, whose list is public model and GitHub hosts. A LAN model therefore needs an explicit, operator-approved path, documented in `deploy/`:

1. **Preferred:** attach a dedicated compose network (or `extra_hosts`) that can reach only the listed LAN model hosts, and add those hosts to `NO_PROXY` so they do not go through the public egress proxy.
2. **Alternative:** extend the egress proxy with a *separate* private-endpoint list that may forward HTTP or HTTPS only to configured private CIDRs and ports. This list is not `allow/base.txt`. A miss still fails closed (same spirit as issue #26).
3. **Not preferred:** running the engine on the host network just to reach a LAN model.

`deploy/allow/<project>.txt` today is for package registries on the public egress path. LAN model hosts belong in a distinct file, for example `deploy/allow/private-models.txt` (gitignored, like other allow extras), reviewed as carefully as a new public allowlist entry because a mis-entry is an egress path.

**Health.** Same checks as local, plus a short connect timeout. Unreachable LAN is `unavailable` (retryable within the LAN / local chain only, subject to §8).

### 4.3 OpenRouter (aggregator)

Verified against OpenRouter docs on 25 November 2026. Paid. Do not configure a live key or spend until the operator says yes.

| Fact | Value | Source |
|---|---|---|
| Base URL | `https://openrouter.ai/api/v1` | [Chat completions](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion) |
| Completions path | `POST /api/v1/chat/completions` | same |
| Auth | `Authorization: Bearer <token>` | same |
| Model IDs | Routable `id` slugs such as `anthropic/claude-3.5-sonnet`; a `canonical_slug` pins a checkpoint; aliases are resolved; `~` rolling aliases follow the latest approved stable of a family | [Models API](https://openrouter.ai/docs/api_reference/models) |
| Model fallback | Request field `models`: an ordered list; if the first model errors, the next is tried (including rate limits, downtime, and also context or moderation errors — see §8) | [Model fallbacks](https://openrouter.ai/docs/guides/routing/model-fallbacks) |
| Provider routing | Request field `provider`: `order`, `allow_fallbacks` (default **true**), `only`, `ignore`, `sort` (`price` / `latency` / `throughput`), `max_price`, `require_parameters`, `data_collection` (`allow` \| `deny`), `zdr` | [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) |
| Usage / cost | Always returned (the old Chat Completions `usage.include` flag is deprecated and has no effect). Chat Completions: `prompt_tokens`, `completion_tokens`, `total_tokens`, `cost`, `cost_details`, `prompt_tokens_details.cached_tokens`, `completion_tokens_details.reasoning_tokens`, `is_byok` | [Usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting) |
| E6 allowlist | Add `openrouter.ai` (and only that, unless a regional host is later chosen) to the public HTTPS allowlist when the operator enables this connection | E6.1 |

**Factory rules when talking to OpenRouter:**

- For security and fresh-context reviewer roles, set `provider.allow_fallbacks: false` unless the fallback targets are an **equivalent class** The operator has named in config. Do not rely on OpenRouter's default `true`.
- Prefer pinned slugs over `~` rolling aliases for reviewers, so a review is reproducible.
- If the operator wants less data retention, set `provider.data_collection: "deny"` and, if he wants zero-data-retention endpoints only, `provider.zdr: true`. These filter OpenRouter's upstreams; they do not keep the prompt on the LAN — the request still leaves the machine.
- OpenRouter also has EU/US regional hostnames on paid plans (`https://eu.openrouter.ai`, `https://us.openrouter.ai`). Use them only if the operator chooses that plan; they are not assumed.

### 4.4 Config examples

**Local only (Ollama sidecar, OpenAI-compatible also shown).**

```json
{
  "providers": {
    "ollama-local": {
      "connection": "local",
      "kind": "ollama",
      "base_url": "http://ollama:11434",
      "api_style": "ollama_native",
      "auth": { "type": "none" },
      "health_path": "/api/tags",
      "allow_hosts": ["ollama"]
    },
    "llamacpp-local": {
      "connection": "local",
      "kind": "openai_compatible",
      "base_url": "http://127.0.0.1:8080/v1",
      "api_style": "openai_chat",
      "auth": { "type": "none" },
      "health_path": "/models",
      "allow_hosts": ["127.0.0.1"]
    }
  }
}
```

**LAN (HTTPS + bearer token; HTTP would be allowed only because the host is RFC1918).**

```json
{
  "providers": {
    "gpu-box": {
      "connection": "lan",
      "kind": "openai_compatible",
      "base_url": "https://gpu-box.lan.example:8000/v1",
      "api_style": "openai_chat",
      "tls": { "ca_file_env": "FACTORY_LAN_CA_FILE", "pin_sha256_env": null },
      "auth": { "type": "bearer", "api_key_env": "FACTORY_LAN_LLM_TOKEN" },
      "health_path": "/models",
      "allow_hosts": ["gpu-box.lan.example"],
      "connect_timeout_seconds": 3
    }
  }
}
```

**OpenRouter.**

```json
{
  "providers": {
    "openrouter": {
      "connection": "openrouter",
      "kind": "openrouter",
      "base_url": "https://openrouter.ai/api/v1",
      "api_style": "openai_chat",
      "auth": { "type": "bearer", "api_key_env": "OPENROUTER_API_KEY" },
      "allow_hosts": ["openrouter.ai"],
      "openrouter": {
        "provider": {
          "allow_fallbacks": false,
          "data_collection": "deny",
          "zdr": true,
          "require_parameters": true
        }
      }
    }
  }
}
```

**Combined** (default local, LAN next, OpenRouter last — and the residency / fail-closed rules in §8 still apply):

```json
{
  "data_leaving_lan": "deny",
  "providers": {
    "ollama-local": {
      "connection": "local",
      "kind": "ollama",
      "base_url": "http://ollama:11434",
      "api_style": "ollama_native",
      "auth": { "type": "none" },
      "health_path": "/api/tags",
      "allow_hosts": ["ollama"]
    },
    "gpu-box": {
      "connection": "lan",
      "kind": "openai_compatible",
      "base_url": "https://192.168.10.20:8000/v1",
      "api_style": "openai_chat",
      "auth": { "type": "bearer", "api_key_env": "FACTORY_LAN_LLM_TOKEN" },
      "health_path": "/models",
      "allow_hosts": ["192.168.10.20"]
    },
    "openrouter": {
      "connection": "openrouter",
      "kind": "openrouter",
      "base_url": "https://openrouter.ai/api/v1",
      "auth": { "type": "bearer", "api_key_env": "OPENROUTER_API_KEY" },
      "allow_hosts": ["openrouter.ai"],
      "openrouter": { "provider": { "allow_fallbacks": false, "data_collection": "deny" } }
    },
    "claude-code": {
      "connection": "harness",
      "kind": "claude_code_cli",
      "command_env": "FACTORY_CLAUDE",
      "command_default": ["claude"]
    }
  },
  "role_bindings": {
    "discovery_spec": {
      "primary": { "provider": "ollama-local", "model": "qwen2.5-coder:32b" },
      "fallback": [
        { "provider": "gpu-box", "model": "qwen2.5-coder:32b" }
      ]
    },
    "security_reviewer": {
      "primary": { "provider": "claude-code", "model": "opus" },
      "fallback": [],
      "fail_closed": true,
      "allow_weaker_model": false
    }
  }
}
```

In that combined example, discovery may fall from local to LAN (same residency). It must **not** fall through to OpenRouter while `data_leaving_lan` is `deny`. The security reviewer has no fallback: if the configured harness or model is unavailable, the job stops.

## 5. Abstraction interface

Factory-owned Protocol. The LiteLLM (or other) client is an implementation detail of the completion adapters, not something stage code imports.

```python
from enum import Enum
from typing import Literal, Protocol, Iterable

class ErrorKind(str, Enum):
    RETRYABLE = "retryable"          # timeouts, connection resets, 5xx
    RATE_LIMIT = "rate_limit"        # 429
    NON_RETRYABLE = "non_retryable"  # 400, 422, malformed request
    AUTH = "auth"                    # 401, 403, bad or missing key
    UNAVAILABLE = "unavailable"      # health failed, no route, 404 model
    BUDGET = "budget"
    POLICY = "policy"                # residency, fail-closed, capability
    HEALTH = "health"

class ProviderError(Exception):
    kind: ErrorKind
    retryable: bool
    provider_id: str
    model_id: str | None
    status_code: int | None
    # retryable is True only for RETRYABLE and RATE_LIMIT.
    # POLICY, AUTH, NON_RETRYABLE, BUDGET never trigger a model fallback.

class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: int
    reasoning_tokens: int
    api_cost_usd: float              # 0.0 for local and LAN
    estimated_local_usd: float | None
    latency_ms: int
    provider_id: str
    model_id: str                    # the model that actually answered
    connection: Literal["local", "lan", "openrouter", "harness"]
    fallback_used: bool
    raw: dict | None                 # OpenRouter cost_details, etc.

class Capabilities:
    streaming: bool
    tools: bool
    system_prompt: bool
    vision: bool
    json_mode: bool

class CompletionProvider(Protocol):
    id: str
    connection: Literal["local", "lan", "openrouter"]
    def capabilities(self, model: str) -> Capabilities: ...
    def health(self) -> None: ...
    def complete(self, req: "CompletionRequest") -> "CompletionResponse": ...
    def stream(self, req: "CompletionRequest") -> Iterable["Chunk"]: ...
    def report_usage(self, response: "CompletionResponse") -> Usage: ...

class StageHarness(Protocol):
    """CLI agent loop. Not interchangeable with complete()."""
    id: str
    connection: Literal["harness"]
    def run_stage(self, req: "StageRequest") -> "StageResult": ...
    def report_usage(self, result: "StageResult") -> Usage: ...
```

The facade the orchestrator calls is `ProviderRouter.for_role(role, job) → handle`, which exposes `run_stage` or `complete` according to the binding, and always `report_usage`. Role logic never names LiteLLM, Ollama, or OpenRouter.

## 6. Configuration

Extend the existing `factory/config.json` (and per-project overrides in the private factory home). Credentials appear **only as environment variable names**. New keys are additive; today's `routing`, `surface_reviewers`, `prices_usd_per_mtok`, and budget fields stay valid.

Suggested top-level keys:

- `providers` — map of provider id → connection, kind, base URL, auth env name, TLS, health path, allow_hosts, OpenRouter sub-object, optional `usd_per_mtok` override.
- `role_bindings` — map of roster role id → `primary`, `fallback[]`, `fail_closed`, `allow_weaker_model`, optional `equivalent_models` (same-class replacements the operator has listed).
- `data_leaving_lan` — `deny` (default) or `allow`. `allow` still logs every off-LAN call and still needs OpenRouter (or any other cloud provider) to be configured and approved.
- `local_cost_estimate` — optional `{ "usd_per_million_tokens": number }` used only to fill `estimated_local_usd` (electricity / amortised hardware). Never treated as `api_cost_usd` and never the sole input to a spend cap unless the operator later asks for a local-cost cap.
- `rate_limits` — per provider id: `requests_per_minute`, `max_concurrency`, `backoff` multipliers.
- Existing budgets remain: `job_budget_usd`, `stage_budget_usd`, `daily_budget_usd`.

Short Claude Code names (`haiku`, `sonnet`, `opus`, `fable`) continue to work on the `claude-code` harness. For OpenRouter, role bindings use full slugs. A small optional alias table may map `sonnet` → `anthropic/…` if the operator wants one glossary; aliases must be explicit, not guessed.

A missing `data_leaving_lan` key fails **closed** (`deny`), in the same spirit as issue #26.

## 7. Model selection

Resolution order for a role on a job:

1. Job-level override, if the engine later grows one (none today).
2. `role_bindings[role]` in project config, else the factory template.
3. Today's tables, while bindings are being filled in: `routing` / `surface_reviewers` / agent front matter, all on the `claude-code` harness. That is the migration default.
4. Health-check the primary endpoint. If it fails, walk `fallback` under the rules in §8.
5. Record the resolved provider, model, connection, and whether a fallback was used, on the `usage.jsonl` row.

Risk tiers from the deployable plan (Tier 1/2/3 mapped onto existing `low`/`medium`/`high`) may continue to pick a *model class* (for example code review at low risk stays on a small model). They do not override `fail_closed` on the security reviewer.

## 8. Fallback behaviour

**Retryable vs not.** Retry the *same* binding on `RATE_LIMIT` and `RETRYABLE`, using the existing `retry_waits_seconds` / transient pattern in `factory/bin/run` (already matches 429, 5xx, overload). Do **not** fall over to another model or connection on `NON_RETRYABLE`, `AUTH`, `BUDGET`, or `POLICY`. A 400 on model A will fail the same way on model B and only wastes money (a practice worth borrowing from Portkey's `on_status_codes` idea; see §15).

**Residency.** A fallback may only change connection type if the project policy allows it:

- `local` → `lan` is allowed (data stays on the LAN).
- `lan` or `local` → `openrouter` (or any future cloud provider) is allowed only when `data_leaving_lan` is `allow`. Otherwise stop and tell the operator the on-prem path is down.
- Default is `deny`. Sensitive-path / Tier 3 jobs should stay `deny` even if the project default is later opened — open question for the operator.

**Fail closed for reviewers and security (no silent downgrade).** Tied to the #26 principle: a missing or weaker substitution is not a pass.

- `security_reviewer` and `fresh_context_reviewer` default to `fail_closed: true` and `allow_weaker_model: false`.
- If the bound model or harness is unavailable, the stage stops for the operator. The job is not reviewed by a cheaper or smaller stand-in, and it is not marked as if the review had run.
- A same-class replacement is allowed only when the operator has listed it under `equivalent_models` for that role (for example two hosts serving the same named weights, or a pinned OpenRouter slug plus its canonical checkpoint). The event log must record the substitution.
- OpenRouter `provider.allow_fallbacks` must be `false` for these roles unless every permitted upstream is in that equivalent list. OpenRouter's `models` array must not be used to slip a weaker model in after a moderation or context error.
- The approver, in this deployable plan, cannot merge; a fallback there is still logged, but the merge gate stays with the operator.

## 9. Cost tracking

Every completion or harness run appends one `usage.jsonl` row and rolls a USD total into the next `events.jsonl` stage row. Extend the current usage record rather than replacing it:

```json
{
  "agent": "reviewer-security",
  "role": "security_reviewer",
  "model": "opus",
  "provider": "claude-code",
  "connection": "harness",
  "round": 1,
  "ok": true,
  "how": "ok",
  "prompt_tokens": 12000,
  "completion_tokens": 800,
  "total_tokens": 12800,
  "latency_ms": 41000,
  "cost_usd": 0.11,
  "api_cost_usd": 0.11,
  "estimated_local_usd": null,
  "fallback_used": false
}
```

| Connection | `api_cost_usd` / `cost_usd` | Also record |
|---|---|---|
| `local`, `lan` | `0` | tokens, `latency_ms`; optional `estimated_local_usd` from `local_cost_estimate` |
| `openrouter` | `usage.cost` from the response (major currency units as OpenRouter returns them) | tokens, cache and reasoning tokens, `cost_details` in `raw` |
| `harness` (Claude Code) | existing CLI `total_cost_usd`, else `prices_usd_per_mtok` | keep today's behaviour; still error if a model has no price |

Budget caps use **`api_cost_usd`** (real money). Local and LAN runs therefore do not burn the USD budget, but they still count toward turn, time, and stall limits. If the operator later wants a cap on local token spend, that is a separate key — do not overload `daily_budget_usd` without his yes.

A job whose `api_cost_usd` total reaches `job_budget_usd` (or the project reaches `daily_budget_usd`) stops before the next call, as `run` already does.

## 10. Rate limiting

- Token bucket (or equivalent) **per provider id and per API key**, configured in `rate_limits`.
- `max_concurrency` per provider, in addition to the factory's job `concurrency`.
- On 429: honour `Retry-After` when present, else the existing `retry_waits_seconds` backoff; classify as `RATE_LIMIT`.
- Local and LAN servers get concurrency caps too — a GPU box can be saturated even though it costs $0 in API fees.

## 11. Security

- Keys and tokens live in `deploy/.env` or the process environment, already gitignored. Config stores only the **name** of the variable.
- Stage environments receive **only** the credential the bound provider needs. An Ollama-only stage does not get `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY`. GitHub tokens stay out of every agent stage (already true).
- Provider secrets are never written to worktrees, `usage.jsonl`, `events.jsonl`, review files, or PR bodies (`SECRET_ENV` must grow the new names).
- Prompts must not be fed raw secrets. The existing "all secrets stay outside the sandbox" hard rule still applies; the provider layer does not relax it.
- E6: each provider declares `allow_hosts`. Public cloud hosts go on the HTTPS egress list only after the operator enables that provider. Private hosts go on the private-endpoint list (§4.2). A provider with no allow-hosts entry fails closed.
- Data handling: local and LAN prompts stay on the machine or the LAN. OpenRouter is a third party; even with `data_collection: "deny"` and `zdr: true`, the content leaves the LAN. Retention is whatever OpenRouter and its upstream document — the factory should not invent a guarantee.
- The v6.4 note still holds: the container is not a hard boundary between engine and agent (one user). The layer must not put unused keys in a stage environment and must not treat the container as sufficient isolation.

## 12. Observability

- Every call already planned for `usage.jsonl` / `events.jsonl` also records `provider`, `connection`, `fallback_used`, and `latency_ms`.
- Dashboard tiles in Phase 4 can then show spend by provider, first-pass green rate, and retry counts without a Prometheus stack (v6.4 non-goal).
- Egress and private-endpoint proxies should keep their ALLOW / DENY logs, including LAN destinations.

## 13. Testing

Extend the existing stand-in pattern (`FACTORY_CLAUDE` pointing at a fake binary; `factory/test_run.py` makes no real model call):

- `FakeProvider` implements both Protocols: scripted responses, usage, and errors (`429`, `400`, unhealthy, weaker-model temptation).
- Tests that must pass before this ships: missing `data_leaving_lan` ⇒ deny; security reviewer cannot fall to a weaker model or to OpenRouter when residency is deny; local usage has `api_cost_usd == 0` and non-zero tokens; OpenRouter usage reads `usage.cost`; 400 does not walk the fallback list; a 429 retries the same binding; secrets in env names never appear in logged rows.
- Live calls to OpenRouter, a LAN box, or a paid API are opt-in and not part of default CI.

## 14. Role-to-provider binding

Roles from `agent-roster.md`. The **Orchestrator is a script and has no model.** Defaults below keep today's Claude Code behaviour until the operator changes a binding. Alternatives are what the layer is for, not what ships on day one.

| Role | Default binding (today) | Allowed connections | Fail-closed? | Notes |
|---|---|---|---|---|
| Orchestrator | none | — | — | Script: `factory run`, `job`, `gate`, `route`. Owns the router, budgets, rate limits, event log, and GitHub token. |
| Discovery / Spec | harness `claude-code` / `fable` (intake + spec-writer) | harness, local, LAN, OpenRouter | no (residency still applies) | Good first raw-API or local-model candidate once quality is measured. |
| Planner | same spec-writer path today | harness, local, LAN, OpenRouter | no (residency still applies) | |
| Builder | harness `claude-code` / `opus` | harness first; raw local/LAN only if a later harness or proven tool-loop exists | no, but do not silently swap the coding model mid-job | Changing this is the v6.4 non-goal the operator must explicitly relax. |
| Test / QA | none (scripted `checks.sh`; later F5 may need a model) | script today; F5: prefer local/LAN | F5 should fail closed if the holdout model is missing | Must not gain a GitHub token. |
| Fresh-context reviewer | harness; model from `routing` / surfaces (`haiku`/`sonnet`) | harness, then only equivalent-class fallbacks | **yes** | No silent weaker model. |
| Security reviewer | harness `claude-code` / `opus` | harness, or a the operator-listed equivalent only | **yes** | Template already pins `opus`. Never fall to haiku or an unlisted local 7B. |
| Release / Ops | none | script + the operator | — | No model required. |
| Research / F4 watcher | none today | **prefer local or LAN** for untrusted-source summarising; OpenRouter only with residency allow and the operator's yes | yes if a required check cannot run | Runs outside the factory container. Cheapest-first input checks still apply (`docs/reference-library/03-layered-llm-guardrails.md`). |
| PM / product steer | none | — | — | The operator. |

## 15. Adopt vs build

The operator's bar: incorporate a direct match first, then partial pieces, then inspiration. Checked on 25 November 2026.

| Option | What it is | Fit | Recommendation |
|---|---|---|---|
| **LiteLLM Python SDK** ([docs](https://docs.litellm.ai/docs/python_sdk), [Ollama](https://docs.litellm.ai/docs/providers/ollama), MIT, `pip install litellm`, Python ≥ 3.10; factory image is Python 3.14) | In-process library: one `completion()` across vendors, Ollama, OpenAI-compatible bases, OpenRouter, usage, exception mapping. Optional proxy server exists but is a separate process. | **Partial, strong.** Covers all three completion connection types. Does not replace `factory/bin/run`'s Claude Code harness, budgets, or fail-closed policy. LiteLLM documents an agent runner that can drive Claude Code and others; that is **not** assumed to replace the factory loop until it passes the existing stand-in tests. | **Adopt as the completion transport** behind the factory Protocol. Do **not** require LiteLLM Proxy (ops surface, would hold every key, extra process in the locked container). Pin a version; do not import `litellm` from role code. Treat `enterprise/` as off-limits without a paid licence ([LiteLLM about](https://www.litellm.ai/about)). |
| **mozilla any-llm** ([GitHub](https://github.com/mozilla-ai/any-llm), [providers](https://docs.mozilla.ai/providers), Apache-2.0, Python ≥ 3.11, package `any-llm-sdk`) | Thin library over official SDKs; verified Ollama provider; `AnyLLM.create_openai_compatible` for llama.cpp / vLLM / LM Studio without mis-labelling them as OpenAI. No built-in budget gateway (that's a sister project). | **Partial, also strong**, and slimmer. Good if we want official SDKs and a smaller dependency. We would still write fallback, residency, and cost policy ourselves — which we want to own anyway. | **Acceptable alternative** to LiteLLM if the SDK stays small and well-licensed. Choose at implementation time with a short spike; either is an adopt, not a build. |
| **OpenRouter** ([docs](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion)) | Hosted aggregator, one key, model and provider fallback, usage.cost. Paid. | **Direct match for connection type 3 only.** Not local, not LAN, not a harness. | **Adopt as a provider backend**, not as the factory's abstraction. Enable only after the operator approves spend and the E6 host entry. |
| **Portkey AI Gateway** (MIT, TypeScript; hosted tier exists) | Proxy with retries, fallback trees, `on_status_codes`, guardrails. | Inspiration / partial. Wrong language for an in-process Python engine; a required Node gateway is the same ops smell as LiteLLM Proxy. | **Do not adopt as the core.** Borrow the rule: fall back on 429/503, not on 400. |
| **Build our own HTTP clients** | One-off Ollama + OpenAI + OpenRouter wrappers. | Duplicates well-solved format and error translation. | **Do not build** a general SDK. **Do build** the thin factory layer: Protocol, role bindings, fail-closed / residency policy, usage.jsonl fields, E6 allowlist wiring, FakeProvider, Claude Code harness adapter (that adapter already exists in all but name, as `run_agent`). |

**Recommendation, in one line:** adopt LiteLLM (or any-llm, after a spike) for completions; keep the Claude Code CLI as a first-class harness adapter; treat OpenRouter, Ollama, and OpenAI-compatible local/LAN servers as connection backends; build only the policy, config, accounting, and allowlist glue the factory already needs to own.

## 16. Migration, mapped to the deployable phases

No official new E/F numbers. Implementation waits for the operator's yes and does not jump Phase 0.

| Phase | Provider work | Exit |
|---|---|---|
| **0 Safety** | None required in code. The written rule that missing residency / binding keys fail closed can be noted in the #26 PR if convenient, but #26 stays about `unattended_merge`. | #26 merged. |
| **1 Steering and discovery** | Docs and config schema: `providers`, `role_bindings`, `data_leaving_lan` default deny, role table in the template. Bindings still point at `claude-code` and today's short model names so behaviour does not change. | Template parses; a missing residency key is deny; no live new vendor. |
| **2 Inner-loop and E1.6** | Implement the Protocol, FakeProvider tests, LiteLLM (or any-llm) behind local and LAN adapters, health checks, private-endpoint allowlist / `NO_PROXY` work if the operator wants a local or LAN model on the signed-in container. OpenRouter adapter may be coded against the fake, but a real key and `openrouter.ai` allowlist wait for his yes. Builder stays on Claude Code unless he relaxes the non-goal. | Stand-in tests green; optional local/LAN path demonstrated on a non-production job if the operator wants it; USD budgets still stop the job. |
| **3 Review and governance** | Enforce fail-closed reviewer and security bindings; no silent downgrade; PR / event evidence shows which provider and model actually ran. | A security review cannot complete on a weaker substitute; missing reviewer model stops for the operator. |
| **4 Operator-scale** | F1 council via the completion path (the "one API gateway" v6.4 already wants). Dashboard tiles by provider and connection. F4 summariser prefers local/LAN. OpenRouter in production only with approved spend. | The operator can see cost and tokens by provider; council does not need a second ad-hoc client. |

## 17. Market-scan cross-check

Cross-checked against `docs/reference-library/04-market-scan-software-factories-2026-11-25.md` after that file landed (same evening). The scan is about factory practices and vendors, not a LiteLLM / OpenRouter bake-off, so the adopt-vs-build table in §15 still rests on those projects' own docs. What the scan does add:

- **Budget tokens and watch the loop.** The scan names cost and review capacity as the real limits. That supports first-class usage rows by provider and connection, and keeping USD caps on *API* cost so local/LAN work is visible without burning the cash budget.
- **Egress allowlists.** Cursor's official cloud-agent security docs (cited in the scan) put a human at merge and restrict egress. That is the same idea as E6. Extending the allowlist for `openrouter.ai`, or adding a *separate* private-endpoint list for LAN/local models, should be as deliberate as any new public host — not a general HTTP hole.
- **Untrusted input is hostile.** The scan reinforces entry 03 and Firecrawl's "detect on every fetch." The F4 / research summariser should prefer a local or LAN model so untrusted web text is not forwarded to OpenRouter by default, and should fail closed if a check cannot run.
- **Keep the control loop a script.** Several LinkedIn write-ups in the scan argue against throwing more agents at orchestration. A provider library must stay a transport, not a new orchestrator, and LiteLLM Proxy / Portkey should not become a required control plane.
- **Do not take vendor "factory merges" counts as a goal** (already in the scan's "do not incorporate" list). Provider fallback must not become a path to unattended merge.

Practices already borrowed from primary docs, and from the guardrails note already in the library:

- Cheapest-first checks and fail-closed if a check cannot run (`docs/reference-library/03-layered-llm-guardrails.md`; issue #26).
- Fall back only on retryable status codes, not on 400 (Portkey docs / write-ups).
- One in-process SDK rather than a required proxy (LiteLLM SDK, any-llm).
- Explicit `allow_fallbacks` / data-collection / ZDR flags (OpenRouter).
- Council through one gateway, keys out of agent reach (v6.4 F1).

## 18. Open questions for the operator

1. Do you want to relax the v6.4 non-goal so builders or reviewers may use local, LAN, or OpenRouter models, or should those connections stay limited to council / research / experiments at first?
2. Which endpoints should we wire first: Ollama (or another local server) on this machine, a LAN GPU box, OpenRouter, or stay on Claude Code only until E1.6 has run?
3. Any OpenRouter (or other paid) spend needs your yes. Do you want an account and a hard monthly cap, or to leave OpenRouter configured but disabled?
4. Should `data_leaving_lan` stay `deny` for all jobs, or only for Tier 3 / `sensitive_paths` / security review?
5. For security review, is a the operator-listed "equivalent" local or LAN model ever acceptable, or is it Claude Code `opus` (or a named cloud equivalent) only?
6. Do you care about `estimated_local_usd` (electricity / amortised hardware), or is token + latency enough for local/LAN?
7. If we adopt a library, are you happy with LiteLLM's MIT SDK (no Proxy, no `enterprise/`), or would you rather spike mozilla any-llm first?

Nothing in this file is on GitHub until he says yes.
