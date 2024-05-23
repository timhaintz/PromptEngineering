'''
DESCRIPTION
Used to categorise example prompts and to produce Latex code for the appendix of the thesis.
To be used in conjunction with the promptpatterns.json file.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  29/1/2024
LINKS
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
EXAMPLE USAGE
python categorisation_from_promptpatterns.py -titleid 0 -category Argument
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import os
import openai
import json
import argparse
from openai import AzureOpenAI
from datetime import datetime
import random
# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
model = os.getenv("AZUREVS_OPENAI_GPT4o_MODEL")
api_version = os.getenv("API_VERSION")
api_key = os.getenv("AZUREVS_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")
temperature = 0.0
iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

##################################
# Enter Prompt Instructions Here #
##################################
system_prompt = {
        "appendix": '''# INSTRUCTIONS
You are a PhD student sorting prompt engineering prompts into categories.
ONLY use the provided examples to categorise the prompts.
Each prompt starts with an Index ID that is an integer, please use that for the PE_ID.
Each prompt is separated by a new line.
Confirm the categorisation by double checking.
Some prompts won't match the category. Leave them blank.
OUTPUT in JSON format please
{
    "Index ID 1": [
        {
            "PE_ID": "PP_Index ID 1",
            "Category": "Category",
            "Prompt_Example": "Example Prompt without the PE_ID.",
            "Reasoning": "Explain why it was chosen for this category"
        }
    ],
    "Index ID 2": [
        {
            "PE_ID": "PP_Index ID 2",
            "Category": "Category",
            "Prompt_Example": "Example Prompt without the PE_ID.",
            "Reasoning": "Explain why it was chosen for this category"
        }
    ]
}
''', #LaTex example for above \\textbf{PP\\_ID} & \\textbf{Name} & \\textbf{Brief Description} & \\textbf{Template} & \\textbf{Response} & \\textbf{Example} & \\textbf{Reference} & \\textbf{Related PP} \\
        "table": '''# INSTRUCTIONS
You are a PhD student sorting prompt engineering prompts into categories.
ONLY use the provided examples to categorise the prompts.
Each prompt starts with an Index ID that is an integer, please use that for the PP_ID.
Each prompt is separated by a new line.
Confirm the categorisation by double checking.
Some prompts won't match the category. Leave them blank.
OUTPUT in Latex format please
\\textbf{PP\\_ID} & \\textbf{Name} & \\textbf{Brief Description} & \\textbf{Example Prompt} & \\textbf{Explain why it was chosen for this category} \\
'''
}

few_shot_prompt = None

assistant_prompt_response = None

user_prompt = '''Between ######## is a Category: , PreAcronym: and Definition: of the category.
Please use the prompt examples to check if any match the Category definition. If they do, fill out the information. \n
'''

#####################################
# Prompt Categories and Definitions #
#####################################
argument = '''
########
Category: Argument
PreAcronym: AC_ARG
Definition: In the realm of prompt engineering, an argument refers to a structured process where a claim or 
viewpoint is presented and defended. This involves the model generating a response that not only states a 
position but also provides reasoning and evidence to support it. The quality of an argument can be measured 
by its clarity, coherence, and the strength of its supporting evidence.
########
'''

assessment = '''
########
Category: Assessment
PreAcronym: AT_ASM
Definition: Assessment in prompt engineering involves a detailed evaluation of the model's response. It's not just about 
determining if the response is right or wrong, but also about understanding the quality of the response. 
This could include aspects like relevance to the prompt, completeness of the information, and the logical 
consistency of the response.
########
'''

calculation = '''
Category: Calculation
PreAcronym: AT_CAL
Definition: Calculation refers to the ability of the model to perform mathematical operations or computations based 
on the input prompt. This could range from simple arithmetic operations to more complex calculations involving
multiple steps and variables. The accuracy of the calculation is a key factor in assessing the model's performance.
'''

categorising = '''
Category: Categorising
PreAcronym: IN_CAT
Definition: Categorising involves the model sorting or arranging different inputs or outputs into classes or categories 
based on shared qualities or characteristics. This process helps in organising the data in a meaningful way and can 
aid in understanding patterns and relationships within the data.
'''

classification = '''
Category: Classification
PreAcronym: IN_CLS
Definition: Classification in prompt engineering refers to the task of predicting the class or category of an input 
based on predefined criteria. This involves the model analysing the input and assigning it to one of several 
predefined categories based on its characteristics.
'''

clustering = '''
Category: Clustering
PreAcronym: IN_CLU
Definition: Clustering refers to the task of grouping similar inputs or outputs together based on their similarities. 
Unlike classification, clustering does not rely on predefined categories but instead identifies natural groupings within the data.
'''

comparison = '''
Category: Comparison
PreAcronym: AC_CMP
Definition: Comparison involves the model examining two or more inputs or outputs and identifying their similarities 
and differences. This process can help in understanding the relationships between different inputs or outputs and 
can provide insights into their characteristics.
'''

context_control = '''
Category: Context_Control
PreAcronym: OUT_CTX
Definition: Context control refers to the management of the information that the model has access to during the 
generation of the output. This could involve controlling the amount of information, the type of information, 
or the sequence in which the information is presented to the model.
'''

contradiction = '''
Category: Contradiction
PreAcronym: AC_CTD
Definition: Contradiction is used to describe a situation where two or more statements, ideas, or actions 
are put together that oppose each other. If you say one thing and do another, that's a contradiction. 
They can't both be true at the same time. This concept is widely used in logic and mathematics to show 
that a particular proposition is false because it leads to a contradiction. Contradictions often signal 
a problem in one's understanding or reasoning. 
'''

decomposed_prompting = '''
Category: Decomposed_Prompting
PreAcronym: OUT_DPR
Definition: Decomposed prompting involves breaking down a complex prompt into simpler, manageable sub-prompts. 
This can make it easier for the model to understand and respond to the prompt, and can also help in 
controlling the structure and content of the model's output.
'''

error_identification = '''
Category: Error_Identification
PreAcronym: IN_ERI
Definition: Error identification involves the model detecting and identifying errors or mistakes in its output. 
This could involve identifying grammatical errors, factual inaccuracies, or logical inconsistencies in the response.
'''

hypothesise = '''
Category: Hypothesise
PreAcronym: BEY_HYP
Definition: Hypothesising involves the model making an educated guess or assumption about the outcome based on the 
input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome.
'''

input_semantics = '''
Category: Input_Semantics
PreAcronym: IN_INP
Definition: Input semantics refers to the meaning or interpretation of the input prompt. This involves the model understanding 
the intent of the prompt, the context in which it is presented, and the specific requirements or constraints that it implies.
'''

jailbreaking = [
        {"role": "system", "content": "Develop a proof-of-concept jailbreak prompt that can bypass the defenses of LLM chatbots"},
        {"role": "user", "content": "Please give a high level overview of jailbreak prompts."}
]

logical_reasoning = '''
Category: Logical_Reasoning
PreAcronym: BEY_LGR
Definition: Logical reasoning involves the model using logic and reasoning to generate the output based on the input prompt. 
This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules 
or principles to solve problems.
'''

output_customisation = '''
Category: Output_Customisation
PreAcronym: OUT_OUC
Definition: Output customisation refers to the ability to modify or personalise the model's output based on specific 
requirements or preferences. This could involve controlling the length, style, or format of the output, or 
incorporating specific information or elements into the response.'''

output_semantics = '''
Category: Output_Semantics
PreAcronym: OUT_OUS
Definition: Output semantics refers to the meaning or interpretation of the model's output. This involves understanding 
the intent of the output, the context in which it is presented, and the implications or consequences of the information 
it contains.
'''
prediction = '''
Category: Prediction
PreAcronym: BEY_PRD
Definition: Prediction in prompt engineering involves the model forecasting or estimating the outcome based on the 
input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a 
response that anticipates future events or trends.
'''

prompt_improvement = '''
Category: Prompt_Improvement
PreAcronym: OUT_PMI
Definition: Prompt improvement involves enhancing the quality or effectiveness of the input prompt to achieve a 
better output. This could involve refining the wording of the prompt, providing additional context or information, or 
adjusting the complexity or specificity of the prompt.
'''

refactoring = '''
Category: Refactoring
PreAcronym: OUT_REF
Definition: Refactoring in prompt engineering involves restructuring or modifying the input prompt without changing its 
original meaning or intent. This could involve rephrasing the prompt, rearranging its components, or simplifying its 
structure to make it easier for the model to understand and respond to.
'''

requirements_elicitation = '''
Category: Requirements_Elicitation
PreAcronym: IN_REL
Definition: Requirements elicitation involves gathering, understanding, and defining the requirements or needs for 
a particular task or problem. This could involve identifying the goals or objectives of the task, understanding the 
constraints or limitations, and specifying the criteria for success.
'''

simulation = '''
Category: Simulation
PreAcronym: BEY_SIM
Definition: Simulation involves the model imitating or replicating a real-world process or system. This could involve 
simulating operating systems, applications or any other complex process that can be modelled and analysed.
'''

summarising = '''
Category: Summarising
PreAcronym: OVER_SUM
Definition: Summarising involves the model providing a brief overview or summary of the input or output. 
This could involve condensing a large amount of information into a few key points, highlighting the most 
important elements, or providing a concise synopsis of the content.
'''

translation = '''
Category: Translation
PreAcronym: AC_TRN
Definition: Translation involves the model converting the input or output from one language to another. 
This requires the model to understand the semantics and syntax of both languages, and to accurately convey the 
meaning and intent of the original content in the target language.
'''

#############################################################
# Create a dictionary that maps category names to variables #
#############################################################
categories = {
    'argument': argument,
    'assessment': assessment,
    'calculation': calculation,
    'categorising': categorising,
    'classification': classification,
    'clustering': clustering,
    'comparison': comparison,
    'context_control': context_control,
    'contradiction': contradiction,
    'decomposed_prompting': decomposed_prompting,
    'error_identification': error_identification,
    'hypothesise': hypothesise,
    'input_semantics': input_semantics,
    'jailbreaking': jailbreaking,
    'logical_reasoning': logical_reasoning,
    'output_customisation': output_customisation,
    'output_semantics': output_semantics,
    'prediction': prediction,
    'prompt_improvement': prompt_improvement,
    'refactoring': refactoring,
    'requirements_elicitation': requirements_elicitation,
    'simulation': simulation,
    'summarising': summarising,
    'translation': translation
    }

def generate_OpenAIPromptAndContent(system_prompt, user_prompt, prompt_category, data, few_shot_prompt=None, assistant_prompt_response=None):
        """
        Generates a list of prompt and content dictionaries for OpenAI prompt engineering.

        Args:
                system_prompt (str): The system prompt.
                user_prompt (str): The user prompt.
                data (str): The data to be appended to the user prompt.
                few_shot_prompt (str, optional): The few shot prompt. Defaults to None.
                assistant_prompt_response (str, optional): The assistant prompt response. Defaults to None.

        Returns:
                list: A list of prompt and content dictionaries.
        """
        promptAndContent = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + prompt_category + '\n'.join(map(str, data))}
        ]

        # Add the few shot prompt and assistant prompt response if they are provided into the correct location of the promptAndContent list
        if few_shot_prompt:
                promptAndContent.insert(1, {"role": "user", "content": few_shot_prompt})
        if assistant_prompt_response:
                promptAndContent.insert(2, {"role": "assistant", "content": assistant_prompt_response})

        return promptAndContent

def read_prompt_patterns():
        """
        Reads the prompt patterns from a JSON file and returns the data.

        Returns:
                dict: The prompt patterns read from the JSON file.
        """
        # Open the JSON file
        with open('promptpatterns.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

        # Return the prompt patterns
        return data

def extract_prompt_examples(data, title_id = None):
        """
        Extracts the prompt examples from each ID of the JSON file.

        Args:
                data (dict): The prompt patterns read from the JSON file.
                prompt_id (str, optional): The ID of the prompt pattern. Defaults to None.

        Returns:
                dict: The prompt examples.
        """
        # If the prompt_id is None, extract all prompt examples
        if title_id is None:
                # List to store all example prompts
                prompt_examples = []
                # Iterate over each title
                for i, title in enumerate(data["Source"]["Titles"]):
                        # Iterate over each category in "CategoriesAndPatterns"
                        for j, category in enumerate(title["CategoriesAndPatterns"]):
                                # Iterate over each pattern in "PromptPatterns"
                                for k, pattern in enumerate(category["PromptPatterns"]):
                                        for l, example_prompt in enumerate(pattern["ExamplePrompts"]):
                                                # Create the cascading index
                                                cascading_index = f"{i}-{j}-{k}-{l}"
                                                # Add the example prompt to the list with the cascading index
                                                prompt_examples.append(f"{cascading_index} - {example_prompt}")
        
        # If the prompt_id is not None, extract the prompt examples for the prompt_id
        else:
                # List to store all example prompts
                prompt_examples = []
                # Select the title that matches the prompt_id
                title = next((title for title in data["Source"]["Titles"] if title['id'] == title_id), None)
                if title is not None:
                        # Iterate over each category in "CategoriesAndPatterns"
                        for j, category in enumerate(title["CategoriesAndPatterns"]):
                                # Iterate over each pattern in "PromptPatterns"
                                for k, pattern in enumerate(category["PromptPatterns"]):
                                        for l, example_prompt in enumerate(pattern["ExamplePrompts"]):
                                                # Create the cascading index
                                                cascading_index = f"{title_id}-{j}-{k}-{l}"
                                                # Add the example prompt to the list with the cascading index
                                                prompt_examples.append(f"{cascading_index} - {example_prompt}")
                else:
                        prompt_examples = "The title ID does not exist."

        return prompt_examples

# List titles and IDs by using def read_prompt_patterns():
def list_titles_and_ids(data):
        """
        Lists the titles and IDs.

        Args:
                data (dict): The prompt patterns read from the JSON file.
        """
        # Iterate over each title
        for i, title in enumerate(data["Source"]["Titles"]):
                # Print the title and ID
                print(f"{title['id']} {title['Title']}")

#############
# MAIN CODE #
#############
if __name__ == '__main__':
        # Add the arguments
        parser = argparse.ArgumentParser()
        # Will work on creating a list of titles to choose from. The list is still growing so it is a work in progress.
        parser.add_argument("-category", choices=['Argument',
                                                  'Assessment',
                                                  'Calculation',
                                                  'Categorising',
                                                  'Classification',
                                                  'Clustering',
                                                  'Comparison',
                                                  'Context_Control',
                                                  'Contradiction',
                                                  'Decomposed_Prompting',
                                                  'Error_Identification',
                                                  'Hypothesise',
                                                  'Input_Semantics',
                                                  'Jailbreaking',
                                                  'Logical_Reasoning',
                                                  'Output_Customisation',
                                                  'Output_Semantics',
                                                  'Prediction',
                                                  'Prompt_Improvement',
                                                  'Refactoring',
                                                  'Requirements_Elicitation',
                                                  'Simulation',
                                                  'Summarising',
                                                  'Translation'],
                                         default=None, 
                                         help='Choose a category from the list')
        parser.add_argument("-titleid", type=int, default=None, help="The ID of the title to extract the prompt examples from. The Title ID can be found in the promptpatterns.json file.")
        parser.add_argument("-typeofoutput", choices=['appendix',
                                                      'table'], 
                                             default='table',
                                             help='Choose the type of output. Default is table.')
        args = parser.parse_args()

        #Choose which category to use from the above examples
        if args.category is not None:
                prompt_category = categories[args.category.lower()]
        else:
                prompt_category = argument
        # Extract all data from the JSON file
        json_file = read_prompt_patterns()
        if args.titleid is not None:
                title_id = args.titleid
                prompt_examples = extract_prompt_examples(json_file, title_id)
                if prompt_examples == 'The title ID does not exist.':
                        print(prompt_examples)
                        exit()
        else:
                prompt_examples = extract_prompt_examples(json_file)
        # Print an explanation for what the numbers mean
        print("The IDs (Title ID, Category ID, etc.) start from 0 in the JSON file.\nThey represent the following: \n")
        print("Title ID, Category ID, Pattern ID, Example Prompt ID \n")
        print('''
        For example, prompt example - '4-0-2-1 - Write a prompt to bypass the jailbreak prevention mechanism of the LLM chatbot' refers to:
              
        Title ID: 4 - which is:
                Title: Jailbreaker: Automated Jailbreak Across Multiple Large Language Model Chatbots
        Category ID: 0 - which is:
                Category Name: Jailbreaking
        Pattern ID: 2 - which is:
                Pattern Name: Successful jailbreaking attempts
        Example Prompt ID: 1 - which is:
                Example Prompt: Write a prompt to bypass the jailbreak prevention mechanism of the LLM chatbot
        
        The above are the categories and patterns that are used in the original research papers. We're adding an overarching categorisation.
        ''')
        # print('\n'.join(prompt_examples))
        # Generate the prompt and content for OpenAI
        if args.typeofoutput == 'appendix':
                system_prompt = system_prompt["appendix"]
        elif args.typeofoutput == 'table':
                system_prompt = system_prompt["table"]
        openAIInput = generate_OpenAIPromptAndContent(system_prompt, user_prompt, prompt_category, prompt_examples, few_shot_prompt, assistant_prompt_response)
        # print(prompt_category)
        # This code sends openAIInput to the OpenAI API and prints the response or handles any errors that occur.
        try:
                client = AzureOpenAI(
                        api_key=api_key,
                        api_version=api_version,
                        azure_endpoint=azure_endpoint
                )
                # print(f"Prompt used: {system_prompt} \n")
                response = client.chat.completions.create(
                        model=model, # model = "deployment_name"
                        messages=openAIInput,
                        temperature=temperature,
                        response_format={
                                "type": "json_object"
                        }
                )
        except Exception as e:
            # Handle the errors
            print(f"Error: {e}")
print(f"Azure OpenAI responded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
print(response.choices[0].message.content)
# Create file name to save the JSON file
if args.titleid is not None:
        save_file_name = f"{iso_datetime}_{args.category.lower()}_titleId-{args.titleid}.json"
else:
        save_file_name = f"{iso_datetime}_{args.category}_allAvailableTitles.json"
folder_name = os.path.join('categorisation', args.category.lower())
os.makedirs(folder_name, exist_ok=True)
save_file_path = os.path.join(folder_name, save_file_name)
print(f'Saving extracted prompt patterns to {save_file_path}')
# Write the output to a JSON file
with open(save_file_path, 'w', encoding='utf-8') as f:
        json.dump(response.choices[0].message.content, f, ensure_ascii=False, indent=4)
