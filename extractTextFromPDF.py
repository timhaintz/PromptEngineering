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
import json

# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
openai.api_type = "azure"
openai.api_base = os.getenv("AZUREVS_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZUREVS_OPENAI_KEY")
iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

#############################################################
# Enter Prompt Instructions Here Separated by '#' character #
#############################################################
prompts = '''# Scope
- You are searching research papers for Prompt Engineering Prompts
- There may be zero examples
- Look for patterns that are an example Prompt Engineering Prompt
- Please respond with 'NO PROMPT PATTERN FOUND' if no Prompt Engineering Prompt is found
- Respond with 'END OF PAPER' in the bibliography or references section
# Expectations
- Provide the prompt patterns found in the paper
- Provide the prompt patterns in the form of a JSON file
- Reflect on the patterns and check they are a prompt engineering pattern before responding
# Style
- You are a PhD researcher looking for prompt patterns
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

            # Add page number and text to the list
            extracted_text_dicts.append({'page': page_num, 'text': text})
            
        # Return the list of dictionaries containing the extracted text
        return title, file_name, extracted_text_dicts

def generate_OpenAIPromptAndContent(prompts, data):
    promptAndContent = [
        {"role": "system", "content": prompts},
        {"role": "user", "content": data}
    ]

    return promptAndContent

if __name__ == '__main__':
    # Get the file path from the command line arguments
    file_path = sys.argv[1]
    # Extract the text from the PDF file
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
            #print(response['choices'][0]['message']['content'])
            
            # Convert response to JSON format
            response_json = json.dumps(response['choices'][0]['message']['content'], indent=4)
            
            # Save extracted prompt patterns to a JSON file
            filename_without_extension = os.path.splitext(file_name)[0].replace('.', '_')
            folder_name = os.path.join('extractedPromptPatternsFromPDF', filename_without_extension)
            os.makedirs(folder_name, exist_ok=True)
            save_file_name = f"{iso_datetime}_{filename_without_extension}_{page_number_range}.json"      
            save_file_path = os.path.join(folder_name, save_file_name)
            print(f'Saving extracted prompt patterns to {save_file_path}')
            with open(save_file_path, 'w') as f:
                f.write(response_json)
            continue
        except Exception as e:
            # Handle the error
            print(f"Error: {e}")
            continue
        