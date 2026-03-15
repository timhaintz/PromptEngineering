# Site Test Strategy

## Purpose

Provide reliable live-site regression coverage for the Ballarat AI Prompt Dictionary while keeping E2E testing separate from the app source tree.

## Best-Practice Summary

Based on official Playwright guidance:

- Verify user-visible behavior.
- Keep tests isolated.
- Prefer role, label, and text locators.
- Use web-first assertions instead of manual waits.
- Use the VS Code extension and codegen to refine locators.
- Record traces on first retry, not on every passing run.
- Avoid brittle DOM-coupled selectors.

## Live-Site Constraints

- The target is a deployed static site.
- Some data can evolve over time; avoid exact count assertions unless intentionally fixed.
- External sites are out of scope.
- Regressions should focus on headings, navigation, visible controls, URLs, and stable descriptive content.

## Recommended Coverage Layers

### 1. Smoke

- Homepage loads
- Global nav works
- Key landing pages render

### 2. Orientation

- Hub content renders
- Role map links route correctly
- Quick paths route correctly

### 3. Core Discovery

- Logic Layers page renders
- Category pages are reachable
- Search page accepts queries and exposes filters

### 4. Policy / Safety

- Responsible Use page renders critical guidance headings

## MCP Usage Pattern

When using Playwright MCP tools:

1. Open the deployed URL.
2. Exercise the exact user flow.
3. Capture stable locator candidates.
4. Verify whether the issue is visual, behavioral, or performance-related.
5. Convert confirmed stable checks into `website-e2e/tests`.

## Regression Authoring Guidelines

- One behavior per test when feasible.
- Prefer direct page navigation for setup unless the navigation path itself is under test.
- Keep assertions small and explicit.
- If a page is content-heavy, assert a small number of contract headings rather than the full document body.
