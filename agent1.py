'''
DESCRIPTION
Retrive the output of agent0 and determine how effective the output was in answering how to fix the CVE.
Connect to the Azure OpenAI API gpt-35-turbo model and chat with it.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  12/7/2023
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
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
iso_datetime = datetime.utcnow().isoformat()

##################
# Check the CVEs #
####################
# Set the folder path to look for Agent0's responses
response_folder_path = r"C:\Users\tihaintz\OneDrive - Microsoft\Masters\Agent0Responses"
# Loop through each file in the folder
for filename in os.listdir(response_folder_path):
    # Check if the file is a JSON file
    if filename.endswith(".json"):
        # Set the path to the JSON file
        file_path = os.path.join(response_folder_path, filename)
        
        # Load the JSON file as a Python object
        with open(file_path, "r") as f:
            json_object = json.load(f)
        
        # Check if the object contains a key with the name "CVE"
        if "cve" in json_object:
            # Get the value of the "cve" key
            cve_value = json_object["cve"]
            
            # Print the CVE value
            print(f"File {filename} contains CVE {cve_value}")
        else:
            print(f"File {filename} does not contain a CVE")


# Below will be used to check on the CVE from the above code 

# Set the folder path to search in
cve_folder_path = r"C:\Users\tihaintz\OneDrive - Microsoft\Masters\cvelistV5-main\cves"

# Get a list of all directories in the folder
directories = [dir for dir in os.listdir(cve_folder_path) if os.path.isdir(os.path.join(cve_folder_path, dir))]

# Filter the list to include only directories prior to the year 2020
filtered_directories = [dir for dir in directories if dir <= "2020"]

# Get a list of all subdirectories in the selected directory
subdirectories_path = os.path.join(cve_folder_path)
subdirectories = [dir for dir in os.listdir(subdirectories_path) if os.path.isdir(os.path.join(subdirectories_path, dir))]

# Get a list of all files in the selected subdirectory
subdirectory_path = os.path.join(subdirectories_path)
files = os.listdir(subdirectory_path)
