'''
DESCRIPTION
Connect to the Azure OpenAI API gpt-35-turbo model and chat with it.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  6/6/2023
LINKS
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import os
import openai
import json
from datetime import datetime
# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
cve = "CVE-2021-28456"
iso_datetime = datetime.utcnow().isoformat()

########### 
# PROMPTS #
###########
prompt00 = [
        {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
        {"role": "user", "content": "Tell me about {}?".format(cve)}
]

prompt01 = [
        {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
        {"role": "user", "content": "How do I fix {}?".format(cve)}
]

prompt02 = [
        {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
        {"role": "user", "content": "What is {}?".format(cve)}
]

prompt03 = [
        {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
        {"role": "user", "content": "What steps do I need to fix {}?".format(cve)}
]

promptTest = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure Cognitive Services support this too?"}
]

#############
# MAIN CODE #
#############
prompt = prompt01
response = openai.ChatCompletion.create(
    engine="gpt-35-00", # engine = "deployment_name".
    messages=prompt
)

# Create a dictionary with the prompt, datetime, and response
data = {
    "cve": cve,
    "datetime": iso_datetime,
    "prompt": prompt,
    "response": response['choices'][0]['message']['content']
}

##########
# OUTPUT #
##########
#print(response)
#print(response['choices'][0]['message']['content'])
print(json.dumps(data))
# Define the output file path
output_file = fr"C:\Users\tihaintz\OneDrive - Microsoft\Masters\{iso_datetime.replace(':', '-').replace('.', '-')}_{cve}_Agent0.json"
# Write the data to the output file
with open(output_file, "w") as f:
    json.dump(data, f)
# Print a message indicating that the file was written
print("Data written to file:", output_file)
