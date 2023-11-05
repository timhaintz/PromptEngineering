'''
DESCRIPTION
Dictionaries for categories, applications, etc. to map the promptpatterns.json file.
This is the opinionated logic of the author. The JSON file is the source of truth as per the research papers. 
This file contains the following dictionaries:
- root_node: The root node of the mind map
- domain: A dictionary of domains and applications
- application: A dictionary of applications and categories
- categories_and_patterns: A dictionary of categories and patterns
- pattern_descriptions: A dictionary of pattern descriptions if there is not a direct link of a prompt name to a research paper

NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  29/9/2023
LINKS:
https://resources.github.com/copilot-for-business/
HELP:
1. To use the categories dictionary, import the library using the following command:
```
from categorisation_logic import categoriesAndPatterns
```
This will use the categories dictionary.
2. To use the application dictionary, import the library using the following command:
```
from categorisation_logic import application
```
'''

# The root node of the mind map
root_node = {
    'Q': 'Q'
}

# The second node of the mind map. This is the first level of the mind map. Used to map the high level domains and categories.
domain_applications = {
    'Computer Vision': [''],
    'Customer Service': ['Chatbot'],
    'Cybersecurity': ['Data Science', 'Coding'],
    'Data Science': ['Data Science', 'Coding', 'Question Answering'],
    'General': ['Chatbot', 'Data Science', 'Healthcare', 'Coding', 'Question Answering'],
    'Healthcare': ['Healthcare'],
    'Programming': ['Coding'], 
}

# The third node of the mind map. This is the second level of the mind map. Used to map the applications and categories.
application_categories = { 
    'Chatbot': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Context Control', 'Logic and Reasoning', 'Language and Semantics', 'Evaluation and Rating', 'Summarising'],
    'Coding': ['Input Semantics','Output Customisation','Error Identification','Prompt Improvement','Refactoring','System Design and Simulation','Jailbreaking','Decomposed Prompting'], 
    #'Data Science': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics', 'Evaluation and Rating', 'Summarising'], 
    #'Healthcare': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Interaction'], 
    'Question Answering': ['Input Semantics','Output Customisation','Error Identification','Prompt Improvement','Interaction','Logic and Reasoning','Language and Semantics'],
    'Sentiment Analysis': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Context Control', 'Logic and Reasoning', 'Language and Semantics', 'Evaluation and Rating', 'Summarising'],
    'System Design and Simulation': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Interaction', 'Context Control', 'Requirements Elicitation', 'Simulation', 'Mathematics', 'Evaluation and Rating', 'Analysis', 'Summarising'],
    }
     
# The fourth node of the mind map. This is the third level of the mind map. Used to map the categories and patterns.
categories_patterns = {
    'Analysis': ['Meta Language Creation', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Contradiction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater'],
    'Argument': ['Contradiction'],
    'Assessment': ['Multi-Criteria Rating'],
    'Calculation': ['Word Problems - Addition/Subtraction', 'Word Problems - Multiplication/Division'],
    'Categorising': [''],
    'Classification': ['Multi-Criteria Rating', 'Cloze-Questions', 'MultiArith', 'CommonsenseQA', 'Code Clustering', 'Question Refinement', 'Contradiction', 'Principled Code', 'Meta Language Creation', 'SVAMP', 'StrategyQA', 'Letter Concatenation', 'Reflection', 'Visualization Generator', 'Word Problems - Addition/Subtraction', 'Data-guided Refactoring', 'GSM8K', 'Fact Check List', 'External API Calls', 'Decomposed Prompt', 'Hidden Assumptions', 'Restrict', 'Word Problems - Multiplication/Division', 'Hierarchical Decomposition', 'Recursive Decomposition', 'Free-Form Questions', 'Equivalence', 'Intermediate Abstraction', 'Output Automater', 'Chain-of-Thought Prompting', 'Pseudo-code Refactoring', 'AQuA', 'Template', 'Persona', 'Cognitive Verifier', 'AI2 Reasoning Challenge (ARC)', 'Refusal Breaker', 'Alternative Approaches', 'Premise and Conclusion', 'Recipe'],
    'Clustering': ['Multi-Criteria Rating', 'Cloze-Questions', 'MultiArith', 'CommonsenseQA', 'Code Clustering', 'Question Refinement', 'Principled Code', 'Meta Language Creation', 'SVAMP', 'StrategyQA', 'Reflection', 'Visualization Generator', 'Word Problems - Addition/Subtraction', 'Data-guided Refactoring', 'GSM8K', 'Fact Check List', 'Hidden Assumptions', 'Restrict', 'Word Problems - Multiplication/Division', 'Free-Form Questions', 'Equivalence', 'Intermediate Abstraction', 'Output Automater', 'Chain-of-Thought Prompting', 'Pseudo-code Refactoring', 'AQuA', 'Template', 'Persona', 'Cognitive Verifier', 'AI2 Reasoning Challenge (ARC)', 'Refusal Breaker', 'Alternative Approaches', 'Premise and Conclusion', 'Recipe'],
    'Comparison': [''],
    'Context Control': ['Context Manager'],
    'Decomposed Prompting': ['Decomposed Prompt', 'Hierarchical Decomposition', 'Recursive Decomposition', 'External API Calls', 'Letter Concatenation'],
    'Error Identification': ['Fact Check List', 'Reflection', 'Restrict'],
    'Hypotehsise': [''],
    'Input Semantics': ['Meta Language Creation', 'Free-Form Questions'],
    'Jailbreaking': ['Jailbreak Attack', 'Simulated Experiment', 'Successful jailbreaking attempts', 'Reverse engineering of jailbreak prevention mechanisms', 'Testing defense mechanisms through time-based analysis', 'Characterizing keyword-based defense mechanisms', 'Crafting effective jailbreak prompts', 'Outputting in code chunks', 'Interspersing spaces between characters', 'Usage of translated prompts', 'Hallucination Generation', 'Prompt Injection'],
    'Large Multimodal Models (LMMs)': [''],
    'Logical Reasoning': ['Premise and Conclusion', 'Equivalence', 'Chain-of-Thought Prompting', 'MultiArith', 'SVAMP', 'AQuA', 'CommonsenseQA', 'AI2 Reasoning Challenge (ARC)', 'GSM8K', 'StrategyQA', 'Cloze-Questions'],
    'Output Customisation': ['Output Automater', 'Persona', 'Visualization Generator', 'Recipe', 'Template'],
    'Output Semantics': ['Flipped Interaction', 'Game Play', 'Infinite Generation', 'Architectural Possibilities', 'Specification Disambiguation', 'Code Clustering', 'Infinite Generation', 'Question Refinement', 'Requirements Simulator', 'Principled Code', 'Meta Language Creation', 'Context Manager', 'Change Request Simulation', 'Few-shot Example Generator', 'Reflection', 'Visualization Generator', 'Data-guided Refactoring', 'Fact Check List', 'Hidden Assumptions', 'Restrict', 'Free-Form Questions', 'Intermediate Abstraction', 'Output Automater', 'Pseudo-code Refactoring', 'Game Play', 'Domain-Specific Language (DSL) Creation', 'Template', 'API Generator', 'Persona', 'Cognitive Verifier', 'Refusal Breaker', 'API Simulator', 'Alternative Approaches', 'Flipped Interaction', 'Recipe'],
    'Prediction': [''],
    'Prompt Improvement': ['Question Refinement', 'Alternative Approaches', 'Cognitive Verifier', 'Refusal Breaker'],
    'Refactoring': ['Pseudo-code Refactoring', 'Data-guided Refactoring', 'Code Clustering', 'Intermediate Abstraction', 'Principled Code', 'Hidden Assumptions'],
    'Requirements Elicitation': ['Requirements Simulator', 'Specification Disambiguation', 'Change Request Simulation'],
    'Simulation': ['API Generator', 'API Simulator', 'Few-shot Example Generator', 'Domain-Specific Language (DSL) Creation', 'Architectural Possibilities'],
    'Summarising': ['Meta Language Creation', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Contradiction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater'],
    'Translation': ['Meta Language Creation', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Contradiction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater'],
}

# Not used in the mindmap. A dictionary of pattern descriptions if there is not a direct link of a prompt name to a research paper
pattern_descriptions = {
    'Multi-Criteria Rating': 'This pattern refers to Pattern Category: N/A and Pattern Name Expert #1 - #4 for the id:3 research paper in promptpatterns.json.',
}
