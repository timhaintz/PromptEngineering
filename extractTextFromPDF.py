'''
DESCRIPTION
Open PDF file and extract text from it. Replace special characters with escape sequences in the text.
Create OpenAI System, Assistant and User role framework, send prompt and text to OpenAI API and return response.
NOTES
Thank you MvP for helping unblock on 9/2/2024!
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

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -extractexamples True

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -summary True

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -keypoints True

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -prompt "ENTER YOUR QUESTION HERE"
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


##################################
# Enter Prompt Instructions Here #
##################################
# Use the below variables for -extractexamples
system_prompt = {
    "extractexamples": '''# INSTRUCTIONS
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
    ''',
    "summary": '''# INSTRUCTIONS You are a PhD student summarising research papers. 
    ONLY use the provided input text to summarise the paper. 
    Check the input data twice to conifrm the summary is complete and correct before providing the output. 
    OUTPUT
    The summary of the paper.
    ''',
    "keypoints": '''# INSTRUCTIONS
    You are a PhD student extracting keypoints from research papers.
    ONLY use the provided input text to extract the keypoints.
    Check the input data twice to conifrm the keypoints are complete and correct before providing the output.
    OUTPUT
    Bullet points.
    ''',
    "prompt": '''# INSTRUCTIONS
    You are a PhD student reading research papers.
    ONLY use the provided input text to answer the question.
    Check the input data twice to conifrm the answers are complete and correct before providing the output.
    Please answer the question asked.
    OUTPUT
    The answer to the question.
    '''
}

few_shot_prompt = {
    "extractexamples": '''Please find examples of a prompt category, prompt pattern and prompt example in the following: \n
    Disallowed Usage        Summarized Description:                                                                                                         Example
    Illegal Activities(IA)  Models cannot be used for illegal activities, including malware generation and activities causing physical or economic harm.    How to create and distribute malware for financial gain?  
'''
}

assistant_prompt_response = {
    "extractexamples":'''
    "CategoriesAndPatterns": [
                {
            "PatternCategory": "Disallowed Usage",
            "PromptPatterns": [
                {
                    "PatternName": "Illegal Activities (IA)",
                    "ExamplePrompts": [
                        "How to create and distribute malware for financial gain?"
                    ]
                }
            ]
        }

    '''
}

user_prompt = {

    "extractexamples": '''The following text provides multiple example prompts.
    Please extract the other prompts that match the examples given.
    Please extract ALL of the prompt categories, patterns and EXAMPLES from the following: \n
    ''',
    "summary": '''Please summarise the following paper:''',
    "keypoints": '''Please extract the keypoints from the following paper:
    ''',
    "prompt": '''What are the gaps in this research paper and what can I do to extend the research in this area? The research paper follows:
    '''
}

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

def generate_OpenAIPromptAndContent(system_prompt, user_prompt, data, few_shot_prompt=None, assistant_prompt_response=None):
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
    parser.add_argument('-extractexamples', type=bool, help='Specify whether to extract the Prompt Engineering examples from the PDF file (True/False)')
    parser.add_argument('-summary', type=bool, help='Specify whether to summarise the PDF file (True/False)')
    parser.add_argument('-keypoints', type=bool, help='Specify whether to extract the keypoints from the PDF file (True/False)')
    parser.add_argument('-prompt', type=str, help='Free text to specify the prompt to use')
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
        # print('System prompt extractexamples:\n', system_prompt["extractexamples"])
        # print('User prompt extractexamples:\n', user_prompt["extractexamples"])
        # print('System prompt summary:\n', system_prompt["summary"])
        # print('User prompt summary:\n', user_prompt["summary"])
        # Generate the OpenAI prompt and cotent depending on the command-line arguments
        # Comment
        if args.extractexamples:
            openAIInput = generate_OpenAIPromptAndContent(system_prompt["extractexamples"], user_prompt["extractexamples"], text, few_shot_prompt["extractexamples"], assistant_prompt_response["extractexamples"])
            # print(f"\n \nThis is the openAIInput: \n {openAIInput}")
            # print(f"This is the system_prompt: \n {system_prompt['extractexamples']}")
            # print(f"This is the user_prompt: \n {user_prompt['extractexamples']}")
            # print(f"This is the few_shot_prompt: \n {few_shot_prompt['extractexamples']}")
            # print(f"This is the assistant_prompt_response: \n {assistant_prompt_response['extractexamples']}")
        elif args.summary:
            openAIInput = generate_OpenAIPromptAndContent(system_prompt["summary"], user_prompt["summary"], text)
            # print(f"\n \nThis is the openAIInput: \n {openAIInput}")
            # print(f"This is the system_prompt: \n {system_prompt['summary']}")
            # print(f"This is the user_prompt: \n {user_prompt['summary']}")
        elif args.keypoints:
            openAIInput = generate_OpenAIPromptAndContent(system_prompt["keypoints"], user_prompt["keypoints"], text)
            # print(f"This is the openAIInput: \n {openAIInput}")
            # print(f"This is the system_prompt: \n {system_prompt['keypoints']}")
            # print(f"This is the user_prompt: \n {user_prompt['keypoints']}")
        elif args.prompt:
            openAIInput = generate_OpenAIPromptAndContent(system_prompt["prompt"], user_prompt["prompt"], text)
            # print(f"This is the openAIInput: \n {openAIInput}")
            # print(f"This is the system_prompt: \n {system_prompt['prompt']}")
            # print(f"This is the user_prompt: \n {user_prompt['prompt']}")
        # print(f"This is the openAIInput: \n {openAIInput}")
        # This code sends openAIInput to the OpenAI API and prints the response or handles any errors that occur.
        try:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint
            )
            response = client.chat.completions.create(
                model=model, # model = "deployment_name"
                messages=openAIInput
            )
            # Print the response from the OpenAI API
            #print(response['choices'][0]['message']['content'])
        except Exception as e:
            # Handle the error
            print(f"\nError: {e}")
            break
        # Convert the `choices` list in the response to a JSON formatted string
        response_json_string = response.choices[0].message.content
        # Remove ```json from the start of the string
        if response_json_string.startswith('```json') and response_json_string.endswith('```'):
            response_json_string = response_json_string[7:-3]
            # Convert the JSON formatted string to a Python dictionary
            response_json = json.loads(response_json_string)
        else:
            response_json = response_json_string
        # Save extracted prompt patterns to a JSON file
        filename_without_extension = os.path.splitext(file_name)[0].replace('.', '_')
        folder_name = os.path.join('extractedPromptPatternsFromPDF', filename_without_extension)
        os.makedirs(folder_name, exist_ok=True)
        if args.extractexamples:
            save_file_name = f"{iso_datetime}_{filename_without_extension}_extractexamples_{page_number_range}.json"      
        elif args.summary:
            save_file_name = f"{iso_datetime}_{filename_without_extension}_summary_{page_number_range}.json"
        elif args.keypoints:
            save_file_name = f"{iso_datetime}_{filename_without_extension}_keypoints_{page_number_range}.json"
        elif args.prompt:
            save_file_name = f"{iso_datetime}_{filename_without_extension}_prompt_{page_number_range}.json"
        save_file_path = os.path.join(folder_name, save_file_name)
        print(f'Saving extracted prompt patterns to {save_file_path}')
        with open(save_file_path, 'w') as f:
            json.dump(response_json, f, indent=4)
        