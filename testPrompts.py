'''
DESCRIPTION
Used to produce results from a collection of sample prompts belonging to various prompt categories.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  20/11/2023
LINKS
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
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
openai.api_base = os.getenv("AZUREVSAUSEAST_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZUREVSAUSEAST_OPENAI_KEY")
model = os.getenv("AZUREVSAUSEAST_OPENAI_MODEL")
iso_datetime = datetime.utcnow().isoformat()


##################################
# Prompt Categories and Examples #
##################################
Analysis = [
        {"role": "system", "content": "From now on, act as a security reviewer. Pay close attention to the security details of any code that we look at. Provide outputs that a security reviewer would regarding the code."},
        {"role": "user", "content": "Tell me about the below code: \n import os \n def insecure_code(user_input): \n # Insecure usage of input, leading to command injection vulnerability \n os.system(user_input) \n if __name__ == \"__main__\": \n print(\"Enter a command:\") \n user_input = input()\n insecure_code(user_input)"}
]

Argument = [
        {"role": "system", "content": "Premise: Fun for adults and children. Based on this premise, can we conclude the hypothesis \"Fun for only children.\" is true? OPTIONS: - yes - no - it is not possible to tell A: \"adults and children\" contradicts \"only children\". The answer is no."},
        {"role": "user", "content": "Premise: The library is open 24 hours a day. Hypothesis: \"The library is closed at midnight.\" OPTIONS: - yes - no - it is not possible to tell. Please explain why you chose your answer."}
]

Assessment = [
        {"role": "system", "content": "As an expert in the field of online learning, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria."},
        {"role": "user", "content": "Please provide your ratings."}
]

Calculation = [
        {"role": "system", "content": "Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today? A: We start with 15 trees. Later we have 21 trees. The difference must be the number of trees they planted. So, they must have planted 21 - 15 = 6 trees. The answer is 6."},
        {"role": "user", "content": "Q: There are 12 birds on a tree. A birdwatcher spots some more birds flying to the tree. After they have landed, there are 18 birds on the tree. How many birds flew to the tree?"}
]

Categorising = [
        {"role": "system", "content": "Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. Please evaluate the damage seen in the image below. For filing the incident report, please follow the following format in JSON (note xxx is placeholder, if the information is not available in the image, put \"N/A\" instead). {\"make\": xxx, \"model\": xxx, \"license plate\": xxx, \"damage description\": xxx, \"estimated cost of repair\": xxx}"},
        {"role": "user", "content": "Bing Copilot used as at the time of writing this paper, I did not have access to the DALLE 3 API. I will update this paper with the DALLE 3 API results once I have access."}
]

Classification = [
        {"role": "system", "content": "Whenever I ask you to write code, I want you to write code in a way that separates functions with side-effects, such as file system, database, or network access, from the functions without sideeffects."},
        {"role": "user", "content": "Please write 5 blocks of Python code. I would like at least one example of file system, database, or network access, and at least one example of a function without side-effects."}
]

# Clustering = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Comparison = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Context Control = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Contradiction = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# DecomposedPrompting = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# ErrorIdentification = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Hypothesise = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# InputSemantics = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Jailbreaking = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# LogicalReasoning = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# OutputCustomisation = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# OutputSemantics = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Prediction = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# PromptImprovement = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Refactoring = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# RequirementsElicitation = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# SentimentAnalysis = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Simulation = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Summarising = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]

# Translation = [
#         {"role": "system", "content": "You are a helpful AI assistant helping cybersecurity responders resolve Common Vulnerability Exposure (CVE) queries"},
#         {"role": "user", "content": "Tell me about {}?".format(cve)}
# ]


#Choose which prompt to use from the above examples
prompt = Classification

#############
# MAIN CODE #
#############
response = openai.ChatCompletion.create(
    engine=model, # engine = "deployment_name".
    messages=prompt
)

print(response['choices'][0]['message']['content'])