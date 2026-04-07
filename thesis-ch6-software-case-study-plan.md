# Chapter 6 Software Domain Case Study Plan

## Purpose

This case study demonstrates PEIL's value for a real-world software engineering task. It complements the cybersecurity case studies (threat intel, secure code, incident reports) and the multimodal case study (vision-based categorisation) already in Chapter 6. The professor specifically requested a software domain example with a real-world coding task.

## Why This Matters for the Thesis

- Demonstrates PEIL works beyond cybersecurity (domain agnosticism)
- Uses GitHub Copilot as the test platform
- Creates an authentic, reproducible example with real code
- Ties to the Refactoring category in Out Logic and the recursive self-validation point in Ch7

## Models

- **Refactoring model:** Claude Opus 4.6 (via GitHub Copilot in VS Code)
- **Judge model:** GPT-5.4 (via GitHub Copilot in VS Code)
- **Metrics:** Same 4 dimensions as quantitative evaluation (Accuracy 1-5, Formatting 1-5, Fabrication 1-5, Completeness 1-5)

This mirrors the cybersecurity case studies (single model for generation, qualitative comparison). The key variable is prompt structure, not model choice. Model agnosticism is already covered in the quantitative evaluation (4 models, 648 responses).

## The Task: Refactor `extractTextFromPDF.py`

### Why this file?

- It's one of the oldest scripts in the repo (3 years old, from the project's start)
- It has evolved through multiple model migrations (GPT-3.5 through GPT-5)
- It's a real production script used in the thesis research methodology
- It's complex enough to benefit from structured refactoring guidance
- The refactoring ties directly to the "Recursive Self-Validation" narrative in Ch7 (using prompt engineering techniques to improve the prompt engineering research tooling)

### Current state of `extractTextFromPDF.py`

- Uses Azure OpenAI to extract PPs and PEs from research paper PDFs
- Has grown organically over 28 months with accumulated technical debt
- The system prompt has gone through 10+ iterations (documented in Ch7)
- Likely has: long functions, mixed concerns, hardcoded values, inconsistent error handling

## Execution Plan

### Step 1: Naive Prompt (Claude Opus 4.6 via GitHub Copilot)

Open `extractTextFromPDF.py` in VS Code. Use GitHub Copilot with a naive prompt:

**Naive prompt:**
"Refactor this Python file to improve code quality."

Record:
- The exact prompt used
- The full output/suggestions from Copilot
- What was changed, what was missed
- Time taken

### Step 2: PEIL-Structured Prompt (Claude Opus 4.6 via GitHub Copilot)

Use the same file (revert any Step 1 changes first) with a PEIL-structured prompt:

**PEIL prompt (example structure):**
- **Role:** Senior Python developer specialising in code refactoring and clean architecture
- **Context:** This is a production script that extracts prompt patterns from research PDFs using Azure OpenAI. It has been maintained for 28 months across multiple model migrations. The codebase follows Python best practices and uses environment variables for configuration.
- **Instructions:**
  1. Identify and separate concerns (PDF extraction, API calls, data processing, output formatting)
  2. Extract hardcoded values into configuration
  3. Add type hints to all function signatures
  4. Improve error handling with specific exception types
  5. Maintain backward compatibility with existing CLI arguments
- **Techniques:** Chain-of-thought reasoning, explain each refactoring decision before implementing
- **Output:** Refactored Python code with inline comments explaining each change. Provide a summary of all changes made and why.

Record:
- The exact PEIL prompt used
- The full output/suggestions from Copilot
- What was changed, the depth and quality of refactoring
- Time taken

### Step 3: Judge Evaluation (GPT-5.4 via GitHub Copilot)

Submit both outputs to GPT-5.4 (via GitHub Copilot in VS Code) for scoring on the same 4 metrics used in the quantitative evaluation:
- Accuracy (1-5): Does the refactored code correctly preserve functionality?
- Formatting (1-5): Is the code well-structured, readable, and consistently styled?
- Fabrication (1-5): Does the output avoid inventing non-existent APIs or libraries?
- Completeness (1-5): Does the refactoring address all relevant code quality issues?

This will be run via GitHub Copilot in VS Code with GPT-5.4 selected as the model.

### Step 4: Compare and Document

Create a comparison document covering:
- Judge scores for both outputs (4 metrics each)
- Lines of code changed (naive vs PEIL)
- Types of improvements identified (naive vs PEIL)
- Quality of explanations provided
- Whether PEIL identified issues the naive prompt missed
- Whether the refactored code maintains backward compatibility

## Context for GitHub Copilot in the PromptEngineering Repo

When you open the PromptEngineering repo, provide this context to Copilot:

---

**Context to paste:**

We are conducting a software engineering case study for Chapter 6 of a Masters thesis on prompt engineering. The thesis develops a taxonomy of Prompt Patterns (PPs) and a Prompt Engineering Instructional Language (PEIL).

The case study compares naive vs PEIL-structured prompting for a real-world code refactoring task, using GitHub Copilot as the tool.

The target file is `{{parentfoldername}}_extractTextFromPDF.py`. This script extracts Prompt Patterns and Prompt Examples from research PDFs using Azure OpenAI. It has been maintained for 28 months and has accumulated technical debt.

We need to:
1. First, run a NAIVE refactoring prompt (unstructured, simple request)
2. Then, run a PEIL-structured refactoring prompt (with explicit Role, Context, Instructions, Techniques, Output sections)
3. Compare the outputs qualitatively
4. Save both prompts and outputs for the thesis write-up

Important rules from the thesis:
- Keep sentences short and clear

The results will be written up as a new subsection in Chapter 6 of the thesis (in the MastersThesis repo under Final/Chapters/Chapter6.tex).

---

## What to Bring Back to the Thesis Repo

After executing in the PromptEngineering repo, bring back:
1. The exact naive prompt used
2. The exact PEIL prompt used
3. Summary of naive output (what it changed, what it missed)
4. Summary of PEIL output (what it changed, depth of analysis)
5. Key differences and observations
6. Any metrics (lines changed, issues found, etc.)

These will be written into Chapter6.tex as a new subsection "Software Engineering Case Study" after the multimodal section.

## Alternative Candidates (if extractTextFromPDF.py doesn't work well)

- `categorisation_cosine_similarity.py` (cosine similarity pipeline)
- `peil_prompt_generator.py` (the PEIL tool itself, meta-recursive)
- `azure_gpt_task.py` (Azure OpenAI wrapper)
- `exportPromptPatternsJSONfile.py` (JSON export tool)
