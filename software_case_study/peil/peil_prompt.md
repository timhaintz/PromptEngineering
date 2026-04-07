# PEIL-Structured Prompt - extractTextFromPDF.py Refactoring

## Exact Prompt Used

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

## PEIL Components Mapping

| PEIL Variable | Content |
|---------------|---------|
| **Role** | Senior Python developer, refactoring and clean architecture specialist, Azure OpenAI experience |
| **ProvideClearContext** | 28-month production script, model migrations, thesis research tool, backward compatibility requirement |
| **BreakDownComplexQuestions** | 9 numbered sub-tasks covering separation of concerns, config, types, logging, errors, validation, extraction, paths, CLI compat |
| **ProvideSpecificInstructions** | Specific exception types named, specific CLI flags listed, specific modules required (logging, pathlib, dataclass) |
| **DefineConciseness** | Inline comments only where non-obvious; numbered summary after code |
| **PromptingTechniques** | Structured Chain-of-Thought (SCoT) - recommended for code generation per TECHNIQUES.md |
| **StateDesiredOutput** | Complete refactored Python file with post-code change summary |

## Category

**Refactoring** - Modifying the input without changing its meaning. From CATEGORIES.md: "Modifying the input prompt without changing its meaning. This can include rephrasing, rearranging, or simplifying the prompt to improve clarity and effectiveness."

## Technique

**Structured Chain-of-Thought (SCoT)** - From TECHNIQUES.md: "Incorporate program structures into reasoning steps for code generation." Selected because the task is code refactoring, and SCoT is the recommended technique for code generation tasks.

## Model

Claude Opus 4.6 (via GitHub Copilot in VS Code)

## Claude-Specific Adaptations (from TECHNIQUES.md Model-Specific Guidance)

- Clear and direct instructions (no ambiguity in the 9 sub-tasks)
- Explicit role setting (opening sentence)
- Structured sections matching the hybrid prompt format (arXiv:2503.06926)

## Summary of Changes Made

### Structural Changes (Separation of Concerns)
1. **Configuration dataclass**: `AzureOpenAIConfig` with `from_env()` classmethod that validates all required environment variables at startup and fails fast with a clear error message
2. **PDF extraction isolated**: `extract_text_from_pdf()` returns a `PageText` dataclass instead of raw dicts
3. **Text escaping extracted**: `_escape_text()` with a documented `_ESCAPE_TABLE` constant
4. **Page filtering isolated**: `filter_pages()` as a standalone pure function
5. **Message construction isolated**: `build_messages()` and `build_messages_for_mode()` separated
6. **Response parsing isolated**: `parse_response()` handles both `json` and ` ```json ``` ` fenced code blocks
7. **File output isolated**: `save_response()` using `pathlib.Path`, creates directories, uses UTF-8 encoding
8. **Mode resolution isolated**: `resolve_mode()` with fail-fast if no mode specified
9. **CLI definition isolated**: `build_arg_parser()` returns a configured parser
10. **Main pipeline**: `main()` orchestrates the above in a clear linear flow

### Type Safety
11. **Type hints on every function** signature and return type
12. **`from __future__ import annotations`** for forward reference support
13. **`PageText` dataclass** replaces anonymous dicts for page data
14. **`AzureOpenAIConfig` dataclass** replaces module-level variables

### Error Handling
15. **Specific API exceptions**: Catches `APIError`, `APIConnectionError`, `RateLimitError` from the openai SDK
16. **Environment variable validation**: Missing vars produce a clear log message and `sys.exit(1)` before any processing begins
17. **Empty page set guard**: Logs a warning and returns early if filtering removes all pages

### Observability
18. **`logging` module** replaces all `print()` calls (except `printtoscreen` which is intentional user output)
19. **Structured log format** with timestamp and level

### Code Quality
20. **Mode constants**: `MODE_EXTRACT`, `MODE_SUMMARY`, etc. replace magic strings
21. **`ensure_ascii=False`** on JSON output to preserve Unicode characters
22. **UTF-8 encoding** specified explicitly on file writes
23. **Client created once** outside the page-set loop
24. **`iso_datetime` generated at runtime** inside `main()`, not at import time
25. **Unused imports removed**: `sys` (repurposed for exit), `time`, `re`, `openai` (base module), duplicate `json`
26. **Prompt templates** use parenthesised string concatenation for readability

### Backward Compatibility
27. **All 8 CLI flags preserved** with identical names and types
28. **Output file naming convention unchanged**: `{timestamp}_{stem}_{mode}_{pagerange}.json`
29. **Output directory structure unchanged**: `extractedPromptPatternsFromPDF/{filename}/`
30. **Prompt text content unchanged** (including the few-shot examples)

## What the Naive Prompt Missed That PEIL Caught

| Issue | Naive | PEIL |
|-------|-------|------|
| Type hints on all functions | Not added | Full coverage |
| Configuration validation | Not added | `AzureOpenAIConfig.from_env()` with fail-fast |
| Logging module | Not used | `logging.basicConfig()` with structured format |
| Specific exception types | Broad `Exception` | `APIError`, `APIConnectionError`, `RateLimitError` |
| Text escaping extraction | Left inline | `_escape_text()` with `_ESCAPE_TABLE` |
| pathlib.Path usage | `os.path.join` only | `Path` for output directory and file operations |
| PageText dataclass | Raw dicts | `PageText(page_number, text)` |
| Mode constants | Magic strings throughout | `MODE_EXTRACT`, `MODE_SUMMARY`, etc. |
| UTF-8 encoding on writes | Not specified | `encoding="utf-8"` |
| Empty page guard | No check | Early return with warning log |
| Docstrings on new functions | None added | Docstrings on all extracted functions |
| `from __future__ import annotations` | Not added | Added for forward references |

## Lines of Code

- Original: 374 lines
- PEIL refactored: ~430 lines (more code, but each unit is smaller and independently testable)

## Time Context

Single-pass refactoring with structured reasoning through each concern area top-to-bottom.
