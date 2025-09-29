# Theming & Design Tokens

This document codifies the semantic theming system for the Prompt Pattern Dictionary (PPD).

> Goal: Zero raw Tailwind palette usage in feature code. All color/spacing/interaction decisions pass through semantic CSS custom properties and utility classes so we can evolve appearance (light/dark/high‑contrast) without churn.

## Layers

1. **Primitive (Design Tokens)** – CSS variables that express purpose‑agnostic decisions (e.g., `--color-base-bg`, `--color-base-text`, `--radius-sm`).
2. **Mode Overrides** – Per theme (light / dark / high-contrast) variable overrides applied via `[data-theme="dark"]` and `[data-theme="hc"]`.
3. **Semantic Tokens** – Mapped variables that components & utilities use: `--surface-1`, `--surface-card`, `--text-primary`, `--border-accent`, etc.
4. **Utilities & Primitives** – Single-class building blocks (`surface-card`, `tile`, `badge-*`, `chip-task`, `highlight-term`, `focus-ring`).
5. **Components** – React primitives (Card, Tile, Badge, PageHeader, StatChip, Spinner) consuming only semantic utilities.

## File Structure

```
src/styles/
  tokens.css        # primitive + semantic variables per mode
  theme.css         # imports tokens.css, defines utility classes only
```

`globals.css` should import `theme.css` (which itself imports `tokens.css`).

## Adding / Changing a Token

1. Add primitive variable in `:root` within `tokens.css` (e.g., `--color-base-accent`).
2. Reference it from a semantic alias if needed (e.g., `--accent = var(--color-base-accent)`).
3. Override only in the mode sections (`[data-theme='dark']`, `[data-theme='hc']`).
4. Expose via a utility if a recurring pattern emerges; otherwise use semantic classes.
5. Never reference raw hex values in component `.tsx` files – only utilities.

## Core Semantic Variables (excerpt)

| Group | Token | Purpose |
|-------|-------|---------|
| Surface | `--surface-1` | Base app background | 
| Surface | `--surface-2` | Slightly elevated section background |
| Surface | `--surface-card` | Card & tile background |
| Text | `--text-primary` | High-emphasis text |
| Text | `--text-secondary` | Body / medium emphasis |
| Text | `--text-muted` | De-emphasized / metadata |
| Accent | `--accent` | Interactive accent / brand tone |
| Accent | `--accent-fg` | Text/icon color atop accent bg |
| Border | `--border-default` | Standard border lines |
| Border | `--border-accent` | Accent border highlight |
| Focus | `--focus-ring` | Outline color for keyboard focus |
| Heatmap | `--heat-0..4` | Relative intensity scale |
| Code | `--code-bg` | Inline/code block background |

(See `tokens.css` for full list.)

## Utilities (selected)

| Class | Role |
|-------|------|
| `surface-card` | Apply card background, border, radius, shadow adaptively |
| `tile` / `tile-title` / `tile-meta` | Compact clickable card for listings |
| `text-primary|secondary|muted` | Text emphasis tiers |
| `badge-id` / `badge-category` / `badge-ai` | Inline badges with consistent sizing |
| `chip-task` | Application domain/task chip styling |
| `highlight-term` | Search term highlight (accessible contrast) |
| `heat-0..4` | Quantitative intensity backgrounds |
| `focus-ring` | Unified focus outline (uses outline + offset) |
| `pill-filter` / `chip-filter` | Filter selectable pills (future interactive states) |

## Accessibility & Contrast

- Minimum body text contrast: 4.5:1 against its background (target 7:1 where practical for `--text-primary`).
- `--text-secondary` ≥ 4.5:1 on `--surface-1` & `--surface-card` in light/dark.
- `--text-muted` reserved for metadata; must remain ≥ 3:1 (never use for paragraph body copy).
- High contrast mode (`[data-theme='hc']`) may re-map accent & surfaces for Windows High Contrast (forced-colors) – rely on semantic tokens so forced-colors adjustments propagate.
- Do not use opacity for disabled states; derive explicit muted tokens (planned: `--text-disabled`).

## Do & Don't Examples

| ✅ Do | ❌ Don’t |
|------|---------|
| `<div className="surface-card text-secondary">` | `<div className="bg-white text-gray-700">` |
| `<span className="badge-id">{id}</span>` | Inline `px-1 bg-blue-50 border-blue-200 text-blue-700` |
| `<p className="text-primary">` | `<p className="text-black">` |
| `.customBox { background: var(--surface-2); }` | `.customBox { background: #f5f5f5; }` |

## Extending the System

When you need a new semantic concept:
1. Ask: is it a variant of an existing token (e.g., another surface elevation)? If yes, extend with `--surface-X` naming.
2. If brand-specific: add a new primitive (`--color-brand-alt`) then alias (`--accent-alt`).
3. Add a utility class only after at least 2–3 usages appear – prefer direct semantic variables in component CSS modules otherwise.
4. Update this document + add a regression test if the new class replaces legacy raw utilities.

## Regression Guardrails

- `bannedClasses.test.ts`: fails the build if deprecated raw palette utilities reappear.
- Dark token snapshot (future enhancement: snapshot `tokens.css` resolved values in each mode).
- `data.integrity.test.ts`: ensures `applicationTasksString` always present.

## Pattern Detail Specifics

Pattern tasks chips rely on `applicationTasksString` generated in normalization. A deterministic fallback from tags guarantees the section persists across builds; enrichment may override with curated content.

## Adding High Contrast Support

1. Provide `[data-theme='hc']` overrides in `tokens.css` (avoid relying on forced-colors detection alone; we polyfill).
2. Use system colors (e.g., `CanvasText`, `Canvas`) where appropriate; keep semantic alias names stable.

## Checklist Before Merging Theming Changes

- No raw `text-gray-*`, `bg-*` direct palette utilities in modified .tsx files.
- New tokens documented here.
- Utilities reused (avoid single-use class proliferation).
- Contrast verified (manually or via jest-axe) on dark & light.

## Roadmap

- [ ] Tailwind plugin to expose semantic tokens (e.g., `theme('semantic.text.primary')`) and forbid palette escape hatches.
- [ ] Token JSON export for design tooling sync.
- [ ] Dynamic contrast test harness (evaluate computed color ratios). 
- [ ] Motion / transitions token layer (`--easing-standard`, `--duration-sm`).

## FAQ

**Why not keep Tailwind palette?**  Direct palette usage couples feature code to brand decisions; semantic tokens decouple.

**Why custom utilities instead of component-scoped styling only?**  Shared atomic semantics enable global refactors (contrast, brand pivot) with minimal churn.

**Can I use Tailwind spacing/typography?**  Yes – only color/visual theme primitives are constrained. Spacing scale remains Tailwind’s.

---

_This file is source of truth; update it with every new token or semantic utility._
