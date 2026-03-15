---
name: playwright-mcp-website-testing
description: "Use Playwright MCP tools and the external website-e2e suite to validate the deployed Ballarat AI Prompt Dictionary website. Use when testing the live site, reproducing browser issues, capturing user-visible regressions, or converting exploratory browser checks into maintained Playwright specs. Keywords: Playwright MCP, website e2e, live site testing, browser regression, VS Code Playwright, deployed website validation."
license: MIT
metadata:
  author: Tim Haintz
  version: "0.1"
  target-site: https://www.timhaintz.com.au/PromptEngineering/
---

# Playwright MCP Website Testing

This skill is for testing the deployed Ballarat AI Prompt Dictionary website with Playwright MCP tools first, and then codifying stable coverage into the external `website-e2e` suite.

## When to Use This Skill

- Reproducing live-site browser issues
- Validating deployments on `https://www.timhaintz.com.au/PromptEngineering/`
- Writing or updating browser regression tests for the website
- Performing exploratory checks in VS Code with Playwright MCP
- Turning validated user journeys into maintained Playwright specs

## Primary Workflow

1. Use Playwright MCP browser tools first for exploratory validation on the deployed site.
2. Confirm the behavior with user-visible assertions only.
3. Add or update the external regression suite in `website-e2e/`.
4. Run the external suite from VS Code tasks or `npm test` in `website-e2e/`.
5. Keep the application folder separate from the E2E project.

## Tooling Priorities

Prefer the following in order:

1. Playwright MCP browser tools for live exploration and debugging.
2. The external `website-e2e` Playwright suite for repeatable regression coverage.
3. VS Code Playwright extension for local run/debug/codegen.

## Test Design Rules

- Test user-visible behavior, not implementation details.
- Prefer `getByRole`, `getByLabel`, and user-visible text.
- Use `getByTestId` only when a user-facing locator is not stable enough.
- Avoid CSS/XPath unless absolutely necessary.
- Keep tests isolated and runnable independently.
- Avoid asserting exact dynamic counts unless the source contract is intentionally fixed.
- Do not test third-party sites or external navigation beyond confirming that links exist.
- Use web-first assertions such as `toBeVisible`, `toHaveURL`, and `toHaveValue`.

## Site Areas Worth Testing

- Homepage rendering and primary navigation
- Orientation Hub role map and quick paths
- Logic Layers and category drill-down
- Search flows and filter controls
- Responsible Use content
- Taxonomy and category browse pages

## What Belongs In MCP Exploration vs. Regression Specs

Use Playwright MCP exploration for:

- Reproducing responsiveness issues
- Checking console/network behavior during live debugging
- Validating suspect selectors before writing tests
- Investigating flaky or environment-specific behavior

Use the `website-e2e` suite for:

- Stable smoke tests
- Navigation regressions
- Accessible control behavior
- Text, URL, and form-flow checks that should survive deployments

## Project Locations

- Skill: `skills/playwright-mcp-website-testing/`
- External suite: `website-e2e/`
- VS Code tasks: `.vscode/tasks.json`
- VS Code extension recommendation: `.vscode/extensions.json`
- CI workflow: `.github/workflows/website-e2e.yml`

## References

- [Strategy](references/SITE_TEST_STRATEGY.md)
- [Website E2E README](../../website-e2e/README.md)
