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

## Dependency maintenance (2026-11-03)

The website uses a GitHub Pages static export with image optimization disabled.
Next.js 16.4.4 addresses the three Next alerts requiring 16.4.1. Mermaid resolves
DOMPurify 3.4.17 through a scoped minimum-version override. Strict Mermaid
sanitization and the existing KaTeX override remain in place. Tests resolve the
actual Mermaid sanitizer and cover split shadow-root templates, detached hook
subtrees, XHTML/HTML SMIL attributes, and ordinary SVG output.

The development graph uses glob 14.0.3 for its cancellation fix
(`GHSA-3g3m-2fjr-6pw4`). Modern minimatch consumers use 11.0.4. The overrides
retain the callable minimatch 3 API required by legacy ESLint plugins. Tests
exercise cancellation after the first directory read and ordinary sync/async
discovery with ignore options; the full Jest coverage run checks its consumers.
The existing ESLint configuration version is retained to preserve the project's
lint policy. Node 20 (CI) and 22 (local validation) support the selected versions.
Its React Hooks validator resolves Zod 4.6.7, addressing
`GHSA-mrhx-c7xc-m3w5`. Bounded regressions verify oversized constrained arrays
and sets fail before element parsing while ordinary transforms still run.

Run both audits from this directory:

```sh
npm audit --omit=dev
npm audit
```

Production audit is clean. Full audit still reports two development-only advisory
roots whose repository alerts have been assessed as inaccurate:

- **minimatch** ([GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249)):
  the installed legacy 3.1.5 compiler does not clone/reprocess globparts or run
  the pairwise preprocessing described by this CVE. The
  [project advisory](https://github.com/isaacs/minimatch/security/advisories/GHSA-g3hv-75wg-m249)
  identifies 10.2.6; the broader database range includes the separate legacy
  implementation. Modern consumers already use 11.0.4. Retaining 3.x preserves
  the callable and `makeRe` APIs required by existing lint plugins. This finding
  is scoped to the named CVE, not every possible glob/regex resource cost.
- **deepmerge** ([GHSA-gcqx-w48m-w2h4](https://github.com/advisories/GHSA-gcqx-w48m-w2h4)):
  its [canonical CVE record](https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/93xxx/CVE-2026-93753.json)
  was rejected by the assigning authority on 2 November 2026 because it does not
  describe a security vulnerability. The GitHub advisory still reflects an older
  assessment. Jest and its merge semantics are retained.

Alerts #596 and #587 were dismissed as inaccurate with evidence after owner
approval and independent review. This is a classification correction, not a
dependency patch; npm audit can continue reporting stale/broad metadata until
the upstream database is corrected. Neither chain is shipped in the exported
browser application, and the full audit is not claimed clean. Reassess the
classification if versions or affected mechanisms change.

The root Python workspace no longer installs ChromaDB: the owner confirmed its
legacy RAG workflow is unused, and its original script is archived as text.
The four ChromaDB alerts are addressed by dependency removal, not dismissal.

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
