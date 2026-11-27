# HyperSoftwareFactory / documentation visual standard

**Build with agents. Verify with evidence.**

Retro arcade and terminal factory floor: issues enter, agents build, independent checks verify, policy governs the outcome. Preserve the approved [banner](../assets/banner-retro-teal-hyper.png), [assembly-line explainer](../assets/banner-assembly-line-retro-sharp.png) and [illustrative animation](../assets/factory-flow.gif).

## Diagram tokens

This is the documentation extension of the existing brand, using the proposed teal-led palette. Use high-contrast text, monospace labels, restrained pixel/terminal motifs and directional flow.

| Token | Hex | Meaning |
|---|---|---|
| Canvas | #091B23 | Dark factory floor |
| Panel | #10262F | Boundary or grouping |
| Node | #18343D | Station |
| Text | #E3EEEF | Readable label |
| Factory | #55E6BC | Implemented engineering/assurance station |
| Input | #7BB7E4 | Intake/data |
| Decision | #E8BC70 | Human or policy decision |
| Blocked | #F27E75 | Failure/stop |
| Learning | #BDABED | Feedback and planned intelligence |

Use [mermaid-theme.json](mermaid-theme.json) as the shared configuration; inline the variables in GitHub Mermaid blocks, since GitHub does not import local JSON. Use labelled dashed links and explicit captions for planned components; colour is not the only status signal. Do not present a target architecture or illustrative animation as a working product recording. Use descriptive alt text. Keep badges flat-square and use genuine status links.

## Product evidence assets

Capture real terminal, dashboard and GitHub PR views only after executing the corresponding scenario. Redact private repositories, credentials and local paths. Distinguish stand-in tests, demonstrator results and real-project evidence. Do not invent screenshots or terminal output.

## Control room and generated project README

The local dashboard uses the same canvas, panel, node, text and semantic accent colours via CSS custom properties in `factory/dashboard.html`. Use readable muted text, monospaced terminal headings, keyboard focus, responsive layout and reduced-motion support. Preserve existing data bindings and read-only behaviour. Human-required and failure states must remain explicitly labelled. The generated project template in `config/README.template.md` uses the shared Mermaid palette and evidence guidance; a project's approved brand takes precedence for its own identity.

Archived README files are immutable historical records and excluded from visual migration. Do not modify vendored third-party skills solely to apply the factory brand. Existing ASCII architecture diagrams may be migrated to Mermaid with semantic review against the build plan; never replace a code or terminal sample with a decorative diagram.
