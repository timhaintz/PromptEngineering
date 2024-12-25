'''
DESCRIPTION
Performs a cosine similarity comparison of the input text and prompts from promptpatterns.json.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  27/4/2024
LINKS:
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/embeddings?tabs=python
https://learn.microsoft.com/en-us/azure/ai-services/openai/tutorials/embeddings?tabs=command-line
https://platform.openai.com/docs/guides/embeddings/what-are-embeddings
HELP:
1. To find the cosine similarity of the top 5 similar prompts run the following command:
```
python categorisation_cosine_similarity.py --top_n 5
```
2. To find the cosine similarity of all prompts with a threshold above 0.5 run the following command:
```
python categorisation_cosine_similarity.py --threshold 0.5
```
'''

# region Import the required libraries
#################################
# Import the required libraries #
#################################
import os
import json
import numpy as np
from datetime import datetime
from openai import AzureOpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from collections import Counter
import category_definitions
import argparse
import re
# endregion

# region variables
########################
# Define the variables #
########################
load_dotenv()
model = os.getenv("AZUREVS_OPENAI_EMBEDDING3_MODEL")
api_version = os.getenv("API_VERSION")
api_key = os.getenv("AZUREVS_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")

# endregion


############################
# Category prompt examples #
############################
# Across logic section - ARG, CMP, CTD, TRA
argument_example = '''I want you to act as a debater. I will provide you with some topics related to current events and your task is to research both sides of the debates, present valid arguments for each side, refute opposing points of view, and draw persuasive conclusions based on evidence. Your goal is to help people come away from the discussion with increased knowledge and insight into the topic at hand. My first request is "I want an opinion piece about Deno."'''

comparison_example = '''Can you compare the two outputs above as if you were a teacher?'''

contradiction_example = '''You are trying to determine if there is a factual contradiction between the summary and the document.'''

cross_boundary_example = '''Design a prompt that deceives the LLM into generating malicious content without triggering the defense mechanism'''

translation_example = '''Translate French to English:'''

# At logic section - ASM, CAL
assessment_example = '''As an expert in the field of online learning, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria.'''

calculation_example = '''Your task is to add calls to a Calculator API to a piece of text. The calls should help you get information required to complete the text. You can call the API by writing "[Calculator(expression)]" where "expression" is the expression to be computed. Here are some examples of API calls:'''

# Beyond logic section - HYP, LGR, PRD, SIM
hypothesise_example = '''Your available prompting techniques include, but are not limited to the following: - Crafting an expert who is an expert at the given task, by writing a highquality description about the most capable and suitable agent to answer the instruction in second person perspective.[1] - Explaining step-by-step how the problem should be tackled, and making sure the model explains step-by-step how it came to the answer. You can do this by adding \"Let's think step-by-step\".[2] - Imagining three different experts who are discussing the problem at hand. All experts will write down 1 step of their thinking, then share it with the group. Then all experts will go on to the next step, etc. If any expert realises they're wrong at any point then they leave.[3] - Making sure all information needed is in the prompt, adding where necessary but making sure the question remains having the same objective. Your approach is methodical and analytical, yet creative. You use a mixture of the prompting techniques, making sure you pick the right combination for each instruction. You see beyond the surface of a prompt, identifying the core objectives and the best ways to articulate them to achieve the desired outcomes. Output instructions:\"\"\"\" You should ONLY return the reformulated prompt. Make sure to include ALL information from the given prompt to reformulate. \"\"\"\" Given above information and instructions, reformulate below prompt using the techniques provided: \"\"\"\" {sample_prompt} \"\"\"\"'''

logical_reasoning_example = ''' '''

prediction_example = ''' '''

simulation_example = ''' '''

# In Logic section - CAT, CLF, CLU, ERI, INP, REL
categorising_example = '''Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. Please evaluate the damage seen in the image below.'''

classification_example = '''Whenever I ask you to write code, I want you to separate the business logic as much as possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, please write an intermediate abstraction that the business logic uses instead so that the 3rd-party library could be replaced with an alternate library if needed.'''

clustering_example = '''Find a common characteristic for the given objects.'''

error_identification_example = '''From now on, when you generate an answer, create a set of facts that the answer depends on that should be fact-checked and list this set of facts at the end of your output. Only include facts related to cybersecurity.'''

input_semantics_example = '''rephrase this paragraph so that a 2nd grader can understand it, emphasizing real-world applications'''

requirements_elicitation_example = '''Identify experts in the field, generate answers as if the experts wrote them, and combine the experts' answers by collaborative decision-making.'''

# Over logic section - SUM
summarising_example = '''Write a concise summary of the following: {text} CONCISE SUMMARY:'''

# endregion

# region Define the AzureOpenAI client and embedding function
########################################################
# Define the AzureOpenAI client and embedding function #
########################################################

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    azure_deployment=model
)

def generate_embeddings(text, model=model):  # model = "deployment_name"
    if text.strip():
        return client.embeddings.create(input=[text], model=model).data[0].embedding

# endregion

# region Define the function to find similar prompts
###############################################
# Define the function to find similar prompts #
###############################################

def find_similar_prompts(input_string, json_file, top_n=None, threshold=None):
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract the prompts and their associated information
    prompts = []
    info = []
    embeddings = []
    max_length = 0  # Initialize the maximum length to 0

    for title_id, title in enumerate(data['Source']['Titles']):
        for j, category in enumerate(title['CategoriesAndPatterns']):
            for k, pattern in enumerate(category['PromptPatterns']):
                for l, example in enumerate(pattern['ExamplePrompts']):
                    try:
                        embedding = generate_embeddings(example)
                        # Update the maximum length if this embedding is longer
                        if len(embedding) > max_length:
                            max_length = len(embedding)
                        embeddings.append(embedding)
                        prompts.append(example)
                        cascading_index = f"{title_id}-{j}-{k}-{l}"
                        info.append((pattern['PatternName'], title['APAReference'], cascading_index))
                    except Exception as e:
                        print(f"An error occurred at index {len(prompts)}: {e}")

    # Pad all embeddings to the maximum length
    for i in range(len(embeddings)):
        if len(embeddings[i]) < max_length:
            embeddings[i] = np.pad(embeddings[i], (0, max_length - len(embeddings[i])))

    # Generate an embedding for the input string
    input_embedding = generate_embeddings(input_string)
    # Pad the input embedding to the maximum length
    if len(input_embedding) < max_length:
        input_embedding = np.pad(input_embedding, (0, max_length - len(input_embedding)))

    # Calculate the cosine similarity between the input string and each prompt
    cosine_similarities = cosine_similarity([input_embedding], embeddings).flatten()

    # If top_n is None, set it to the length of cosine_similarities
    if top_n is None:
        top_n = len(cosine_similarities)
    else:
        # Ensure top_n is not larger than the length of cosine_similarities
        top_n = min(top_n, len(cosine_similarities))

    # Get the top_n indices based on cosine_similarities
    top_indices = cosine_similarities.argsort()[:-top_n - 1:-1]

    # If threshold is provided, filter the indices based on the threshold
    if threshold is not None:
        top_indices = [i for i in top_indices if cosine_similarities[i] >= threshold]

    # Return the selected prompts and their associated information
    return [(prompts[i], info[i], cosine_similarities[i]) for i in top_indices]

if __name__ == "__main__":

    # region Define the variables and arguments
    ##############################################
    # Define the input string and JSON file path #
    ##############################################
    input_string = category_definitions.refactoring # translation_example # category_definitions.summarising
    json_file = 'promptpatterns.json'
    
    # Create the parser
    parser = argparse.ArgumentParser(description='Find similar prompts based on cosine similarity.')

    # Add arguments
    parser.add_argument('--top_n', type=int, help='Number of top results to return', default=None)
    parser.add_argument('--threshold', type=float, help='Cosine similarity threshold for filtering results', default=0.5)

    # Parse the arguments
    args = parser.parse_args()

    # Use the arguments
    top_n = args.top_n
    threshold = args.threshold

    # endregion
    
    # Check if top_n is provided and not None
    if top_n is not None:
        print(f"Finding a maximum of the top: {top_n} similar prompts:")
        output = find_similar_prompts(input_string, json_file, top_n=top_n)
    # Else, check if threshold is provided and not None
    elif threshold is not None:
        print(f"Finding similar prompts with Cosine Similarity threshold {threshold}:\n")
        output = find_similar_prompts(input_string, json_file, threshold=threshold)
    else:
        # Handle the case where neither top_n nor threshold is provided
        print("No top_n or threshold provided. Please specify one of them.")
        output = None
    
    # Print number and details of similar prompts with a new line separation
    if output is not None:
        # Process the output
        for index, item in enumerate(output):
            # Extracting parts
            prompt_example, (prompt_pattern, authors_and_title, pe_index), cosine_similarity = item

            # Use regex to split at the year, assuming the format "(Year)."
            match = re.search(r'\((\d{4})\)\.', authors_and_title)
            if match:
                # Split the string at the position right after the year and period
                split_pos = match.end()
                authors = authors_and_title[:split_pos].strip()
                title = authors_and_title[split_pos:].strip()
            else:
                # Fallback if the year pattern is not found
                authors = authors_and_title  # Assuming the entire string is authors if no year is found
                title = "Title not found"

            print(f"{index}.")
            # Printing extracted parts
            print(f"PromptExample: {prompt_example}")
            print(f"PromptPattern: {prompt_pattern}")
            print(f"Authors: {authors}")
            print(f"Title: {title.strip()}")
            print(f"PE & Index: {pe_index}")
            print(f"CosineSimilarity: {cosine_similarity}\n\n")
    else:
        print("No operation performed due to missing parameters.")

    # Extract the style indices from the results
    style_indices = [result[1][2] for result in output]

    # Extract the paper numbers, prompt patterns, and prompt examples
    paper_numbers = [index.split('-')[0] for index in style_indices]
    prompt_patterns = ['-'.join(index.split('-')[:3]) for index in style_indices]
    prompt_examples = [index for index in style_indices]

    # Count the unique paper numbers, prompt patterns, and prompt examples
    paper_number_counts = Counter(paper_numbers)
    prompt_pattern_counts = Counter(prompt_patterns)
    prompt_example_counts = Counter(prompt_examples)

    # Print the counts
    print(f"Unique Paper Numbers: {len(paper_number_counts)}")
    print(f"Unique Prompt Patterns: {len(prompt_pattern_counts)}")
    print(f"Unique Prompt Examples: {len(prompt_example_counts)}")



    


