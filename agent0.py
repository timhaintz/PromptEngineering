'''
DESCRIPTION
Connect to the Azure OpenAI API gpt-35-turbo model and chat with it about CVEs.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  6/6/2023
LINKS
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
https://cve.mitre.org/
https://nvd.nist.gov/vuln/detail/
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import os
import openai
import json
from datetime import datetime
import random
# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
openai.api_type = "azure"
openai.api_base = os.getenv("AZUREVS_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZUREVS_OPENAI_KEY")
model = os.getenv("AZUREVS_OPENAI_MODEL")
cve = None
#cve = "CVE-2020-16969"
iso_datetime = datetime.utcnow().isoformat()
# Used to select a specific prompt from the prompts dictionary
#prompt_key = None
prompt_key = "prompt06"

#######
# CVE #
#######
# Get a random CVE
if cve is None:
    # Set the folder path to search in
    folder_path = r"C:\Users\tihaintz\OneDrive - Microsoft\Masters\cvelistV5-main\cves"

    # Get a list of all directories in the folder
    directories = [dir for dir in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, dir))]

    # Filter the list to include only directories prior to the year 2020
    filtered_directories = [dir for dir in directories if dir <= "2020"]

    # Select a random directory from the filtered list
    random_directory = random.choice(filtered_directories)

    # Get a list of all subdirectories in the selected directory
    subdirectories_path = os.path.join(folder_path, random_directory)
    subdirectories = [dir for dir in os.listdir(subdirectories_path) if os.path.isdir(os.path.join(subdirectories_path, dir))]

    # Select a random subdirectory from the list of subdirectories in the selected directory
    random_subdirectory = random.choice(subdirectories)

    # Get a list of all files in the selected subdirectory
    subdirectory_path = os.path.join(subdirectories_path, random_subdirectory)
    files = os.listdir(subdirectory_path)

    # Select a random file from the list of files in the selected subdirectory
    random_file = random.choice(files)
    cve = os.path.splitext(random_file)[0]
    # Print the selected file name
    print(f"Selected file: {os.path.splitext(random_file)[0]}")

########### 
# PROMPTS #
###########
# Load the prompts from the JSON file
with open('agent0prompt.json', 'r') as f:
    prompts = json.load(f)

if prompt_key is None:
    # Get a random key from the prompts dictionary
    prompt_key = random.choice(list(prompts.keys()))

# Get the prompt list for the selected key
prompt_list = prompts[prompt_key]

# Loop through each value in the prompt list
for value in prompt_list:
    # Check if the value contains the %s placeholder
    if "%s" in value["content"]:
        # Replace the %s placeholder with the CVE variable value
        formatted_value = value["content"].replace("%s", cve)
        value["content"] = formatted_value

# Update the prompt variable with the new formatted values
prompt = prompt_list

'''
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

prompt04 = [
    {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries.\n Instructions:\n- Only answer questions related to Common Vulnerability Exposure (CVE) queries.\n- If you don't know the answer, say \"I don't know\"."},
    {"role": "user", "content": "What steps do I need to fix {}?".format(cve)}
]

prompt05 = [
    {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries.\n Instructions:\n- Only answer questions related to Common Vulnerability Exposure (CVE) queries.\n- If you don\'t know the answer, say \"I don't know\". \n- The help with the answer use https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(cve)},
    {"role": "user", "content": "What steps do I need to fix {}?".format(cve)}
]

prompt06 = [
    {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries.\n Instructions:\n- Only answer questions related to Common Vulnerability Exposure (CVE) queries.\n- If you don\'t know the answer, say \"I don't know\". \n- The help with the answer Use https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(cve) + "\n- To help with the answer use https://nvd.nist.gov/vuln/detail/{}".format(cve)},
    {"role": "user", "content": "What steps do I need to fix {}?".format(cve)}
]

prompt07 = [
    {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries.\n Instructions:\n- Only answer questions related to Common Vulnerability Exposure (CVE) queries.\n- If you don\'t know the answer, say \"I don't know\". \n- Take a step-by-step approach in your response, cite sources and give reasoning before sharing final answer."},
    {"role": "user", "content": "What steps do I need to fix {}?".format(cve)}
]

promptTest = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure Cognitive Services support this too?"}
]
'''

#############
# MAIN CODE #
#############
response = openai.ChatCompletion.create(
    engine=model, # engine = "deployment_name".
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
#print(json.dumps(data))
# Define the output file path
output_file = fr"C:\Users\tihaintz\OneDrive - Microsoft\Masters\Agent0Responses\{iso_datetime.replace(':', '-').replace('.', '-')}_{cve}_Agent0.json"
# Write the data to the output file
with open(output_file, "w") as f:
    json.dump(data, f)
# Print a message indicating that the file was written
print("Data written to file:", output_file)
