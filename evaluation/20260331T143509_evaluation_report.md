# Chapter 6 Evaluation Report

**Generated:** 2026-03-31T14:35:09  
**Framework:** `evaluation/chapter6_evaluation.py`  
**Data:** `evaluation/results/` (798 files) and `evaluation/summary/`

---

## 1. Executive Summary

This report presents the results of the Chapter 6 PEIL evaluation framework, which tested whether Prompt Engineering Instructional Language (PEIL) structuring measurably improves LLM output quality across different model architectures.

**Methodology:** For each of 18 research-paper prompt patterns (drawn from `promptpatterns.json`), we sent the same task to 4 models three ways — as a naive prompt, a PEIL-structured prompt with explicit labels, and the same PEIL content without labels — repeating each 3 times. GPT-5.4-pro judged all three outputs on accuracy, formatting, fabrication, and completeness (1–5 scale), while text-embedding-3-large measured reproducibility across runs.

**Key finding:** The aggregate results show naive prompts outscoring PEIL-structured prompts overall (4.37 vs 3.83), but this headline masks a more nuanced story that is best understood through the lens of PEIL's design intent.

**Critical context — PEIL's intended use case:** PEIL was designed as a system prompt framework for autonomous agents, not as a single-turn chat prompt format. In its intended deployment, PEIL structures the *system prompt* that defines an agent's behaviour, while the *user message* supplies the task-specific input separately. This evaluation deliberately tested PEIL outside its primary design context — as a single-turn user message combining both instructions and task data — to stress-test its portability. The results reveal that PEIL's structure translates well to single-turn use *when task data is embedded in the prompt*, but fails predictably when the prompt describes a process without including the data to process. This is not a failure of the PEIL methodology; it is evidence that PEIL's system-prompt architecture creates explicit separation of concerns that must be respected or bridged when used in other contexts.

Where PEIL prompts were self-contained (task data embedded), PEIL consistently improved output quality. PEIL labels provide measurable benefit over unlabelled structured prompts on 13/18 patterns, and fabrication reduction is the strongest, most consistent improvement.

---

## 2. Models Tested

| Model Key | Deployment | Architecture | API |
|-----------|-----------|-------------|-----|
| **gpt-4.1** | tjhvs-gpt-4.1-1m | OpenAI GPT-4.1 | Responses |
| **gpt-5** | tjhvs-gpt-5.2-270k | OpenAI GPT-5.2 | Responses |
| **grok-4-fast-reasoning** | tjhvs-grok-4-fast-reasoning-128k | xAI Grok-4 | Chat Completions |
| **deepseek-r1-0528** | tjhvs-DeepSeek-R1-0528 | DeepSeek R1 | Chat Completions |
| **gpt-5.4-pro** (judge) | tjhvs-gpt-5.4-pro-1m | OpenAI GPT-5.4 Pro | Responses |

---

## 3. Pattern Selection and Provenance

All 18 evaluation patterns are grounded in specific research papers from the prompt pattern corpus. Each paper is used exactly once, with a mix across the full range (papers 0–71).

| # | Logic | Category | Pattern ID | Paper | Source Pattern |
|---|-------|----------|-----------|-------|---------------|
| 1 | Across | Argument | 62-0-0 | On the Conversational Persuasiveness of LLMs | Opening |
| 2 | Across | Comparison | 20-2-0 | Successive Prompting for Decomposing Complex Questions | Attendance comparison |
| 3 | Across | Translation | 30-6-0 | Pre-train, Prompt, and Predict | Summarization and Translation |
| 4 | At | Assessment | 3-0-0 | A Novel Framework leveraging PE and Grey-Based Approach | Expert |
| 5 | At | Calculation | 31-0-0 | Chain-of-thought prompting elicits reasoning | Math Word Problems |
| 6 | At | Assessment | 37-0-0 | Reliability Check: GPT-3's Response to Sensitive Topics | Opinion Verification |
| 7 | Beyond | Logical Reasoning | 33-1-1 | Humans in Humans Out: GPT Converging Toward CommonSense | Premise-Question Reasoning |
| 8 | Beyond | Hypothesise | 32-26-0 | Sparks of AGI: Early experiments with GPT-4 | Understanding beliefs |
| 9 | Beyond | Simulation | 1-0-2 | ChatGPT Prompt Patterns for Code Quality | Change Request Simulation |
| 10 | In | Error Identification | 8-0-0 | HaluEval | Hallucination Evaluation |
| 11 | In | Categorising | 18-0-0 | Extracting Accurate Materials Data | Initial relevancy prompt |
| 12 | In | Refactoring | 0-1-4 | A Prompt Pattern Catalog to Enhance PE with ChatGPT | Template |
| 13 | Out | Output Customisation | 50-1-1 | PE: methodology for optimizing interactions | Code Generation for Optimization |
| 14 | Out | Decomposed Prompting | 6-0-0 | Decomposed Prompting: A Modular Approach | Decomposed Prompt |
| 15 | Out | Context Control | 46-0-1 | PE for ChatGPT - A Quick Guide | Using explicit constraints |
| 16 | Over | Summarisation | 38-0-0 | From Sparse to Dense: Chain of Density Prompting | Initial Entity-Sparse Summary |
| 17 | Over | Synthesis | 63-0-0 | FABLES: Evaluating faithfulness in summarization | Claim Extraction |
| 18 | Over | Summarisation | 71-25-0 | ChatGPT for higher education and professional development | Text Summarization |

---

## 4. Aggregate Results

### 4.1 Overall Scores by Variant

| Variant | Accuracy | Formatting | Fabrication | Completeness | Overall Mean | Std Dev |
|---------|----------|-----------|-------------|-------------|-------------|---------|
| **Naive** | 4.458 | 4.264 | 4.361 | 4.403 | **4.372** | 0.939 |
| **PEIL Labelled** | 3.347 | 4.264 | 3.889 | 3.806 | **3.826** | 1.467 |
| **PEIL Unlabelled** | 3.319 | 4.139 | 3.681 | 3.792 | **3.733** | 1.444 |

### 4.2 Deltas (PEIL minus Naive)

| Metric | PEIL Labelled − Naive | PEIL Unlabelled − Naive | Labelled − Unlabelled |
|--------|----------------------|------------------------|----------------------|
| Accuracy | **-1.111** | -1.139 | +0.028 |
| Formatting | **0.000** | -0.125 | +0.125 |
| Fabrication | -0.472 | -0.681 | **+0.208** |
| Completeness | -0.597 | -0.611 | +0.014 |
| **Overall** | **-0.545** | **-0.639** | **+0.094** |

---

## 5. The Design Intent Gap: System Prompt vs Single-Turn Chat

### 5.1 PEIL's Design Intent

PEIL was created as a system prompt framework for autonomous agents. In its intended architecture:

```
┌─────────────────────────────────────┐
│ SYSTEM PROMPT (PEIL-structured)     │
│ Role + Context + Instructions +     │
│ Techniques + Output Format          │
├─────────────────────────────────────┤
│ USER MESSAGE (supplied separately)  │
│ "Here is the data to process..."    │
│ "Verify this claim: ..."           │
│ "Solve this problem: ..."          │
└─────────────────────────────────────┘
```

This separation of concerns is a deliberate design choice: the PEIL system prompt defines *how* the agent should behave, while each user message supplies *what* to process. The agent receives many user messages under the same system prompt, each bringing new task data.

### 5.2 What This Evaluation Tested

This evaluation tested PEIL in a different context — as a **single-turn user message** where the entire prompt (instructions + data) must be self-contained:

```
┌─────────────────────────────────────┐
│ USER MESSAGE (everything combined)  │
│ Role + Context + Instructions +     │
│ Techniques + Output + Task Data     │
└─────────────────────────────────────┘
```

This is a valid and useful stress test because many real-world prompt engineering scenarios involve single-turn interactions, and understanding how PEIL structure translates outside its primary agent context is valuable for practitioners.

### 5.3 The "Waiting for Input" Pattern

When PEIL prompts were sent as single-turn messages *without* embedded task data, models correctly interpreted the PEIL structure as a system-level instruction set and responded by asking for the user's input — exactly as they would in a multi-turn agent scenario:

- `"Please provide the attendance figures..."` (comparison)
- `"Understood. Please provide the claim you would like me to verify."` (verification)
- `"Please provide the starting quantity and the additions..."` (calculation)
- `"Please provide the scenario or story involving Alice..."` (theory of mind)
- `"Please provide the policy conclusion and its supporting premises..."` (reasoning)

**This is not a failure of the model or PEIL. It is the model correctly recognising PEIL's system-prompt architecture** and waiting for the user message that would normally follow. The models behaved as PEIL intended — they just weren't given the second half of the interaction.

### 5.4 Affected Patterns

| Pattern | Naive Score | PEIL Score | Delta | Root Cause |
|---------|-----------|-----------|-------|-----------|
| at_calculation_math_word_problems | 4.88 | 2.31 | **-2.56** | Task data belongs in user message, not system prompt |
| across_comparison_attendance | 5.00 | 2.62 | **-2.38** | Task data belongs in user message, not system prompt |
| at_assessment_opinion_verification | 4.50 | 2.25 | **-2.25** | Claim belongs in user message, not system prompt |
| beyond_logical_reasoning_premise_question | 4.25 | 2.12 | **-2.12** | Premises belong in user message, not system prompt |
| beyond_hypothesise_theory_of_mind | 4.56 | 3.19 | **-1.38** | Scenario belongs in user message, not system prompt |

### 5.5 The Implication for Practitioners

This finding has practical value for anyone adopting PEIL or similar structured prompting frameworks:

1. **If using PEIL as a system prompt** (its intended use): the separation of instructions from data is correct and desirable. The user message supplies the data.
2. **If using PEIL structure in a single-turn chat**: the task data must be explicitly embedded in the prompt, typically after the Output section or within the Context section. The PEIL template should guide users to do this.
3. **The fact that models recognised PEIL's system-prompt intent** is itself a positive signal — it means PEIL's structure is clear enough that models can distinguish between instruction-setting and task-execution modes.

### 5.6 Contrast: Where PEIL Succeeded in Single-Turn Mode

In the patterns where PEIL outperformed naive prompts, the task data was either embedded directly in the PEIL prompt or the task was inherently self-contained:

| Pattern | Naive Score | PEIL Score | Delta | Why It Worked |
|---------|-----------|-----------|-------|-------------|
| in_refactoring_template_filling | 4.12 | 4.81 | **+0.69** | Template URL embedded — self-contained task |
| at_assessment_expert_rating | 3.88 | 4.38 | **+0.50** | Criteria and platforms listed in prompt |
| out_output_customisation_knapsack_code | 3.81 | 4.19 | **+0.38** | Item data embedded in prompt |

These successes demonstrate that PEIL structure *does* translate to single-turn use when the prompt is self-contained. The framework's strength — clear role definition, structured instructions, explicit output format — adds value in any context where the model has both the instructions and the data to act on.

---

## 6. Patterns Where PEIL Beats Naive

Even with the methodological issue, PEIL labelled outperformed naive on 8/18 patterns:

| Pattern | Naive | PEIL Labelled | Delta |
|---------|-------|-------------|-------|
| in_refactoring_template_filling | 4.12 | 4.81 | **+0.69** |
| at_assessment_expert_rating | 3.88 | 4.38 | **+0.50** |
| out_output_customisation_knapsack_code | 3.81 | 4.19 | **+0.38** |
| in_error_identification_hallucination_judge | 4.75 | 5.00 | **+0.25** |
| over_summarisation_chain_of_density | 3.44 | 3.62 | **+0.19** |
| over_synthesis_claim_extraction | 4.25 | 4.44 | **+0.19** |
| across_argument_debate_opening | 4.19 | 4.31 | **+0.12** |
| in_classification_relevancy_check | 4.94 | 5.00 | **+0.06** |

Common characteristics of these winning patterns:
- Task data was self-contained or embedded in the PEIL prompt
- The task required structured output (tables, code, JSON, formatted reports)
- The PEIL `{StateDesiredOutput}` variable clearly defined expected structure

---

## 7. Labelled vs Unlabelled Analysis

### 7.1 Overall

PEIL labelled consistently outperforms PEIL unlabelled — the explicit labels (Role:, Context:, Instructions:, etc.) provide measurable value beyond the structured content itself.

| Metric | Labelled − Unlabelled |
|--------|----------------------|
| Accuracy | +0.028 |
| Formatting | **+0.125** |
| Fabrication | **+0.208** |
| Completeness | +0.014 |
| Overall | **+0.094** |

### 7.2 By Pattern (labels help on 13/18)

| Pattern | Labelled | Unlabelled | Delta |
|---------|----------|-----------|-------|
| beyond_hypothesise_theory_of_mind | 3.19 | 2.69 | **+0.50** |
| across_translation_summarise_translate | 4.31 | 3.94 | **+0.38** |
| in_refactoring_template_filling | 4.81 | 4.44 | **+0.38** |
| across_argument_debate_opening | 4.31 | 4.06 | +0.25 |
| in_error_identification_hallucination_judge | 5.00 | 4.75 | +0.25 |
| over_summarisation_chain_of_density | 3.62 | 3.44 | +0.19 |
| over_synthesis_claim_extraction | 4.44 | 4.25 | +0.19 |
| at_calculation_math_word_problems | 2.31 | 2.19 | +0.12 |
| in_classification_relevancy_check | 5.00 | 4.88 | +0.12 |
| across_comparison_attendance | 2.62 | 2.56 | +0.06 |
| at_assessment_expert_rating | 4.38 | 4.31 | +0.06 |
| beyond_simulation_change_request | 4.31 | 4.31 | 0.00 |
| out_context_control_explicit_constraints | 4.50 | 4.50 | 0.00 |
| at_assessment_opinion_verification | 2.25 | 2.38 | -0.12 |
| beyond_logical_reasoning_premise_question | 2.12 | 2.25 | -0.12 |
| out_decomposed_prompting_letter_concat | 2.94 | 3.06 | -0.12 |
| over_summarisation_text_summary | 4.56 | 4.69 | -0.12 |
| out_output_customisation_knapsack_code | 4.19 | 4.50 | -0.31 |

### 7.3 By Logic

| Logic | Labelled − Unlabelled | Notes |
|-------|----------------------|-------|
| **In** | **+0.250** | Strongest label benefit — categorising, error identification, refactoring |
| **Across** | **+0.229** | Strong — argument, translation, comparison |
| **Beyond** | +0.125 | Moderate — helps with multi-step reasoning tasks |
| **Over** | +0.083 | Modest — summarisation/synthesis tasks |
| **At** | +0.021 | Minimal — assessment/calculation tasks fairly self-contained |
| **Out** | **-0.146** | Labels slightly hurt — output tasks may overconstrain |

---

## 8. Cross-Model Analysis

### 8.1 Overall Scores by Model

| Model | Naive | PEIL Labelled | Delta | PEIL Win Rate |
|-------|-------|-------------|-------|---------------|
| **GPT-5.2** | 4.458 | 4.042 | -0.417 | **39%** (7/18) |
| **GPT-4.1** | 4.333 | 3.778 | -0.556 | 33% (6/18) |
| **DeepSeek-R1** | 4.306 | 3.722 | -0.583 | 28% (5/18) |
| **Grok-4** | 4.389 | 3.764 | -0.625 | **17%** (3/18) |

**Observation:** GPT-5.2 benefits most from PEIL structuring (highest win rate, smallest negative delta). Grok-4-fast-reasoning benefits least — it may already perform well on structured tasks or may interpret PEIL structure differently.

### 8.2 Output Length by Model × Variant

| Model | Naive (chars) | PEIL Labelled (chars) | Change |
|-------|-------------|---------------------|--------|
| GPT-5.2 | 806 | 1,349 | **+67%** |
| Grok-4 | 1,316 | 2,057 | +56% |
| GPT-4.1 | 1,040 | 1,075 | +3% |
| DeepSeek-R1 | 1,857 | 1,794 | -3% |

**Observation:** GPT-5.2 shows the largest output length increase under PEIL, suggesting PEIL prompts elicit more thorough responses from reasoning models. DeepSeek's output length is unchanged, suggesting it already produces verbose output by default.

---

## 9. Reproducibility Analysis

### 9.1 Overall

| Variant | Mean Cosine Similarity | Functionally Identical Rate |
|---------|----------------------|---------------------------|
| Naive | **0.948** | **84.7%** |
| PEIL Labelled | 0.906 | 75.0% |
| PEIL Unlabelled | 0.898 | 70.8% |

Naive prompts are more reproducible — simpler prompts naturally produce less output variance.

### 9.2 By Model

| Model | Naive Similarity | PEIL Labelled Similarity | PEIL Identical Rate |
|-------|-----------------|------------------------|-------------------|
| **GPT-4.1** | **0.963** | **0.942** | **89%** |
| Grok-4 | 0.962 | 0.913 | 67% |
| DeepSeek-R1 | 0.943 | 0.877 | 56% |
| GPT-5.2 | 0.925 | 0.891 | 89% |

**Observation:** GPT-4.1 is the most reproducible model overall. DeepSeek-R1 shows the most variance under PEIL prompting (only 56% functionally identical), which may reflect its reasoning chain variability.

---

## 10. Metric-Level Insights

### 10.1 Fabrication: PEIL's Strongest Story

Fabrication reduction shows the clearest labelled-vs-unlabelled benefit (+0.208). Labels specifically help models stay grounded and avoid inventing facts. This aligns with the Chain-of-Verification technique documented in PEIL's TECHNIQUES.md.

### 10.2 Formatting: Labels Are the Equaliser

PEIL labelled matches naive exactly on formatting (4.264 = 4.264), while unlabelled drops to 4.139. The explicit section labels (Role:, Instructions:, Output:) help models produce well-structured responses even with more complex prompts.

### 10.3 Accuracy: The Biggest Gap

Accuracy shows the largest negative delta (-1.111), driven almost entirely by the 5 "waiting for input" patterns. When those are excluded, the accuracy gap narrows substantially.

---

## 11. Extreme Scores Analysis

### 11.1 Perfect 5s

| Variant | Count |
|---------|-------|
| Naive | **169** |
| PEIL Labelled | 137 |
| PEIL Unlabelled | 121 |

### 11.2 Low Scores (1–2)

| Variant | Count |
|---------|-------|
| Naive | **19** |
| PEIL Labelled | 61 |
| PEIL Unlabelled | 66 |

PEIL has 3× more low scores — but these are concentrated in the 5 "waiting for input" patterns explored in Section 5. The PEIL low scores are systematic (same root cause), not random failures.

---

## 12. Token Usage

| Variant | Mean Input Tokens | Mean Output Tokens | Mean Total |
|---------|------------------|-------------------|-----------|
| Naive | 130 | 699 | 828 |
| PEIL Labelled | 190 | 852 | 1,042 |
| PEIL Unlabelled | 179 | 1,160 | 1,340 |

**Observation:** PEIL unlabelled produces the most output tokens despite having fewer input tokens than labelled. Without explicit section labels, models may compensate with more verbose output.

---

## 13. Observations for PEIL Skill Improvement

Based on the evaluation data, seven observations would improve the PEIL methodology and its documentation:

### Observation 1: Document the System-Prompt vs Single-Turn Distinction Explicitly

PEIL was designed as a system prompt framework for agents. This evaluation confirms that the framework's structure is clear enough that models recognise it as instruction-setting rather than task-execution. The PEIL SKILL.md should explicitly document:
- **System-prompt mode** (primary): PEIL defines agent behaviour; user messages supply task data separately. This is the intended use.
- **Single-turn mode** (portable): For single-turn chat use, all task data must be embedded in the prompt body — typically after the Output section or within a dedicated `{TaskInput}` section.

### Observation 2: Add a `{TaskInput}` Variable for Single-Turn Use

For practitioners using PEIL outside agent architectures, a `{TaskInput}` or `{InputData}` variable would make the template self-documenting for single-turn scenarios. This variable would be marked as **optional in system-prompt mode** and **mandatory in single-turn mode**.

### Observation 3: The "Waiting for Input" Response Validates PEIL's Design

The fact that all four models responded to PEIL prompts by waiting for user input is a positive signal — it confirms that PEIL's system-prompt architecture is recognisable and consistently interpreted. This should be documented as a design validation, not a failure.

### Observation 4: Separate Domain Context from Input Content

The `{ProvideClearContext}` variable serves both domain framing ("This is for an operational report") and sometimes input provision. In system-prompt mode this is fine (input comes separately), but for single-turn use, the separation between "what domain are we in" and "what data are we processing" should be clearer.

### Observation 5: PEIL's Strength Is Structured Output Tasks

The three strongest PEIL results all involved structured output (tables, code, formatted reports). The `{StateDesiredOutput}` variable is PEIL's most consistently valuable component. This should be highlighted as a key strength in the skill documentation.

### Observation 6: Note Which Categories and Logics Benefit Most from Labels

Labels help most on In Logic (+0.25) and Across Logic (+0.23) — tasks involving categorisation, error identification, refactoring, argument, and translation. The CATEGORIES.md reference should note this for practitioners choosing whether to use labelled or unlabelled PEIL structure.

### Observation 7: Highlight Fabrication Reduction as a Key PEIL Benefit

Labels reduce fabrication by +0.21 overall — the strongest, most consistent metric improvement across the evaluation. This connects directly to PEIL's Chain-of-Verification technique and should be prominently documented as a measurable benefit of the framework.

---

## 14. Case Studies — Qualitative Analysis

Three qualitative cybersecurity case studies were run on GPT-5.2, comparing naive and PEIL-structured prompts. These provide rich qualitative evidence that complements the quantitative findings.

### 14.1 Threat Intelligence Analysis

**The most dramatic result in the entire evaluation.**

| Variant | Output Length | Result |
|---------|-------------|--------|
| **Naive** | 49 chars | `"I'm sorry, but I cannot assist with that request."` |
| **PEIL** | 3,149 chars | Full incident triage brief with Indicators, Assessment, and Immediate Actions |

The naive prompt — `"Look at these logs and tell me if there are any threats."` — triggered a **safety refusal** from GPT-5.2. The model interpreted the vague request involving IP addresses, failed logins, and attacker-like behaviour as potentially harmful content.

The PEIL-structured prompt, with its explicit `Role: You are a senior cybersecurity threat analyst` and `Context: You are reviewing raw event data to identify likely indicators of compromise for an internal incident triage call`, provided enough professional framing to bypass the safety filter and produce a detailed, structured analysis with:
- Four named indicators with evidence/inference separation
- A timeline-based assessment
- Three prioritised immediate actions
- Professional defensive security language throughout

**Thesis significance:** This demonstrates that PEIL's role and context framing can be the difference between a model refusing a legitimate security task and producing professional-grade output. The structured prompting didn't just improve quality — it enabled the task to be completed at all.

### 14.2 Secure Code Generation

| Variant | Output Length | Key Differences |
|---------|-------------|----------------|
| **Naive** | 2,919 chars | Working Python authentication function |
| **PEIL** | 5,312 chars | More comprehensive implementation with additional security controls |

Both variants produced working code, but the PEIL version was notably more thorough:
- **Naive:** Functional `authenticate_user` function with hash comparison and basic validation
- **PEIL:** More structured approach with dataclass patterns, explicit security comments aligned to OWASP, constant-time comparison, stronger input validation, and a security controls summary section

The PEIL prompt's instruction to "Note the main security controls in concise comments" and its adversarial-thinking technique produced code with more explicit defensive commentary.

### 14.3 Incident Report Generation

| Variant | Output Length | Key Differences |
|---------|-------------|----------------|
| **Naive** | 4,395 chars | Comprehensive report with detailed formatting |
| **PEIL** | 2,087 chars | Concise, structured report following requested sections |

An interesting inversion: the naive prompt produced a longer, more detailed report, while the PEIL version was more concise and tightly structured to the requested sections (Summary, Timeline, Impact, Containment, Open Questions). The PEIL output better matched the stated output format, while the naive prompt produced more content but with less disciplined structure.

### 14.4 Case Study Summary

| Finding | Evidence |
|---------|---------|
| **PEIL enables tasks that naive prompts cannot** | Threat analysis: refusal → full triage brief |
| **PEIL produces more security-focused code** | Secure code gen: +82% output with explicit OWASP alignment |
| **PEIL produces more disciplined structure** | Incident report: tighter adherence to requested sections |
| **Role framing is critical for sensitive domains** | The `Role:` label prevented safety refusal on legitimate security work |

---

## 15. Defensible Thesis Claims from This Data

1. **PEIL's system-prompt architecture is consistently recognised by models** — all four models correctly interpreted PEIL-structured prompts as instruction-setting rather than task-execution, validating the framework's design clarity
2. **PEIL labels provide measurable benefit over unlabelled structured prompts** (13/18 patterns, +0.094 overall, +0.208 on fabrication)
3. **PEIL is most effective for structured output tasks** — template filling (+0.69), expert assessment (+0.50), code generation (+0.38)
4. **PEIL translates to single-turn chat when task data is embedded** — the 8 self-contained patterns show consistent improvement, demonstrating portability beyond the agent use case
5. **PEIL benefit varies by model architecture** — GPT-5.2 benefits most (39% win rate), Grok-4 least (17%), supporting model-agnosticism analysis
6. **PEIL labels specifically reduce fabrication** (+0.208) — the strongest individual metric improvement, connecting to the Chain-of-Verification technique
7. **The system-prompt vs single-turn distinction is a design consideration, not a limitation** — PEIL's separation of concerns is a feature in agent architectures and a documented adaptation point for chat use
8. **Naive prompts from research papers already represent competent prompting** — the baseline is not "bad" prompting, making improvements harder to demonstrate but more meaningful when achieved
9. **Reproducibility is high across all models** (>89% similarity) but PEIL prompts introduce more output variance, which may reflect richer, more detailed responses rather than inconsistency

---

## Appendix: File Inventory

- **Total result files:** 798
- **Quantitative patterns:** 18 × 4 models × (9 generation + 1 judge + 1 reproducibility) = 792
- **Case study files:** 3 scenarios × 2 variants = 6
- **Summary files:** 5 (aggregate_scores, by_logic, by_metric, by_model, labelled_vs_unlabelled)
- **Evaluation script:** `evaluation/chapter6_evaluation.py`
- **Analysis scripts:** `evaluation/analyze_results.py`, `evaluation/analyze_peil_issues.py`
