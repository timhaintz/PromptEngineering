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
