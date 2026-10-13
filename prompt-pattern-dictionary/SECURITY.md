# Security Policy

## Supported Versions

We actively maintain the latest main branch. Older tags receive fixes only for critical vulnerabilities at the maintainers' discretion.

| Version | Supported |
|---------|----------|
| main    | ✅        |
| tags < 1.0.0 | ⚠️ Security fixes case‑by‑case |

## Reporting a Vulnerability

Please DO NOT open a public issue for security vulnerabilities or potential misuse patterns.

1. Email: `security@timhaintz.dev` (placeholder – replace with active address) OR create a private GitHub Security Advisory.
2. Provide:
   - Description of the issue
   - Steps to reproduce (avoid sensitive data)
   - Affected routes, scripts, or pattern IDs
   - Potential impact / severity
3. Expect initial acknowledgment within 72 hours. We will coordinate a fix or mitigation timeline and may request additional clarification.

If you discover misuse (e.g., patterns adapted for harmful generation) rather than a code vulnerability, open a public issue using the "Responsible Use Report" template.

## Coordinated Disclosure

We follow a responsible approach:
- Validate the issue internally.
- Prepare a fix or mitigation.
- Provide CVE assignment where appropriate (for widely impactful vulnerabilities).
- Publish security notes after patch availability.

## Scope

In scope:
- Application code (Next.js pages, components, data pipeline scripts)
- Build tooling & normalization/enrichment scripts
- Prompt pattern data transformation processes

Out of scope:
- Upstream model provider vulnerabilities (Azure OpenAI, etc.)
- Third‑party dependencies (report to their maintainers first unless impact is unique locally)
- Local environment misconfiguration outside documented setup

## Temporary Workarounds

If an immediate patch cannot be shipped:
- We may temporarily disable a route or feature flag (e.g., comparison playground)
- Add a warning or caution badge to affected patterns
- Document risk in PRD Responsible Use section

## Dependency maintenance (2026-10-13)

The website uses a GitHub Pages static export with image optimization disabled.
Next.js 16.3.8, Sharp 0.35.5 and source-map-js 1.2.2 remove the newly published
production high-severity advisories. The scoped Mermaid override selects KaTeX
0.18.2 because maintained Mermaid releases still request affected 0.16 versions.
The public rendering API is retained, and strict Mermaid sanitization remains
in place. Regression tests cover inherited trust, normal maths, explicit trust,
and invalid or cumulative indexed source-map offsets. Jest 30 removes the old
Jest Braces chain; the unused ts-jest transformer was removed because Next's
Jest configuration already uses SWC, also removing its Handlebars dependency.

Run both audits from this directory:

```sh
npm audit --omit=dev
npm audit
```

Production audit is clean. Full audit still reports development-only advisories:

- **Braces** (`GHSA-vfj7-8cjw-p6xm`), through Next's ESLint plugin, fast-glob
  and micromatch: five affected packages are rated high. Braces 3.0.3 remains
  the latest published release and is affected. Do not feed untrusted glob
  patterns into local lint tooling. Downgrading the Next lint configuration
  is not a compatible security fix.
- **sprintf-js** (`GHSA-hp3w-g68c-fv3c`), through Istanbul's YAML configuration
  loader and Jest: nineteen affected packages are rated moderate. The latest
  published sprintf-js 1.1.3 is affected. Test configuration comes from the
  trusted checkout. Do not downgrade Jest to follow audit's suggested fix.

These residual findings are upstream blockers, not a clean full-audit result.
Recheck published versions and dependency chains before the next remediation.
Neither chain is shipped in the exported browser application.

To verify the Pages prefix as well as the default local routes, build with
`GITHUB_PAGES=true GITHUB_REPOSITORY=timhaintz/PromptEngineering npm run build`,
serve the exported artifact at `/PromptEngineering`, then run
`BASE_URL=http://localhost:4300 BASE_PATH=/PromptEngineering npm run test:a11y`.
The 33 cases retain the same routes, themes and severity threshold.

## Verifying Fixes

Security fixes will:
- Include regression tests where feasible
- Reference advisory ID or issue number in commit message
- Update this SECURITY.md if new classes of risk emerge

## Safe Prompt & Pattern Usage

For reporting harmful or dual‑use prompt adaptations:
Use the public "Responsible Use Report" issue template with anonymized examples.

## Contact

For urgent issues mark the advisory or email subject with [URGENT]. Non‑security feature requests should use standard issue templates.
