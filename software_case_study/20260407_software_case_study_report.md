# Software Engineering Case Study Report

## Generated: 2026-04-07

## Overview

This report documents a software engineering case study comparing naive versus PEIL-structured prompting for a real-world code refactoring task. The study was conducted as part of Chapter 6 of a Masters thesis on prompt engineering. The target file was `extractTextFromPDF.py`, a production script maintained for 28 months across multiple Azure OpenAI model migrations (GPT-3.5 through GPT-5).

## Study Design

### Purpose

Demonstrate that PEIL produces measurably better results than unstructured prompting on a real-world software engineering task, complementing the cybersecurity and multimodal case studies already in Chapter 6.

### Models

| Role | Model | Platform |
|------|-------|----------|
| Refactoring (both runs) | Claude Opus 4.6 | GitHub Copilot in VS Code |
| Judge | GPT-5.4 | GitHub Copilot in VS Code |

### Metrics

Same 4 dimensions as the quantitative evaluation (1-5 scale each):

- **Accuracy**: Does the refactored code correctly preserve functionality?
- **Formatting**: Is the code well-structured, readable, and consistently styled?
- **Fabrication**: Does the output avoid inventing non-existent APIs or libraries?
- **Completeness**: Does the refactoring address all relevant code quality issues?

### Target File

`extractTextFromPDF.py` (338 lines, created 20 August 2023)

The script opens research paper PDFs, extracts text page-by-page, constructs structured prompts for Azure OpenAI, and saves categorised JSON responses. It supports four extraction modes (prompt pattern extraction, summarisation, keypoint extraction, free-form questions) with optional few-shot prompting.

### Why This File

- One of the oldest scripts in the repository (approximately 3 years old at the time of this study)
- Evolved through multiple model migrations (GPT-3.5, GPT-4, GPT-4.1, GPT-5)
- A real production script used in the thesis research methodology
- Complex enough to benefit from structured refactoring guidance
- Ties directly to the "Recursive Self-Validation" narrative in Chapter 7 (using prompt engineering techniques to improve the prompt engineering research tooling)

---

## Prompts Used

### Naive Prompt

```
Refactor this Python file to improve code quality.
```

No role. No context. No constraints. No output specification. The file contents were the only input.

### PEIL-Structured Prompt

```
Role: You are a senior Python developer specialising in code refactoring and clean architecture, with
deep experience in Azure OpenAI SDK integrations and CLI tooling.

Context: This is a production script that extracts prompt patterns and examples from research PDFs
using Azure OpenAI. It has been actively maintained for 28 months across multiple model migrations
(GPT-3.5 through GPT-5). The codebase follows Python best practices (PEP 8, type hints, virtual
environments with venv). Environment variables manage all Azure credentials and endpoints. The
script is a core part of a Masters thesis research methodology and must remain backward-compatible
with existing CLI invocations.

Instructions:
1. Identify and separate concerns: PDF text extraction, prompt construction, API interaction,
   response parsing, and file output should each be isolated
2. Extract hardcoded values (temperature, pages_per_set, output directory) into a configuration
   dataclass with environment-variable loading and validation
3. Add type hints to all function signatures and return types
4. Replace bare print() calls with the logging module
5. Improve error handling: catch specific Azure OpenAI exceptions (APIError, APIConnectionError,
   RateLimitError) instead of broad Exception
6. Validate that required environment variables are present at startup and fail fast with a clear
   message if any are missing
7. Extract the text-escaping logic into a named function with a documented escape table
8. Use pathlib.Path for file system operations where it improves clarity
9. Maintain full backward compatibility with all existing CLI arguments (-filename, -pages,
   -extractexamples, -use_few_shot, -summary, -keypoints, -prompt, -printtoscreen)

Techniques: Use Structured Chain-of-Thought (SCoT). For each refactoring decision, incorporate the
program structure into the reasoning: identify the code smell, state the structural improvement,
then implement. Work through the file top-to-bottom: imports, configuration, data structures,
extraction logic, API interaction, CLI, main pipeline.

Output: Produce the complete refactored Python file. Use inline comments only where a refactoring
decision is non-obvious. After the code, provide a numbered summary of every change made and why.
```

### PEIL Components Mapping

| PEIL Variable | What Was Provided |
|---------------|-------------------|
| **Role** | Senior Python developer, refactoring and clean architecture specialist, Azure OpenAI SDK experience |
| **ProvideClearContext** | 28-month production script, model migrations, thesis research tool, backward compatibility requirement |
| **BreakDownComplexQuestions** | 9 numbered sub-tasks covering separation of concerns, config, types, logging, errors, validation, extraction, paths, CLI compatibility |
| **ProvideSpecificInstructions** | Specific exception types named, specific CLI flags listed, specific modules required (logging, pathlib, dataclass) |
| **DefineConciseness** | Inline comments only where non-obvious; numbered summary after code |
| **PromptingTechniques** | Structured Chain-of-Thought (SCoT), recommended for code generation per TECHNIQUES.md |
| **StateDesiredOutput** | Complete refactored Python file with post-code change summary |

### PEIL Category

**Refactoring**: Modifying the input without changing its meaning. From the PEIL CATEGORIES.md definition: "Modifying the input prompt without changing its meaning. This can include rephrasing, rearranging, or simplifying the prompt to improve clarity and effectiveness."

### PEIL Technique

**Structured Chain-of-Thought (SCoT)**: From TECHNIQUES.md: "Incorporate program structures into reasoning steps for code generation." Selected because the task is code refactoring, and SCoT is the recommended technique for code generation tasks per the PEIL technique selection guide.

### Claude-Specific Adaptations

Per the TECHNIQUES.md model-specific guidance table for Claude:

- Clear and direct instructions (no ambiguity in the 9 sub-tasks)
- Explicit role setting (opening sentence)
- Structured sections matching the hybrid prompt format (arXiv:2503.06926)

---

## Judge Scores

### Score Table

| Metric | Naive (1-5) | PEIL (1-5) | Delta |
|--------|:-----------:|:----------:|:-----:|
| Accuracy | 4 | 4 | 0 |
| Formatting | 3 | 5 | +2 |
| Fabrication | 5 | 5 | 0 |
| Completeness | 2 | 4 | +2 |
| **Total** | **14** | **18** | **+4** |

### Score Justifications

#### Accuracy (Naive 4, PEIL 4)

Both refactors compile successfully (`py_compile` passed for both files). Both preserve the core workflow: PDF extraction, prompt construction, Azure OpenAI API call, response parsing, and JSON file output. Both CLIs render valid help output with all 8 original flags preserved.

Neither version was tested end-to-end against a live Azure OpenAI endpoint during this study, which prevents a score of 5 for either.

One notable difference: the PEIL version changes the CLI contract slightly by making `-filename` explicitly `required=True` in the argument parser. The original left it as optional (defaulting to `None`), which would cause a runtime error later when `fitz.open(None)` was called. The PEIL version fails earlier and more clearly. This is arguably an improvement, but it is a behavioral change.

#### Formatting (Naive 3, PEIL 5)

The VS Code editor diagnostics provided the most objective evidence here.

**Naive version**: 173 diagnostic issues reported, including:
- 45+ lines exceeding 79-character PEP 8 limit
- Multiple trailing whitespace and blank-line-with-whitespace violations
- Missing type annotations on all function signatures
- Unknown parameter types flagged by the type checker
- No docstrings on any of the newly extracted helper functions

**PEIL version**: 0 diagnostic issues reported. Clean pass across all checks.

The PEIL version uses consistent section separators (`# -----`), proper docstrings on every function, type hints throughout, and structured imports with `from __future__ import annotations`.

#### Fabrication (Naive 5, PEIL 5)

Neither version invents non-existent libraries, APIs, or features.

The PEIL version imports `APIError`, `APIConnectionError`, and `RateLimitError` from the `openai` package. These were verified at runtime:

```
python -c "from openai import AzureOpenAI, APIError, APIConnectionError, RateLimitError; print('ok')"
# Output: ok
```

Both versions correctly use `fitz` (PyMuPDF), `AzureOpenAI`, `argparse`, `json`, `pathlib`, and other standard libraries.

#### Completeness (Naive 2, PEIL 4)

This is where the largest gap appears. The naive refactor performs surface-level cleanup. The PEIL refactor performs a structural architectural improvement.

The PEIL version does not receive a 5 because:
- It preserves the original `type=bool` argument parser pattern, which has a known Python issue (passing `-extractexamples False` still evaluates as `True` because `bool("False")` is `True`)
- It does not move all hardcoded operational values into environment-backed configuration
- It preserves the original text-escaping approach without questioning whether the escaping is still necessary

---

## Detailed Change Comparison

### Diff Statistics (vs Original)

| Metric | Naive | PEIL |
|--------|------:|-----:|
| Lines in original | 338 | 338 |
| Lines in refactored | 285 | 486 |
| Insertions | 123 | 541 |
| Deletions | 171 | 350 |
| Net line change | -53 | +148 |

### Changes Made by Naive Prompt

| # | Change | Category |
|---|--------|----------|
| 1 | Replaced multi-line comment block with proper Python docstring | Style |
| 2 | Removed unused imports (`sys`, `time`, `re`, `openai`, duplicate `json`) | Cleanup |
| 3 | Renamed module-level variables to UPPER_CASE (`model` to `MODEL`, etc.) | Convention |
| 4 | Removed commented-out legacy code (`openai.api_type`, `openai.api_base`) | Cleanup |
| 5 | Renamed prompt dictionaries (`system_prompt` to `SYSTEM_PROMPTS`, etc.) | Convention |
| 6 | Extracted `main()` function from `if __name__` block | Structure |
| 7 | Extracted `build_messages()` helper function | Structure |
| 8 | Extracted `parse_response()` helper function | Structure |
| 9 | Extracted `save_output()` helper function | Structure |
| 10 | Extracted `get_page_range()` helper function | Structure |
| 11 | Moved `AzureOpenAI` client creation outside the loop | Performance |
| 12 | Moved `iso_datetime` inside `main()` (runtime vs import time) | Correctness |

**Total: 12 changes across 4 categories (Style, Cleanup, Convention, Structure/Performance)**

### Changes Made by PEIL Prompt

| # | Change | Category |
|---|--------|----------|
| 1 | `AzureOpenAIConfig` frozen dataclass with `from_env()` classmethod | Architecture |
| 2 | Environment variable validation with fail-fast and clear error message | Robustness |
| 3 | `PageText` dataclass replacing anonymous dicts | Type Safety |
| 4 | `_escape_text()` function with documented `_ESCAPE_TABLE` constant | Separation of Concerns |
| 5 | `extract_text_from_pdf()` returns typed `PageText` list | Type Safety |
| 6 | `filter_pages()` as standalone pure function | Separation of Concerns |
| 7 | `build_messages()` with keyword-only arguments for few-shot params | API Design |
| 8 | `build_messages_for_mode()` as mode-dispatch wrapper | Separation of Concerns |
| 9 | `parse_response()` handles both `json` and fenced code blocks | Robustness |
| 10 | `save_response()` using `pathlib.Path` with UTF-8 encoding | Modernisation |
| 11 | `resolve_mode()` with fail-fast if no mode specified | Robustness |
| 12 | `build_arg_parser()` returns configured parser | Separation of Concerns |
| 13 | `main()` as clean linear pipeline orchestrator | Architecture |
| 14 | Type hints on every function signature and return type | Type Safety |
| 15 | `from __future__ import annotations` for forward references | Type Safety |
| 16 | `logging` module replacing all `print()` calls | Observability |
| 17 | Structured log format with timestamp and level | Observability |
| 18 | Specific API exceptions (`APIError`, `APIConnectionError`, `RateLimitError`) | Error Handling |
| 19 | Empty page set guard with warning log | Robustness |
| 20 | Mode constants (`MODE_EXTRACT`, `MODE_SUMMARY`, etc.) | Maintainability |
| 21 | `ensure_ascii=False` on JSON output | Correctness |
| 22 | UTF-8 encoding specified on file writes | Correctness |
| 23 | Client created once outside loop | Performance |
| 24 | `iso_datetime` generated at runtime inside `main()` | Correctness |
| 25 | Unused imports removed and repurposed (`sys` for exit) | Cleanup |
| 26 | Prompt templates use parenthesised string concatenation | Readability |
| 27 | All 8 CLI flags preserved with identical names | Backward Compatibility |
| 28 | Output file naming convention unchanged | Backward Compatibility |
| 29 | Output directory structure unchanged | Backward Compatibility |
| 30 | Prompt text content unchanged (including few-shot examples) | Backward Compatibility |

**Total: 30 changes across 10 categories (Architecture, Robustness, Type Safety, Separation of Concerns, API Design, Modernisation, Observability, Error Handling, Maintainability, Backward Compatibility)**

---

## Issues Identified Only by PEIL

The following table lists issues that the PEIL-structured prompt identified and addressed but the naive prompt did not.

| Issue | Naive | PEIL |
|-------|-------|------|
| Type hints on all functions | Not added | Full coverage on every signature and return type |
| Configuration validation | Not added | `AzureOpenAIConfig.from_env()` with fail-fast |
| Logging module | Not used; bare `print()` throughout | `logging.basicConfig()` with structured format |
| Specific exception types | Broad `Exception` catch | `APIError`, `APIConnectionError`, `RateLimitError` |
| Text escaping extraction | Left inline in extraction function | `_escape_text()` with documented `_ESCAPE_TABLE` |
| `pathlib.Path` usage | `os.path.join` only | `Path` for output directory and file operations |
| Typed data structures | Raw dicts for page data | `PageText(page_number, text)` dataclass |
| Mode constants | Magic strings throughout | `MODE_EXTRACT`, `MODE_SUMMARY`, etc. |
| UTF-8 encoding on writes | Not specified | `encoding="utf-8"` explicit |
| Empty page guard | No check | Early return with warning log |
| Docstrings on new functions | None added | Docstrings on all extracted functions |
| `from __future__ import annotations` | Not added | Added for forward references |
| Mode resolution with fail-fast | No mode validation | `resolve_mode()` exits with clear message |
| CLI `-filename` as required | Left optional (fails later at runtime) | Marked `required=True` (fails immediately with clear message) |

---

## Static Analysis Evidence

### VS Code Editor Diagnostics

| File | Issues Reported |
|------|----------------:|
| Original `extractTextFromPDF.py` | Not measured (baseline) |
| `naive_extractTextFromPDF.py` | 173 |
| `peil_extractTextFromPDF.py` | 0 |

The 173 issues in the naive version included:
- PEP 8 line length violations (45+ lines over 79 characters)
- Trailing whitespace violations
- Blank lines containing whitespace
- Missing type annotations on all function parameters
- Unknown parameter types flagged by the type checker
- Stub file warnings for the `fitz` module (also present in original)

### Python Compilation

Both files passed `py_compile` with no errors.

### Runtime Import Verification

The PEIL version's specific OpenAI exception imports were verified:

```
from openai import AzureOpenAI, APIError, APIConnectionError, RateLimitError
# Result: Success
```

### CLI Help Output

Both versions produce valid CLI help. The PEIL version additionally:
- Includes a program description ("Extract text from a PDF and process it with Azure OpenAI")
- Uses shorter, cleaner help strings
- Marks `-filename` as required

---

## Observations and Analysis

### The naive prompt produced a "good enough" cleanup

The naive refactoring is competent. It removed dead code, normalised naming conventions, extracted helper functions, and created a proper `main()` entry point. A developer receiving this output would have a cleaner codebase. However, the improvements are shallow. Every change falls into one of four categories: style, cleanup, convention, or basic structure. No new abstractions were introduced, no type safety was added, and no error handling was improved.

### The PEIL prompt produced an architectural refactor

The PEIL refactoring goes deeper. It introduces new abstractions (`AzureOpenAIConfig`, `PageText`), adds defensive coding practices (environment validation, specific exception handling, empty-input guards), modernises the codebase (logging, pathlib, type hints), and maintains backward compatibility as an explicit constraint. The changes span 10 categories versus 4.

### PEIL's specificity drove deeper analysis

The naive prompt gives the model freedom to decide what "improve code quality" means. The model chose the lowest-cost improvements: cleanup and reorganisation. The PEIL prompt explicitly named 9 sub-tasks, each targeting a specific code quality dimension. This forced the model to address concerns it would otherwise skip.

### The technique choice mattered

The PEIL prompt specified Structured Chain-of-Thought (SCoT), which instructs the model to work through the program structure systematically. This produced a top-to-bottom refactoring that addressed imports, configuration, data structures, extraction logic, API interaction, CLI, and main pipeline in order. The naive refactoring jumped between concerns less methodically.

### Both versions preserved the known `type=bool` bug

Neither version fixed the `argparse` `type=bool` issue. In Python, `parser.add_argument('-flag', type=bool)` means that passing `-flag False` on the command line calls `bool("False")`, which returns `True`. The correct fix is `action='store_true'`. This was present in the original and carried through by both refactors. The PEIL prompt's instructions did not specifically call out argparse patterns, so the model preserved what was there.

### PEIL added approximately 148 net lines

The PEIL version is longer (486 lines vs 338 original vs 285 naive). This is not bloat. Each new function is small, focused, and independently testable. The configuration dataclass, mode resolver, and argument parser builder each add lines but reduce cognitive load in the main pipeline. The naive version reduced lines by 53, primarily through dead code removal.

### One backward compatibility nuance

The PEIL version makes `-filename` a required argument (`required=True`). The original did not mark it as required, but it would crash at runtime without it (when `fitz.open(None)` was called). The PEIL change surfaces this failure earlier and with a clearer message. This is arguably an improvement, but it is a contract change that should be noted.

---

## Files Produced

```
software_case_study/
    extractTextFromPDF.py              # Original file (untouched copy, 338 lines)
    naive/
        naive_extractTextFromPDF.py    # Naive refactored output (285 lines)
        naive_prompt.md                # Exact prompt, changes, observations
    peil/
        peil_extractTextFromPDF.py     # PEIL refactored output (486 lines)
        peil_prompt.md                 # Exact prompt, PEIL mapping, changes, comparison
```

---

## Summary for Chapter 6 Write-Up

The naive prompt ("Refactor this Python file to improve code quality") produced 12 surface-level improvements: dead code removal, naming conventions, basic function extraction. It scored 14/20 on the four-metric judge evaluation.

The PEIL-structured prompt produced 30 improvements across 10 categories: architecture, type safety, error handling, observability, robustness, and backward compatibility. It scored 18/20, with the largest gains on Formatting (+2) and Completeness (+2).

The PEIL version passed static analysis with 0 editor diagnostics versus 173 for the naive version. Both compiled and both preserved CLI compatibility.

The key variable was prompt structure, not model choice. Both runs used the same model (Claude Opus 4.6 via GitHub Copilot) on the same file. The PEIL prompt's explicit Role, Context, Instructions, Techniques, and Output sections drove the model to address concerns the naive prompt left untouched.

This result aligns with the quantitative evaluation finding that PEIL is most effective for structured output tasks (template filling +0.69, expert assessment +0.50, code generation +0.38). Code refactoring is inherently a structured task with multiple interdependent concerns, and the PEIL prompt's decomposition into 9 sub-tasks mapped directly to those concerns.
