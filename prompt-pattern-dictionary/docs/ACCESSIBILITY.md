# Accessibility & Readability Program

This document tracks the project-wide accessibility strategy, standards mapping, implementation status, and audit history.

## Standards & Targets
- **Primary Standard**: WCAG 2.2 Level AA
- **Selective AAA**: 1.4.6 / 1.4.8 (Enhanced Contrast & Visual Presentation), 2.4.9 (Link Purpose), portions of 3.1.3 (Unusual Words via Glossary), 1.4.1 (Use of Color – already covered)
- **Authoring Practices**: WAI-ARIA Authoring Practices 1.2 for components (Disclosure, Navigation, Buttons, Live Regions)
- **Assistive Tech**: NVDA, JAWS, VoiceOver (spot checks); axe-core automation

## Design Foundations
| Layer | Tokens / Decisions |
|-------|--------------------|
| Font Stack | `system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif` |
| Base Size | Clamp 17–18px (body) | 
| Line Height | 1.55 body, 1.3 headings |
| Prose Width | 70–75ch max for long-form |
| Themes | light, dark, high-contrast (HC) |
| Contrast Goals | Body text ≥7:1 (HC), ≥4.5:1 (light/dark); UI controls ≥3:1 against adjacent background |
| Focus Ring | 2px solid tokenized color + 2px offset |
| Motion | Respect `prefers-reduced-motion`; disable smooth scroll transitions |

## Display Modes
| Mode | Purpose | Notes |
|------|---------|-------|
| Light | Default neutral | System preference honored first visit |
| Dark | Low luminance | Adjust semantic colors, maintain ≥4.5:1 for body |
| High-Contrast | Maximum legibility | Increase borders/outline, remove subtle gradients |

## User Readability Controls (Planned)
- Font size S/M/L (scales semantic size tokens)
- Width toggle (standard vs narrow reading)
- Theme selector (Light / Dark / High Contrast)
- Persistence via localStorage (`ppd_prefs_v1`)
- Announcements via `aria-live="polite"` (e.g., "Font size set to Large")

## Component Audit (Initial Inventory)
| Component | Status | Required Actions |
|-----------|--------|------------------|
| PatternDetail (collapsibles) | Baseline | Replace custom toggles w/ disclosure button semantics; ensure heading nesting |
| Similarity Chips | Baseline | Convert to buttons/links; add focus outline |
| Copy Button | Present | Add `aria-live` feedback and `aria-label` if icon-only |
| Search Input & Filters | Baseline | Ensure programmatic label, results count live region, keyboard trap avoidance |
| Orientation Side Nav | Good start | Add `nav[aria-label]`, ensure active state not color-only |
| Cheat Sheet Print Button | OK | Confirm accessible name & focus indicator |
| Matrix / Future Visualizations | Pending | Provide table fallback or textual summary of data |
| Comparison UI (planned) | Pending | Define roles for interactive cells, allow keyboard cell navigation |

## WCAG 2.2 Mapping (Excerpt)
| WCAG SC | Level | Status | Notes / Actions |
|---------|-------|--------|-----------------|
| 1.1.1 Non-text Content | A | In progress | Provide alt text / hidden labels for all icons |
| 1.3.1 Info & Relationships | A | In progress | Ensure headings reflect structure; dl usage for metadata |
| 1.3.2 Meaningful Sequence | A | ✅ | Logical DOM order already enforced by layout |
| 1.3.5 Identify Input Purpose | AA | N/A | Few personal data inputs; monitor future forms |
| 1.4.3 Contrast (Minimum) | AA | In progress | Reassess gray body text & subtle list styling |
| 1.4.6 Contrast (Enhanced) | AAA | Planned | Achieved in HC theme |
| 1.4.10 Reflow | AA | ✅ | Responsive design present; test narrow viewport post tokens |
| 1.4.11 Non-text Contrast | AA | In progress | Ensure focus rings & toggle icons meet ≥3:1 |
| 1.4.12 Text Spacing | AA | Pending test | Add QA procedure for user CSS overrides |
| 2.1.1 Keyboard | A | In progress | Verify all custom toggles & chips focusable |
| 2.1.2 No Keyboard Trap | A | ✅ | No modal traps currently |
| 2.4.1 Bypass Blocks | A | In progress | Add multiple skip links |
| 2.4.3 Focus Order | A | In progress | Re-verify after footer introduction |
| 2.4.4 Link Purpose (Context) | A | In progress | Provide descriptive link text in footer/nav |
| 2.4.6 Headings & Labels | AA | In progress | Ensure orientation numbering semantic but not cluttered |
| 2.4.7 Focus Visible | AA | In progress | Replace default outline with consistent style |
| 2.5.3 Label in Name | A | Pending | Ensure visible label text appears in accessible name |
| 3.2.2 On Input | A | ✅ | No unexpected context changes |
| 3.3.1 Error Identification | A | N/A | Few inputs; revisit when forms added |
| 4.1.2 Name/Role/Value | A | In progress | Normalize ARIA roles for disclosures & chips |

## Roadmap Phases
1. **Foundations**: Tokens, themes, width constraints, base contrast adjustments.
2. **Controls & Nav**: Readability panel, skip links, side nav semantics, focus styling.
3. **Component Remediation**: Disclosures, chips, copy/live regions, search semantics.
4. **Orientation Hybrid**: Multi-page orientation + redirect legacy anchors.
5. **Automation & Docs**: axe-core CI, manual audit, finalize ACCESSIBILITY.md mapping.
6. **Advanced**: Visualization alternatives, comparison keyboard grid, clustering a11y.

## Automation Plan
- **axe-core**: Node script or Playwright integration scanning critical routes.
- **Lighthouse CI**: Track accessibility & performance; fail if score < defined threshold.
- **Contrast Regression**: Optional script validating color tokens vs WCAG formulas.

## Testing Procedure (Manual Core Set)
1. Navigate entire site with keyboard only (Tab/Shift+Tab, Enter, Space, Arrow keys in disclosures).
2. Screen reader smoke (NVDA): confirm heading outline, nav landmarks, disclosure announcements.
3. Zoom to 200% & 400%: verify responsive reflow (no horizontal scroll except code blocks).
4. Switch themes: verify persisted, accessible names announced.
5. Run custom axe scan script: document results in Audit Log.

## Audit Log
| Date | Auditor | Scope | Issues Found | Notes |
|------|---------|-------|--------------|-------|
| (pending) |  |  |  |  |

## Exceptions & Justifications
Document here any SC we accept partial compliance on (e.g., complex visualization requiring future text alternative) with mitigation & timeline.

## Change Management
- All new components must include: keyboard operability, focus style, visible label / accessible name, and contrast validation.
- PR Checklist will include accessibility verification steps (to be added once CI automation is live).

---
This file evolves with implementation; update concurrently with code changes to keep provenance and compliance auditable.
