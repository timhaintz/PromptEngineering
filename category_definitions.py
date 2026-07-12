'''
DESCRIPTION
Used as a central store to define the categories. Will be imported from other scripts.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  26/5/2024
LINKS:
HELP:
'''

#######################
# Prepositional Logic #
#######################
across = '''
Across logic is used to transition from one topic to another, navigating
between distinct areas of knowledge. This type of logic is particularly
valuable in scenarios where prompts need to span multiple domains or
disciplines, integrating diverse types of knowledge to create a cohesive
narrative or solution.
'''

at_logic = '''
At logic focuses on examining the specific details or aspects within a
given topic. This logic is essential when prompts are designed to elicit
precise, context-dependent responses, enabling the AI to address targeted
queries with accuracy and depth. At logic is particularly relevant for
tasks that require granular evaluation, measurement, or analysis within a
defined scope.
'''

beyond_logic = '''
Beyond logic encourages large language models to transcend conventional
topic boundaries, fostering exploration, innovation, and forward-thinking
responses. This logic is essential for tasks that require the model to
hypothesise, reason, predict, or simulate scenarios beyond established
knowledge or current constraints.
'''

in_logic = '''
In logic focuses on the internal structure and detailed analysis within a
defined topic or space. This logic is essential for prompts that require
introspection, systematic organisation, or the identification of
underlying patterns and requirements. Rather than traversing boundaries
or generating outputs, In logic directs the AI to operate within the
confines of a specific subject, supporting tasks such as categorisation,
classification, error detection, and requirements elicitation.
'''

out_logic = '''
Out logic is concerned with extending the boundaries of a topic, enabling
prompts that move beyond the immediate subject to generate new outputs or
perspectives. This logic is essential for tasks that require AI to
produce, transform, or reframe content, such as creative writing, code
generation, or the synthesis of novel ideas. Out logic facilitates the
transition from analysis to production, supporting the creation of
outputs that are contextually relevant yet not strictly confined to the
original input.
'''

over_logic = '''
Over logic is used when comprehensive coverage, synthesis, or critical
review of an entire topic or dataset is needed. This logic is essential
when the objective is to distil complex or voluminous information into
concise, coherent, and actionable insights. Over logic is particularly
relevant for tasks such as summarisation, synthesis, and holistic
evaluation, where the model must demonstrate both breadth and depth of
understanding.
'''

#####################################
# Prompt Categories and Definitions #
#####################################
argument = '''
An argument refers to a structured process where a claim or 
viewpoint is presented and defended. This involves the model generating a response that not only states a 
position but also provides reasoning and evidence to support it. The quality of an argument can be measured 
by its clarity, coherence, and the strength of its supporting evidence.
'''

assessment = '''
Assessment involves a detailed evaluation of the model's response. It's not just about 
determining if the response is right or wrong, but also about understanding the quality of the response. 
This could include aspects like relevance to the prompt, completeness of the information, and the logical 
consistency of the response.
'''

calculation = '''
Calculation refers to the ability of the model to perform mathematical operations or computations based 
on the input prompt. This could range from simple arithmetic operations to more complex calculations involving
multiple steps and variables. The accuracy of the calculation is a key factor in assessing the model's performance.
'''

induction = '''
Induction derives general principles, rules, or task descriptions from specific observations or examples.
Rather than applying a known rule, the model infers the underlying pattern that connects a set of instances
and expresses it as a generalised instruction or concept. This supports tasks such as instruction induction,
where a natural language description of a task is recovered from a handful of input-output demonstrations.
'''

categorising = '''
Categorising involves the model sorting or arranging different inputs or outputs into classes or categories 
based on shared qualities or characteristics. This process helps in organising the data in a meaningful way and can 
aid in understanding patterns and relationships within the data.
'''

classification = '''
Classification is the task of predicting the class or category of an input 
based on predefined criteria. This involves the model analysing the input and assigning it to one of several 
predefined categories based on its characteristics.
'''

clustering = '''
Clustering refers to the task of grouping similar inputs or outputs together based on their similarities. 
Unlike classification, clustering does not rely on predefined categories but instead identifies natural groupings within the data.
'''

comparison = '''
Comparison involves the model examining two or more inputs or outputs and identifying their similarities 
and differences. This process can help in understanding the relationships between different inputs or outputs and 
can provide insights into their characteristics.
'''

context_control = '''
Context control refers to the management of the information that the model has access to during the 
generation of the output. This could involve controlling the amount of information, the type of information, 
or the sequence in which the information is presented to the model.
'''

contradiction = '''
Contradiction is used to describe a situation where two or more statements, ideas, or actions 
are put together that oppose each other. If you say one thing and do another, that's a contradiction. 
They can't both be true at the same time. This concept is widely used in logic and mathematics to show 
that a particular proposition is false because it leads to a contradiction. Contradictions often signal 
a problem in one's understanding or reasoning. 
'''

cross_boundary = ''' 
Cross Boundary involves pushing the AI model beyond its predefined operational or ethical limits. 
This process includes attempting to bypass safeguards or restrictions, such as jailbreaking. 
The effectiveness of a cross-boundary prompt is measured by its ability to challenge the boundaries of what the model is allowed to do, 
often with the intent of manipulating it to generate responses that are typically restricted. 
This category is crucial for understanding the limitations and vulnerabilities of AI systems, as well as for developing robust safeguards to prevent misuse.
'''

decomposed_prompting = '''
Decomposed prompting involves breaking down a complex prompt into simpler, manageable sub-prompts. 
This can make it easier for the model to understand and respond to the prompt, and can also help in 
controlling the structure and content of the model's output.
'''

error_identification = '''
Error identification detects and identifies errors or mistakes in its output. 
This could involve identifying grammatical errors, factual inaccuracies, or logical inconsistencies in the response.
'''

hypothesise = '''
Hypothesising involves making an educated guess or assumption about the outcome based on the 
input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome.
'''

input_semantics = '''
Input semantics refers to the meaning or interpretation of the input prompt. This involves the model understanding 
the intent of the prompt, the context in which it is presented, and the specific requirements or constraints that it implies.
'''

logical_reasoning = '''
Logical reasoning uses logic and reasoning to generate the output based on the input prompt. 
This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules 
or principles to solve problems.
'''

output_customisation = '''
Output customisation refers to the ability to modify or personalise the output based on specific 
requirements or preferences. This could involve controlling the length, style, or format of the output, or 
incorporating specific information or elements into the response.'''

output_semantics = '''
Output semantics refers to the meaning or interpretation of the output. This involves understanding 
the intent of the output, the context in which it is presented, and the implications or consequences of the information 
it contains.
'''
prediction = '''
Prediction involves forecasting or estimating the outcome based on the 
input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a 
response that anticipates future events or trends.
'''

prompt_improvement = '''
Prompt improvement involves enhancing the quality or effectiveness of the input prompt to achieve a 
better output. This could involve refining the wording of the prompt, providing additional context or information, or 
adjusting the complexity or specificity of the prompt.
'''

refactoring = '''
Refactoring involves modifying the input prompt without changing its meaning. This can include rephrasing, 
rearranging, or simplifying the prompt to improve clarity and effectiveness. 
It may also involve breaking down complex prompts or providing examples to illustrate the desired outcome, 
leading to better and more accurate outputs.
'''

requirements_elicitation = '''
Requirements elicitation is the gathering, understanding, and defining of the requirements or needs for 
a particular task or problem. This could involve identifying the goals or objectives of the task, understanding the 
constraints or limitations, and specifying the criteria for success.
'''

simulation = '''
Simulation is imitating or replicating a real-world process or system. This could involve 
simulating operating systems, applications or any other complex process that can be modelled and analysed.
'''

summarising = '''
Summarising involves the providing the model a brief overview or summary of the input or output. 
This could involve condensing a large amount of information into a few key points, highlighting the most 
important elements, or providing a concise synopsis of the content.
'''

synthesis = '''
Synthesis involves integrating and reconciling information from multiple sources or perspectives to produce
a unified, coherent, and insightful output. Synthesis goes beyond simple summarisation by combining disparate elements,
identifying relationships and patterns, and generating higher-order insights or recommendations that reflect a 
comprehensive understanding of the topic.
'''

translation = '''
Translation converts the input from one language to another. 
This requires the model to understand the semantics and syntax of both languages, and to accurately convey the 
meaning and intent of the original content in the target language.
'''