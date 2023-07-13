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

####################
# Get a random CVE #
####################
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

# Print the selected file name
print(f"Selected file: {os.path.splitext(random_file)[0]}")