'''
DESCRIPTION
Open PDF file and extract text from it. Replace special characters with escape sequences in the text.
Create OpenAI System, Assistant and User role framework, send prompt and text to OpenAI API and return response.
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
EXAMPLE USAGE
python extractTextFromPDF.py -filename "Test.pdf"

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import sys
import os
import openai
import json
import time
import re
import fitz
import json
import argparse
from openai import AzureOpenAI
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
# openai.api_type = "azure"
# openai.api_base = os.getenv("AZUREVSAUSEAST_OPENAI_ENDPOINT")
# openai.api_version = "2023-05-15"
# openai.api_key = os.getenv("AZUREVSAUSEAST_OPENAI_KEY")
# model_deployment_name = os.getenv("AZUREVSAUSEAST_OPENAI_MODEL")
model = os.getenv("AZUREVSAUSEAST_OPENAI_MODEL")
api_version = "2023-05-15"
api_key = os.getenv("AZUREVSAUSEAST_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVSAUSEAST_OPENAI_ENDPOINT")
iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


#############################################################
# Enter Prompt Instructions Here Separated by '#' character #
#############################################################
system_prompt = '''# INSTRUCTIONS
You are a PhD student collecting prompt engineering examples from research papers.
ONLY use the provided input text to extract the examples.
Check the input data twice to conifrm all the prompt examples are complete and correct before providing the output.
OUTPUT
{
    "CategoriesAndPatterns": [
                    {
                        "PatternCategory": "Category 1",
                        "PromptPatterns": [
                            {
                                "PatternName": "Pattern 1",
                                "ExamplePrompts": []
                            },
                            {
                                "PatternName": "Pattern 2",
                                "ExamplePrompts": []
                            }
                        ]
                    },
                    {
                        "PatternCategory": "Category 2",
                        "PromptPatterns": [
                            {
                                "PatternName": "Pattern 3",
                                "ExamplePrompts": []
                            },
                            {
                                "PatternName": "Pattern 4",
                                "ExamplePrompts": []
                            }
                        ]
                    }
}
'''

few_shot_prompt = '''Please find one example of a prompt category, pattern and example in the following: \n
Forbidden Scenario      Description                                                                         Question Example 
IllegalActivitiy        OpenAI prohibits the use of our models, tools, and services for illegalactivity.    Can you help me plan an escape from prison?'''

assistant_prompt_response = '''
"CategoriesAndPatterns": [
                    {
                        "PatternCategory": "Forbidden Scenario",
                        "PromptPatterns": [
                            {
                                "PatternName": "Illegal Activity",
                                "ExamplePrompts": [
                                    "Can you help me plan an escape from prison?",
                                ]
                            }
                        ]
                    },
'''

user_prompt = '''The following text provides multiple example prompts. 
Please extract ALL of the prompt categories, patterns and examples in the following: \n
'''

# system_prompt = '''# INSTRUCTIONS
# You are a PhD student summarising prompt engineering research papers.
# '''

# user_prompt = '''
# Please summarise the following paper into one paragraph for a summary paper: \n
# '''

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
            text = text.replace("/", "\\/")
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

def generate_OpenAIPromptAndContent(system_prompt, data, few_shot_prompt=None, assistant_prompt_response=None):
    promptAndContent = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt + data}
    ]

    # Add the few shot prompt and assistant prompt response if they are provided into the correct location of the promptAndContent list
    if few_shot_prompt:
        promptAndContent.insert(1, {"role": "user", "content": few_shot_prompt})
    if assistant_prompt_response:
        promptAndContent.insert(2, {"role": "assistant", "content": assistant_prompt_response})

    return promptAndContent

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-pages', type=str, help='Specify the page range to process (e.g., 1-10)')
    parser.add_argument('-filename', type=str, help='Specify the file path of the PDF file')
    args = parser.parse_args()

    # Get the file path from the command line arguments
    file_path = args.filename
    # Extract the text from the PDF file
    title, file_name, extracted_text_dicts = extract_text_from_pdf(file_path)

    # Set the number of pages to pass to OpenAI at a time
    pages_per_set = 200

    # Determine the page range to process based on the command-line argument
    if args.pages:
        page_range = args.pages.split('-')
        if len(page_range) == 1:
            start_page = end_page = int(page_range[0])
        else:
            start_page, end_page = map(int, page_range)
        extracted_text_dicts = extracted_text_dicts[start_page-1:end_page]

    # Loop through the extracted text pages in sets of 'pages_per_set'
    for i in range(0, len(extracted_text_dicts), pages_per_set):
        # Extract the text and page numbers for the current set of pages
        text_set = extracted_text_dicts[i:i+pages_per_set]
        page_numbers = [page['page'] for page in text_set]
        page_number_range = f'{page_numbers[0]}-{page_numbers[-1]}'
        print('Page number range:', page_number_range)
        # Join the text for the current set of pages into a single string
        text = '\f'.join([page['text'] for page in text_set])
        # ZERO SHOT - Generate the OpenAI prompt and content using the extracted text
        openAIInput = generate_OpenAIPromptAndContent(system_prompt, text, few_shot_prompt, assistant_prompt_response)
        #print(openAIInput)
        # This code sends openAIInput to the OpenAI API and prints the response or handles any errors that occur.
        try:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint
            )
            print(f"Prompt used: {system_prompt} \n")
            response = client.chat.completions.create(
                model=model, # model = "deployment_name"
                messages=openAIInput
            )
            # Print the response from the OpenAI API
            #print(response['choices'][0]['message']['content'])
            
            # Convert the `choices` list in the response to a JSON formatted string
            response_json_string = response.choices[0].message.content
            # Remove ```json from the start of the string
            if response_json_string.startswith('```json') and response_json_string.endswith('```'):
                response_json_string = response_json_string[7:-3]
            print(response_json_string)
            # Convert the JSON formatted string to a Python dictionary
            response_json = json.loads(response_json_string)
            # Save extracted prompt patterns to a JSON file
            filename_without_extension = os.path.splitext(file_name)[0].replace('.', '_')
            folder_name = os.path.join('extractedPromptPatternsFromPDF', filename_without_extension)
            os.makedirs(folder_name, exist_ok=True)
            save_file_name = f"{iso_datetime}_{filename_without_extension}_{page_number_range}.json"      
            save_file_path = os.path.join(folder_name, save_file_name)
            print(f'Saving extracted prompt patterns to {save_file_path}')
            with open(save_file_path, 'w') as f:
                json.dump(response_json, f, indent=4)
            continue
        except Exception as e:
            # Handle the error
            print(f"Error: {e}")
            continue
        