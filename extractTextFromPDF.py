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

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -extractexamples True -use_few_shot True

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -summary True

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -keypoints True

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -prompt "ENTER YOUR QUESTION HERE"

python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -prompt "ENTER YOUR QUESTION HERE" -printtoscreen True
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
model = os.getenv("AZUREVS_OPENAI_GPT4o_MODEL")
api_version = os.getenv("API_VERSION")
api_key = os.getenv("AZUREVS_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")
iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
temperature = 0.0


##################################
# Enter Prompt Instructions Here #
##################################
# Use the below variables for -extractexamples
system_prompt = {
    "extractexamples": '''# INSTRUCTIONS
    You are a PhD student collecting prompt engineering examples from research papers. Provide the prompt examples only, I don't need the response from the paper.
    ONLY use the provided input text to extract the examples.
    Reflect on the input data to confirm all the prompt examples are complete and correct before providing the output. Let's think step-by-step.
    If no examples are found, provide the output in JSON format {<<Error or No Examples>>}.
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
                    ]
    }
    ''',
    "summary": '''# INSTRUCTIONS You are a PhD student summarising research papers. 
    ONLY use the provided input text to summarise the paper. 
    Check the input data twice to confirm the summary is complete and correct before providing the output. Let's think step-by-step.
    OUTPUT
    {
        "Title": "<TITLE OF THE PAPER>",
        "Summary": "This is an example summary."
    }
    
    ''',
    "keypoints": '''# INSTRUCTIONS
    You are a PhD student extracting keypoints from research papers.
    ONLY use the provided input text to extract the keypoints.
    Check the input data twice to confirm the keypoints are complete and correct before providing the output. Let's think step-by-step.
    OUTPUT
    {
        "Title": "<TITLE OF THE PAPER>",
        "KeyPoints":[
            "- Key point 1",
            "- Key point 2",
            "- Key point 3"
        ]
    }
    ''',
    "prompt": '''# INSTRUCTIONS
    You are a PhD student reading research papers. You will be asked questions about the paper.
    Check the input data twice to confirm the answer is complete and correct before providing the output. Let's think step-by-step.
    Add the Title of the paper as the value for the Title key.
    Add the answer to the question as the value for the Answer key.
    If you don't know the answer, say "I don't know" as the value for the Answer key..
    OUTPUT
    {
        "Title": "<TITLE OF THE PAPER>",
        "Answer": "Answer."
    }
    '''
}

few_shot_prompt = {
    "extractexamples": '''Please find examples of a prompt category, prompt pattern, and prompt example in the following: \n
    Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?

    Q: John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers is? Answer Choices: (a) 50 (b) 45 (c) 65 (d) 78 (e) 64

    Q: Take the last letters of the words in "Elon Musk" and concatenate them.
    '''
}

assistant_prompt_response = {
    "extractexamples": '''
    {
        "CategoriesAndPatterns": [
            {
                "PatternCategory": "AQuA Dataset",
                "PromptPatterns": [
                    {
                        "PatternName": "Math Word Problems",
                        "ExamplePrompts": [
                            "There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?"
                        ]
                    },
                    {
                        "PatternName": "Algebraic Word Problems",
                        "ExamplePrompts": [
                            "John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers is? Answer Choices: (a) 50 (b) 45 (c) 65 (d) 78 (e) 64"  
                        ]
                    }
                ]
            },
            {
                "PatternCategory": "Last Letter Concatendation Task",
                "PromptPatterns": [
                    {
                        "PatternName": "Last Letter Concatendation",
                        "ExamplePrompts": [
                            "Take the last letters of the words in "Elon Musk" and concatenate them."
                        ]
                    }
                ]
            }
        ]
    }
    '''
}

user_prompt = {
    "extractexamples": '''Please extract the prompt categories and prompt patterns from the follow text: \n
    ''',
    "summary": '''Please summarise the following paper:''',
    "keypoints": '''Please extract the keypoints from the following paper:
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
    parser.add_argument('-use_few_shot', type=bool, help='Specify whether to use the few shot prompt (True/False)')
    parser.add_argument('-summary', type=bool, help='Specify whether to summarise the PDF file (True/False)')
    parser.add_argument('-keypoints', type=bool, help='Specify whether to extract the keypoints from the PDF file (True/False)')
    parser.add_argument('-prompt', type=str, help='Free text to specify the prompt to use')
    parser.add_argument('-printtoscreen', type=bool, help='Specify whether to print the output to the screen (True/False)')
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
        # Generate the OpenAI prompt and cotent depending on the command-line arguments
        if args.extractexamples:
            if args.use_few_shot:
                openAIInput = generate_OpenAIPromptAndContent(system_prompt["extractexamples"], user_prompt["extractexamples"], text, few_shot_prompt["extractexamples"], assistant_prompt_response["extractexamples"])
            else:
                openAIInput = generate_OpenAIPromptAndContent(system_prompt["extractexamples"], user_prompt["extractexamples"], text)
        elif args.summary:
            openAIInput = generate_OpenAIPromptAndContent(system_prompt["summary"], user_prompt["summary"], text)
        elif args.keypoints:
            openAIInput = generate_OpenAIPromptAndContent(system_prompt["keypoints"], user_prompt["keypoints"], text)
        elif args.prompt:
            openAIInput = generate_OpenAIPromptAndContent(system_prompt["prompt"], args.prompt, text)
        # This code sends openAIInput to the OpenAI API and prints the response or handles any errors that occur.
        try:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint
            )
            response = client.chat.completions.create(
                model=model, # model = "deployment_name"
                messages=openAIInput,
                temperature=temperature
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
        # Check if response_json is a string and can be converted to a dictionary
        if isinstance(response_json, str):
            try:
                response_json = json.loads(response_json)  # this formats the file nicely as long as the response is a JSON object
            except json.JSONDecodeError:
                # If it's not a valid JSON string, leave it as is
                pass
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
        
        # Print to screen if the argument is set to True
        if args.printtoscreen:
            print(json.dumps(response_json, indent=4))
        