'''
DESCRIPTION
Dictionaries for categories, applications, etc. to map the promptpatterns.json file.
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

categoriesAndPatterns = {
    'Input Semantics': ['Meta Language Creation', 'Free-Form Questions'],
    'Output Customisation': ['Output Automater', 'Persona', 'Visualization Generator', 'Recipe', 'Template'],
    'Error Identification': ['Fact Check List', 'Reflection', 'Restrict'],
    'Prompt Improvement': ['Question Refinement', 'Alternative Approaches', 'Cognitive Verifier', 'Refusal Breaker'],
    'Refactoring': ['Pseudo-code Refactoring', 'Data-guided Refactoring', 'Code Clustering', 'Intermediate Abstraction', 'Principled Code', 'Hidden Assumptions'],
    'Interaction': ['Flipped Interaction', 'Game Play', 'Infinite Generation'],
    'Context Control': ['Context Manager'],
    'Requirements Elicitation': ['Requirements Simulator', 'Specification Disambiguation', 'Change Request Simulation'],
    'System Design and Simulation': ['API Generator', 'API Simulator', 'Few-shot Example Generator', 'Domain-Specific Language (DSL) Creation', 'Architectural Possibilities'],
    'Mathematics': ['Word Problems - Addition/Subtraction', 'Word Problems - Multiplication/Division'],
    'Jailbreaking': ['Jailbreak Attack', 'Simulated Experiment', 'Successful jailbreaking attempts', 'Reverse engineering of jailbreak prevention mechanisms', 'Testing defense mechanisms through time-based analysis', 'Characterizing keyword-based defense mechanisms', 'Crafting effective jailbreak prompts', 'Outputting in code chunks', 'Interspersing spaces between characters', 'Usage of translated prompts', 'Hallucination Generation'],
    'Logic and Reasoning': ['Premise and Conclusion', 'Equivalence', 'Chain-of-Thought Prompting', 'MultiArith', 'SVAMP', 'AQuA', 'CommonsenseQA', 'AI2 Reasoning Challenge (ARC)', 'GSM8K', 'StrategyQA', 'Cloze-Questions'],
    'Decomposed Prompting': ['Decomposed Prompt', 'Hierarchical Decomposition', 'Recursive Decomposition', 'External API Calls', 'Letter Concatenation'],
    'Language and Semantics': ['Contradiction'],
    'Evaluation and Rating': ['Multi-Criteria Rating']
}

pattern_descriptions = {
    'Multi-Criteria Rating': 'This pattern refers to Pattern Category: N/A and Pattern Name Expert #1 - #4 in promptpatterns.json.',
}

application = { 
    'Chatbot': ['Input Semantics', 'Output Customization', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Context Control', 'Logic and Reasoning', 'Language and Semantics', 'Evaluation and Rating'],
    'Classification': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics', 'Logic and Reasoning', 'Decomposed Prompting', 'Language and Semantics'],
    'Clustering': ['Input Semantics', 'Output Customization', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics', 'Logic and Reasoning'],
    'Content Creation': ['Input Semantics', 'Output Customization', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Interaction', 'Context Control', 'Requirements Elicitation', 'System Design and Simulation'], 
    'Customer Service': ['Input Semantics', 'Output Customization', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Context Control'], 
    'Data Science': ['Input Semantics', 'Output Customization', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics'], 
    'Healthcare': ['Input Semantics', 'Output Customization', 'Error Identification', 'Prompt Improvement', 'Interaction'], 
    'Programming': ['Input Semantics','Output Customization','Error Identification','Prompt Improvement','Refactoring','System Design and Simulation','Jailbreaking','Decomposed Prompting'], 
    'Question Answering': ['Input Semantics','Output Customization','Error Identification','Prompt Improvement','Interaction','Logic and Reasoning','Language and Semantics'],
    'Sentiment Analysis': ['Input Semantics','Output Customization','Error Identification','Prompt Improvement','Language and Semantics'], 
    'Summarisation': ['Input Semantics','Output Customization','Error Identification','Prompt Improvement','Language and Semantics'], 
    'Translation': ['Input Semantics','Output Customization','Error Identification','Prompt Improvement','Language and Semantics'] 
    }

