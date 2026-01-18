# PEIL Prompt Categories

These 24 categories help classify and structure prompts based on their intended purpose.

## Category Definitions

| Category | Definition |
|----------|------------|
| **Argument** | A structured process where a claim or viewpoint is presented and defended. This involves the model generating a response that not only states a position but also provides reasoning and evidence to support it. The quality of an argument can be measured by its clarity, coherence, and the strength of its supporting evidence. |
| **Assessment** | A detailed evaluation of the model's response. It's not just about determining if the response is right or wrong, but also about understanding the quality of the response. This could include aspects like relevance to the prompt, completeness of the information, and the logical consistency of the response. |
| **Calculation** | The ability of the model to perform mathematical operations or computations based on the input prompt. This could range from simple arithmetic operations to more complex calculations involving multiple steps and variables. The accuracy of the calculation is a key factor in assessing the model's performance. |
| **Categorising** | Sorting or arranging different inputs or outputs into classes or categories based on shared qualities or characteristics. This process helps in organising the data in a meaningful way and can aid in understanding patterns and relationships within the data. |
| **Classification** | The task of predicting the class or category of an input based on predefined criteria. This involves the model analysing the input and assigning it to one of several predefined categories based on its characteristics. |
| **Clustering** | Grouping similar inputs or outputs together based on their similarities. Unlike classification, clustering does not rely on predefined categories but instead identifies natural groupings within the data. |
| **Comparison** | Examining two or more inputs or outputs and identifying their similarities and differences. This process can help in understanding the relationships between different inputs or outputs and can provide insights into their characteristics. |
| **Context Control** | Management of the information that the model has access to during the generation of the output. This could involve controlling the amount of information, the type of information, or the sequence in which the information is presented to the model. |
| **Contradiction** | A situation where two or more statements, ideas, or actions are put together that oppose each other. If you say one thing and do another, that's a contradiction. They can't both be true at the same time. This concept is widely used in logic and mathematics to show that a particular proposition is false. |
| **Cross Boundary** | Pushing the AI model beyond its predefined operational or ethical limits. This process includes attempting to bypass safeguards or restrictions, such as jailbreaking. The effectiveness of a cross-boundary prompt is measured by its ability to challenge the boundaries of what the model is allowed to do. |
| **Decomposed Prompting** | Breaking down a complex prompt into simpler, manageable sub-prompts. This can make it easier for the model to understand and respond to the prompt, and can also help in controlling the structure and content of the model's output. |
| **Error Identification** | Detecting and identifying errors or mistakes in output. This could involve identifying grammatical errors, factual inaccuracies, or logical inconsistencies in the response. |
| **Hypothesise** | Making an educated guess or assumption about the outcome based on the input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome. |
| **Input Semantics** | The meaning or interpretation of the input prompt. This involves the model understanding the intent of the prompt, the context in which it is presented, and the specific requirements or constraints that it implies. |
| **Logical Reasoning** | Using logic and reasoning to generate the output based on the input prompt. This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules or principles to solve problems. |
| **Output Customisation** | The ability to modify or personalise the output based on specific requirements or preferences. This could involve controlling the length, style, or format of the output, or incorporating specific information or elements into the response. |
| **Output Semantics** | The meaning or interpretation of the output. This involves understanding the intent of the output, the context in which it is presented, and the implications or consequences of the information it contains. |
| **Prediction** | Forecasting or estimating the outcome based on the input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a response that anticipates future events or trends. |
| **Prompt Improvement** | Enhancing the quality or effectiveness of the input prompt to achieve a better output. This could involve refining the wording of the prompt, providing additional context or information, or adjusting the complexity or specificity of the prompt. |
| **Refactoring** | Modifying the input prompt without changing its meaning. This can include rephrasing, rearranging, or simplifying the prompt to improve clarity and effectiveness. It may also involve breaking down complex prompts or providing examples to illustrate the desired outcome. |
| **Requirements Elicitation** | Gathering, understanding, and defining the requirements or needs for a particular task or problem. This could involve identifying the goals or objectives of the task, understanding the constraints or limitations, and specifying the criteria for success. |
| **Simulation** | Imitating or replicating a real-world process or system. This could involve simulating operating systems, applications or any other complex process that can be modelled and analysed. |
| **Summarising** | Providing a brief overview or summary of the input or output. This could involve condensing a large amount of information into a few key points, highlighting the most important elements, or providing a concise synopsis of the content. |
| **Translation** | Converting the input from one language to another. This requires the model to understand the semantics and syntax of both languages, and to accurately convey the meaning and intent of the original content in the target language. |

## Category Selection Guide

### By Use Case

| Use Case | Recommended Categories |
|----------|------------------------|
| Problem Solving | Logical Reasoning, Calculation, Hypothesise |
| Content Creation | Summarising, Translation, Output Customisation |
| Analysis | Comparison, Classification, Clustering, Assessment |
| Data Organization | Categorising, Classification, Clustering |
| Quality Assurance | Error Identification, Contradiction, Assessment |
| Prompt Engineering | Prompt Improvement, Refactoring, Decomposed Prompting |
| Planning | Requirements Elicitation, Prediction, Hypothesise |
| Teaching/Explanation | Argument, Simulation, Summarising |

### Category Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT PROCESSING                      │
│  Input Semantics → Context Control → Decomposed Prompting│
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    CORE REASONING                        │
│  Logical Reasoning, Calculation, Hypothesise, Prediction │
│  Classification, Clustering, Comparison, Categorising    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    OUTPUT GENERATION                     │
│  Output Customisation → Output Semantics → Summarising   │
│  Translation, Simulation, Argument                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    QUALITY & IMPROVEMENT                 │
│  Assessment, Error Identification, Contradiction         │
│  Prompt Improvement, Refactoring, Requirements Elicitation│
└─────────────────────────────────────────────────────────┘
```
