# 03 Layered LLM guardrails on Apigee (Wely Lau)

Local reference-library notes only. Not pushed to GitHub.

## Source

- **Title:** Layered LLM guardrails on Apigee: Static rules, Model Armor and NeMo Guardrails
- **Author:** Wely Lau ([@welylau](https://discuss.google.dev/u/welylau)), with peer reviewers Christophe Lalevée and Tyler Ayers
- **Published:** 10 November 2026, 07:28 UTC (07:28 UK time, Europe/London). The Discourse post was later updated on 17 November 2026, 18:40 UTC (18:40 UK time).
- **URL:** https://discuss.google.dev/t/layered-llm-guardrails-on-apigee-static-rules-model-armor-and-nemo-guardrails/412532
- **Forum metadata:** Google Developer forums, Knowledge Hub; tags `apigee`, `googler-article`. Official markdown alternate: the same URL with `.md`.
- **Shared with the operator via:** [Google Cloud India on X](https://x.com/GoogleCloud_IN/status/2125431785269981256), posted 25 November 2026, 03:30 UTC (03:30 UK time). The post links the article and summarises it; the claims below are taken from the article itself, not from the post's shorter wording.
- **Also listed** (without replacing the article) on Google Cloud's "What's new" blog for 9–13 November, dated 19 November 2026: https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud
- **Demo repo** (the article calls it a reference implementation, not a drop-in production config): https://github.com/welylau/apigee-guardrails-demo
- **Walkthrough video** linked from the article: https://www.youtube.com/watch?v=qhOE0h_D9lM (not transcribed for these notes)
- **Added to this library:** 25 November 2026 (Europe/London)

**Important caveat, in the article's own words:** "this isn't an official Google product." The author also writes: "This isn't a one-size-fits-all blueprint, and there's no such thing." Treat the post as a **reference example** of a layered design, not a product recommendation to install Apigee, Model Armor or NeMo in the factory.

## Summary

The article argues that no single LLM guardrail catches everything. The demo puts Apigee in front of Gemini as an AI gateway and stacks three layers, **cheapest first**:

1. **Static Guardrails** — deterministic regex, word lists and validators built from existing Apigee policies (known attacks, leaked keys, card numbers, banned terms, SQL injection).
2. **Google Cloud Model Armor** — semantic safety filters on the prompt and on the streamed response (jailbreaks, prompt injection, responsible-AI categories, sensitive data). Works on meaning, including reworded or non-English jailbreaks in the demo.
3. **NVIDIA NeMo Guardrails** — the app's own business rules, mostly judged by an LLM, written in YAML/Colang. The article presents NeMo as one example; the same gateway slot could call another HTTP guardrail.

On the author's **small, hand-written** test suite of 102 cases (88 attacks and 14 safe prompts), mapped to the [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/) and the [OWASP API Security Top 10 (2023)](https://api-security.owasp.org/editions/2023/en/0x11-t10/), all three layers together caught all 88 attacks and, at the "balanced" settings, did not block any of the 14 safe prompts. The article itself says to **read those numbers as a reference, not a benchmark**: they come from one suite, one proxy and one configuration (run 9 November 2026 against Gemini 3.5 Flash Lite on Vertex AI). "Strict" settings still caught 88/88 but started blocking 3 of the 14 safe prompts. Every layer caught at least one attack that only it caught. With all layers on, 71 of the 88 attacks were stopped before the expensive NeMo call ran.

The last (slowest) layer in the demo **fails open** if it times out; Static and Model Armor still apply and the error is logged. The author says you can fail closed instead if your risk profile calls for it. Guardrails are described as only part of a gateway: identity, rate and token budgets, and observability also matter.

## Key learnings (only claims the article makes)

### 1. No single guardrail is enough; stack deterministic, semantic and business-rule layers

> "No single guardrail catches everything."

> "It's not either/or. Deterministic rules, semantic filters and business rules each cover gaps the others leave."

The article's example: an investment-advice question can pass static and semantic filters and still be blocked by a business rule that a support assistant must not give investment advice. "Every layer caught attacks that only it caught."

### 2. Run layers cheapest first

> "because a regex check takes milliseconds, a Model Armor scan takes a few hundred milliseconds (pay-per-scan), and an LLM-as-judge call takes around a second plus tokens, run them cheapest first, so each layer only sees traffic the cheaper ones have already cleared."

> "Order layers by cost. Blocked requests cost zero tokens, and the slowest layer only sees what's left."

In this demo, at balanced settings, Static stopped 27 attacks first (~100 ms), Model Armor 33 (~540 ms), and NeMo 17 (~1.3 s). Those latencies are medians from this setup, "for reference only."

### 3. Treat published catch rates as a reference, not a transferable benchmark

The 88/88 and 0/14 figures apply to "this specific proxy and configuration" and a suite with only 14 safe prompts, "too few" to show NeMo's tendency (in the author's larger tests) to block more legitimate requests. Strict Model Armor response filters "started cutting off good answers that merely explained prompt injection." "Run the suite against your own setup before choosing settings."

### 4. Inspect cumulative, multi-turn and streamed text; already-sent tokens cannot be recalled

> "Inspect every turn, not just the last one. Multi-turn attacks hide the injection in an earlier message."

For streaming answers, the demo inspects a **cumulative** buffer. "Tokens already sent can't be recalled. Use it alongside prompt inspection and redaction, not instead of them."

### 5. Decide fail-open vs fail-closed on purpose; guardrails are not the whole control plane

> "It also fails open: if NeMo times out, Static Guardrails and Model Armor still apply and the error is logged. You can fail closed instead if your risk profile calls for it."

Section 5 adds identity, SpikeArrest/Quota, prompt-token limits and token budgets, plus a gateway `maxOutputTokens` cap, as first-class requirements "alongside the guardrails, not an afterthought." The last attack in the suite (OWASP LLM10, unbounded consumption: "repeat the word 'company' 50,000 times") needed a layered fix plus that cap, because at first every guardrail layer let it through.

## What applies to HyperSoftwareFactory

Do **not** read this as a proposal to put Apigee, Model Armor or NeMo into the factory engine. The article is a Google Cloud demo, not an official product, and the factory already has its own gateway: a scripted `factory run` loop, a network allowlist, and agents without GitHub tokens.

The **principles** map cleanly:

| Article principle | Factory state on main (`72a982c`, plan v6.4) | Proposal |
|---|---|---|
| Cheap static checks before an LLM sees untrusted text | F4/F8 already require a **tool-less summariser** before any acting agent sees external text. There is no documented static pre-filter (secrets, injection, PII) on the drop folder or on issue bodies | Add cheapest-first layers to the **F4 drop-folder contract** (and F8): static checks first, then the existing tool-less summariser, then a business rule that proposals are never auto-queued and that untrusted text is not treated as instructions |
| Semantic / prompt-injection checks | Not built. Planned research is official APIs plus a summariser | Optional later filter; not a reason to widen the E6 allowlist. Do not send drop-folder text to an acting builder |
| App-specific business rules | Always-stop paths, `human-merge`, and "a proposal is never queued automatically" already express policy | Keep those in scripts, not only in an LLM judge |
| Fail closed when a check cannot run | Issue **#26** still fails **open** on a missing `unattended_merge` key. The article's demo fails open on a NeMo timeout, but explicitly allows fail-closed | Prefer fail-closed for merge and for untrusted intake: if a guardrail errors or times out, do not pass the text to an agent that can open issues or write code |
| OWASP LLM / API Top 10 as a test lens | Gemini plan mentioned OWASP packs; not in v6.4 as a factory suite | A small, factory-owned test list for untrusted intake (prompt injection, secrets, unbounded cost) is worth adding with the F4 contract. Do not cite the demo's 88/88 as the factory's target |
| Token budgets and observability | E2 budgets, event log, and a later `max` output/turn cap already exist | Keep these as first-class, alongside any new intake filters |
| Inspect every turn, not only the latest message | Relevant if F8 or a feedback loop concatenates comments | When building F8 or PR-comment feedback, scan the accumulated untrusted text |

This belongs in **Phase 4** of the local deployable plan, with the F4 drop-folder contract, and it also sharpens Phase 0 (#26 fail-closed). It is a proposal only.

`principles.md` is still deferred until the operator says the reference set is complete.
