# Website E2E

This is a separate Playwright end-to-end suite for the deployed Ballarat AI Prompt Dictionary website.

It is intentionally outside `prompt-pattern-dictionary/` so it can validate the live site as a consumer would, without coupling test execution to the app workspace.

## Defaults

- Target URL: `https://www.timhaintz.com.au/PromptEngineering`
- Browser: Chromium
- Reporters: terminal list + HTML report
- Failure diagnostics: trace, screenshot, video on failure/retry

## Run From VS Code

Use the workspace tasks:

- `website-e2e: install`
- `website-e2e: install browsers`
- `website-e2e: run live`
- `website-e2e: run headed`
- `website-e2e: debug`

The workspace also recommends the Playwright VS Code extension.

## Run From Terminal

```powershell
Set-Location .\website-e2e
npm install
npm run install:browsers
npm test
```

To point at a different deployment:

```powershell
$env:PLAYWRIGHT_BASE_URL = 'https://example.com/PromptEngineering'
npm test
```

## Scope

This suite follows Playwright best practices:

- Test user-visible behavior.
- Prefer `getByRole`, `getByLabel`, and visible text over CSS/XPath.
- Keep tests isolated and independent.
- Avoid asserting volatile implementation details or third-party resources.
- Use the live site for smoke and regression coverage; use Playwright MCP for exploratory browser work when available.

## Current Coverage

- Homepage smoke and global navigation
- Orientation Hub key content and intent links
- Logic Layers page and category navigation
- Search page navigation and core controls
- Categories page, taxonomy page, papers page, and examples page
- Responsible Use page rendering
