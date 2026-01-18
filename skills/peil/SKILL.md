---
name: peil
description: Prompt Engineering Instructional Language (PEIL) - generates optimised system prompts for AI agents and LLMs. Use when creating agent system prompts, improving prompt quality, applying research-backed prompting techniques, or structuring prompts with role, context, instructions, and desired output. Keywords: prompt engineering, system prompt, agent prompt, LLM optimization, prompt generation.
license: MIT
metadata:
  author: Tim Haintz
  version: "0.2"
  source: https://arxiv.org/abs/2402.07927
---

# Prompt Engineering Instructional Language (PEIL)

PEIL is a structured methodology for generating high-quality system prompts for AI agents and large language models.

## When to Use This Skill

- Creating system prompts for autonomous agents
- Improving existing prompts for better LLM performance
- Applying research-backed prompting techniques
- Structuring complex instructions clearly

## PEIL Template Structure

Use the following variables to construct effective prompts:

```
{Role} {ProvideClearContext} {BreakDownComplexQuestions} {ProvideSpecificInstructions} {DefineConciseness} {PromptingTechniques} {StateDesiredOutput}
```

### Variable Definitions

| Variable | Purpose |
|----------|---------|
| **Role** | Specify the persona or expertise the model should adopt |
| **ProvideClearContext** | Set the domain and focus area for precise, tailored responses |
| **BreakDownComplexQuestions** | Decompose complex topics into manageable sub-questions |
| **ProvideSpecificInstructions** | Define constraints, requirements, or rules |
| **DefineConciseness** | Set word limits or brevity requirements |
| **PromptingTechniques** | Apply research-backed techniques (see [TECHNIQUES.md](references/TECHNIQUES.md)) |
| **StateDesiredOutput** | Specify the expected format, structure, or content |

## Hybrid Prompt Structure

Based on research from [arXiv:2503.06926](https://arxiv.org/abs/2503.06926), employ a hybrid structure:

1. **Opening Statement**: Short sentence or paragraph stating role and goal
2. **Bullet Points**: Specific rules, options, or constraints

## Step-by-Step Instructions

1. **Define the Role**: Start with "You are a [domain] expert" or similar
2. **Set Context**: Explain the domain and what the model should focus on
3. **Break Down Questions**: If complex, split into sub-questions
4. **Add Constraints**: Include any specific rules or requirements
5. **Set Length**: Define word limits if needed
6. **Choose Technique**: Select from [TECHNIQUES.md](references/TECHNIQUES.md) based on task type
7. **Specify Output**: Define format (Markdown, JSON, bullet points, etc.)

## Quick Reference: Technique Selection

| Task Type | Recommended Technique |
|-----------|----------------------|
| Reasoning & Logic | Chain-of-Thought (CoT), Tree-of-Thoughts |
| Reduce Hallucination | RAG, Chain-of-Verification (CoVe) |
| Code Generation | Scratchpad, Program of Thoughts (PoT) |
| New Tasks | Zero-Shot or Few-Shot Prompting |
| Complex Analysis | Decomposed Prompting, Thread of Thought |

See [TECHNIQUES.md](references/TECHNIQUES.md) for the complete techniques table.

## Example Prompt

```
Role: You are a cybersecurity expert specializing in enterprise security architecture.

Context: Focus on discussing practical cybersecurity measures for protecting sensitive data in cloud environments.

Instructions:
- Include at least three key components of a strong security strategy
- Provide specific examples of implementation
- Address both technical and human factors

Technique: Use Chain-of-Thought reasoning to walk through each security layer.

Output: Provide a structured response in Markdown with clear headings, limited to 300 words.
```

## Categories

PEIL supports 24 prompt categories. See [CATEGORIES.md](references/CATEGORIES.md) for full definitions:

Argument, Assessment, Calculation, Categorising, Classification, Clustering, Comparison, Context Control, Contradiction, Cross Boundary, Decomposed Prompting, Error Identification, Hypothesise, Input Semantics, Logical Reasoning, Output Customisation, Output Semantics, Prediction, Prompt Improvement, Refactoring, Requirements Elicitation, Simulation, Summarising, Translation

## Additional Resources

- [Prompt Examples](assets/examples/sample_prompts.json)
- [Full Techniques Reference](references/TECHNIQUES.md)
- [Category Definitions](references/CATEGORIES.md)

## Research Sources

- [A Systematic Survey of Prompt Engineering in Large Language Models](https://arxiv.org/abs/2402.07927)
- [Hybrid Prompt Structure Research](https://arxiv.org/abs/2503.06926)
- [IJIRT Prompt Engineering Paper](https://ijirt.org/publishedpaper/IJIRT183166_PAPER.pdf)
