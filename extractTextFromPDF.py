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
import sys
import PyPDF2

def extract_text_from_pdf(pdf_file_name):
    # Open the PDF file in read-binary mode
    with open(pdf_file_name, 'rb') as pdf_file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)

        # Get the number of pages in the PDF file
        num_pages = pdf_reader.getNumPages()

        # Loop through each page in the PDF file
        for page_num in range(num_pages):
            # Get the page object for the current page
            page_obj = pdf_reader.getPage(page_num)

            # Extract the text from the page object
            page_text = page_obj.extractText()

            # Print the text for the current page
            print(f'Text for page {page_num + 1}:')
            print(page_text)

if __name__ == '__main__':
    # Get the file path from the command line arguments
    file_path = sys.argv[1]
    # Replace 'path/to/your/pdf_file.pdf' with the actual file path
    extract_text_from_pdf(file_path)
