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
Creation Date:  19/10/2023
LINKS:
https://resources.github.com/copilot-for-business/
HELP:
1. To use the categories dictionary, import the library using the following command:
```
from categorisation_logic_app_cat_pat import root_node
```
This will import the root_node dictionary.
```
'''
from categorisation_logic_app_cat_pat import root_node

# The root node of the mind map
root_node

# The second node of the mind map. This is the first level of the mind map. Used to map the high level domains and categories.
# Replace the placeholders with the string representations of the dictionaries from modify_logic.py
###"<<REPLACE DOMAIN_CATEGORIES>>"###
domain_categories = {
    'Coding': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Interaction', 'Context Control', 'Requirements Elicitation', 'System Design and Simulation', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'System Design and Simulation', 'Jailbreaking', 'Decomposed Prompting'], 
    'Cybersecurity': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics', 'Evaluation and Rating', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'System Design and Simulation', 'Jailbreaking', 'Decomposed Prompting', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Language and Semantics'],
    'General': ['Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Context Control', 'Logic and Reasoning', 'Language and Semantics', 'Evaluation and Rating', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics', 'Logic and Reasoning', 'Decomposed Prompting', 'Language and Semantics', 'Evaluation and Rating', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics', 'Logic and Reasoning', 'Evaluation and Rating', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Interaction', 'Context Control', 'Requirements Elicitation', 'System Design and Simulation', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Context Control', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'Mathematics', 'Evaluation and Rating', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Refactoring', 'System Design and Simulation', 'Jailbreaking', 'Decomposed Prompting', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Interaction', 'Logic and Reasoning', 'Language and Semantics', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Language and Semantics', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Language and Semantics', 'Input Semantics', 'Output Customisation', 'Error Identification', 'Prompt Improvement', 'Language and Semantics']
}

# The third node of the mind map. This is the second level of the mind map. Used to map the applications and categories.
# Replace the placeholders with the string representations of the dictionaries from modify_logic.py
###"<<REPLACE CATEGORIES_APPLICATIONS>>"###
categories_applications = {
    'Input Semantics': ['Chatbot', 'Classification', 'Clustering', 'Content Creation', 'Customer Service', 'Data Science', 'Healthcare', 'Programming', 'Question Answering', 'Sentiment Analysis', 'Summarisation', 'Translation'], 
    'Output Customisation': ['Chatbot', 'Classification', 'Clustering', 'Content Creation', 'Customer Service', 'Data Science', 'Healthcare', 'Programming', 'Question Answering', 'Sentiment Analysis', 'Summarisation', 'Translation'], 
    'Error Identification': ['Chatbot', 'Classification', 'Clustering', 'Content Creation', 'Customer Service', 'Data Science', 'Healthcare', 'Programming', 'Question Answering', 'Sentiment Analysis', 'Summarisation', 'Translation'], 
    'Prompt Improvement': ['Chatbot', 'Classification', 'Clustering', 'Content Creation', 'Customer Service', 'Data Science', 'Healthcare', 'Programming', 'Question Answering', 'Sentiment Analysis', 'Summarisation', 'Translation'], 
    'Interaction': ['Chatbot', 'Content Creation', 'Customer Service', 'Healthcare', 'Question Answering'], 
    'Context Control': ['Chatbot', 'Content Creation', 'Customer Service'], 
    'Logic and Reasoning': ['Chatbot', 'Classification', 'Clustering', 'Question Answering'], 
    'Language and Semantics': ['Chatbot', 'Classification', 'Question Answering', 'Sentiment Analysis', 'Summarisation', 'Translation'], 
    'Evaluation and Rating': ['Chatbot', 'Classification', 'Clustering', 'Data Science'],
    'Refactoring': ['Classification', 'Clustering', 'Content Creation', 'Data Science', 'Programming'], 
    'Mathematics': ['Classification', 'Clustering', 'Data Science'], 
    'Decomposed Prompting': ['Classification', 'Programming'], 
    'Requirements Elicitation': ['Content Creation'],
    'System Design and Simulation': ['Content Creation', 'Programming'], 
    'Jailbreaking': ['Programming']
}
     
# The fourth node of the mind map. This is the third level of the mind map. Used to map the categories and patterns.
# Replace the placeholders with the string representations of the dictionaries from modify_logic.py
###"<<REPLACE APPLICATIONS_PATTERNS>>"###
applications_patterns = {
    'Chatbot': ['Multi-Criteria Rating', 'Cloze-Questions', 'MultiArith', 'CommonsenseQA', 'Infinite Generation', 'Question Refinement', 'Contradiction', 'Meta Language Creation', 'Context Manager', 'SVAMP', 'StrategyQA', 'Reflection', 'Visualization Generator', 'GSM8K', 'Fact Check List', 'Restrict', 'Free-Form Questions', 'Equivalence', 'Output Automater', 'Chain-of-Thought Prompting', 'AQuA', 'Game Play', 'Template', 'Persona', 'Cognitive Verifier', 'AI2 Reasoning Challenge (ARC)', 'Refusal Breaker', 'Alternative Approaches', 'Flipped Interaction', 'Premise and Conclusion', 'Recipe'], 
    'Classification': ['Multi-Criteria Rating', 'Cloze-Questions', 'MultiArith', 'CommonsenseQA', 'Code Clustering', 'Question Refinement', 'Contradiction', 'Principled Code', 'Meta Language Creation', 'SVAMP', 'StrategyQA', 'Letter Concatenation', 'Reflection', 'Visualization Generator', 'Word Problems - Addition/Subtraction', 'Data-guided Refactoring', 'GSM8K', 'Fact Check List', 'External API Calls', 'Decomposed Prompt', 'Hidden Assumptions', 'Restrict', 'Word Problems - Multiplication/Division', 'Hierarchical Decomposition', 'Recursive Decomposition', 'Free-Form Questions', 'Equivalence', 'Intermediate Abstraction', 'Output Automater', 'Chain-of-Thought Prompting', 'Pseudo-code Refactoring', 'AQuA', 'Template', 'Persona', 'Cognitive Verifier', 'AI2 Reasoning Challenge (ARC)', 'Refusal Breaker', 'Alternative Approaches', 'Premise and Conclusion', 'Recipe'], 
    'Clustering': ['Multi-Criteria Rating', 'Cloze-Questions', 'MultiArith', 'CommonsenseQA', 'Code Clustering', 'Question Refinement', 'Principled Code', 'Meta Language Creation', 'SVAMP', 'StrategyQA', 'Reflection', 'Visualization Generator', 'Word Problems - Addition/Subtraction', 'Data-guided Refactoring', 'GSM8K', 'Fact Check List', 'Hidden Assumptions', 'Restrict', 'Word Problems - Multiplication/Division', 'Free-Form Questions', 'Equivalence', 'Intermediate Abstraction', 'Output Automater', 'Chain-of-Thought Prompting', 'Pseudo-code Refactoring', 'AQuA', 'Template', 'Persona', 'Cognitive Verifier', 'AI2 Reasoning Challenge (ARC)', 'Refusal Breaker', 'Alternative Approaches', 'Premise and Conclusion', 'Recipe'], 
    'Content Creation': ['Architectural Possibilities', 'Specification Disambiguation', 'Code Clustering', 'Infinite Generation', 'Question Refinement', 'Requirements Simulator', 'Principled Code', 'Meta Language Creation', 'Context Manager', 'Change Request Simulation', 'Few-shot Example Generator', 'Reflection', 'Visualization Generator', 'Data-guided Refactoring', 'Fact Check List', 'Hidden Assumptions', 'Restrict', 'Free-Form Questions', 'Intermediate Abstraction', 'Output Automater', 'Pseudo-code Refactoring', 'Game Play', 'Domain-Specific Language (DSL) Creation', 'Template', 'API Generator', 'Persona', 'Cognitive Verifier', 'Refusal Breaker', 'API Simulator', 'Alternative Approaches', 'Flipped Interaction', 'Recipe'], 
    'Customer Service': ['Meta Language Creation', 'Context Manager', 'Game Play', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Infinite Generation', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Flipped Interaction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater'], 
    'Data Science': ['Multi-Criteria Rating', 'Code Clustering', 'Question Refinement', 'Principled Code', 'Meta Language Creation', 'Reflection', 'Visualization Generator', 'Word Problems - Addition/Subtraction', 'Data-guided Refactoring', 'Fact Check List', 'Hidden Assumptions', 'Restrict', 'Word Problems - Multiplication/Division', 'Free-Form Questions', 'Intermediate Abstraction', 'Output Automater', 'Pseudo-code Refactoring', 'Template', 'Persona', 'Cognitive Verifier', 'Refusal Breaker', 'Alternative Approaches', 'Recipe'], 
    'Healthcare': ['Meta Language Creation', 'Game Play', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Infinite Generation', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Flipped Interaction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater'], 
    'Programming': ['Architectural Possibilities', 'Successful jailbreaking attempts', 'Interspersing spaces between characters', 'Code Clustering', 'Characterizing keyword-based defense mechanisms', 'Question Refinement', 'Crafting effective jailbreak prompts', 'Testing defense mechanisms through time-based analysis', 'Principled Code', 'Meta Language Creation', 'Hallucination Generation', 'Few-shot Example Generator', 'Reverse engineering of jailbreak prevention mechanisms', 'Letter Concatenation', 'Reflection', 'Visualization Generator', 'Data-guided Refactoring', 'External API Calls', 'Fact Check List', 'Decomposed Prompt', 'Hidden Assumptions', 'Restrict', 'Hierarchical Decomposition', 'Recursive Decomposition', 'Free-Form Questions', 'Jailbreak Attack', 'Intermediate Abstraction', 'Output Automater', 'Outputting in code chunks', 'Usage of translated prompts', 'Pseudo-code Refactoring', 'Domain-Specific Language (DSL) Creation', 'Template', 'API Generator', 'Persona', 'Cognitive Verifier', 'Simulated Experiment', 'Prompt Injection', 'Refusal Breaker', 'API Simulator', 'Alternative Approaches', 'Recipe'], 
    'Question Answering': ['Cloze-Questions', 'MultiArith', 'CommonsenseQA', 'Infinite Generation', 'Question Refinement', 'Contradiction', 'Meta Language Creation', 'SVAMP', 'StrategyQA', 'Reflection', 'Visualization Generator', 'GSM8K', 'Fact Check List', 'Restrict', 'Free-Form Questions', 'Equivalence', 'Output Automater', 'Chain-of-Thought Prompting', 'AQuA', 'Game Play', 'Template', 'Persona', 'Cognitive Verifier', 'AI2 Reasoning Challenge (ARC)', 'Refusal Breaker', 'Alternative Approaches', 'Flipped Interaction', 'Premise and Conclusion', 'Recipe'], 
    'Sentiment Analysis': ['Meta Language Creation', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Contradiction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater'], 
    'Summarisation': ['Meta Language Creation', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Contradiction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater'], 
    'Translation': ['Meta Language Creation', 'Template', 'Reflection', 'Persona', 'Visualization Generator', 'Restrict', 'Cognitive Verifier', 'Question Refinement', 'Refusal Breaker', 'Alternative Approaches', 'Contradiction', 'Fact Check List', 'Free-Form Questions', 'Recipe', 'Output Automater']
}

# Not used in the mindmap. A dictionary of pattern descriptions if there is not a direct link of a prompt name to a research paper
pattern_descriptions = {
    'Multi-Criteria Rating': 'This pattern refers to Pattern Category: N/A and Pattern Name Expert #1 - #4 for the id:3 research paper in promptpatterns.json.',
}
