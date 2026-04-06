---
name: peil-evaluation
description: "Evaluates and judges PEIL-generated prompts for quality and effectiveness. Use when assessing prompt quality, providing feedback on system prompts, rating prompts against criteria, or improving prompt engineering outputs. Keywords: prompt evaluation, prompt quality, prompt feedback, prompt rating, prompt assessment, LLM evaluation, prompt judge."
license: MIT
metadata:
  author: Tim Haintz
  version: "0.2"
  companion-skill: peil
---

# PEIL Evaluation Skill

This skill evaluates prompts generated using the Prompt Engineering Instructional Language (PEIL) methodology for quality and effectiveness.

## When to Use This Skill

- Assessing the quality of generated system prompts
- Providing constructive feedback on prompt design
- Rating prompts against established criteria
- Iteratively improving prompts before deployment
- Comparing multiple prompt versions

## Evaluation Criteria (Weighted)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Clarity and Coherence** | 30% | Is the language clear and unambiguous? Does the prompt have a logical flow? |
| **Completeness and Comprehensiveness** | 25% | Does the prompt cover all necessary aspects? Are important elements missing? |
| **Relevance and Applicability** | 20% | How well does the prompt align with its intended purpose? Is it practical? |
| **Creativity and Originality** | 15% | Does the prompt introduce novel approaches? How original is it? |
| **Technical Accuracy** | 10% | Are technical details and instructions accurate? |

## Evaluation Process

### Step 1: Initial Assessment
Read the prompt completely before scoring. Identify:
- The intended purpose/task
- Target audience (agent, human, specific domain)
- Expected output format

### Step 2: Criterion-by-Criterion Analysis
For each of the 5 criteria:
1. Identify specific strengths
2. Identify areas for improvement
3. Assign a score (0-100)

### Step 3: Calculate Overall Score
```
Overall = (Clarity × 0.30) + (Completeness × 0.25) + (Relevance × 0.20) + (Creativity × 0.15) + (Accuracy × 0.10)
```

### Step 4: Generate Feedback
Provide actionable recommendations for improvement.

## Evaluation Output Format

```markdown
## Prompt Evaluation Report

### Overall Score: [X]/100

### Criterion Breakdown

| Criterion | Score | Strengths | Areas for Improvement |
|-----------|-------|-----------|----------------------|
| Clarity (30%) | X/100 | ... | ... |
| Completeness (25%) | X/100 | ... | ... |
| Relevance (20%) | X/100 | ... | ... |
| Creativity (15%) | X/100 | ... | ... |
| Technical Accuracy (10%) | X/100 | ... | ... |

### Key Recommendations
1. [Specific, actionable recommendation]
2. [Specific, actionable recommendation]
3. [Specific, actionable recommendation]

### Summary
[2-3 sentence summary of the evaluation]
```

## Scoring Guidelines

### Clarity and Coherence (30%)

| Score Range | Indicators |
|-------------|------------|
| 90-100 | Crystal clear instructions, perfect logical flow, no ambiguity |
| 70-89 | Mostly clear, minor ambiguities, good structure |
| 50-69 | Some unclear sections, could be better organized |
| 30-49 | Confusing in places, poor flow, significant ambiguity |
| 0-29 | Very unclear, disorganized, highly ambiguous |

### Completeness and Comprehensiveness (25%)

| Score Range | Indicators |
|-------------|------------|
| 90-100 | All PEIL components present, thorough coverage |
| 70-89 | Most components present, good coverage with minor gaps |
| 50-69 | Some components missing, moderate coverage |
| 30-49 | Several components missing, incomplete coverage |
| 0-29 | Most components missing, very incomplete |

### Relevance and Applicability (20%)

| Score Range | Indicators |
|-------------|------------|
| 90-100 | Perfectly aligned with purpose, immediately applicable |
| 70-89 | Well-aligned, practical with minor adjustments |
| 50-69 | Somewhat aligned, needs modification for use |
| 30-49 | Poorly aligned, limited practical value |
| 0-29 | Not aligned with purpose, impractical |

### Creativity and Originality (15%)

| Score Range | Indicators |
|-------------|------------|
| 90-100 | Highly innovative approach, novel techniques |
| 70-89 | Some creative elements, good use of techniques |
| 50-69 | Standard approach, minimal creativity |
| 30-49 | Very basic, formulaic |
| 0-29 | No creativity, copied template |

### Technical Accuracy (10%)

| Score Range | Indicators |
|-------------|------------|
| 90-100 | All technical details correct, best practices followed |
| 70-89 | Mostly accurate, minor technical issues |
| 50-69 | Some inaccuracies, deviations from best practices |
| 30-49 | Several inaccuracies, poor technical implementation |
| 0-29 | Major technical errors, incorrect information |

## Quick Evaluation Checklist

Before detailed evaluation, check:

- [ ] Does the prompt have a clear Role defined?
- [ ] Is the Context specific and relevant?
- [ ] Are complex questions broken down?
- [ ] Are there specific, actionable instructions?
- [ ] Is there a length/conciseness constraint?
- [ ] Is an appropriate prompting technique applied?
- [ ] Is the desired output format specified?

## Common Issues and Recommendations

| Issue | Recommendation |
|-------|----------------|
| Vague role definition | Add specific expertise and domain context |
| Missing context | Explain the situation and constraints |
| Overly complex | Break into sub-prompts or stages |
| No output format | Specify Markdown, JSON, bullet points, etc. |
| Wrong technique | Match technique to task type (see PEIL techniques) |
| Too long | Focus on essential instructions, move details to examples |
| Too short | Add constraints, examples, or edge case handling |

## Empirical Evaluation Findings (2026)

A quantitative LLM-as-Judge evaluation tested PEIL across 4 model architectures (GPT-4.1, GPT-5.2, Grok-4, DeepSeek-R1) on 18 research-grounded patterns. Key findings for evaluators:

| Finding | Implication for Evaluation |
|---------|---------------------------|
| Labels improve 13/18 patterns (+0.094 overall) | **Penalise prompts missing explicit PEIL labels** (Role:, Context:, etc.) |
| Fabrication reduction strongest (+0.208) | **Prioritise grounding and citation techniques** when evaluating accuracy |
| Formatting consistency identical with/without PEIL | Don't over-weight formatting — it's not where PEIL adds value |
| PEIL excels at structured output (+0.69 template, +0.50 assessment) | **Score higher for tasks requiring defined output schemas** |
| Role framing prevents safety refusals | **Check that sensitive domain prompts include Role and Context framing** |
| PEIL designed as system prompt | **Evaluate system-prompt prompts differently** — "waiting for input" is correct behaviour, not a failure |

### Red Flags to Watch For
- PEIL prompt used in single-turn mode without embedded task data → will produce "waiting for input" responses
- Missing Role label when task is domain-sensitive → risk of model refusal
- Using Auto-CoT or Self-Consistency as technique labels without corresponding instructions → technique name alone is insufficient

## Additional Resources

- [PEIL Skill](../peil/SKILL.md) - Main prompt generation methodology
- [Evaluation Criteria Details](references/CRITERIA.md) - Extended criterion definitions
- [The Prompt Report](https://arxiv.org/abs/2406.06608) - 58 text-based techniques taxonomy (Schulhoff et al., 2024)
