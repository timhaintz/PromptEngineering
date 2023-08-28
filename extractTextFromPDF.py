'''
DESCRIPTION
Open PDF file and extract text from it. Replace special characters with escape sequences in the text.
Create OpenAI System and User role framework, send prompt and text to OpenAI API and return response.
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
https://pypi.org/project/PyMuPDF/
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import sys
import os
import openai
import json
from datetime import datetime
import time
import re
import fitz

# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

#############################################################
# Enter Prompt Instructions Here Separated by '#' character #
#############################################################
prompts = '''# Scope
- You are searching research papers for Prompt Engineering Patterns
- There may be none or many patterns in a paper.
- You are looking for patterns that are in the form of a Prompt Engineering example
- If you do not find a prompt pattern, please respond with 'NO PROMPT PATTERN FOUND'
- If you're in the references section, please respond with 'END OF PAPER'
# Expectations
- You will provide the prompt patterns found in the paper
# Style
- You are a researcher looking for prompt patterns
# Structure
- Please output in JSON format
#Safety
- You will not provide harmful content'''

def extract_text_from_pdf(pdf_file_name):
    with fitz.open(pdf_file_name) as pdf_file:
        # Get the document information
        document_info = pdf_file.metadata

        # Extract the title from the document information
        title = document_info.get('title')

        # Get the file name from the file path
        file_name = os.path.basename(pdf_file_name)

        # Print the file name and extracted title
        print(f'Title: {title}')
        print(f'File name: {file_name}')

        # Create a list to store the extracted text
        extracted_text_dicts = []

        # Iterate over the pages of the PDF file
        for page_num in range(pdf_file.page_count):
            # Get the page object
            page = pdf_file[page_num]

            # Extract the text from the page
            text = page.get_text()
            # Replace any special characters that need to be escaped in Python
            text = text.replace("\\", "\\\\")
            text = text.replace("/", "\/")
            text = text.replace("'", "\\\\'")
            text = text.replace('"', '\\"')
            text = text.replace("\n", "\\n")
            text = text.replace("\r", "\\r")
            text = text.replace("\t", "\\t")
            # Replace any special additional characters that need to be escaped in JSON
            text = text.replace("\b", "\\b")
            text = text.replace("\f", "\\f")

            # Add the text to the list
            extracted_text_dicts.append(text)
            
        # Return the list of dictionaries containing the extracted text
        return f'Title: {title}', f'File name: {file_name}', extracted_text_dicts

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
    title, file_name, extracted_text_dicts = extract_text_from_pdf(file_path)

    # Print the extracted text for each page
    #print(title, file_name)
    for i, text in enumerate(extracted_text_dicts):
        print(f'Page {i + 1}:')
        # Generate JSON data
        openAIInput = generate_json(prompts, text)
        #print(openAIInput)
        # Parse the JSON string into a Python object and send to OpenAI
        try:
            openAIInput_obj = json.loads(openAIInput)
            openAIInput_list = list(openAIInput_obj)
            #print(openAIInput_list)
            ###############
            # OpenAI CODE #
            ###############
            try:
                response = openai.ChatCompletion.create(
                    engine="gpt-35-00", # engine = "deployment_name".
                    messages=openAIInput_list
                )
                # Print the response from the OpenAI API
                print(response['choices'][0]['message']['content'])
                continue
            except  openai.Error as e:
                # Handle the error
                print(f"Error: {e}")
                continue
        except json.JSONDecodeError:
            print(f"Invalid JSON on page {i + 1}")
            continue