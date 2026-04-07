"""
Extract text from PDF files and process with Azure OpenAI.

Opens a PDF file, extracts text, sends it to Azure OpenAI API
with configurable prompts, and saves the response.

Example Usage:
    python extractTextFromPDF.py -filename "Test.pdf"
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -extractexamples True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -use_few_shot True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -summary True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -keypoints True
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -prompt "ENTER YOUR QUESTION HERE"
    python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -prompt "ENTER YOUR QUESTION HERE" -printtoscreen True
"""

from dotenv import load_dotenv
import os
import json
import fitz
import argparse
from openai import AzureOpenAI
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

# Configuration
MODEL = os.getenv("AZUREVSEASTUS2_OPENAI_GPT41_MODEL")
API_VERSION = os.getenv("AZUREVSEASTUS2_OPENAI_GPT41_API_VERSION")
API_KEY = os.getenv("AZUREVSEASTUS2_OPENAI_KEY")
AZURE_ENDPOINT = os.getenv("AZUREVSEASTUS2_OPENAI_ENDPOINT")
TEMPERATURE = 0.0
PAGES_PER_SET = 200

# System prompts for different modes
SYSTEM_PROMPTS = {
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

FEW_SHOT_PROMPT = {
    "extractexamples": '''Please find examples of a prompt category, prompt pattern, and prompt example in the following: \n
    Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?

    Q: John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers is? Answer Choices: (a) 50 (b) 45 (c) 65 (d) 78 (e) 64

    Q: Take the last letters of the words in "Elon Musk" and concatenate them.
    '''
}

ASSISTANT_PROMPT_RESPONSE = {
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
                            "Take the last letters of the words in \u201cElon Musk\u201d and concatenate them."
                        ]
                    }
                ]
            }
        ]
    }
    '''
}

USER_PROMPTS = {
    "extractexamples": '''Please extract the prompt categories and prompt patterns from the follow text: \n
    ''',
    "summary": '''Please summarise the following paper:''',
    "keypoints": '''Please extract the keypoints from the following paper:
    '''
}


def extract_text_from_pdf(pdf_file_name):
    """Extract text from a PDF file and return page-by-page results."""
    with fitz.open(pdf_file_name) as pdf_file:
        document_info = pdf_file.metadata
        title = document_info.get('title')
        file_name = os.path.basename(pdf_file_name)

        print(f'Title: {title}')
        print(f'File name: {file_name}')

        extracted_text_dicts = []
        for each_page in range(pdf_file.page_count):
            page = pdf_file[each_page]
            text = page.get_text()
            # Escape special characters
            text = text.replace("\\", "\\\\")
            text = text.replace("/", "\\/")
            text = text.replace("'", "\\\\'")
            text = text.replace('"', '\\"')
            text = text.replace("\n", "\\n")
            text = text.replace("\r", "\\r")
            text = text.replace("\t", "\\t")
            text = text.replace("\b", "\\b")
            text = text.replace("\f", "\\f")

            extracted_text_dicts.append({'page': each_page + 1, 'text': text})
            
        return title, file_name, extracted_text_dicts


def build_messages(system_prompt, user_prompt, data, few_shot=None, assistant_response=None):
    """Build the messages list for the OpenAI API call."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt + data}
    ]

    if few_shot:
        messages.insert(1, {"role": "user", "content": few_shot})
    if assistant_response:
        messages.insert(2, {"role": "assistant", "content": assistant_response})

    return messages


def parse_response(response_text):
    """Parse the API response, handling JSON code blocks."""
    if response_text.startswith('```json') and response_text.endswith('```'):
        response_text = response_text[7:-3]

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return response_text


def save_output(response_data, folder_name, save_file_name):
    """Save response data to a JSON file."""
    os.makedirs(folder_name, exist_ok=True)
    save_file_path = os.path.join(folder_name, save_file_name)
    print(f'Saving extracted prompt patterns to {save_file_path}')
    with open(save_file_path, 'w') as f:
        json.dump(response_data, f, indent=4)
    return save_file_path


def get_page_range(extracted_text_dicts, pages_arg):
    """Filter extracted text to the specified page range."""
    if not pages_arg:
        return extracted_text_dicts
    
    page_range = pages_arg.split('-')
    if len(page_range) == 1:
        start_page = end_page = int(page_range[0])
    else:
        start_page, end_page = map(int, page_range)
    return extracted_text_dicts[start_page - 1:end_page]


def main():
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

    file_path = args.filename
    title, file_name, extracted_text_dicts = extract_text_from_pdf(file_path)
    extracted_text_dicts = get_page_range(extracted_text_dicts, args.pages)

    iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename_without_extension = os.path.splitext(file_name)[0].replace('.', '_')
    folder_name = os.path.join('extractedPromptPatternsFromPDF', filename_without_extension)

    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )

    for i in range(0, len(extracted_text_dicts), PAGES_PER_SET):
        text_set = extracted_text_dicts[i:i + PAGES_PER_SET]
        page_numbers = [page['page'] for page in text_set]
        page_number_range = f'{page_numbers[0]}-{page_numbers[-1]}'
        print('Page number range:', page_number_range)
        text = '\f'.join([page['text'] for page in text_set])

        # Build messages based on mode
        if args.extractexamples:
            if args.use_few_shot:
                messages = build_messages(
                    SYSTEM_PROMPTS["extractexamples"],
                    USER_PROMPTS["extractexamples"],
                    text,
                    FEW_SHOT_PROMPT["extractexamples"],
                    ASSISTANT_PROMPT_RESPONSE["extractexamples"]
                )
            else:
                messages = build_messages(SYSTEM_PROMPTS["extractexamples"], USER_PROMPTS["extractexamples"], text)
            mode = "extractexamples"
        elif args.summary:
            messages = build_messages(SYSTEM_PROMPTS["summary"], USER_PROMPTS["summary"], text)
            mode = "summary"
        elif args.keypoints:
            messages = build_messages(SYSTEM_PROMPTS["keypoints"], USER_PROMPTS["keypoints"], text)
            mode = "keypoints"
        elif args.prompt:
            messages = build_messages(SYSTEM_PROMPTS["prompt"], args.prompt, text)
            mode = "prompt"

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=TEMPERATURE
            )
        except Exception as e:
            print(f"\nError: {e}")
            break

        response_data = parse_response(response.choices[0].message.content)
        save_file_name = f"{iso_datetime}_{filename_without_extension}_{mode}_{page_number_range}.json"
        save_output(response_data, folder_name, save_file_name)

        if args.printtoscreen:
            print(json.dumps(response_data, indent=4) if isinstance(response_data, dict) else response_data)


if __name__ == '__main__':
    main()
