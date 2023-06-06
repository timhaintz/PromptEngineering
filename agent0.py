'''
DESCRIPTION
Connect to the Azure OpenAI API gpt-35-turbo model and chat with it.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  6/6/2023
LINK
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import os
import openai
# Load environment variables from the .env file
load_dotenv()

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

response = openai.ChatCompletion.create(
    engine="gpt-35-00", # engine = "deployment_name".
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure Cognitive Services support this too?"}
    ]
)

print(response)
print(response['choices'][0]['message']['content'])
