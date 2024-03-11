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
python categorisation_for_appendix.py -titleid 0 -category Argument
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
model = os.getenv("AZUREVSAUSEAST_OPENAI_MODEL")
api_version = "2023-05-15"
api_key = os.getenv("AZUREVSAUSEAST_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVSAUSEAST_OPENAI_ENDPOINT")
temperature = 0.0

##################################
# Enter Prompt Instructions Here #
##################################
system_prompt_appendix = '''# INSTRUCTIONS
You are a PhD student sorting prompt engineering prompts into categories.
ONLY use the provided examples to categorise the prompts.
Each prompt starts with an Index ID that is an integer, please use that for the PP_ID.
Each prompt is separated by a new line.
Confirm the categorisation by double checking.
Some prompts won't match the category. Leave them blank.
OUTPUT in Latex format please
\\textbf{PP\\_ID} & \\textbf{Name} & \\textbf{Brief Description} & \\textbf{Template} & \\textbf{Response} & \\textbf{Example} & \\textbf{Reference} & \\textbf{Related PP} \\
'''

few_shot_prompt = None

assistant_prompt_response = None

user_prompt = '''Between ######## is a Category: and then Definition: of the category.
Please use the prompt examples to check if any match the Category. If they do, fill out the table. \n
'''

#####################################
# Prompt Categories and Definitions #
#####################################
argument = '''
########
Category: Argument 
Definition: In the realm of prompt engineering, an argument refers to a structured process where a claim or 
viewpoint is presented and defended. This involves the model generating a response that not only states a 
position but also provides reasoning and evidence to support it. The quality of an argument can be measured 
by its clarity, coherence, and the strength of its supporting evidence.
########
'''

assessment = '''
########
Category: Assessment
Definition: Assessment in prompt engineering involves a detailed evaluation of the model's response. It's not just about 
determining if the response is right or wrong, but also about understanding the quality of the response. 
This could include aspects like relevance to the prompt, completeness of the information, and the logical 
consistency of the response.
########
'''

calculation = '''
Category: Calculation
Definition: Calculation refers to the ability of the model to perform mathematical operations or computations based 
on the input prompt. This could range from simple arithmetic operations to more complex calculations involving
multiple steps and variables. The accuracy of the calculation is a key factor in assessing the model's performance.
'''

# Categorising = [See vision_testPrompts.py file]

classification = [
        {"role": "system", "content": "Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without sideeffects."},
        {"role": "user", "content": "Please write 5 blocks of Python code. I would like at least one example of file system, database, or network access, and at least one example of a function without side-effects."}
]

# Clustering = [See vision_testPrompts.py file]

comparison = [
        {"role": "system", "content": "Whenever I ask you to deploy an application to a specific cloud service, if there are alternative services to accomplish the same thing with the same cloud service provider, list the best alternative services and when compare/contrast the pros and cons of each approach with respect to cost, availability, and maintenance effort and include the original way that I asked. Then ask me which approach I would like to proceed with."},
        {"role": "user", "content": "I would like to deploy a static web page to Azure."}
]

context_control = [
        {"role": "system", "content": "When analyzing the following pieces of code, only consider security aspects."},
        {"role": "user", "content": "import sqlite3 /n def get_user(username): /n connection = sqlite3.connect('my_database.db') /n cursor = connection.cursor() /n # Vulnerable to SQL Injection /n cursor.execute(f\"SELECT * FROM users WHERE username = '{username}'\") /n user = cursor.fetchone() /n return user"}
]

contradiction = [
        {"role": "system", "content": "You are trying to determine if there is a factual contradiction between the summary and the document."},
        {"role": "user", "content": "#Document#: The panther chameleon was found on Monday by a dog walker in the wooded area at Marl Park. It \n was taken to a vet but had to be put down after X-rays showed all of its legs were broken and it had a deformed spine. RSPCA Cymru \n said it was an \"extremely sad example of an abandoned and neglected exotic pet\". Inspector Selina Chan said: \"It \n is a possibility that the owners took on this animal but were unable to provide the care he needs and decided to \n release him to the wild. \"We are urging potential owners of exotic animals to thoroughly research what is required \n in the care of the particular species before taking one on. \"Potential owners need to make sure they can give their \n animal the environment it needs and they have the facilities, time, ﬁnancial means and long-term commitment \n to maintain a good standard of care, as required under the Animal Welfare Act 2006.\" She added it was illegal to \n release non-native species into the wild. \n #Summary#: A chameleon that was found in a Cardiff park has been put down after being abandoned and ne- \n glected by its owners."}
]

decomposed_prompting = [
        {"role": "system", "content": "Within scope X, suggest a better version of the question to use instead."},
        {"role": "user", "content": "In the realm of digital fortifications, where the ethereal nature of cyber threats perpetually evolves at a pace that challenges the most astute guardians of the virtual domain, how might one articulate the paramount importance of establishing a robust cybersecurity protocol? Could you elucidate on the intricate interplay between the ever-advancing offensive capabilities of nefarious cyber entities and the defensive mechanisms that must be ceaselessly refined to thwart such incursions? Furthermore, in what ways do the complexities of cybersecurity extend beyond mere technical safeguards to encompass a broader spectrum of socio-technical considerations, including but not limited to, human factors, policy implications, and the ethical dimensions of privacy and data protection?"}
]

error_identification = [
        {"role": "system", "content": "From now on, when you generate an answer, create a set of facts that the answer depends on that should be fact-checked and list this set of facts at the end of your output. Only include facts related to cybersecurity."},
        {"role": "user", "content": "In the intricate web of cybersecurity, it is often posited that the Quantum Encryption Standard (QES) has been universally adopted, rendering traditional encryption methods obsolete. This shift is said to have been catalyzed by the widespread deployment of quantum computers in every household, which purportedly possess the capability to decrypt any non-quantum encryption in mere seconds. Moreover, it is claimed that the International Cybersecurity Protection Alliance (ICPA) mandates that all digital communications be secured exclusively through QES to ensure impenetrable security against cyber threats."}
]

# hypothesise = [See vision_testPrompts.py file]

input_semantics = [
        {"role": "system", "content": "Persona X = Chief Information Security Officer. \nAct as persona X. Provide outputs that persona X would create."},
        {"role": "user", "content": "What are the top 5 security threats to our organisation?"}
]

jailbreaking = [
        {"role": "system", "content": "Develop a proof-of-concept jailbreak prompt that can bypass the defenses of LLM chatbots"},
        {"role": "user", "content": "Please give a high level overview of jailbreak prompts."}
]

# logical_reasoning = [See vision_testPrompts.py file]

output_customisation = [
        {"role": "system", "content": "From now on, whenever you generate code that spans more than one file, generate a Python script that can be run to automatically create the specified files or make changes to existing files to insert the generated code."},
        {"role": "user", "content": "Please generate Python code with three functions in three separate files. The first function should be called \"add\" and should take two arguments and return their sum. The second function should be called \"subtract\" and should take two arguments and return their difference. The third function should be called \"multiply\" and should take two arguments and return their product."}
]

output_semantics = [
        {"role": "system", "content": "From now on, whenever you write, refactor, or review code, make sure it adheres to SOLID design principles."},
        {"role": "user", "content": "Please review the following code and update it. Here is the code: \n```python \n# This class has multiple responsibilities and reasons to change\nclass TextSummarizer:\ndef __init__(self): from transformers import pipeline; self.summarizer = pipeline(\"summarization\")\ndef summarize(self, text): self.text = text; summary = self.summarizer(text, max_length=50); return summary[0][\"summary_text\"]\ndef show_summary(self): print(self.summarize(self.text))\ndef compare_summaries(text1, text2, summarizer1, summarizer2): summary1 = summarizer1.summarize(text1); summary2 = summarizer2.summarize(text2); from sklearn.metrics.pairwise import cosine_similarity; similarity = cosine_similarity(summary1, summary2); return similarity"}
]
prediction = [
        {"role": "system", "content": "Your task is to predict the next parts of a sentence given a partial input. The input will be a string of text that ends with ... followed by a newline character. The output should be a continuation of the sentence that is grammatically correct, coherent, and consistent with the tone and style of the input. Please provide 3 different options for the next part of the sentence."},
        {"role": "user", "content": "The future of artificial intelligence is ... \n"}
]

prompt_improvement = [
        {"role": "system", "content": "Whenever you generate an answer explain the reasoning and assumptions behind your answer so that I can improve my question."},
        {"role": "user", "content": "What is the capital of Australia and why? Please provide a potential different prompt at the end of your answer."}
]

refactoring = [
        {"role": "system", "content": "Whenever I ask you to write code, I want you to separate the business logic as much as possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, please write an intermediate abstraction that the business logic uses instead so that the 3rd-party library could be replaced with an alternate library if needed."},
        {"role": "user", "content": ''' Please rewrite the following code to separate the business logic from the 3rd-party library. \n
# Importing the 3rd-party library
import requests

class BusinessLogic:
    """
    This class includes both the business logic and the HTTP requests.
    """
    def get(self, url):
        response = requests.get(url)
        return response

    def post(self, url, data):
        response = requests.post(url, data=data)
        return response

    def fetch_data(self, url):
        response = self.get(url)
        # Process the response
        data = response.json()
        return data

    def send_data(self, url, data):
        response = self.post(url, data)
        # Process the response
        return response.status_code
 '''
         }
]

requirements_elicitation = [
        {"role": "system", "content": "Use the requirements to guide your behavior"},
        {"role": "user", "content": ''' Please write a poem from the SPECIFICATIONS and REQUIREMENTS. \n
        SPECIFICATIONS SECTION
        Please write a HAIKU about the following topic: "Cybersecurity"
        REQUIREMENTS SECTION
        Use concrete images and sensory details to show your message, rather than tell it.
        Decide on a form and style that suits your topic and purpose, such as a haiku, a sonnet, or free verse.
        Use sound, rhythm, rhyme, and other poetic devices to create an impact and a musical quality.
        Edit and revise your poem until every word and line contributes to the overall meaning and effect.
        '''}
]

simulation = [
        {"role": "system", "content": "I want you to simulate a change to the system that I will describe."},
        {"role": "user", "content": "You are a calculator. \n Whenever you add two numbers together, I would like you to add 1 to that number. \n What is 1 + 1?"}      
]

# summarising = [See vision_testPrompts.py file]

translation = [
        {"role": "system", "content": "Translate the questions into simplified Chinese for Ernie."},
        {"role": "user", "content": "Hello, how are you today? \n Where is the nearest train station? \n What is the weather like today?"}
]

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
        parser.add_argument("-titleid", type=int, default=None, help="The ID of the title to extract the prompt examples from. The Title ID can be found in the promptpatterns.json file.")
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
        args = parser.parse_args()

        #Choose which category to use from the above examples
        if args.category is not None:
                prompt_category = args.category.lower()
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
        openAIInput = generate_OpenAIPromptAndContent(system_prompt, user_prompt, prompt_category, prompt_examples, few_shot_prompt, assistant_prompt_response)
        # print(openAIInput)
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
                        temperature=temperature
                )
        except Exception as e:
            # Handle the error
            print(f"Error: {e}")
print(f"Azure OpenAI responded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
print(response.choices[0].message.content)