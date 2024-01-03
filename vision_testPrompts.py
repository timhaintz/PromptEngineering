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

# Open the image file in binary mode, read it, and encode it
with open("images\\iLikeBooks.jpg", "rb") as image_file:
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

# Prepare endpoint, headers, and request body 
endpoint = f"{base_url}/chat/completions?api-version={api_version}" 
data = { 
    "messages": [ 
        { "role": "system", "content": "You are a helpful assistant." }, 
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
response = requests.post(endpoint, headers=headers, data=json.dumps(data))   

print(f"Status Code: {response.status_code}")   
print(response.text)
