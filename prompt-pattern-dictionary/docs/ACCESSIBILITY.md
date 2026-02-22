# Accessibility & Readability Program

This document tracks the project-wide accessibility strategy, standards mapping, implementation status, automation tooling, and audit history.

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

## Theme & Preference Provider
A global `ThemeProvider` manages persisted theme mode (`pe-theme`) and separately tracks the last applied effective theme (`pe-theme-effective`) for analytics/debug. An inline pre-hydration script sets both `data-theme` and `data-theme-mode` before paint to eliminate FOUC. The deprecated `useTheme` hook has been removed to prevent divergence—add new theme variants by extending the provider enum and adding token sets; tests should assert new mode presence in the axe multi-theme matrix.

Theme persistence is verified via a Jest + JSDOM unit test (`tests/themePersistence.test.tsx`) that asserts:
1. Stored mode re-applies on mount.
2. Effective theme key (`pe-theme-effective`) mirrors the applied resolved mode (important for `system` → light/dark resolution).
3. DOM attributes `data-theme` and `data-theme-mode` reflect the current state and survive re-renders.

For a detailed overview of the semantic design token system, high-contrast strategy, and extension guidelines, see `docs/THEMING.md`.

## User Readability Controls (Planned)
- Font size S/M/L (scales semantic size tokens)
- Width toggle (standard vs narrow reading)
- Theme selector (Light / Dark / High Contrast)
- Persistence via localStorage (`ppd_prefs_v1`)
- Announcements via `aria-live="polite"` (e.g., "Font size set to Large")

## Automation Scripts
| Command | Purpose |
|---------|---------|
| `npm run a11y:install` | Install browsers for Playwright (one-time or CI cache restore). |
| `npm run test:a11y` | Run axe-core accessibility checks on selected routes. |
| `npm run a11y:contrast` | Generate contrast report (does not fail). |
| `npm run a11y:contrast:fail` | Run contrast audit and exit non-zero if any AA failures. |

## Multi-Theme Test Coverage
The automated axe-core suite executes each audited route under three visual themes: `light`, `dark`, and `high-contrast`. The Playwright spec (`tests/a11y/accessibility.spec.ts`) programmatically sets the `data-theme` attribute on the document root before running axe for each theme, ensuring color contrast and structural accessibility regressions are caught across all supported modes.

If you introduce a new theme token set, simply add its identifier to the `THEMES` array in the spec to include it in future scans.

### Adding Routes
Edit `tests/a11y/accessibility.spec.ts` and append to the `ROUTES` array.

### Adjusting Severity
We currently filter out violations whose `impact` is not `serious` or `critical`. Update the filter if you want to fail on `moderate`.

## Contrast Audit Method
The script (`scripts/contrast-audit.cjs`) performs the following:
1. Reads `:root` variables in `src/styles/tokens.css`.
2. Filters tokens ending with `background` or `surface` as potential backgrounds.
3. Tests a curated list of foreground tokens (text-primary, text-secondary, text-muted, accent).
4. Uses standard WCAG relative luminance formula.
5. Flags pairs with ratio < 4.5 as failures (normal text baseline). For large text you may choose a 3.0 threshold; adapt script if needed.

### High Contrast Token Audit (Phase 6 P4)
An automated WCAG contrast audit script (`scripts/contrast_audit.js`) evaluates representative foreground/background pairs from the High Contrast theme block in `tokens.css` and exits non-zero if `text-primary` contrast drops below 7:1 (enhanced baseline). Latest run produced:

| Pair | Ratio | AA | Enhanced |
|------|-------|----|----------|
| text-primary vs surface-1 | 19.95 | Pass | Pass |
| text-secondary vs surface-1 | 18.67 | Pass | Pass |
| text-muted vs surface-1 | 15.79 | Pass | Pass |
| accent vs surface-1 | 14.03 | Pass | Pass |
| accent-fg vs accent | 14.77 | Pass | Pass |
| focus-ring vs surface-2 | 18.82 | Pass | Pass |

All sampled pairs exceed AA (4.5:1) and enhanced (7:1) targets; no remediation items required.

## Component Audit
| Component | Status | Notes |
|-----------|--------|-------|
| PatternDetail (collapsibles) | ✅ Good | Disclosure button semantics with aria-expanded/aria-controls, aria-live copy feedback |
| Similarity Chips | Baseline | Convert to buttons/links; add focus outline |
| Copy Button | Present | Add `aria-live` feedback and `aria-label` if icon-only |
| Search Input & Filters | ✅ Good | Labelled, result count live region, keyboard accessible |
| Top Navigation | ✅ Good | Semantic nav, aria-label, active state styling |
| Theme Switcher | ✅ Excellent | Radiogroup pattern, roving tabindex, mobile dialog, keyboard navigation |
| Orientation Side Nav | Good start | Add `nav[aria-label]`, ensure active state not color-only |
| Cheat Sheet Print Button | OK | Confirm accessible name & focus indicator |
| Matrix / Future Visualizations | Pending | Provide table fallback or textual summary of data |
| Comparison UI (planned) | Pending | Define roles for interactive cells, allow keyboard cell navigation |

## WCAG 2.2 Mapping (Excerpt)
| WCAG SC | Level | Status | Notes / Actions |
|---------|-------|--------|-----------------|
| 1.1.1 Non-text Content | A | In progress | Provide alt text / hidden labels for all icons |
| 1.3.1 Info & Relationships | A | In progress | Ensure headings reflect structure; dl usage for metadata |
| 1.3.2 Meaningful Sequence | A | ✅ | Logical DOM order enforced by layout |
| 1.3.5 Identify Input Purpose | AA | N/A | Few personal data inputs; monitor future forms |
| 1.4.3 Contrast (Minimum) | AA | ✅ | All theme tokens verified via automated audit |
| 1.4.6 Contrast (Enhanced) | AAA | ✅ | Achieved in HC theme (all pairs >7:1) |
| 1.4.10 Reflow | AA | ✅ | Responsive design present; tested narrow viewport |
| 1.4.11 Non-text Contrast | AA | In progress | Ensure focus rings & toggle icons meet ≥3:1 |
| 1.4.12 Text Spacing | AA | Pending test | Add QA procedure for user CSS overrides |
| 2.1.1 Keyboard | A | ✅ | All interactive elements focusable, ThemeSwitcher roving tabindex |
| 2.1.2 No Keyboard Trap | A | ✅ | No modal traps |
| 2.4.1 Bypass Blocks | A | ✅ | Global skip-to-main link in root layout |
| 2.4.3 Focus Order | A | In progress | Re-verify after footer introduction |
| 2.4.4 Link Purpose (Context) | A | In progress | Provide descriptive link text in footer/nav |
| 2.4.6 Headings & Labels | AA | In progress | Ensure orientation numbering semantic but not cluttered |
| 2.4.7 Focus Visible | AA | ✅ | Consistent double-layer focus ring with forced-colors fallback |
| 2.5.3 Label in Name | A | Pending | Ensure visible label text appears in accessible name |
| 3.2.2 On Input | A | ✅ | No unexpected context changes |
| 3.3.1 Error Identification | A | N/A | Few inputs; revisit when forms added |
| 4.1.2 Name/Role/Value | A | In progress | Normalize ARIA roles for disclosures & chips |

## Roadmap Phases
1. **Foundations**: Tokens, themes, width constraints, base contrast adjustments. ✅
2. **Controls & Nav**: Readability panel, skip links, side nav semantics, focus styling. ✅
3. **Component Remediation**: Disclosures, chips, copy/live regions, search semantics. ✅
4. **Orientation Hybrid**: Multi-page orientation + redirect legacy anchors.
5. **Automation & Docs**: axe-core CI, manual audit, finalize ACCESSIBILITY.md mapping. ✅
6. **Advanced**: Visualization alternatives, comparison keyboard grid, clustering a11y.

## Testing Procedure (Manual Core Set)
1. Navigate entire site with keyboard only (Tab/Shift+Tab, Enter, Space, Arrow keys in disclosures).
2. Screen reader smoke (NVDA): confirm heading outline, nav landmarks, disclosure announcements.
3. Zoom to 200% & 400%: verify responsive reflow (no horizontal scroll except code blocks).
4. Switch themes: verify persisted, accessible names announced.
5. Run custom axe scan script: document results in Audit Log.

## CI Integration (GitHub Actions)
```yaml
- name: Install deps
  run: npm ci
- name: Install Playwright Browsers
  run: npm run a11y:install
- name: Build app
  run: npm run build
- name: Start app
  run: npx next start &
- name: Wait for server
  run: npx wait-on http://localhost:3000
- name: Accessibility Tests
  run: npm run test:a11y
- name: Contrast Audit
  run: npm run a11y:contrast:fail
```

## Content Redundancy (Phase 6 P4)
The Orientation content was scanned with `orientation_redundancy_scan.js` to detect duplicate paragraph blocks. Result: 0 duplicates found. This guards against cognitive overload and improves scan efficiency for users relying on screen readers.

## Interpreting Failures
- **Accessibility test soft failures**: `expect.soft` lists violations while continuing other tests; adapt to hard fails by changing to `expect(violations).toEqual([])`.
- **Contrast audit**: Review failing pairs; adjust color tokens or introduce alternative theming for specific components.

## Audit Log
| Date | Auditor | Scope | Issues Found | Notes |
|------|---------|-------|--------------|-------|
| 2026-02-22 | Automated | Full a11y audit | 0 critical | Dependencies current (jest-axe 9.0, axe-core 4.10, Playwright 1.48); all token contrast pairs passing |

## Exceptions & Justifications
Document here any SC we accept partial compliance on (e.g., complex visualization requiring future text alternative) with mitigation & timeline.

## Change Management
- All new components must include: keyboard operability, focus style, visible label / accessible name, and contrast validation.
- PR Checklist includes accessibility verification steps (enforced via CI workflow).

## Roadmap / Ideas
- Add screenshot diff overlay for focus outlines.
- Integrate `@axe-core/cli` for additional static HTML snapshots.
- Add keyboard tab order test (custom script) ensuring all interactive elements are reachable.
- Expand contrast audit to parse dark / high contrast theme blocks separately.
- Add ARIA role landmark coverage report.
- Extend Jest preference tests to cover upcoming readability attributes (font scale, width mode) and reduced-motion toggling.
- Integrate Lighthouse CI: track accessibility & performance; fail if score below threshold.

---
This file evolves with implementation; update concurrently with code changes to keep provenance and compliance auditable.
