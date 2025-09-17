# Theming & Design Tokens

This document describes the theming architecture, semantic design tokens, switching mechanics, and contribution guidelines for the Prompt Pattern Dictionary web application.

## Goals
- Provide accessible, WCAG-compliant color palettes across Light, Dark, and High Contrast modes.
- Centralize all color definition in a single token layer to eliminate hard-coded hex values in components.
- Support future theme expansion with minimal component churn (add tokens, not conditionals per component).
- Preserve user preference (including system mode) with graceful hydration and no perceptible flash of incorrect theme.
- Enable automated accessibility (axe + contrast audit) to validate every supported theme.

## High-Level Architecture
```
<html data-theme="light|dark|high-contrast">  <-- applied by useTheme / preferences
  <body class="... Tailwind utilities ... semantic token utility classes">
    Components referencing semantic classes (e.g., text-primary, bg-surface)
  </body>
</html>
```

Layers:
1. Raw CSS Variables (per theme) – defined in `theme.css` (imported by `globals.css`).
2. Semantic Mapping Utilities – small set of classnames (e.g., `.text-primary { color: var(--color-fg-primary); }`).
3. Components – exclusively consume semantic classes / tailored utilities (never raw hex values).
4. Theme Persistence – `useTheme` hook sets `data-theme` + localStorage; Orientation `usePreferences` integrates theme with other readability prefs.

## Token Taxonomy
Tokens are grouped by functional purpose, not specific colors, allowing palette evolution without component rewrites.

| Category | Examples | Purpose |
|----------|----------|---------|
| Base / Surfaces | `--color-bg-base`, `--color-bg-subtle`, `--color-surface-raised` | Layering & elevation semantics |
| Borders / Separators | `--color-border`, `--color-border-strong`, `--color-border-focus` | Delineation & focus outlines |
| Text | `--color-fg-primary`, `--color-fg-secondary`, `--color-fg-muted`, `--color-fg-inverse` | Hierarchical typography & inversion |
| Accent / Brand | `--color-accent`, `--color-accent-emphasis`, `--color-accent-hover` | Interactive & brand-forward elements |
| State / Feedback | `--color-danger`, `--color-warning`, `--color-success`, `--color-info` | Validation & status messaging |
| Focus | `--color-focus-ring` | Highly visible focus outlines |
| Code / Mono (optional) | `--color-code-bg`, `--color-code-border` | Inline / block code regions |
| Overlay / Backdrop | `--color-backdrop` | Dialogs, dropdown layering |

High Contrast overrides selectively boost contrast ratios (e.g., stronger separation of surface vs. base; brighter focus ring).

## Theme Definitions
Each theme declares a root scope of variables:
```
:root { /* Light (default) */ }
:root[data-theme="dark"] { /* Dark overrides */ }
:root[data-theme="high-contrast"] { /* HC overrides */ }
```
When `data-theme` is absent and the user selected "system", a `prefers-color-scheme: dark` media query may add dark adjustments (if implemented). High Contrast always requires explicit selection (no OS mapping yet).

## Switching Mechanism
- `useTheme` hook returns `[theme, setTheme]` where `theme` ∈ `light | dark | high-contrast | system`.
- Setting `system` removes `data-theme` attribute, letting media queries decide.
- Other values set `data-theme` directly.
- Preferences stored via localStorage key (orientation layer also stores font scaling & width mode). Migration logic handled legacy `hc` → `high-contrast` rename.

## Accessibility Strategy
1. Maintain minimum 4.5:1 contrast for normal body text, 3:1 for large text (as practical baseline) across Light & Dark. High Contrast raises many pairs above 7:1.
2. Avoid conveying information with color alone; structural states (active/selected) use combined shape, border, or weight changes.
3. Provide visible, consistent focus ring (`--color-focus-ring`) with at least 3:1 contrast against adjacent surface.
4. Use semantic tokens for text tiers; never lighten text via opacity (prefer distinct tokens for secondary/muted).
5. Axe + Playwright test suite iterates all supported themes per route.
6. Contrast audit script (currently scanning light tokens) planned to expand support for Dark & High Contrast (roadmap).

## Adding a New Theme
1. Define an attribute value (e.g., `data-theme="sepia"`).
2. Add a new override block in `theme.css` mirroring existing token keys.
3. Ensure minimum viable pairs pass contrast (run audit script; manual spot checks for interactive states, focus, badges, code blocks).
4. Append the new theme id to `THEMES` array in `tests/a11y/accessibility.spec.ts`.
5. Update documentation (this file & README) and optionally add screenshot references.
6. Avoid introducing theme‑specific component logic; rely on tokens. Only branch in CSS if absolutely necessary (e.g., invert drop shadow intensity in dark modes).

## Extending Tokens Safely
- Introduce a token only after confirming it is broadly reusable (avoid one-off tokens).
- Provide a fallback value in the base scope before overriding in dark/high-contrast.
- Prefer derivative composition (e.g., computed shades) only if determinism improves maintainability—otherwise keep explicit hex for audit clarity.
- Document new tokens in the table above or append a "Changelog" section.

## Do & Don't Examples
| Do | Don't |
|----|-------|
| Use `<div class="text-secondary">` | Hard-code `text-slate-500` |
| Use `bg-surface-raised` for cards | Reuse `bg-base` everywhere causing flat hierarchy |
| Use `focus-visible` + tokenized outline | Add custom inline `style="outline: 1px solid #fff"` |
| Adjust palette in `theme.css` | Inline edit per-component hex values |

## Focus Rings
Focus is applied via a utility using `outline` or `box-shadow` referencing `--color-focus-ring`. In High Contrast, the ring becomes thicker and brighter. Ensure interactive elements have `:focus-visible` styling and no removal of default outline without replacement.

## Migration Notes
Legacy value `hc` was renamed to `high-contrast`. A migration block in the preferences hook maps stored `hc` to the new canonical value. Avoid reintroducing `hc` in new code or docs.

## Testing Checklist (per change)
- Run `npm run test:a11y` (ensures all themes scanned; verify zero serious/critical regressions).
- Spot check manually: Theme switcher transitions, focus states, active navigation pill, code samples, buttons in dark & high-contrast.
- Contrast script: `npm run a11y:contrast` (light currently). If introducing dark variant adjustments, temporarily duplicate tokens into a dark audit branch or extend the script.

## Roadmap Enhancements
- Extend contrast audit to parse dark / high-contrast variable scopes.
- Add visual regression snapshots per theme (e.g., Playwright screenshot diff on key pages).
- Dynamic prefers-reduced-motion and large text scaling tokens.
- Token-driven spacing scale for denser vs. comfortable reading modes.

## Quick Reference (Common Classes)
| Utility | Maps To | Typical Use |
|---------|---------|-------------|
| `text-primary` | `--color-fg-primary` | Body copy, main content |
| `text-secondary` | `--color-fg-secondary` | Subhead, metadata |
| `text-muted` | `--color-fg-muted` | De-emphasized captions |
| `bg-base` | `--color-bg-base` | Page background |
| `bg-surface` | `--color-bg-surface` | Cards, panels |
| `bg-surface-raised` | `--color-surface-raised` | Elevated cards / modals |
| `border-default` | `--color-border` | Dividers, card borders |
| `border-strong` | `--color-border-strong` | Emphasis lines, side markers |
| `ring-focus` | `--color-focus-ring` | Focus outline application |
| `text-accent` | `--color-accent` | Links, accent inline emphasis |
| `bg-accent` | `--color-accent-emphasis` | Accent buttons, pills |

## FAQ
**Why not rely entirely on Tailwind's color palette?**  
Because semantic longevity and accessibility guarantees are easier when components don't depend on a palette that may shift for styling reasons. Semantic tokens decouple design intent from theme implementation.

**Can I use opacity for disabled states?**  
Prefer a dedicated token (`--color-fg-muted`) plus reduced contrast border or background. Opacity can harm contrast for users with low vision.

**Where do spacing & typography tokens live?**  
Currently handled via Tailwind scale + attribute-based modifiers. Future expansion may introduce explicit spacing tokens if cross-theme adaptation is needed.

---
Maintain discipline: if you find yourself typing a hex color in a component, add or reuse a token instead.
