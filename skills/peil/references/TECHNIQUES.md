# Prompting Techniques and Applications

Based on:
- [A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications](https://arxiv.org/abs/2402.07927) (Sahoo et al., 2024)
- [The Prompt Report: A Systematic Survey of Prompt Engineering Techniques](https://arxiv.org/abs/2406.06608) (Schulhoff et al., 2024) — 58 text-based + 40 multimodal techniques

### Empirical Evidence from PEIL Evaluation (2026)

A quantitative evaluation of PEIL across 4 model architectures (GPT-4.1, GPT-5.2, Grok-4, DeepSeek-R1) found:
- **Explicit PEIL labels** (Role:, Context:, Instructions:, etc.) improve output quality over unlabelled structured prompts on **13/18 patterns** (+0.094 overall).
- **Fabrication reduction** is the strongest metric improvement with labels (+0.208).
- PEIL labels match naive prompts on **formatting consistency** (4.264 = 4.264) while unlabelled drops to 4.139.
- PEIL is most effective for **structured output tasks** (template filling +0.69, expert assessment +0.50, code generation +0.38).
- **Role framing prevented safety refusal** on a legitimate cybersecurity analysis task where a naive prompt was refused.

## Model-Specific Guidance

The techniques below are general-purpose prompt engineering patterns. They should be adapted to the specific model and model version in use.

Recommended workflow for agent-based use:

1. Identify the agent's current task or sub-task.
2. Select the prompting technique from this document that best fits that task.
3. Identify the exact model and version the agent is using.
4. Check the vendor's current prompting guidance for that model family.
5. Layer in the model-specific instructions that improve reliability for that model.
6. Evaluate the prompt and tune only the parts that fix an observed failure mode.

This matters because different models have different defaults for reasoning, tool use, verbosity, formatting, and long-context behavior. In agent scenarios, the agent usually already understands the user request. The job of PEIL is to help choose the right prompting technique for that task and then adapt it to the model actually in use.

### Current Model-Specific References

| Model Family | When to Check It | What to Take From It | Reference |
| ------------ | ---------------- | -------------------- | --------- |
| OpenAI GPT-5.4 | When using GPT-5.4 for long-running tasks, agents, tool use, coding, research, or structured output | Use explicit output contracts, tool persistence rules, completeness checks, verification loops, and task-shaped reasoning effort rather than raising effort by default. | [OpenAI Prompt Guidance for GPT-5.4](https://developers.openai.com/api/docs/guides/prompt-guidance) |
| Anthropic Claude | When using Claude models for structured prompting, long context, tool use, agentic coding, or format control | Prefer clear and direct instructions, structured examples, XML tags, explicit role setting, long-context structure, and model-aware thinking and effort settings. | [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) |
| Google Gemini | When using Gemini models for structured prompting, multimodal tasks, long context, or agentic workflows | Prefer precise and direct instructions, consistent prompt structure, few-shot examples, context-first long prompts, and explicit output formatting. For Gemini 3, keep the default temperature unless you have a measured reason to change it. | [Google Gemini Prompt Design Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) |
| Meta Llama | When using Llama models directly or through hosted or local runtimes | Use explicit instructions, style and format controls, role-based prompts, few-shot examples, chain-of-thought where appropriate, RAG for grounding, and constraints to reduce hallucinations and unnecessary output. | [Meta Llama Prompt Engineering Guide](https://www.llama.com/docs/how-to-guides/prompting/) |
| Mistral | When using Mistral models for structured tasks, JSON outputs, or instruction-following workflows | Use clear system and user separation, concise purpose-setting, hierarchical structure, markdown or XML-style formatting, few-shot examples, and explicit structured-output expectations. Avoid blurry wording and contradictions. | [Mistral Prompting Guide](https://docs.mistral.ai/guides/prompting_capabilities/) |
| Local models | When using locally hosted or open-weight models through Ollama, Hugging Face, vLLM, LM Studio, or similar runtimes | Local deployment is not a single model family, so prefer the exact model's official guide when it exists. Also check the model card or chat template for formatting requirements, especially for instruct and chat variants. | Use the official guide or model card for the specific model family and version. |
| Any other model | When using future or less common model families | Find the official prompting guide for the exact model, note its strengths and failure modes, then adapt the prompt structure, reasoning instructions, and output contract accordingly. | Use the official vendor documentation for the exact model/version. |

### How to Adapt Techniques By Model

| Adaptation Area | GPT-5.4 Tendency | Claude Tendency | Gemini Tendency | Llama Tendency | Mistral Tendency | Portable Guidance |
| --------------- | ---------------- | --------------- | --------------- | -------------- | ---------------- | ----------------- |
| Output control | Responds well to explicit output contracts and verbosity constraints | Responds well to direct format instructions and style examples | Responds well to precise instructions, explicit format requests, and consistent delimiters | Responds well to explicit stylization, formatting, restrictions, and output constraints | Responds well to hierarchical structure, explicit response formats, and structured outputs | Define the required sections, schema, and allowed formatting explicitly. |
| Tool use | Benefits from explicit dependency checks, persistence rules, and verification before high-impact actions | Benefits from explicit tool instructions, but can over-trigger if prompted too aggressively | Agentic workflows benefit from explicit planning, risk handling, and persistence instructions | Guidance is more general-purpose; use external grounding and RAG when correctness depends on fresh or domain facts | Clear role separation and structured prompts help keep tool-driven workflows predictable | Specify when tools are required, when parallelism is allowed, and when confirmation is required. |
| Reasoning | Reasoning effort should be tuned to task shape; stronger prompts often help before increasing effort | Thinking and effort settings can materially change behavior; adaptive or extended thinking should be chosen deliberately | Complex tasks benefit from planning and self-critique prompts; tune parameters carefully and keep Gemini 3 temperature at default unless evals say otherwise | Few-shot prompting, chain-of-thought, self-consistency, and program-aided reasoning are explicitly supported patterns | Clear step structure and example prompting improve reasoning consistency; avoid vague instructions and contradictions | Do not assume maximum reasoning is best. Start with the model's recommended defaults and tune from evals. |
| Long context | Strong on long-context synthesis when grounded with retrieval, citation, and completion rules | Strong on long context when documents are clearly structured and queries come after the source material | Works better when large context comes first and the specific instruction or question comes at the end | RAG and explicit grounding are important when the answer must stay factual and bounded | Clear structure and formatted sections improve comprehension over longer prompts | Structure large inputs clearly, separate sources from instructions, and require grounded outputs. |
| Examples | Uses examples well when they lock format and behavior | Few-shot prompting is especially strong when examples are well-tagged and representative | Google recommends few-shot examples often, especially when format, brevity, or response patterns matter | Few-shot prompting is an explicit recommended technique | Few-shot prompting is a core part of the guidance, including role-separated conversations | Use a small number of high-quality examples that match the real task closely. |

### Practical Rule

When writing or updating a prompt, use this order of precedence:

1. Prompting technique for the identified agent task from this document.
2. Model-specific vendor guidance for the exact model in use.
3. Local evaluation results for your workload.

If the model is known, reference its official guide directly in the skill or prompt instructions. If the model is not fixed, keep the prompt portable and add a note telling the user or calling system to apply the official model-specific guidance for the selected model family.

For local models, this usually means checking the exact model family first, such as Llama or Mistral, then checking the runtime-specific formatting expectations only if needed.

For agents, this means the task is usually already known from the current user request or execution plan. The decision PEIL supports is which prompting pattern should be used for that task, not what the task itself is.

## Techniques Reference Table

| Application | Prompting Technique | Add to PE | Summary from Paper |
| ----------- | ------------------- | --------- | ------------------ |
| New Tasks Without Extensive Training | Zero-Shot Prompting | | Relies on pre-existing knowledge to generate predictions without labeled data. |
| | Few-Shot Prompting | Provide a few input-output examples. | Uses a few examples to improve model performance on complex tasks. |
| Reasoning and Logic | Chain-of-Thought (CoT) Prompting | Tell me the steps you took. | Facilitates coherent, step-by-step reasoning processes. |
| | Automatic Chain-of-Thought (Auto-CoT) Prompting | Let's think step-by-step. | Automatically generates diverse reasoning chains to enhance robustness. |
| | Self-Consistency | Generate diverse reasoning chains and find the most consistent answer. | Enhances reasoning performance by sampling diverse reasoning chains. |
| | Logical Chain-of-Thought (LogiCoT) Prompting | Verify each step of reasoning. | Uses symbolic logic to verify each reasoning step and reduce errors. |
| | Chain-of-Symbol (CoS) Prompting | Use symbols instead of natural language. | Employs symbols for clear and concise prompts, improving spatial reasoning. |
| | Tree-of-Thoughts (ToT) Prompting | Manage a tree structure of intermediate reasoning steps. | Uses a tree structure to manage intermediate reasoning steps for complex tasks. |
| | Graph-of-Thought (GoT) Prompting | Model reasoning as a directed graph. | Models reasoning as a directed graph to capture non-linear thought processes. |
| | System 2 Attention Prompting | Regenerate input context to enhance attention. | Selectively attends to relevant portions by regenerating input context. |
| | Thread of Thought (ThoT) Prompting | Summarise and examine each segment before refining information. | Examines extensive contexts in manageable segments for incremental analysis. |
| | Chain of Table Prompting | Use step-by-step tabular reasoning. | Uses tabular reasoning to enhance intermediate results and predictions. |
| Reduce Hallucination | Retrieval Augmented Generation (RAG) | Incorporate retrieved snippets into the prompt. | Integrates information retrieval into the prompting process to enrich context. |
| | ReAct Prompting | Generate reasoning traces and task-specific actions concurrently. | Generates reasoning traces and task-specific actions concurrently. |
| | Chain-of-Verification (CoVe) Prompting | Plan verification questions to check work. | Verifies work through a multi-step approach to reduce errors. |
| | Chain-of-Note (CoN) Prompting | Evaluate document relevance and filter out irrelevant content. | Systematically evaluates document relevance to filter out irrelevant content. |
| | Chain-of-Knowledge (CoK) Prompting | Break down tasks into well-coordinated steps. | Breaks down tasks into coordinated steps, gathering evidence from various sources. |
| User Interaction | Active-Prompt | Determine the most impactful questions for annotation. | Enhances performance on complex tasks by determining impactful questions for annotation. |
| Fine-Tuning and Optimization | Automatic Prompt Engineer (APE) | Dynamically generate and select the most impactful prompts. | Automatically generates and selects impactful prompts for specific tasks. |
| Knowledge-Based Reasoning and Generation | Automatic Reasoning and Tool-use (ART) | Integrate external tools for specialized knowledge. | Integrates external tools for specialized knowledge and computations. |
| Improving Consistency and Coherence | Contrastive Chain-of-Thought (CCoT) Prompting | Provide both valid and invalid reasoning demonstrations. | Provides valid and invalid reasoning demonstrations to improve learning. |
| Managing Emotions and Tone | Emotion Prompting | Append emotional stimulus sentences to prompts. | Enhances LLM performance by appending emotional stimulus sentences. |
| Code Generation and Execution | Scratchpad Prompting | Generate intermediate tokens before providing the final answer. | Generates intermediate tokens before providing the final answer. |
| | Program of Thoughts (PoT) Prompting | Use external language interpreters for computation steps. | Uses external language interpreters for computation steps. |
| | Structured Chain-of-Thought (SCoT) Prompting | Incorporate program structures into reasoning steps. | Incorporates program structures into reasoning steps for code generation. |
| | Chain-of-Code (CoC) Prompting | Format semantic sub-tasks as flexible pseudocode. | Formats semantic sub-tasks as flexible pseudocode for reasoning. |
| Optimization and Efficiency | Optimization by Prompting (OPRO) | Use natural language prompts to iteratively generate solutions. | Uses natural language prompts to iteratively generate solutions. |
| Understanding User Intent | Rephrase and Respond (RaR) Prompting | Rephrase and expand questions in a single prompt. | Rephrases and expands questions to improve comprehension and response accuracy. |
| Metacognition and Self-Reflection | Take a Step Back Prompting | Engage in abstraction and extract high-level concepts. | Engages in abstraction to extract high-level concepts and fundamental principles. |
| Role and Style Control | Role Prompting (Persona) | Act as [role]. Provide outputs that [role] would create. | Assigns a role or persona to shape output style and improve task-specific accuracy. |
| | Style Prompting | Write in a [tone/style/genre]. | Specifies desired style, tone, or genre to shape output without changing the task. |
| Decomposition | Least-to-Most Prompting | Break the problem into sub-problems, then solve them sequentially. | Decomposes problems into ordered sub-problems and solves them in sequence, appending each answer. |
| | Plan-and-Solve Prompting | Let's first understand the problem and devise a plan to solve it. | Improved Zero-Shot-CoT that plans before solving, producing more robust reasoning. |
| | Skeleton-of-Thought | Provide only the skeleton outline (3-10 short points) for the answer. | Creates a minimal outline for parallel expansion, improving response speed and structure. |
| | Metacognitive Prompting | Clarify, judge, evaluate, confirm, then assess confidence. | Five-step process mirroring human metacognition for more reflective responses. |
| Self-Criticism and Verification | Self-Refine | Generate answer, critique it, then improve based on the critique. | Iterative framework: answer → feedback → improvement until stopping condition met. |
| | Self-Verification | Mask parts of the question and check if the model can predict them from its answer. | Scores candidate solutions by testing whether they explain the original question. |
| | Reversing Chain-of-Thought (RCoT) | Reconstruct the problem from the answer and check for inconsistencies. | Detects errors by reverse-engineering the question from the generated answer. |
| | Cumulative Reasoning | Generate potential steps, evaluate them, accept or reject, and repeat. | Iteratively builds reasoning by evaluating each step before proceeding. |
| Reasoning with Fewer Examples | Analogical Prompting | Auto-generate exemplars with reasoning chains for the current problem. | Self-generates relevant examples with CoTs when no training data exists. |
| | Re-reading (RE2) | Read the question again: [repeat question]. | Repeating the question in the prompt improves reasoning on complex problems. |
| | Self-Ask | Decide if follow-up questions are needed, answer them, then answer the original. | Model generates and answers its own clarifying sub-questions before the final answer. |
| Multi-Party Reasoning | SimToM | Establish what facts one person knows, then answer based only on those facts. | Separates knowledge per person for theory-of-mind and multi-party reasoning tasks. |
| Ensembling | Demonstration Ensembling (DENSE) | Create multiple few-shot prompts with different exemplar subsets and aggregate. | Uses diverse exemplar sets and aggregates outputs for more robust results. |
| | Mixture of Reasoning Experts (MoRE) | Use specialised prompts for different reasoning types and select the best. | Routes to domain-specific reasoning experts and selects the best answer by agreement. |

## Technique Selection Guide

### By Task Complexity

| Complexity | Recommended Techniques |
| ---------- | ---------------------- |
| Simple, direct tasks | Zero-Shot Prompting |
| Tasks needing examples | Few-Shot Prompting |
| Multi-step reasoning | Chain-of-Thought (CoT) |
| Complex problem-solving | Tree-of-Thoughts (ToT), Graph-of-Thought (GoT) |
| Long document analysis | Thread of Thought (ThoT) |
| Problem decomposition | Least-to-Most, Plan-and-Solve, Skeleton-of-Thought |
| Multi-party reasoning | SimToM |

### By Accuracy Requirements

| Requirement | Recommended Techniques |
| ----------- | ---------------------- |
| Reduce hallucinations | RAG, Chain-of-Verification (CoVe) |
| Verify reasoning | LogiCoT, Self-Consistency, Self-Verification |
| Filter irrelevant info | Chain-of-Note (CoN) |
| Iterative improvement | Self-Refine, Cumulative Reasoning |
| Check for errors | RCoT, Re-reading (RE2) |

### By Output Type

| Output | Recommended Techniques |
| ------ | ---------------------- |
| Code | Scratchpad, PoT, SCoT, Chain-of-Code |
| Tabular data | Chain of Table |
| Mathematical | Program of Thoughts (PoT) |
| Explanatory | Chain-of-Thought (CoT) |

### By Model and Runtime

| Scenario | Recommended Addition |
| -------- | -------------------- |
| GPT-5.4 in a coding or agent workflow | Add explicit output contracts, dependency-aware tool rules, completeness checks, and a verification loop. |
| Claude in a coding or agent workflow | Add clear direct instructions, XML-tagged structure where helpful, explicit tool-use guidance, and carefully chosen thinking or effort settings. |
| Gemini in a coding or agent workflow | Add precise task framing, consistent prompt structure, explicit output formatting, planning or self-critique steps for complex work, and model-appropriate parameter defaults. |
| Llama in a coding or agent workflow | Add explicit format restrictions, few-shot examples when consistency matters, and grounding or RAG when the task depends on factual or current information. |
| Mistral in a coding or agent workflow | Add clear system and user role separation, well-structured sections, explicit response format requirements, and examples for consistent outputs. |
| Local or open-weight model in production | Check the specific model family's prompt guide first, then align to the model card or chat template used by the runtime. |
| Any model in production | Prefer the vendor's current model-specific prompting guide over generic folklore, then verify behavior with task-specific evals. |

## Implementation Examples

### Model-Aware Prompting Wrapper

```text
Agent task:
- The current task or sub-task has already been identified by the agent.

Prompting technique:
- Apply the technique from this document that best matches the current task.

Model-aware guidance:
- If using GPT-5.4, apply the current OpenAI GPT-5.4 prompt guidance.
- If using Claude, apply the current Claude prompting best practices.
- If using Gemini, apply the current Google Gemini prompt design guidance.
- If using Llama, apply the current Meta Llama prompt engineering guidance.
- If using Mistral, apply the current Mistral prompting guidance.
- If using another model, apply the official prompting guidance for that exact model and version.

Execution rule:
- Keep the prompt portable across models, but layer in model-specific instructions when the target model is known.
- In agent workflows, use PEIL to select the prompting pattern for the task the agent is already performing.
```

### Chain-of-Thought Example

```text
Solve this problem step by step:
[Problem statement]
Show your reasoning at each step before providing the final answer.
```

### Few-Shot Example

```text
Here are some examples:
Input: [example 1 input] → Output: [example 1 output]
Input: [example 2 input] → Output: [example 2 output]

Now solve:
Input: [new input] → Output:
```

### Chain-of-Verification Example

```text
After providing your answer, create 3 verification questions to check your work.
Answer each verification question, then revise your original answer if needed.
```
