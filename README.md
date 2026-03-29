# Prompt Engineering

This repository contains a collection of Python scripts and tools designed for various tasks related to text extraction, categorisation, and prompt engineering. The main functionalities include a JSON database of research papers with Prompt Patterns (PPs) and Prompt Examples (PEs) extracted, extracting text from PDFs, categorising text using Cosine Similarity, and generating and testing prompts for AI models.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Extract Text from PDF](#extract-text-from-pdf)
  - [Categorise Text Using Cosine Similarity](#categorise-text-using-cosine-similarity)
  - [Generate and Test Prompt](#generate-and-test-prompt)
  - [Export PPs and PEs from the JSON File](#export-pps-and-pes-from-the-json-file)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)
- [Security Policy](#security-policy)
- [Responsible Use Guidelines](#responsible-use-guidelines)
- [Chapter 6 Evaluation (CLI)](#chapter-6-evaluation-cli)
- [Prompt Pattern Dictionary (Web App)](#prompt-pattern-dictionary-web-app)
  - [Orientation Architecture](#orientation-architecture)
  - [Readability & Theming Controls](#readability--theming-controls)
  - [Legacy Anchor Redirect Behavior](#legacy-anchor-redirect-behavior)
  - [Extending the Preference System](#extending-the-preference-system)

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

2. Create the environment with `uv` and activate the generated `.venv`:

```sh
uv venv --python 3.12
.venv\Scripts\Activate.ps1  # On Windows PowerShell
source .venv/bin/activate    # On macOS/Linux
```

3. Sync the project dependencies from `pyproject.toml` and `uv.lock`:

```sh
uv sync
```

Notes:

- The root `pyproject.toml` is now the primary dependency source for the Python workspace.
- `.venv` is still the environment directory; `uv` just manages it faster and more reproducibly.
- `requirements.txt` and `requirements_updated.txt` are legacy snapshots from the previous workflow and should not be the primary install target for new setup.


4. Set up environment variables by creating a `.env` file in the root directory and adding the necessary keys:

    ```env
    AZURE_OPENAI_MODEL=<your-model>
    API_VERSION=<your-api-version>
    AZURE_OPENAI_KEY=<your-api-key>
    AZURE_OPENAI_ENDPOINT=<your-endpoint>
    ```

## Usage

### Extract Text from PDF

To extract text from a PDF file, use the `extractTextFromPDF.py` script. Below are some examples:

```sh
python extractTextFromPDF.py -filename "Test.pdf"
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -extractexamples True
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -summary True
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -keypoints True
```

### Categorise Text Using Cosine Similarity

To categorise text using Cosine Similarity, use the categorisation_cosine_similarity.py script:

```sh
python categorisation_cosine_similarity.py --top_n 5
python categorisation_cosine_similarity.py --threshold 0.5
```

### Generate and Test Prompt

To generate and test prompts, use the testPrompts.py script:

```sh
python testPrompts.py
python vision_testPrompts.py
```

### Export PPs and PEs from the JSON File

To export and count the PPs and PEs from the `promptpatterns.json` JSON file, use the `exportPromptPatternsJSONfile.py` script.
Below are some example usages:

1. **Print the PPs and PEs to the console:**
This will print the PPs and PEs to the console in a formatted way.

```sh
python exportPromptPatternsJSONfile.py --format console
``` 

2. **Write the PPs and PEs to an HTML file with the default filename `promptpatterns.html`:**

This will write the PPs and PEs to an HTML file called `promptpatterns.html` in the same directory as the script.

```sh
python exportPromptPatternsJSONfile.py --format html
```

3. **Write the PPs and PEs to an HTML file with a custom filename:**
This will write the PPs and PEs to an HTML file called `mypromptpatterns.html` in the same directory as the script.

```sh
python exportPromptPatternsJSONfile.py --format html --filename mypromptpatterns.html
```

4. **Include the current date in the filename of the HTML file:**
This will write the PPs and PEs to an HTML file with a filename that includes the current date in the format `promptpatterns_YYYYmmdd.html`.

```sh
python exportPromptPatternsJSONfile.py --format html --filename promptpatterns_{date}.html
```

5. **Count the number of Titles, PatternCategory, and pattern name:**

This will count the number of Titles, PatternCategory, and pattern name and output it to the console.

```sh
python exportPromptPatternsJSONfile.py --count
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements, research paper additions or bug fixes.

For ethical / dual‑use concerns use the "Responsible Use Report" issue template. For AI-enriched metadata corrections use the "AI-Assisted Field Correction" template.

Security vulnerabilities should follow the coordinated disclosure process in `SECURITY.md` (private advisory or email) rather than a public issue.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Security Policy

See `prompt-pattern-dictionary/SECURITY.md` for supported versions and coordinated disclosure steps. Avoid including sensitive exploit payloads or personal data in reports.

## Responsible Use Guidelines

A standalone page at `/responsible-use` in the web app and the Orientation "Accessibility & Responsible Use" section document:

- Core principles: transparency, defensive focus, privacy, inclusivity.
- Acceptable uses: research, defensive tooling, education, evaluation with non-sensitive data.
- Prohibited uses: real exploit/malware generation, phishing deployment, guardrail bypass attempts.
- Safeguards: provenance badges, planned caution indicators, issue templates, minimal telemetry (opt-in, excludes prompt content).

Report ethical concerns with the issue label `responsible-use-review`; corrections to AI-assisted fields with `ai-assist-correction`.

---

## Chapter 6 Evaluation (CLI)

The Chapter 6 thesis evaluation workflow now lives under `evaluation/`.

Primary CLI:

```powershell
python .\evaluation\chapter6_evaluation.py doctor
python .\evaluation\chapter6_evaluation.py run-quantitative
python .\evaluation\chapter6_evaluation.py run-cybersecurity
python .\evaluation\chapter6_evaluation.py summarize
python .\evaluation\chapter6_evaluation.py run-all
```

What it does:

- Runs the quantitative LLM-as-Judge workflow for the 18 Chapter 6 prompt patterns.
- Runs the 3 qualitative cybersecurity case studies.
- Writes raw artifacts under `evaluation/results/` and aggregate outputs under `evaluation/summary/`.

Default model setup in the CLI:

- Quantitative evaluation models: `gpt-4o`, `gpt-5`, `o4-mini`, `deepseek-r1-0528`
- Judge model: `gpt-5.4-pro`
- Qualitative cybersecurity model: `gpt-5`

Auth behavior:

- Default is `--auth-mode auto`, which prefers an API key when one is present in `.env`, otherwise it falls back to Microsoft Entra ID via `DefaultAzureCredential`.
- GPT-family requests use the Responses API.
- The DeepSeek deployment uses chat completions by default.

Useful options:

```powershell
python .\evaluation\chapter6_evaluation.py doctor --probe
python .\evaluation\chapter6_evaluation.py run-quantitative --models gpt-4o,gpt-5,o4-mini,deepseek-r1-0528
python .\evaluation\chapter6_evaluation.py run-cybersecurity --cyber-model gpt-5
python .\evaluation\chapter6_evaluation.py run-all --auth-mode entra
```

Generated artifacts inside `evaluation/` are ignored by a local `evaluation/.gitignore` so the raw results do not pollute the main repo status by default.

---

## Prompt Pattern Dictionary (Web App)

The `prompt-pattern-dictionary/` subfolder contains a Next.js application and a data pipeline to build a searchable dictionary of prompt patterns.

Key build notes:
- Data pipeline script: `prompt-pattern-dictionary/scripts/build-data.js`
- Python steps (embeddings, categorization, enrichment) auto-detect and prefer `uv run` when available. To force uv on Windows PowerShell:

```powershell
$env:USE_UV = "1"
node .\prompt-pattern-dictionary\scripts\build-data.js --enrich --enrich-limit 10 --enrich-fields template
```

- Enrichment flags:
  - `--enrich` to enable optional enrichment via Azure OpenAI (GPT-5)
  - `--enrich-limit <n>` to cap items processed
  - `--enrich-fields <csv>` to scope fields: `template,application,dependentLLM,turn`

- GPT-5 temperature behavior: The enrichment pipeline does not set `temperature` for GPT-5 (Azure requires default temperature). The client also retries without `temperature` if the service rejects the parameter.

### Build and Run (Windows PowerShell)

Run these from the repository root unless noted.

1) Install dependencies for the web app:

```powershell
cd .\prompt-pattern-dictionary
npm install
```

2) Build data (required before first run and whenever source JSON changes):

```powershell
# Optional: prefer uv for any Python steps in the pipeline
$env:USE_UV = "1"
node .\scripts\build-data.js
```

3) Start in development mode:

```powershell
npm run dev
# Open http://localhost:3000
```

4) Build for production and start the server:

```powershell
npm run build
npm start
# Open http://localhost:3000
```

Notes:
- The `npm run build` script runs the full pipeline: data transform, normalized schema, semantic categories, and `next build`.
- Use `npm run export` if you want a static export (files in `prompt-pattern-dictionary/out`).

### Known issue: OneDrive/OneNote locking `.next` folder

If the repo is inside a OneDrive-synced directory (including OneNote notebooks), the `.next` build folder may be locked or partially synced, causing build or dev server errors (e.g., EBUSY/EPERM on Windows).

Workarounds:
- Exclude the project (or at least the `.next` folder) from OneDrive sync.
- Move the project outside OneDrive-synced paths (recommended for Next.js development).
- If a lock occurs, close OneNote/OneDrive temporarily, delete `.next`, and re-run `npm run dev` or `npm run build`.

### Orientation Architecture

The Orientation content (how to use the dictionary) was refactored from a single long page into a hybrid, multi-page structure:

- Hub: `/orientation` – overview cards linking to each section plus links to “All Sections” and the Cheat Sheet.
- Per-section routes: `/orientation/{slug}` – focused pages (quick-start, what-is-a-pattern, pattern-anatomy, lifecycle, choosing-patterns, combining-patterns, adaptation, anti-patterns, quality-evaluation, accessibility-responsible-use, glossary, faq, feedback, next-steps).
- Consolidated legacy view: `/orientation/all` – full scrollable content (retains original anchors for deep link continuity).
- Printable / rapid reference: `/orientation/cheatsheet` – condensed key constructs and workflows.

Sections are metadata-driven via `ORIENTATION_SECTIONS` (number, slug, title, component). Navigation components (sidebar + inline chip set) render from this single source of truth; the pager component wires previous/next traversal.

### Readability & Theming Controls

User-adjustable preferences enhance accessibility and reading comfort:

- Font scale: data attribute `data-font-scale` applied to `<html>` with supported values -1, 0, 1, 2 (base, + steps). CSS scales body text and headings accordingly.
- Width mode: `data-width-mode` = `default` | `relaxed`; relaxed widens prose up to ~85ch for users needing fewer line wraps.
- Theme / contrast: `data-theme` = `light` | `dark` | `high-contrast` with a `system` option that removes the attribute and defers to `prefers-color-scheme` media queries. (The legacy value `hc` is auto-migrated if found in saved preferences.) See `prompt-pattern-dictionary/docs/THEMING.md` for full token architecture.
- Persistence: Stored under localStorage key `orientation:readability:v1`; hydration script replays settings and applies attributes with minimal layout shift.
- UI: `ReadabilityControls` component (toolbar) with buttons for font scaling, width toggle, and a select for theme mode. Appears in orientation layout (sidebar desktop + inline mobile). Can be reused site‑wide later.

### Legacy Anchor Redirect Behavior

A lightweight client component (`LegacyHashRedirect`) preserves backward compatibility for old single-page anchors:

1. On mount, it inspects `window.location.hash`.
2. If the hash matches a known section slug and you are not already on that route, it `router.replace()` to `/orientation/{slug}`.
3. If the hash does not match a known slug and you are not on `/orientation/all`, it redirects to `/orientation/all#hash`, ensuring deep links to sub‑headings still land meaningfully.
4. If already on `/orientation/all`, no action is taken.

This maintains existing external links and bookmarks without server‑side redirects. A future enhancement may introduce explicit server (or Next.js middleware) 301 mappings for improved SEO signals—tracked as a backlog item.

### Extending the Preference System

To add a new user preference:

1. Extend the `usePreferences` hook (under `prompt-pattern-dictionary/src/app/orientation/hooks/`) with state, localStorage serialization, and dataset syncing.
2. Choose a descriptive `data-*` attribute name; keep attribute count minimal (prefer reusing existing tokens vs. additive bespoke classes).
3. Update the `ReadabilityControls` UI (or create a new modular control) with accessible semantics (button labels, `aria-pressed`, or form elements as appropriate).
4. Document the accepted values and rationale in this README (and optionally in a dedicated `docs/ACCESSIBILITY.md` or `docs/PREFERENCES.md`).
5. Add non-destructive CSS tied to the attribute in `globals.css` guarded by clear comments.

Guardrails:
- Avoid preferences that require layout reflow more than once per interaction.
- Provide reversible changes (toggle or reset option) if adding multi-step controls.
- Maintain WCAG contrast compliance across all themes and states.

---
