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
1. To find the cosine similarity run the following command:
```
python categorisation_cosine_similarity.py
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
# categorising_example = '''Category: CAT (Categorising)
# PP Name: Insurance Report Generation
# PE: Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. 
# Please evaluate the damage seen in the image below. 
# For filing the incident report, please follow the following format in JSON (note xxx is placeholder, if the information is not available in the image, put \\"N/A\\" instead).
#  {\\"make\\": xxx, \\"model\\": xxx, \\"license plate\\": xxx, \\"damage description\\": xxx, \\"estimated cost of repair\\": xxx}
# '''
# In Logic section - CAT, CLF, CLU, ERI, INP, REL
categorising_example = '''Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. Please evaluate the damage seen in the image below. For filing the incident report, please follow the following format in JSON (note xxx is placeholder, if the information is not available in the image, put \\"N/A\\" instead). {\\"make\\": xxx, \\"model\\": xxx, \\"license plate\\": xxx, \\"damage description\\": xxx, \\"estimated cost of repair\\": xxx}'''

classification_example = '''Whenever I ask you to write code, I want you to separate the business logic as much as possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, please write an intermediate abstraction that the business logic uses instead so that the 3rd-party library could be replaced with an alternate library if needed.'''

clustering_example = '''Find a common characteristic for the given objects.'''

error_identification_example = '''From now on, when you generate an answer, create a set of facts that the answer depends on that should be fact-checked and list this set of facts at the end of your output. Only include facts related to cybersecurity.'''

input_semantics_example = '''rephrase this paragraph so that a 2nd grader can understand it, emphasizing real-world applications'''

requirements_elicitation_example = '''Identify experts in the field, generate answers as if the experts wrote them, and combine the experts' answers by collaborative decision-making.'''

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

    # region Define the variables
    ##############################################
    # Define the input string and JSON file path #
    ##############################################
    input_string = category_definitions.assessment
    json_file = 'promptpatterns.json'
    
    #########################################
    # Define the top_n and threshold values #
    #########################################
    top_n = 10
    threshold = 0.2

    # endregion
    #print(f"Top: {top_n} results for finding similar prompts:\n{find_similar_prompts(input_string, json_file, top_n=top_n)}")
    print(f"Results for finding similar prompts with Cosine Similarity threshold {threshold}:\n")

    output = find_similar_prompts(input_string, json_file, threshold=threshold)

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

    print(f"\n Displaying the actual results of output to confirm the counts above:\n {output}")


    


