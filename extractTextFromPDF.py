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
openai.api_base = os.getenv("AZUREVS_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZUREVS_OPENAI_KEY")

#############################################################
# Enter Prompt Instructions Here Separated by '#' character #
#############################################################
prompts = '''# Scope
- You are searching research papers for Prompt Engineering Patterns
- There may be zero or many patterns in a paper.
- You are looking for patterns that are in the form of a Prompt Engineering example
- If you do not find a prompt pattern, please respond with 'NO PROMPT PATTERN FOUND'
- If you're in the references section, please respond with 'END OF PAPER'
# Expectations
- You will provide the prompt patterns found in the paper
- You will provide the prompt patterns in the form of a JSON file
- You will reflect on the patterns and check they are actually a prompt engineering pattern before responding
# Style
- You are a researcher looking for prompt patterns
# Structure
- Please output in the JSON format below:
"CategoriesAndPatterns":
   "PatternCategory": "Category 1",
    "PromptPatterns":
            "PatternName": "Pattern 1",
            "ExamplePrompts":
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
        for each_page in range(pdf_file.page_count):
            # Get the page object
            page = pdf_file[each_page]
            page_num = each_page + 1

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
            extracted_text_dicts.append({'page': page_num, 'text': text})
            
        # Return the list of dictionaries containing the extracted text
        return f'Title: {title}', f'File name: {file_name}', extracted_text_dicts

def generate_OpenAIPromptAndContent(prompts, data):
    promptAndContent = [
        {"role": "system", "content": prompts},
        {"role": "user", "content": data}
    ]

    return promptAndContent

if __name__ == '__main__':
    # Get the file path from the command line arguments
    file_path = sys.argv[1]
    # Replace 'file_path' with the actual file path
    title, file_name, extracted_text_dicts = extract_text_from_pdf(file_path)

    # Set the number of pages to pass to OpenAI at a time
    pages_per_set = 4

    # Loop through the extracted text pages in sets of 'pages_per_set'
    for i in range(0, len(extracted_text_dicts), pages_per_set):
        # Extract the text and page numbers for the current set of pages
        text_set = extracted_text_dicts[i:i+pages_per_set]
        page_numbers = [page['page'] for page in text_set]
        page_number_range = f'{page_numbers[0]}-{page_numbers[-1]}'
        print('Page number range:', page_number_range)
        # Join the text for the current set of pages into a single string
        text = '\f'.join([page['text'] for page in text_set])
        # Generate the OpenAI prompt and content using the extracted text
        openAIInput = generate_OpenAIPromptAndContent(prompts, text)
        #print(openAIInput)
        # This code sends openAIInput to the OpenAI API and prints the response or handles any errors that occur.
        try:
            response = openai.ChatCompletion.create(
                engine="tjhvs-gpt-35-Turbo-16k", # engine = "model deployment name".
                messages=openAIInput
            )
            # Print the response from the OpenAI API
            print(response['choices'][0]['message']['content'])
            continue
        except Exception as e:
            # Handle the error
            print(f"Error: {e}")
            continue
        