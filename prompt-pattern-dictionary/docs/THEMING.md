# Theming & Design Tokens (Canonical)

This canonical document unifies prior theming guidance (previously split across two files) for the Prompt Pattern Dictionary (PPD). It covers architecture, tokens, utilities, accessibility, guardrails, and roadmap. All new theming or accessibility-related contributions MUST reference and update this file.

> Principle: Zero raw Tailwind palette usage in feature code. All color / spacing / interaction decisions pass through semantic CSS custom properties and utility classes so we can evolve appearance (light / dark / high‑contrast) without refactoring component code.

## Goals
- WCAG-compliant palettes across Light, Dark, and High Contrast modes.
- Single source of truth for color & surface decisions (design tokens) – no ad‑hoc hex values in components.
- Predictable theme switching with no flash-of-unstyled-theme (FOUC) and durable persistence of user preference.
- Extensible system: adding a theme or elevation means adding tokens, not rewriting components.
- Automated guardrails (tests + lint patterns) to prevent raw palette regressions.

## Architecture Overview
```
<html data-theme="light|dark|hc">  <-- (effective mode set pre-hydration)
	<body class="... semantic utilities ...">
		React components -> semantic utilities -> semantic tokens -> primitives
	</body>
</html>
```

### Layer Model
1. Primitive Tokens – Purpose‑agnostic decisions (`--color-base-bg`, `--radius-sm`).
2. Mode Overrides – Per theme overrides applied via `[data-theme="dark"]`, `[data-theme="hc"]`.
3. Semantic Tokens – Role-based aliases consumed by utilities/components (`--surface-card`, `--text-primary`).
4. Utilities & Primitives – Single-class building blocks (`surface-card`, `tile`, `badge-*`, `focus-ring`).
5. Components – React primitives (Card, Tile, Badge, PageHeader, StatChip, Spinner) that only use semantic utilities.
6. Regression Tests – Enforce design contract (banned raw classes, data integrity, future contrast snapshots).

## File Structure
```
src/styles/
	tokens.css        # primitive + semantic variables per mode (light, dark, hc)
	theme.css         # imports tokens.css; defines utility classes only
```
`globals.css` imports `theme.css` (which itself imports `tokens.css`). Components never import tokens directly.

## Token Taxonomy (Functional Groups)
Tokens are grouped by functional purpose allowing palette evolution without component churn.

| Category | Examples | Purpose |
|----------|----------|---------|
| Base / Surfaces | `--surface-1`, `--surface-2`, `--surface-card`, `--surface-hover` | Layering & elevation |
| Borders / Separators | `--border-default`, `--border-strong` | Delineation & focus |
| Text | `--text-primary`, `--text-secondary`, `--text-muted` | Hierarchical typography |
| Accent / Brand | `--accent`, `--accent-hover`, `--accent-active-bg`, `--accent-fg` | Interactive / brand emphasis |
| State / Feedback | (future) `--status-danger`, `--status-warning`, `--status-success` | Validation & status |
| Focus | `--focus-ring`, `--focus-ring-outer` | Visible focus outline |
| Code | `--code-bg` | Code blocks & inline code |
| Overlay / Backdrop | (future) `--layer-backdrop` | Dialog / dropdown layering |
| Heatmap (semantic) | `--heat-0`..`--heat-4` | Quantitative intensity scale |

High Contrast (hc) elevates contrast ratios (≥7:1 for primary pairs) and may simplify gradients or neutral surfaces to ensure scannability.

### Core Semantic Variables (Excerpt)
| Group | Token | Purpose |
|-------|-------|---------|
| Surface | `--surface-1` | Base app background |
| Surface | `--surface-2` | Slight elevation / grouping |
| Surface | `--surface-card` | Card & tile background |
| Text | `--text-primary` | High-emphasis reading text |
| Text | `--text-secondary` | Secondary / body meta |
| Text | `--text-muted` | De-emphasized metadata |
| Accent | `--accent` | Interactive accent / brand tone |
| Accent | `--accent-fg` | Text/icon color atop accent background |
| Border | `--border-default` | Standard separators |
| Border | `--border-accent` | Accent border highlight |
| Focus | `--focus-ring` | Unified keyboard focus outline |
| Code | `--code-bg` | Inline/ block code background |
| Heatmap | `--heat-0..4` | Relative intensity stops |

Legacy `--color-*` variable names have been removed; do not reintroduce them. See `tokens.css` for the authoritative semantic list.

## Utilities (Selected)
| Class | Role |
|-------|------|
| `surface-card` | Card background, border, radius, shadow adapts per mode |
| `tile` / `tile-title` / `tile-meta` | Compact clickable listing card |
| `text-primary|secondary|muted` | Text emphasis tiers |
| `badge-id` / `badge-category` / `badge-ai` | Consistent inline badge sizing |
| `chip-task` | Application task chips from `applicationTasksString` |
| `highlight-term` | Accessible search term highlight |
| `heat-0..4` | Quantitative heat backgrounds |
| `focus-ring` | Unified focus outline (outline + offset) |
| `pill-filter` / `chip-filter` | Filterable pill UI (future interactive states) |

Add utilities only after ≥2–3 use sites; otherwise consume semantic tokens directly in component CSS.

## Switching Mechanism
- Pre-hydration script sets `data-theme` (effective) + `data-theme-mode` (user selection) to eliminate FOUC and enable analytics on divergence from system preference.
- ThemeProvider persists selection (`pe-theme`) and current effective mode (`pe-theme-effective`) syncing across tabs via `storage` events and listening to `prefers-color-scheme` changes.
- Supported values: `light`, `dark`, `hc` (alias for `high-contrast`), `system`. Stored legacy `hc` strings are migrated at load.

## Accessibility & Contrast Strategy
1. Body text (primary) aims ≥ 7:1 where feasible; guaranteed ≥4.5:1.
2. Secondary text maintains ≥4.5:1 on surfaces; muted text stays ≥3:1 and never used for paragraphs.
3. No opacity-based disabled states (planned token `--text-disabled`).
4. Focus styling uses `focus-ring` utility; do not remove outlines without replacement.
5. High Contrast mode re-maps accent & surfaces; avoid relying on raw color values in logic.
6. Jest + axe tests run in CI; future expansion: per-theme visual regression and computed contrast audits.

## Focus Rings
Provided via `focus-ring` utility using outline + offset referencing `--focus-ring`. High Contrast may increase thickness/contrast automatically via token remap.

## Pattern Detail & Application Tasks
`applicationTasksString` provides 1–8 concise tasks (comma separated). Chips are order-preserving, non-interactive (future: clickable filter). Normalization script guarantees deterministic fallback generation; enrichment can replace with curated tasks. Guarded by `data.integrity.test.ts`.

## Adding / Changing a Token
1. Add primitive variable in `:root` inside `tokens.css`.
2. Alias through semantic variable if it expresses a role (e.g., `--accent` referencing `--color-accent`).
3. Add overrides in dark / hc sections only (avoid repeating unchanged values).
4. Expose via existing utilities or create a new utility after sufficient reuse.
5. Update this doc & (if necessary) add/extend a regression test.

## Adding High Contrast Support
1. Define `[data-theme='hc']` overrides in `tokens.css` (avoid forced-colors reliance only; we can polyfill).
2. Prefer system colors (`CanvasText`, `Canvas`) where appropriate while retaining semantic alias names.
3. Validate contrast manually + (future) automated ratio script.
4. Avoid decorative shadows; emphasize clear borders & focus outlines.

## Do & Don't Examples
| ✅ Do | ❌ Don’t |
|------|---------|
| `<div className="surface-card text-secondary">` | `<div className="bg-white text-gray-700">` |
| `<span className="badge-id">{id}</span>` | Inline `px-1 bg-blue-50 border-blue-200 text-blue-700` |
| `<p className="text-primary">` | `<p className="text-black">` |
| `.customBox { background: var(--surface-2); }` | `.customBox { background: #f5f5f5; }` |

## Extending the System Safely
| Step | Rationale |
|------|-----------|
| Assess reuse potential | Avoid one-off semantic bloat |
| Add primitive then alias | Keeps raw color list centralized |
| Override only diffs per mode | Reduces maintenance noise |
| Add utility after ≥2 usages | Prevent premature abstraction |
| Document + test | Ensures future contributors respect contract |

## Regression Guardrails
- `bannedClasses.test.ts` – fails build if deprecated raw palette utilities reappear.
- `legacy.variables.ban.test.ts` – asserts no legacy `--color-*` variables re-enter code.
- `contrast.tokens.test.ts` – validates minimum contrast for core text tiers (light & dark).
- `data.integrity.test.ts` – ensures `applicationTasksString` present & non-empty.
- (Planned) Token snapshot tests per mode.
- (Planned) Expanded computed contrast audit across all semantic pairs & high contrast mode.

## Migration Notes
Legacy stored theme `hc` is normalized to `high-contrast`/`hc` consistently. Do not reintroduce inconsistent identifiers.

## Checklist Before Merging Theming Changes
- [ ] No raw `text-gray-*`, `bg-*` palette utilities added in .tsx changes.
- [ ] New tokens added only once & documented here.
- [ ] Utilities reused (avoid single-use additions).
- [ ] Contrast verified in light & dark (and hc if affected).
- [ ] Tests pass (banned classes + data integrity + a11y).

## Adding a New Theme (Beyond hc)
1. Choose attribute value: `[data-theme='sepia']`.
2. Duplicate variable set in `tokens.css` reusing existing semantic keys.
3. Provide accessible contrast (audit + manual checks).
4. Add to ThemeProvider allowed list + tests.
5. Update this document + README.

## Roadmap
- Tailwind plugin to expose semantic tokens & forbid palette escape hatches.
- Token JSON export for design tooling synchronization.
- Dynamic contrast test harness (programmatic ratio validation across modes).
- Motion / transitions token layer (`--easing-standard`, `--duration-sm`).
- Per-theme visual regression snapshots (Playwright) on key routes.
- Readability controls (font scale, width) integrated with tokenized line-length.

## Quick Reference (Common Classes)
| Utility | Maps To | Typical Use |
|---------|---------|-------------|
| `text-primary` | `--text-primary` | Main body copy |
| `text-secondary` | `--text-secondary` | Subhead / meta |
| `text-muted` | `--text-muted` | De-emphasized metadata |
| `bg-base` | `--surface-1` | Page background |
| `surface-card` | `--surface-card` | Cards / tiles |
| `focus-ring` | `--focus-ring` | Focus outline |
| `badge-id` | tokens + accent vars | Pattern/example IDs |
| `chip-task` | task chip styling | Application tasks |
| `heat-0..4` | heatmap scale | Similarity / intensity displays |

## FAQ
**Why not rely entirely on Tailwind's palette?**  
Semantic longevity & accessibility. Raw palette usage couples feature code to brand choices; semantic tokens decouple intent from implementation.

**Can I use opacity for disabled states?**  
Prefer explicit `--text-disabled` (future) + adjusted surface/border. Opacity undermines contrast for low vision users.

**Where do spacing & typography tokens live?**  
Currently Tailwind's scale. A spacing/typography token layer may be introduced if cross-theme adaptation emerges.

**Why both `data-theme` and `data-theme-mode`?**  
One reflects effective applied mode, the other preserves user selection (so analytics & system sync logic can detect divergence).

**Heatmap tokens vs. state tokens?**  
Heatmap expresses quantitative intensity; state tokens communicate validation/status. Do not mix.

---
Maintain discipline: if you find yourself typing a hex value or Tailwind color utility for visual styling, add or reuse a token instead.

_Canonical Source: `docs/THEMING.md`. Remove duplicates elsewhere; update links when relocating._
