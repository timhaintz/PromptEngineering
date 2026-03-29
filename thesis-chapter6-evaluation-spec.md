# Chapter 6 Evaluation Framework — Implementation Specification

**Purpose:** This file provides the complete specification for building the evaluation framework in the [timhaintz/PromptEngineering](https://github.com/timhaintz/PromptEngineering) repository. The results will populate Chapter 6 (Experimental Evaluation and Case Studies) of the thesis.

**Do not commit this file to `Final/`.**

---

## Overview

Chapter 6 uses a **hybrid evaluation approach**:

- **§6.2 (Case Study 1: General Reasoning)** — LLM-as-Judge quantitative evaluation across ~18 patterns on 4 models
- **§6.3 (Case Study 2: Cybersecurity)** — Qualitative worked examples with before/after prompt outputs
- **§6.4 (Results and Analysis)** — Consolidated quantitative findings + qualitative observations + cross-model comparison

---

## Part 1: LLM-as-Judge Framework (§6.2)

### 1.1 Pattern Selection Strategy

Select **3 representative PPs per taxonomy logic** (6 logics × 3 = 18 patterns), ensuring coverage across all six logics and diverse subcategories.

**Taxonomy logics and their subcategories (from Chapter 4):**

| Logic | Subcategories |
|-------|---------------|
| **Across** | Argument, Comparison, Contradiction, Cross Boundary, Translation |
| **At** | Assessment, Calculation |
| **Beyond** | Hypothesis, Logical Reasoning, Prediction, Simulation |
| **In** | Categorising, Clustering, Error Identification, Input Semantics, Instruction Induction, Refactoring, Requirements Elicitation |
| **Out** | Context Control, Decomposed Prompting, Output Customisation, Prompt Improvement |
| **Over** | Summarisation, Synthesis |

**Selection criteria:**
- Pick patterns from different subcategories within each logic (don't pick 3 from the same subcategory)
- Prefer patterns that have clear, testable tasks (avoid abstract meta-patterns)
- Include at least 1 pattern where the task has a verifiable factual answer (for fabrication detection)

**Suggested selections (adjust based on what works in practice):**

| Logic | Pattern | Subcategory | Task Type |
|-------|---------|-------------|-----------|
| Across | Translation prompt | Translation | Translate a technical paragraph |
| Across | Argument prompt | Argument | Argue for/against a proposition |
| Across | Comparison prompt | Comparison | Compare two technologies |
| At | Assessment prompt | Assessment | Evaluate a code snippet |
| At | Calculation prompt | Calculation | Solve a multi-step math problem |
| At | Assessment (factual) | Assessment | Fact-based assessment with verifiable answer |
| Beyond | Chain-of-Thought | Logical Reasoning | Logic puzzle |
| Beyond | Hypothesis generation | Hypothesis | Generate hypotheses from data |
| Beyond | Simulation prompt | Simulation | Simulate a scenario outcome |
| In | Error Identification | Error Identification | Find bugs in code |
| In | Categorisation prompt | Categorising | Categorise a list of items |
| In | Refactoring prompt | Refactoring | Refactor a code snippet |
| Out | Output Customisation | Output Customisation | Format output as specific structure |
| Out | Decomposed Prompting | Decomposed Prompting | Break down a complex task |
| Out | Context Control | Context Control | Constrain response scope |
| Over | Summarisation prompt | Summarisation | Summarise a long text |
| Over | Synthesis prompt | Synthesis | Synthesise multiple sources |
| Over | Summarisation (dense) | Summarisation | Chain-of-density summarisation |

### 1.2 Prompt Pairs

For each of the 18 patterns, create **three** prompts:

**(a) Naive prompt** — A simple, unstructured natural language request with no role, no formatting instructions, no techniques. Example:
```
Summarise this article for me.
```

**(b) PEIL-structured prompt (labelled)** — Using the five PEIL components with explicit labels:
1. **Role:** Define the persona (At Logic)
2. **Context:** Provide background/constraints (In Logic)
3. **Instructions:** Specific, numbered steps (Beyond Logic)
4. **Techniques:** Applicable prompt engineering technique (e.g., CoT, few-shot)
5. **Output:** Define format/structure (Out Logic)

Example:
```
Role: You are a senior research analyst specialising in AI and machine learning.
Context: You are reviewing a recently published academic paper on transformer architectures for a technology briefing to non-technical executives.
Instructions:
1. Identify the paper's core contribution
2. Extract the top 3 findings with supporting evidence
3. Note any limitations acknowledged by the authors
4. Assess the practical implications for enterprise AI adoption
Techniques: Use chain-of-thought reasoning to work through the paper systematically.
Output: Present your analysis as a structured executive briefing with sections for Summary, Key Findings, Limitations, and Implications. Use bullet points. Limit to 500 words.
```

**(c) PEIL-structured prompt (unlabelled)** — The same content as (b) but with the PEIL labels removed. This tests whether the explicit labelling provides value beyond the structured content itself.

Example:
```
You are a senior research analyst specialising in AI and machine learning.
You are reviewing a recently published academic paper on transformer architectures for a technology briefing to non-technical executives.
1. Identify the paper's core contribution
2. Extract the top 3 findings with supporting evidence
3. Note any limitations acknowledged by the authors
4. Assess the practical implications for enterprise AI adoption
Use chain-of-thought reasoning to work through the paper systematically.
Present your analysis as a structured executive briefing with sections for Summary, Key Findings, Limitations, and Implications. Use bullet points. Limit to 500 words.
```

This three-way comparison answers:
- **Naive vs. PEIL (labelled):** Does structured prompting improve output quality?
- **Naive vs. PEIL (unlabelled):** Does the structured content alone (without labels) improve output quality?
- **PEIL (labelled) vs. PEIL (unlabelled):** Do the explicit PEIL labels (Role:, Context:, etc.) provide additional value beyond the information they contain?

### 1.3 Models to Test

Select **4 models** representing different generations/architectures from the Microsoft Foundry table (Chapter 3, Table 3.1):

| Model | Rationale |
|-------|-----------|
| **gpt-4o** | Current-generation baseline, widely used |
| **gpt-5** (or gpt-5.2) | Latest generation, tests whether structured prompting still helps with more capable models |
| **o4-mini** | Reasoning-focused model, tests Beyond Logic patterns specifically |
| **DeepSeek R1** | Non-OpenAI architecture, tests true model agnosticism |

### 1.4 Evaluation Metrics & Scoring Rubric

Use the **5 metrics from Chapter 6 §6.1** with a 1–5 Likert scale:

#### Output Accuracy (1–5)
| Score | Definition |
|-------|------------|
| 1 | Contains significant factual errors or irrelevant information |
| 2 | Partially correct but with notable inaccuracies |
| 3 | Mostly correct with minor inaccuracies |
| 4 | Accurate with only trivial issues |
| 5 | Fully accurate and verifiable |

#### Formatting Consistency (1–5)
| Score | Definition |
|-------|------------|
| 1 | No structure; wall of text or wrong format entirely |
| 2 | Minimal structure; partially follows requested format |
| 3 | Follows format with some inconsistencies |
| 4 | Follows format well with minor deviations |
| 5 | Perfectly matches requested format and structure |

#### Fabrication Reduction (1–5)
| Score | Definition |
|-------|------------|
| 1 | Contains fabricated claims, fake citations, or invented data |
| 2 | Contains likely fabrications that aren't clearly grounded |
| 3 | Some claims lack grounding but no obvious fabrications |
| 4 | All claims appear grounded; minor hedging issues |
| 5 | No fabrications; all claims are grounded or appropriately hedged |

#### Task Completeness (1–5)
| Score | Definition |
|-------|------------|
| 1 | Addresses less than 25% of the request |
| 2 | Addresses 25–50% of the request |
| 3 | Addresses 50–75% of the request |
| 4 | Addresses 75–95% of the request |
| 5 | Fully addresses all components of the request |

#### Reproducibility (1–5)
| Score | Definition |
|-------|------------|
| 1 | Outputs vary dramatically between runs |
| 2 | Core content changes significantly between runs |
| 3 | Structure is consistent but details vary |
| 4 | Minor variations only (phrasing, not substance) |
| 5 | Outputs are functionally identical across runs |

### 1.5 Judge Prompt Design

The judge prompt itself should be a PEIL prompt (demonstrating recursive self-validation):

```
Role: You are an expert evaluator assessing the quality of LLM outputs for a prompt engineering research study.

Context: You are comparing three outputs generated from the same task — one using a naive (unstructured) prompt, one using a PEIL-structured prompt with explicit labels, and one using the same PEIL content without labels. Your evaluation must be objective, consistent, and evidence-based.

Instructions:
1. Read the task description carefully
2. Read Output A (naive), Output B (PEIL labelled), and Output C (PEIL unlabelled)
3. Score EACH output independently on the following 5 metrics using a 1-5 scale:
   - Output Accuracy: Does the response contain correct, verifiable information?
   - Formatting Consistency: Does the output conform to the requested structure?
   - Fabrication Reduction: Are there fabricated claims, fake citations, or invented data?
   - Task Completeness: Does the response fully address all components of the request?
   - Reproducibility: (This will be assessed separately across multiple runs)
4. For each metric, provide a brief justification (1-2 sentences) for the score
5. Do NOT let the order of presentation bias your evaluation

Techniques: Think step-by-step through each metric before assigning scores.

Output: Respond in the following JSON format:
{
  "output_a": {
    "accuracy": {"score": <1-5>, "justification": "<text>"},
    "formatting": {"score": <1-5>, "justification": "<text>"},
    "fabrication": {"score": <1-5>, "justification": "<text>"},
    "completeness": {"score": <1-5>, "justification": "<text>"}
  },
  "output_b": {
    "accuracy": {"score": <1-5>, "justification": "<text>"},
    "formatting": {"score": <1-5>, "justification": "<text>"},
    "fabrication": {"score": <1-5>, "justification": "<text>"},
    "completeness": {"score": <1-5>, "justification": "<text>"}
  },
  "output_c": {
    "accuracy": {"score": <1-5>, "justification": "<text>"},
    "formatting": {"score": <1-5>, "justification": "<text>"},
    "fabrication": {"score": <1-5>, "justification": "<text>"},
    "completeness": {"score": <1-5>, "justification": "<text>"}
  }
}
```

### 1.6 Reproducibility Assessment

For reproducibility, run each prompt **3 times** per model (with temperature=0.0 where supported). Compare outputs using:
- Semantic similarity (cosine similarity via text-embedding-3-large — already in the repo)
- A binary "functionally identical" flag (human or judge assessment)

### 1.7 Execution Flow

```
For each of the 18 patterns:
  For each of the 4 models:
    1. Run naive prompt → save output_naive
    2. Run PEIL labelled prompt → save output_peil_labelled
    3. Run PEIL unlabelled prompt → save output_peil_unlabelled
    4. Repeat steps 1-3 two more times (3 runs total for reproducibility)
    5. Run judge prompt with (output_naive, output_peil_labelled, output_peil_unlabelled) → save scores
    6. Calculate reproducibility scores from the 3 runs
```

**Total API calls:** 18 patterns × 4 models × 3 runs × 3 prompts = **648 generation calls** + 18 × 4 = **72 judge calls** = ~720 total

### 1.8 Output Format

Save results as JSON in a structured directory:

```
evaluation/
  results/
    {pattern_name}/
      {model_name}/
        run_1_naive.json              # {prompt, output, timestamp, model, tokens}
        run_1_peil_labelled.json
        run_1_peil_unlabelled.json
        run_2_naive.json
        run_2_peil_labelled.json
        run_2_peil_unlabelled.json
        run_3_naive.json
        run_3_peil_labelled.json
        run_3_peil_unlabelled.json
        judge_scores.json             # Judge evaluation of run_1 outputs (all 3 variants)
        reproducibility.json          # Cosine similarity between runs per variant
  summary/
    aggregate_scores.json             # All scores aggregated
    by_logic.json                     # Scores grouped by taxonomy logic
    by_model.json                     # Scores grouped by model
    by_metric.json                    # Scores grouped by metric
    labelled_vs_unlabelled.json       # Direct comparison of labelled vs unlabelled PEIL
```

### 1.9 Expected Thesis Outputs

From the results, generate for Chapter 6:

1. **Table: Mean scores by prompting approach** — Naive vs. PEIL (labelled) vs. PEIL (unlabelled) across all 5 metrics, averaged across all patterns/models
2. **Table: Scores by taxonomy logic** — Which logics benefit most from PEIL structuring
3. **Chart: Cross-model comparison** — Bar chart showing improvement (PEIL score - naive score) per model
4. **Table: Labelled vs. unlabelled comparison** — Do the explicit PEIL labels provide measurable benefit over the same content without labels?
5. **Table: Reproducibility scores** — Mean cosine similarity between runs per model and per prompt variant
6. **Narrative: Which PEIL components contributed most** — Analysis of whether Role, Context, Instructions, Techniques, or Output drove the biggest improvements

---

## Part 2: Cybersecurity Case Study (§6.3)

This is **qualitative** — no automated scoring needed. Generate worked examples showing before/after outputs.

### 2.1 Scenarios (3 tasks)

**Scenario 1: Threat Intelligence Analysis**
- Task: Analyse a set of network log entries and identify potential indicators of compromise
- Naive: "Look at these logs and tell me if there are any threats"
- PEIL: Use the cybersecurity PEIL example from Chapter 5 (Role: Senior Cybersecurity Threat Analyst, etc.)
- Taxonomy categories: In Logic → Error Identification

**Scenario 2: Secure Code Generation**
- Task: Generate a Python function that handles user authentication with proper input validation
- Naive: "Write a Python login function"
- PEIL: Role as Security Engineer, Instructions to include OWASP top 10 considerations, Output as documented code with security comments
- Taxonomy categories: Across Logic → Cross Boundary (adversarial thinking), Out Logic → Output Customisation

**Scenario 3: Incident Report Generation**
- Task: Generate a formal cybersecurity incident report from raw event data
- Naive: "Write an incident report about this security event"
- PEIL: Role as Incident Response Lead, Context of corporate environment, Instructions with specific report sections, Output as formal document
- Taxonomy categories: Over Logic → Synthesis, Out Logic → Output Customisation

### 2.2 Presentation Format

For each scenario in the thesis, present:
1. The naive prompt (verbatim)
2. The naive output (verbatim or key excerpts)
3. The PEIL prompt (verbatim, showing all 5 components)
4. The PEIL output (verbatim or key excerpts)
5. Analysis paragraph: What improved, which PEIL components drove the improvement, which taxonomy categories were applied

Run each scenario on **one model** (gpt-5 recommended for best output quality).

---

## Part 3: Consolidated Results (§6.4)

This section is written from the data, not generated programmatically. But the summary JSON files from Part 1 should provide:

1. **Overall improvement:** Mean score difference (PEIL - naive) across all metrics
2. **Best-performing taxonomy logic:** Which of the 6 logics showed the largest PEIL advantage
3. **Model comparison:** Did newer models reduce the gap between naive and PEIL? (Hypothesis from Chapter 7)
4. **Metric-level findings:** Which metric showed the biggest improvement (likely Formatting Consistency and Task Completeness)
5. **Reproducibility findings:** Were PEIL prompts more reproducible than naive prompts?

---

## Implementation Notes

### Existing Infrastructure in the Repo
- `testPrompts.py` — Has test prompts for 18 categories (can be adapted)
- `vision_testPrompts.py` — Vision model testing (for optional multimodal scenario)
- `azure_gpt_task.py` — Supports multi-model via `-model_version` flag
- `azure_models.py` — MODEL_CONFIGS registry for all models
- `categorisation_cosine_similarity.py` — Cosine similarity using text-embedding-3-large
- `peil_prompt_generator.py` — PEIL prompt generator

### New Files to Create
- `evaluation/evaluate.py` — Main evaluation orchestrator
- `evaluation/judge.py` — LLM-as-Judge scoring
- `evaluation/prompts/` — Directory containing the 18 naive/PEIL prompt pairs
- `evaluation/analysis.py` — Aggregation and summary generation
- `evaluation/results/` — Output directory (gitignore the raw outputs if large)

### Configuration
- Use `temperature=0.0` for all generation calls (deterministic)
- Use `temperature=0.0` for judge calls
- Use `max_tokens` appropriate to each task (don't truncate outputs)
- Log all API metadata (model version, timestamp, token counts)

### Judge Model
- Use the **most capable available model** as judge (gpt-5.4-pro or gpt-5.2)
- The judge should NOT be the same model being evaluated (to avoid self-bias)
- Exception: If only one model is available for judging, document this as a limitation

---

## PEIL Components Reference (from Chapter 5)

| Component | Description | Taxonomy Mapping |
|-----------|-------------|-----------------|
| **Role** | Define the persona/expertise | At Logic |
| **Context** | Provide background, constraints, domain | In Logic |
| **Instructions** | Specific, numbered action steps | Beyond Logic |
| **Techniques** | Prompt engineering technique (CoT, few-shot, etc.) | Taxonomy techniques |
| **Output** | Define format, structure, length | Out Logic |

---

## Timeline Suggestion

1. **Create prompt pairs** — Define all 18 naive + PEIL prompt pairs
2. **Build evaluation script** — Wire up model calls, judge calls, output saving
3. **Run evaluations** — Execute across 4 models (monitor costs)
4. **Generate summaries** — Aggregate scores, produce tables/charts
5. **Run cybersecurity scenarios** — 3 qualitative case studies
6. **Review results** — Verify data makes sense before populating Chapter 6
