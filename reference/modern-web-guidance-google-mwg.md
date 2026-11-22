# Modern Web Guidance (MWG) — Web Platform Best Practices for AI Agents

**Source:** Google Chrome Team (2026)
**Repository:** https://github.com/GoogleChrome/modern-web-guidance
**Blog:** https://developer.chrome.com/blog/modern-web-guidance-v1
**License:** Apache 2.0
**Status:** v1.0 stable (Nov 2026)

---

## What It Is

Modern Web Guidance is an official skill pack + CLI from the Google Chrome team (with Microsoft Edge team + web community contributors) that embeds web platform best practices and Baseline browser compatibility data directly into AI coding agents.

**Core goal:** Stop AI coding agents from generating outdated JavaScript patterns and hacky workarounds. Steer them toward native HTML/CSS APIs that are secure, performant, and match the project's browser support target.

## Coverage

100+ expert-verified use cases across 17 disciplines:

| Category | What's inside |
|---|---|
| **accessibility** | Semantic HTML, focus management, ARIA, form accessibility |
| **built-in-ai** | On-device browser AI: Prompt API, Summarizer, Translator |
| **canvas** | WebGL shaders, exporting media from canvas |
| **css** | Scrollbar styling, dark mode, clip-path, container styling |
| **css-layout** | Flexbox, grid, subgrid, container queries, anchor positioning |
| **datetime** | Duration math, time zones, non-Gregorian calendars |
| **forms** | Autofill, custom select, validation after interaction |
| **html** | Dialog/Popover/Details APIs, invoker commands, resource prioritization |
| **motion** | View transitions, physics-based easing, cross-document transitions |
| **overlays** | Dialogs, popovers, tooltips, navigation drawers, context menus |
| **passkeys** | WebAuthn: registration, authentication, passkey management |
| **performance** | Core Web Vitals (LCP, INP, CLS), long tasks, image/script priority |
| **privacy** | Data minimization, third-party audits, security headers |
| **scroll** | Scroll-snap, parallax, scrollytelling, infinite scroll UX |
| **security** | XSS, CSP, cookies, Cross-Origin Isolation |
| **typography** | Stable font fallbacks, text balancing, precise alignment |
| **webmcp** | Exposing client-side functions as tools for AI agents |

## Integration into the Software Factory

### Installation

```bash
# Install the skill pack
npx @google/modern-web-guidance setup

# Or add as a Claude Code skill
claude plugin install @google/modern-web-guidance

# Declare Baseline target in CLAUDE.md or AGENTS.md
# This project's Baseline target is Baseline 2024.
```

### Two Factory Roles

**1. Build Floor — Pre-Implementation Guidance**
Before writing any web feature, agents consult MWG:
- "Before building any component, check MWG first to see if a standard pattern exists"
- "Never use jQuery or deprecated JS workarounds — MWG has the modern equivalent"
- MWG's guides are framework-agnostic (React, Vue, vanilla JS — same best practices)

**2. Verification Layer — Anti-Slop Lint Standard**
The Anti-Slop Lint Agent uses MWG as the ground truth for code review:
- Does the implementation follow MWG's recommended pattern?
- Is the feature Baseline-compatible for the project's target?
- Are fallbacks provided for features not yet widely available?

### Baseline Target Declaration

Each project declares its Baseline target in `CLAUDE.md` or `AGENTS.md`:

```markdown
# This project's Baseline target is Baseline 2024.
# Follow Modern Web Guidance for all web platform features.
# Check MWG before implementing any web component.
```

This ensures agents:
- Use features in the Baseline window
- Generate appropriate fallbacks for older browsers
- Never suggest experimental or incompatible APIs

## MWG vs Model Knowledge

MWG fills specific gaps that frontier models still get wrong:

| Area | Model failure | MWG fix |
|---|---|---|
| Accessibility | Keyboard focus + inert management | Expert-verified ARIA and focus patterns |
| UX | Dialog/popover transitions, swipe gestures | Native browser APIs instead of JS hacks |
| Performance | Main-thread scheduling, layout shift prevention | Core Web Vitals optimisation patterns |
| Security | Safe HTML sanitization, CSP | Strict Content Security Policy templates |

## Factory Impact

| Before MWG | After MWG |
|---|---|
| Agents write pre-2026 JS patterns | Agents use native HTML/CSS APIs |
| Code needs human review for web standards | Code passes MWG-based lint checks |
| Accessibility must be fixed after build | Accessibility is built in from the start |
| Browser compatibility is guessed | Baseline declares the target, agents comply |