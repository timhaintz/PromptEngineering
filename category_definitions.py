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
Across logic is used to transition from one topic to another, navigating between distinct areas of knowledge. This type of logic is particularly valuable in scenarios where prompts need to span **multiple domains** or disciplines, integrating diverse types of knowledge to create a cohesive narrative or solution.

The PP categories under across logic include:
1. **Argument**: Refers to a structured process where a claim or viewpoint is presented and defended. This type of prompt enables the AI model to generate a response that not only states a position, but also provides reasoning and evidence to support it.
2. **Comparison**: Examining two or more objects and identifying their similarities and differences. This type of prompt helps in exploring the relationships between different objects, and discovering insights from their characteristics.
3. **Contradiction**: Refers to presenting opposing statements or viewpoints that cannot be true simultaneously. This type of prompt enables the AI model to recognise and articulate conflicting information, helping in critical reasoning by evaluating inconsistencies and detecting logical errors.
4. **Cross Boundary**: Involves pushing the AI model beyond its predefined operational or ethical limits, such as attempting to bypass safeguards or restrictions (e.g., jailbreaking). This type of prompt challenges the boundaries of what the model is allowed to do, often with the intent of manipulating it to generate responses that are typically restricted.
5. **Translation**: Refers to converting data from one interpretation to another while preserving the original meaning. This type of prompt helps humans understand complex concepts by transforming information into a more familiar or accessible format.
'''

at_logic = '''
At logic is utilised to denote a more granular aspect or detail of the overarching topic. This concept is particularly pertinent when the prompts are tailored to a specific context or scenario, with the objective of eliciting precise responses.

Prompt engineering is a process that involves the creation of prompts to guide an artificial intelligence model’s responses. The prompts serve as a catalyst, steering the model’s output in a direction that aligns with the desired outcome. In this context, at logic is a crucial component of this process, as it pertains to the creation of prompts that are context-specific or scenario-specific.

For instance, if the scenario involves a user seeking advice on a technical issue, at logic would encompass prompts that are specifically designed to address technical queries. These prompts would be engineered in such a way that they target precise responses, thereby ensuring that the user’s query is addressed in a comprehensive and accurate manner.

In essence, at logic in prompt engineering is about honing in on the specifics of a given context or scenario. It is about crafting prompts that are not just relevant, but also precise, thereby enabling the AI model to generate responses that are both accurate and contextually appropriate. 

At logic is a fundamental element in the process of prompt engineering, playing a pivotal role in the creation of context-specific prompts that target precise responses. Its significance lies in its ability to enhance the relevance and accuracy of the AI model’s responses, thereby improving the overall user experience.

The PP categories under at logic include:
1. **Assessment**: Provides a comprehensive evaluation of the input, verifying its correctness, providing feedback, and considering factors such as the completeness of the information, ratings, and the input’s relevance to the context. 
2. **Calculation**: Is the capability to execute mathematical operations, ranging from simple arithmetic to complex multi-step computations with various variables, with the accuracy of these calculations being crucial to the model’s performance evaluation. 
'''

beyond_logic = '''
Beyond logic is used to discuss aspects that lie beyond the conventional boundaries of a topic, pushing the limits of what is typically explored. This type of logic is instrumental in crafting prompts that challenge the AI to explore **new capabilities** or **innovative ideas**, thereby extending its functional and conceptual horizons. By employing beyond logic, we can design prompts that encourage the AI to venture into uncharted territories, fostering creativity and innovation. This approach not only enhances the AI's ability to generate novel and forward-thinking responses but also its capacity to adapt to emerging trends and technologies. For instance, beyond logic can be used to explore futuristic scenarios, hypothesise about potential advancements, or integrate cutting-edge research into the AI's responses. This not only enriches the user experience but also positions the AI as a tool for pioneering thought and discovery.

The PP categories under beyond logic include:
1. **Hypothesise**: Making an educated guess or assumption about the outcome based on the input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome.
2. **Logical Reasoning**: Using logic and reasoning to generate the output based on the input prompt. This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules or principles to solve problems.
3. **Prediction**: Forecasting or estimating the outcome based on the input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a response that anticipates future events or trends.
4. **Simulation**: Imitating or replicating a real-world process or system. This could involve simulating operating systems, applications or any other complex process that can be modelled and analysed.
'''

in_logic = '''
In logic specifically focuses on the intricacies and details within a given topic. The logic is often employed to denote the encapsulation of a particular subject matter or space. This encapsulation can be perceived as a boundary that delineates the scope of a system’s introspective analysis or self-reflection. For example, when we refer to prompts that are internal to a system, we are discussing prompts that direct the system to engage in a form of self-analysis or introspection. These prompts are designed to trigger internal processes, rather than external interactions.

The PP categories under in logic include:
1. **Categorising**: Sorts or arranges different inputs or outputs into classes or categories based on shared qualities or characteristics, aiding in data organisation and pattern recognition.
2. **Classification**: Refers to predicting the class or category of an input based on predefined criteria, enabling more precise analysis and interpretation.
3. **Clustering**: Identifying natural groupings within the data or topic without pre-established categories, often revealing hidden patterns or relationships.
4. **Error Identification**: Focuses on pinpointing inaccuracies, inconsistencies, or logical fallacies within the topic, aiding in refining and improving the quality of the information or argument.
5. **Input Semantics**: Understanding and interpreting the meaning and context of the inputs related to the topic, ensuring the AI accurately grasps the nuances of the discussion.
6. **Requirements Elicitation**: Identifying and defining the specific needs or conditions that must be met within the topic, crucial for tasks that involve planning, development, or specification.
'''

out_logic = '''
Out logic is employed to convey the idea of expanding upon or moving beyond the general scope of a topic. This type of logic is particularly useful for prompts that aim to generate **outputs**, such as creative writing, code generation, or other forms of content creation. By utilising out logic, we can design prompts that encourage the AI to think outside the box, producing outputs that are not only relevant but also innovative and imaginative. This approach enhances the AI's ability to contribute to creative processes, whether it be crafting compelling narratives, developing complex algorithms, or generating unique solutions to problems. For instance, out logic can be used to prompt the AI to write a story that explores new genres, generate code that implements novel functionalities, or create art that pushes the boundaries of traditional aesthetics. In essence, out logic in prompt engineering is about expanding the AI's creative and productive capabilities, enabling it to produce high-quality, original outputs that enrich the user experience and drive innovation.

The PP categories under out logic include:
1. **Context Control**: involves managing the context in which the AI operates to ensure that the responses are accurate and relevant. This could involve providing additional background information, setting specific parameters or constraints, or guiding the AI to focus on particular aspects of the topic.
2. **Decomposed Prompting**: refers to breaking down complex tasks into simpler, more manageable components. This approach allows the AI to tackle each part of the task individually, leading to more accurate and comprehensive outputs.
3. **Output Customisation**: Output customisation refers to the ability to modify or personalise the model’s output based on specific requirements or preferences. This could involve controlling the length, style, or format of the output, or incorporating specific information or elements into the response.
4. **Output Semantics**: refers to the meaning or interpretation of the model’s output. This involves understanding the intent of the output, the context in which it is presented, and the implications or consequences of the information it contains.
5. **Prompt Improvement**: involves enhancing the quality or effectiveness of the input prompt to achieve a better output. This could involve refining the wording of the prompt, providing additional context or information, or adjusting the complexity or specificity of the prompt.
6. **Refactoring**: involves restructuring or modifying the input prompt without changing its original meaning or intent. This could involve rephrasing the prompt, rearranging its components, or simplifying its structure to make it easier for the model to understand and respond to.
'''

over_logic = '''
Over logic refers to a comprehensive approach that encompasses all aspects of a given topic. This holistic perspective ensures that no facet of the subject matter is overlooked, thereby providing a thorough and complete understanding of the topic at hand.

The application of over logic is particularly pertinent in scenarios that necessitate a broad overview or a detailed examination, such as the process of editing or enhancing existing content. In these instances, the use of over logic facilitates a meticulous review of the material, enabling the identification and rectification of any potential issues or areas for improvement.

Furthermore, over logic underscores the importance of a comprehensive perspective in prompt engineering. By ensuring that all elements of a topic are considered, it allows for the creation of prompts that are not only accurate and relevant but also encompassing in their scope. This, in turn, contributes to the production of high-quality, effective prompts that serve to enhance the overall user experience.

Over logic plays a crucial role in prompt engineering, providing a framework for comprehensive coverage and review. Its application contributes significantly to the quality and effectiveness of the prompts, thereby playing a pivotal role in enhancing user engagement and satisfaction.

The PP categories under over logic include:
1. **Summarising**: Providing a brief overview or summary of the input or output. This could involve condensing a large amount of information into a few key points, highlighting the most important elements, or providing a concise synopsis of the content.
2. **Synthesis**: Integrating and reconciling information from multiple sources or perspectives to produce a unified, coherent, and insightful output. Synthesis goes beyond simple summarisation by combining disparate elements, identifying relationships and patterns, and generating higher-order insights or recommendations that reflect a comprehensive understanding of the topic.
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