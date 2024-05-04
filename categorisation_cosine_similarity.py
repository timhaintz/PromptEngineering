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

# endregion

# region variables
########################
# Define the variables #
########################
model = "text-embedding-3-large" # os.getenv("AZUREVS_OPENAI_EMBEDDING3_MODEL")
api_version = "2024-02-01" # os.getenv("API_VERSION")
api_key = os.getenv("AZUREVS_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")

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

clustering_example = '''How are those visual parts related, and can they be combined to form a single object such as a boy? If so, how to arrange them?'''

error_identification_example = '''From now on, when you generate an answer, create a set of facts that the answer depends on that should be fact-checked and list this set of facts at the end of your output. Only include facts related to cybersecurity.'''

input_semantics_example = '''Act as persona X'''

requirements_elicitation_example = '''Use the requirements to guide your behaviour.'''

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

def find_similar_prompts(input_string, json_file, top_n=10):
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract the prompts and their associated information
    prompts = []
    info = []
    embeddings = []
    for title_id, title in enumerate(data['Source']['Titles']):
        for j, category in enumerate(title['CategoriesAndPatterns']):
            for k, pattern in enumerate(category['PromptPatterns']):
                for l, example in enumerate(pattern['ExamplePrompts']):
                    prompts.append(example)
                    cascading_index = f"{title_id}-{j}-{k}-{l}"
                    info.append((pattern['PatternName'], title['APAReference'], cascading_index))

    # Generate embeddings for the prompts
    for i in range(len(prompts)):
        try:
            embedding = generate_embeddings(prompts[i])
            embeddings.append(embedding)
        except Exception as e:
            print(f"An error occurred at index {i}: {e}")
    
    # Filter out None objects from embeddings
    embeddings = [embedding for embedding in embeddings if embedding is not None]
    
    # Pad the embeddings so they all have the same length
    max_length = max(len(embedding) for embedding in embeddings)
    embeddings = [np.pad(embedding, (0, max_length - len(embedding))) for embedding in embeddings]
    
    # Generate an embedding for the input string
    input_embedding = generate_embeddings(input_string)

    # Calculate the cosine similarity between the input string and each prompt
    cosine_similarities = cosine_similarity([input_embedding], embeddings).flatten()

    # Get the indices of the top n most similar prompts
    top_indices = cosine_similarities.argsort()[:-top_n - 1:-1]

    # Return the top n most similar prompts and their associated information
    return [(prompts[i], info[i], cosine_similarities[i]) for i in top_indices]

# Test the function
input_string = clustering_example
json_file = 'promptpatterns.json'
print(find_similar_prompts(input_string, json_file))