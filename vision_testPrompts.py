'''
DESCRIPTION
Testing the vision Azure OpenAI API
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  3/1/2024
LINKS
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/gpt-with-vision
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
https://www.loc.gov/free-to-use/
https://www.loc.gov/resource/ppmsca.42766/ - I LIKE BOOKS
https://tile.loc.gov/storage-services/service/pnp/ppmsca/42700/42766v.jpg - I LIKE BOOKS
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import os
import base64
import json
import requests
from openai import AzureOpenAI
from datetime import datetime
import random
# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
deployment_name = os.getenv("AZUREVSAUSEAST_OPENAI_VISION_MODEL")
api_version = "2023-12-01-preview"
API_KEY = os.getenv("AZUREVSAUSEAST_OPENAI_KEY") 
api_base = os.getenv("AZUREVSAUSEAST_OPENAI_ENDPOINT")

##########################
# Base64 Encode an Image #
##########################
categorising_image = "images\\categorising_sision_model_blue_corolla_crash.jpg"
clustering_image = "images\\clustering_vision_model_household_objects.jpg"
hypothesise_image = "images\\hypothesise_vision_model_goal_kick.png"
logical_reasoning_image = "images\\logical_reasoning_vision_model_circle_and_square_two_by_two.jpg"
summarising_image = "images\\summarising_vision_model_walking.jpeg"

# Change the below variable to change the image
image = summarising_image

# Open the image file in binary mode, read it, and encode it
with open(image, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()
data_url = f"data:image/jpeg;base64,{encoded_string}"

#########################
# Setup the API Request #
#########################

base_url = f"{api_base}openai/deployments/{deployment_name}" 
headers = {   
    "Content-Type": "application/json",   
    "api-key": API_KEY 
}

##################################
# Prompt Categories and Examples #
##################################
categorising = "Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. Please evaluate the damage seen in the image below. For filing the incident report, please follow the following format in JSON (note xxx is placeholder, if the information is not available in the image, put \"N/A\" instead). {\"make\": xxx, \"model\": xxx, \"license plate\": xxx, \"damage description\": xxx, \"estimated cost of repair\": xxx}"
clustering = "How are the visual parts related? If so, how to arrange them?"
hypothesise = "Predict what will happen next based on the images."
logical_reasoning = "Here are three sub images arranged in a 2-by-2 matrix. First, look at the two images in the first column, in the top left and bottom left. Then, find out the pattern in the first column based on the left two images. Next, use the found pattern and the image in the top right to infer the missing figure. Finally, describe what would the missing image look like?"
summarising = "Summarize the activities of the person."

# Change the below variable to change the prompt
system_prompt = summarising

# Prepare endpoint, headers, and request body 
endpoint = f"{base_url}/chat/completions?api-version={api_version}" 
data = { 
    "messages": [ 
        { "role": "system", "content": system_prompt }, 
        { "role": "user", "content": [  
            { 
                "type": "text", 
                "text": "Describe this picture:" 
            },
            { 
                "type": "image_url",
                "image_url": {
                "url": data_url
                }
            }
        ] } 
    ], 
    "max_tokens": 2000 
}   
#####################
# Make the API call #
#####################
print(f"Image used: {image} \nPrompt used: {system_prompt}")

response = requests.post(endpoint, headers=headers, data=json.dumps(data))   

print(f"Status Code: {response.status_code}")
# Parse the JSON string into a dictionary
response_dict = json.loads(response.text)
# Extract the content
content = response_dict['choices'][0]['message']['content']
print(content)
