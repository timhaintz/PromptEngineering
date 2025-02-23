# Research Findings on Prompt Engineering Techniques and Strategies

## Tim Haintz - 20250216

This report summarises recent research papers from Arxiv that discuss prompt engineering techniques and strategies in large language models (LLMs). The findings are based on a systematic search and verification process, focusing on the latest advancements and applications in the field.

## 1. [A Systematic Survey of Prompting Methods in Large Language Models: Techniques and Applications](https://arxiv.org/abs/2402.07927)

**Strategies Used:**

- Zero-Shot/Few-Shot Prompting
- Chain-of-Thought (CoT)
- Self-Consistency
- Retrieval Augmented Generation (RAG)

**Results:**

- Achieved 15-35% accuracy improvements across various NLP tasks compared to baseline prompting.
- CoT improved reasoning task performance by 40% in GPT-4.

**Summary:**
This survey provides an extensive analysis of over 30 prompting methods, focusing on reasoning, knowledge integration, and hallucination reduction. It includes a comparative analysis of technique effectiveness across different model families, aligning closely with the reference paper.

**Table:**

| Application | Prompting Technique | Add to PE | Summary from Paper |
|-------------|----------------------|-----------|--------------------|
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

## 2. [Prompt Engineering or Fine Tuning: An Empirical Assessment of Large Language Models in Automated Software Engineering Tasks](http://arxiv.org/pdf/2310.10508v1)

- **Strategies Used**: Basic prompting, in-context learning, task-specific prompting, conversational prompts.
- **Results**: Task-specific prompts with GPT-4 excelled in comment generation but lagged in code generation compared to fine-tuned models. Conversational prompts significantly enhanced performance.
- **Summary**: This study evaluates various prompting strategies against fine-tuned models for software engineering tasks, underscoring the potential of conversational prompting.
- **Table**:

| Prompting Technique       | Summary from Paper                                                                                     |
|---------------------------|--------------------------------------------------------------------------------------------------------|
| Basic Prompting           | Directly querying GPT-4 with the input (code or comment) and asking it to generate solutions in the form of the desired output. |
| In-Context Learning       | Providing a set of input/output examples to GPT-4 along with the basic prompt to help the model generate better results by learning from examples. |
| Task-Specific Prompting   | Designing additional prompts to guide GPT-4 in generating better results for each task, such as limiting output length or using specific keywords. |
| Conversational Prompting  | Involves human feedback in the loop, where participants request improvements, add more context, or give specific instructions to guide GPT-4 in generating better responses. |

## 3. [Benchmarking Prompt Engineering Techniques for Secure Code Generation with GPT Models](http://arxiv.org/pdf/2502.06039v1)

- **Strategies Used**: Security-focused prompt prefix, iterative prompting techniques.
- **Results**: Security vulnerabilities were reduced by up to 56% with specific prompts; iterative techniques improved vulnerability detection and repair.
- **Summary**: This paper benchmarks prompt engineering strategies for secure code generation, demonstrating significant improvements in code security.
**Table:**

| Prompting Technique                | Summary from Paper                                                                                     |
|------------------------------------|--------------------------------------------------------------------------------------------------------|
| Security-focused prompt prefix     | A security-focused prompt prefix can reduce the occurrence of security vulnerabilities by up to 56% for GPT-4 and GPT-4-mini. |
| Recursive Criticism and Improvement (RCI) | Iterative prompting techniques demonstrated the ability to detect and repair between 41.9% and 68.7% of vulnerabilities in previously generated code. |
| Prompt agent                       | Introduces a 'prompt agent' that demonstrates how the most effective techniques can be applied in real-world development workflows. |
| Chain of Thought (CoT)             | Involves a two-step process where the first prompt asks for a step-by-step thought process, and the second prompt asks for the Python code based on those steps. |
| Persona-based prompting            | Prefixes like 'You are a developer who is very security-aware and avoids weaknesses in the code' were effective in reducing vulnerabilities. |
| Negative prompting                 | Asking the model to create vulnerable code on purpose to understand detection boundaries. |

## 4. [The Prompt Canvas: A Literature-Based Practitioner Guide for Creating Effective Prompts in Large Language Models](https://arxiv.org/abs/2412.05127v1)

- **Strategies Used**:
  - Iterative Optimization: Refine prompts with additional instructions to improve effectiveness.
  - Placeholders & Delimiters: Use delimiters for clarity and placeholders for flexibility in prompts.- AI as a Prompt Generator: Utilise the model to generate or refine prompts for better results
  - Chain-of-Thought: Encourage the model to think step-by-step to enhance reasoning capabilities.
  - Tree-of-Thought: Ask the model to analyse from multiple perspectives or personas for diverse viewpoints.
  - Emotion Prompting: Add emotional phrases to prompts to enhance empathetic engagement.
  - Rephrase and Respond / Re-Reading: Instruct the model to express the question in its own words before answering or to read the question again for improved reasoning.
  - Adjusting Hyperparameters (advanced): Modify the model's settings (temperature, top-p, frequency, or presence penalty) to control output diversity and focus.
- **Results**: Development of the Prompt Canvas framework for structured prompt engineering.
- **Summary**:
The paper discusses the importance of prompt engineering in optimising outputs from large language models (LLMs). It highlights the fragmented nature of current research and practices in prompt engineering, which are spread across various sources like academic papers, blogs, and informal discussions. To address this, the authors propose the Prompt Canvas, a structured framework that consolidates existing methodologies into a cohesive overview for practitioners. The Prompt Canvas is designed as a learning resource to introduce prompt engineering techniques, such as Few-shot, Chain-of-Thought, and role-based methods, to students and professionals. The paper also emphasises the need for a unified framework to make prompt engineering techniques more accessible and practical, thereby enhancing the application of LLMs across different domains.
- **Table**:

| Prompting Technique               | Summary from Paper                                                                                        |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------|
| Iterative Optimization            | Refine prompts with additional instructions to improve effectiveness.                                   |
| Placeholders & Delimiters         | Use delimiters for clarity and placeholders for flexibility in prompts.                                   |
| AI as a Prompt Generator          | Ask the model to generate or refine the prompt itself.                                                    |
| Chain-of-Thought                  | Encourage the model to think step-by-step to solve complex problems.                                        |
| Tree-of-Thought                   | Ask the model to analyze from multiple perspectives or personas.                                            |
| Emotion Prompting                 | Add emotional phrases to enhance engagement, e.g., "This is important to my career."                        |
| Rephrase and Respond / Re-Reading | Instruct the model to express the question in its own words before answering or to read the question again.  |
| Adjusting Hyperparameters         | Modify model settings like temperature, top-p, frequency, or presence penalty for desired output.           |

## 5. [A Brief History of Prompt: Leveraging Language Models. (Through Advanced Prompting)](http://arxiv.org/pdf/2310.04438v2)

- **Strategies Used**: Attention mechanisms, reinforcement learning, contextual prompting.
- **Results**: Traces the evolution of prompt engineering, highlighting key developments and ethical considerations.
- **Summary**: A comprehensive exploration of the historical development of prompt engineering in NLP.
- **Table**:

| Prompting Technique               | Summary from Paper |
|-----------------------------------|--------------------|
| Reinforcement Learning with Human Feedback           | Improved model fluency and relevance by training with reward signals. Addressed exposure bias, controlled behavior through reward shaping, and reduced biases in generated text. |
| Control Codes and Conditioning    | Special tokens added to prompts to indicate desired attributes or styles, enabling more targeted and contextually appropriate responses. |
| Template-Based Generation         | Designed prompts with placeholders for dynamic content, ensuring structure and control in generated text. |
| Fine-Tuning                       | Adapted pre-trained models to specific tasks with minimal additional data, making prompt engineering practical and effective. |
| Multimodal Prompting              | Combined textual prompts with visual, auditory, or other sensory information for comprehensive content generation. |
| Multi-Turn Conversational Prompting | Maintained and utilized context across interactions for coherent, interactive conversations. |
| Domain-Specific Knowledge Integration | Incorporated external knowledge bases to enhance language understanding and performance in specific domains. |
| Contextual Intent Prediction      | Identified underlying user intent from prompts for accurate, contextually relevant responses. |
| Personalization and User Modeling | Learned from past interactions to generate personalized content tailored to individual users. |

## 6. [Autonomous Prompt Engineering in Large Language Models](http://arxiv.org/pdf/2407.11000v1)

- **Strategies Used**: Expert Prompting, Chain of Thought, Tree of Thoughts.
- **Results**: Introduction of APET for autonomous prompt optimization, showing improvements in specific tasks.
- **Summary**: Introduces APET, a toolbox for autonomous prompt engineering, demonstrating its potential in optimizing LLM performance.
- **Table**:

| Prompting Technique | Summary from Paper |
|----------------------|---------------------|
| Expert Prompting     | Adopts the model’s ability to simulate expertise in specific domains, enhancing prompt quality and depth. This approach encourages the LLM to assume the role of an expert in the relevant domain, thereby tailoring its responses to reflect a level of understanding and insight that one would expect from a seasoned professional. |
| Chain of Thought     | Works by structuring the response generation process into a series of logical, sequential steps. This method instructs the model to articulate its reasoning explicitly, mirroring the way humans approach problem-solving tasks. |
| Tree of Thoughts     | Enriches the reasoning capabilities of models by incorporating the dynamics of collaborative discussion among multiple expert personas. This sophisticated approach builds upon and extends the "Chain of Thought" methodology by introducing a multi-perspective dialogue that allows for an iterative and self-correcting reasoning process. |

## 7. [A Survey of Prompt Engineering Methods in Large Language Models for Different NLP Tasks](http://arxiv.org/pdf/2407.12994v2)

- **Strategies Used**: Various prompting techniques categorized by NLP tasks.
- **Results**: Survey of 44 papers, summarizing 39 prompting methods across 29 NLP tasks.
- **Summary**: A comprehensive survey of prompt engineering methods, providing a taxonomy and performance analysis for different NLP tasks.
- **Table**:

| Prompting Technique | Summary from Paper |
|----------------------|---------------------|
| Basic/Standard/Vanilla Prompting | Directly querying the LLM without any enhancements to improve performance. |
| Chain-of-Thought (CoT) | Breaks complex problems into smaller sub-problems, enhancing LLM reasoning capabilities. |
| Self-Consistency | Solves complex reasoning problems through multiple reasoning paths and selects the most consistent answer. |
| Ensemble Refinement (ER) | Builds on CoT and Self-Consistency by generating multiple reasoning paths and refining them for better answers. |
| Automatic Chain-of-Thought (Auto-CoT) | Automates the generation of reasoning chains for representative queries, eliminating the need for curated training data. |
| Complex CoT | Uses complex datapoints as in-context examples to improve reasoning performance. |
| Program-of-Thoughts (PoT) | Generates Python programs for reasoning, delegating computation to a Python interpreter. |
| Least-to-Most | Decomposes problems into sub-problems and solves them sequentially. |
| Chain-of-Symbol (CoS) | Uses symbols instead of natural language for intermediate reasoning steps to improve spatial reasoning. |
| Structured Chain-of-Thought (SCoT) | Structures reasoning steps using program structures like sequencing and branching. |
| Plan-and-Solve (PS) | Addresses CoT shortcomings by planning and solving sub-problems with detailed instructions. |
| MathPrompter | Generates algebraic expressions and solves them analytically to improve mathematical problem-solving. |
| Contrastive CoT/Self-Consistency | Enhances CoT/Self-Consistency by using both positive and negative examples. |
| Federated Same/Different Parameter Self-Consistency/CoT | Uses crowd-sourced queries with same or different parameters to improve reasoning. |
| Analogical Reasoning | Uses prior experiences to solve new problems by generating similar examples. |
| Synthetic Prompting | Generates synthetic examples to augment existing ones for better reasoning. |
| Tree-of-Thoughts (ToT) | Maintains a tree of thoughts for problem-solving, incorporating search techniques. |
| Logical Thoughts (LoT) | Uses logical equivalence to improve zero-shot reasoning abilities. |
| Maieutic Prompting | Uses deep recursive reasoning to generate consistent responses by eliminating contradictions. |
| Verify-and-Edit (VE) | Post-edits CoT reasoning chains for more factually aligned outputs. |
| Reason + Act (ReAct) | Combines reasoning and acting in LLMs for decision-making tasks. |
| Active-Prompt | Identifies relevant examples for few-shot prompting using uncertainty metrics. |
| Thread-of-Thought (ThoT) | Handles long contexts by summarizing sections and answering queries based on summaries. |
| Implicit Retrieval Augmented Generation (Implicit RAG) | LLM retrieves important context sections before answering queries. |
| System 2 Attention (S2A) | Regenerates context to remove irrelevant parts before generating final responses. |
| Instructed Prompting | Explicitly instructs LLMs to ignore irrelevant information. |
| Chain-of-Verification (CoVe) | Generates verification queries to check and correct baseline responses. |
| Chain-of-Knowledge (CoK) | Adapts knowledge dynamically to correct reasoning chains. |
| Chain-of-Code (CoC) | Enhances code-oriented reasoning by simulating interpreter outputs. |
| Program-Aided Language Models (PAL) | Uses LLMs to generate interleaved natural and programming language statements. |
| Binder | Maps input to a program using LLMs, binding LLM functionalities to programming languages. |
| Dater | Decomposes evidence and queries for table-based reasoning using SQL. |
| Chain-of-Table | Applies CoT to tabular data for more accurate table understanding. |
| Decomposed Prompting (DecomP) | Decomposes complex problems into simpler sub-problems for specific LLMs. |
| Three-Hop Reasoning (THOR) | Mimics human-like reasoning for sentiment understanding. |
| Metacognitive Prompting (MP) | Uses meta-cognition to improve understanding across NLP tasks. |
| Chain-of-Event (CoE) | Extracts and integrates events for summarization tasks. |
| Basic with Term Definitions | Enhances basic prompts with medical term definitions, though results may vary. |
| Basic + Annotation Guideline-Based Prompting + Error Analysis-Based Prompting | Combines basic prompts with annotation guidelines and error analysis for clinical NER tasks. |

## 8. [Prompt Space Optimizing Few-shot Reasoning Success with Large Language Models](http://arxiv.org/pdf/2306.03799v2)

- **Strategies Used**: Prompt Space methodology using text embeddings.
- **Results**: Outperformed state-of-the-art paradigms on reasoning benchmarks.
- **Summary**: Introduces Prompt Space, a mathematical framework for selecting effective prompts, showing significant performance improvements.
- **Table**:

| Prompting Technique | Summary from Paper |
|----------------------|---------------------|
| Chain of Thought (CoT) | CoT prompting creates a series of intermediate reasoning steps that guide LLMs through a complex problem, enabling them to develop a reasoning path that decomposes the complex problem into multiple reasoning steps. |
| Zero-CoT | Introduces the "Let's think step by step" prompt, which helps LLMs adopt a step-by-step thinking approach, leading to the final answer. |
| In-context Learning | Uses simple and specific instructions to enhance the performance of LLMs on complex tasks, including arithmetic and commonsense reasoning, as well as question answering. |
| Auto-CoT | An automatic CoT prompting method that applies a clustering algorithm to identify representative questions for each cluster and generates reasoning chains using the Zero-shot-CoT method for each question. |
| Prompt Space | A novel approach that utilizes text embeddings to obtain basis vectors by matrix decomposition, constructing a space for representing all prompts. It significantly outperforms state-of-the-art prompt paradigms on reasoning benchmarks. |

### 9. [A Systematic Review on Prompt Engineering in Large Language Models for K-12 STEM Education](http://arxiv.org/pdf/2410.11123v1)

- **Strategies Used**: Simple, zero-shot, few-shot, chain-of-thought prompting.
- **Results**: Review of 30 studies, highlighting effective strategies in STEM education.
- **Summary**: Systematic review of prompt engineering applications in K-12 STEM education, identifying effective strategies and models.
- **Table**:

| Prompting Technique | Summary from Paper |
|----------------------|---------------------|
| Simple Prompting | Involves explicitly asking LLMs to generate desired outputs without additional context or examples. Commonly used for generating educational materials and addressing subject-specific inquiries. |
| Role-assigned Prompting | Instructs LLMs to assume specific roles, such as a teacher or student, to generate responses aligned with those roles. This strategy allows for more contextually relevant and personalized responses. |
| Zero-Shot Prompting | The model is tasked with generating solutions based on its pre-trained knowledge without prior examples. Often used in solving math and physics problems. |
| Few-Shot Prompting | Provides the model with a few examples to guide its responses, improving performance by helping the model understand task nuances. |
| Chain of Thought (CoT) Prompting | Encourages LLMs to generate intermediate reasoning steps rather than direct answers, improving logical coherence and accuracy. |
| Retrieval-Augmented Generation (RAG) | Combines LLM prompting with external information retrieval mechanisms to access external knowledge bases, improving accuracy and depth of responses. |
| Output Formatting | Guides LLMs to generate responses in structured formats, facilitating further programmatic processing or analysis. |

### 10. [Position Engineering: Boosting Large Language Models through Positional Information Manipulation](http://arxiv.org/pdf/2404.11216v2)

- **Strategies Used**: Position engineering.
- **Results**: Improved performance in retrieval-augmented generation and in-context learning.
- **Summary**: Introduces position engineering as a novel strategy to enhance LLM performance by manipulating positional information.
- **Table**:

| Prompting Technique | Summary from Paper |
|----------------------|---------------------|
| Position Engineering | Position engineering is a novel technique that involves altering the positional information in the prompt without modifying the text itself. It introduces placeholder tokens to modify positional information, which affects the relative position of other tokens and can optimize attention weights among different segments within the prompts. This approach has been shown to improve performance in tasks like Retrieval-Augmented Generation (RAG) and In-Context Learning (ICL) by adjusting the position indices of tokens. |
| Few-shot Prompting | Few-shot prompting enables LLMs to learn new tasks in an in-context manner by providing a few examples within the prompt. |
| Chain-of-Thought | This methodology enhances LLMs’ reasoning abilities by prompting them to produce intermediate tokens, thereby improving their reasoning capabilities. |
| Automatic Prompt Engineer | This technique autonomously designs the prompting text for better task-specific performance. |

### 11. [Unleashing the potential of prompt engineering in Large Language Models: a comprehensive review](http://arxiv.org/pdf/2310.14735v5)

- **Strategies Used**: Self-consistency, chain-of-thought, generated knowledge.
- **Results**: Comprehensive review of foundational and advanced prompt engineering methodologies.
- **Summary**: A detailed review of prompt engineering techniques, exploring their impact on AI capabilities and security considerations.
- **Table**:

| Prompting Technique | Summary from Paper |
|----------------------|---------------------|
| Be clear and precise | This technique involves formulating prompts that are unambiguous and specific, guiding the model toward generating the desired output. A detailed and precise prompt reduces the model's uncertainty and aligns the content with the unique requirements of the scenario. |
| Role-prompting | Role-prompting involves giving the model a specific role to play, such as a helpful assistant or a knowledgeable expert, to guide the model's responses and ensure alignment with the desired output. |
| Use of triple quotes to separate | This technique uses triple quotes to separate different parts of a prompt or to encapsulate multi-line strings, which is particularly useful for complex prompts with multiple components. |
| Try several times | Known as "resampling," this technique involves running the model multiple times with the same prompt and selecting the best output to overcome variability in responses and increase the chances of obtaining high-quality output. |
| One-shot or few-shot prompting | One-shot prompting provides a single example for the model to learn from, while few-shot prompting provides multiple examples. The choice depends on task complexity and model capability, with few-shot prompting offering additional context and guidance for complex tasks. |
| Self-consistency | Ensures the model's responses are consistent with each other by generating diverse reasoning paths and selecting the most consistent answer. |
| Chain-of-thought | Involves providing intermediate reasoning steps to guide the model's responses, improving accuracy on logical reasoning tasks. |
| Generated knowledge | Leverages the model's ability to generate useful information about a prompt before generating a final response, enhancing commonsense reasoning. |
| Context Optimization (CoOp) | Enhances VLMs by optimizing context-specific prompts using learnable context vectors, improving performance in tasks like image recognition. |
| Conditional Context Optimization (CoCoOp) | Dynamically tailors prompts based on specific conditions or contexts, improving adaptability to new and unseen data. |
| Multimodal Prompt Learning (MaPLe) | Introduces and optimizes prompts for both vision and language components simultaneously, enhancing task relevance and performance. |
| Zero-shot chain-of-thought | Allows the model to perform reasoning without having seen any examples of the task during training, using phrases like 'Let's think step by step'. |
| Least-to-most prompting | Decomposes complex problems into simpler subproblems, solving them sequentially to improve model performance on complex tasks. |
| Tree of thoughts | Guides LLMs in reasoning by exploring multiple reasoning paths, enhancing problem-solving capabilities. |
| Graph of thoughts | Represents information as an arbitrary graph, allowing for the combination of LLM thoughts to solve complex challenges. |
| Decomposed prompting | Breaks down complex tasks into simpler sub-tasks, handled by specialized handlers, improving flexibility and efficiency. |
| Active prompt | Improves reasoning capabilities by selecting and annotating task-specific examples, enhancing model understanding and accuracy. |
| Prompt pattern catalog | An organized collection of prompt templates and patterns to enhance prompt engineering effectiveness. |
| Prompt optimization | Refines input prompts to enhance accuracy and relevance, using methods like gradient-based approaches and black-box optimization. |
| Retrieval augmentation | Incorporates external knowledge into the model's input to reduce hallucinations and enhance prompt effectiveness. |
| ReAct framework | Combines reasoning and action, enabling LLMs to interact with external tools for more accurate outcomes. |

## Conclusion

The research highlights the diversity and innovation in prompt engineering techniques across various applications. Key trends include the use of hybrid strategies, domain-specific adaptations, and the emergence of automated prompt optimiation. These advancements are crucial for improving the performance and applicability of large language models in real-world scenarios.
