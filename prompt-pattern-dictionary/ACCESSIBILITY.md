# Accessibility & Contrast Automation

This project includes an automated accessibility (a11y) and contrast auditing setup.

## Summary
- **axe-core + Playwright** tests scan core routes for WCAG 2.0/2.1 A/AA violations (serious & critical impacts cause soft test failures).
- **Contrast audit script** parses design token colors in `src/app/globals.css` and checks key foreground tokens against background/surface tokens.
- **Baseline report generation**: CI can run `npm run test:a11y` and archive results; contrast audit can fail the build with `--fail` flag.

## Scripts
| Command | Purpose |
|---------|---------|
| `npm run a11y:install` | Install browsers for Playwright (one-time or CI cache restore). |
| `npm run test:a11y` | Run axe-core accessibility checks on selected routes. |
| `npm run a11y:contrast` | Generate contrast report (does not fail). |
| `npm run a11y:contrast:fail` | Run contrast audit and exit non‑zero if any AA failures. |

## Multi-Theme Coverage
The automated axe-core suite now executes each audited route under three visual themes: `light`, `dark`, and `high-contrast`. The Playwright spec (`tests/a11y/accessibility.spec.ts`) programmatically sets the `data-theme` attribute on the document root before running axe for each theme, ensuring color contrast and structural accessibility regressions are caught across all supported modes.

If you introduce a new theme token set, simply add its identifier to the `THEMES` array in the spec to include it in future scans.

## Adding Routes
Edit `tests/a11y/accessibility.spec.ts` and append to the `ROUTES` array.

## Adjusting Severity
We currently filter out violations whose `impact` is not `serious` or `critical`. Update the filter if you want to fail on `moderate`.

## Contrast Method
The script:
1. Reads `:root` variables in `globals.css`.
2. Filters tokens ending with `background` or `surface` as potential backgrounds.
3. Tests a curated list of foreground tokens (text, accent, link, danger, muted).
4. Uses standard WCAG relative luminance formula.
5. Flags pairs with ratio < 4.5 as failures (normal text baseline). For large text you may choose a 3.0 threshold; adapt script if needed.

## Roadmap / Ideas
- Add screenshot diff overlay for focus outlines.
- Integrate `@axe-core/cli` for additional static HTML snapshots.
- Add keyboard tab order test (custom script) ensuring all interactive elements are reachable.
- Expand contrast audit to parse dark / high contrast theme blocks separately.
- Add ARIA role landmark coverage report.

## CI Example (GitHub Actions Snippet)
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

## Interpreting Failures
- **Accessibility test soft failures**: We use `expect.soft` to list violations while continuing other tests; adapt to hard fails by changing to `expect(violations).toEqual([])`.
- **Contrast audit**: Review failing pairs; adjust color tokens or introduce alternative theming for specific components.

---
Maintaining accessibility is an ongoing process—treat these tools as guardrails while continuing manual reviews with assistive tech.
