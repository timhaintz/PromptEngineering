# Naive Prompt - extractTextFromPDF.py Refactoring

## Exact Prompt Used

```
Refactor this Python file to improve code quality.
```

No role, no context, no constraints, no output specification. The file contents were the only input.

## Model

Claude Opus 4.6 (via GitHub Copilot in VS Code)

## Summary of Changes Made

### Structural Changes
1. **Moved module docstring**: Replaced the multi-line comment block with a proper Python docstring
2. **Removed unused imports**: Dropped `sys`, `time`, `re`, `openai`, and duplicate `json` import
3. **Renamed constants to UPPER_CASE**: `model` to `MODEL`, `api_key` to `API_KEY`, etc.
4. **Removed commented-out legacy code**: Cleaned up old `openai.api_type` / `openai.api_base` lines
5. **Renamed prompt dictionaries**: `system_prompt` to `SYSTEM_PROMPTS`, `user_prompt` to `USER_PROMPTS`, etc.
6. **Extracted `main()` function**: Moved the `if __name__` block body into a `main()` function
7. **Extracted helper functions**: `build_messages()`, `parse_response()`, `save_output()`, `get_page_range()`
8. **Moved `AzureOpenAI` client creation** outside the loop (created once instead of per-iteration)
9. **Moved `iso_datetime`** inside `main()` so it is generated at runtime rather than import time

### What It Did Well
- Removed genuinely unused imports
- Created a cleaner entry point with `main()`
- Broke up the monolithic `__main__` block into smaller functions
- Moved the client instantiation out of the loop (performance fix)
- Fixed the `iso_datetime` being set at import time

### What It Missed
- No type hints added to any function signatures
- No dataclass or configuration object for settings
- No `logging` module (still uses bare `print()`)
- No specific exception handling (still catches broad `Exception`)
- The text escaping block was left inline without extraction or explanation
- No `Path` usage (still uses `os.path.join` throughout)
- No docstrings on any of the new functions (only the module-level one)
- No validation of required environment variables (will fail with `None` values silently)
- The argparse `type=bool` issue was not fixed (passing `-extractexamples False` still evaluates as `True`)
- No separation of prompt templates from code logic
- The few-shot prompt content was left with the typo "Concatendation"
- No `__future__` annotations import

## Lines of Code

- Original: 374 lines
- Naive refactored: ~270 lines

## Time Context

Single-pass refactoring with no iterative refinement.
