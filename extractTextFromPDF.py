'''
DESCRIPTION
Open PDF file and extract text from it.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  20/8/2023
LINKS
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
https://resources.github.com/copilot-for-business/
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import sys
import os
import openai
import json
from datetime import datetime
import re
import PyPDF2

# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

################################################
# Enter Prompts Here Separated by '#' character#
################################################
prompts = '''# Prompt Example 0.
# Prompt Example 1.
# Prompt Example 2.'''

###################################################################################################
# Enter Instructions Here Separated by '#' character - this can be used in the future for prompts #
###################################################################################################
'''# Example prompt instructions below
# Scope
-Helpful assistant
-item Cybersecurity etc
# Expectations
- Provide output in bullet points etc.
- Provide references
# Style
- Written in a professional manner
- Etc
# Structure
- Output as JSON
- Or example output given
# Grounding
- Source data to use for grounding
#Safety
- You will not provide harmful content
- Etc'''

def extract_text_from_pdf(pdf_file_name):
    with open(pdf_file_name, 'rb') as pdf_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the title of the document
        title = pdf_reader.metadata.title

        # Print the title of the document
        print(f'Title: {title}')

        # Get the number of pages in the PDF file
        num_pages = len(pdf_reader.pages)

        # Loop through each page in the PDF file
        for page_num in range(num_pages):
            # Get the page object for the current page
            page_obj = pdf_reader.pages[page_num]

            # Extract the text from the page object
            page_text = page_obj.extract_text()

            # Print the text for the current page
            print(f'Text for page {page_num + 1}:')
            print(page_text)

def generate_json(prompts, data):
    initial_prompt = [
    {"role": "system", "content": "#Prompt:"},
    {"role": "user", "content": "#Content:"}
    ]
    # Convert the initial prompt to a JSON string
    prompt_json = json.dumps(initial_prompt)

    # Add the deidentified data and prompt to the prompt variable
    promptAndContent = prompt_json.replace('"#Prompt:"', f'"{prompts}"')
    promptAndContent = promptAndContent.replace('"#Content:"', f'"#Content:{data}"')

    # Replace newline characters with the escape sequence \n
    promptAndContent = promptAndContent.replace('\n', '\\n')

    return promptAndContent

if __name__ == '__main__':
    # Get the file path from the command line arguments
    file_path = sys.argv[1]
    # Replace 'file_path' with the actual file path
    extract_text_from_pdf(file_path)

'''
####################
# OpenAI CODE #
####################
response = openai.ChatCompletion.create(
    engine="gpt-35-00", # engine = "deployment_name".
    messages=prompt
)

# Print the response from the OpenAI API
print(response['choices'][0]['message']['content'])
#print(response)
'''