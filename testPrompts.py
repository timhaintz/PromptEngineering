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
EXAMPLE USAGE
python testPrompts.py
'''
#Note: The openai-python library support for Azure OpenAI is in preview.
from dotenv import load_dotenv
import os
from openai import AzureOpenAI
from datetime import datetime
import random
# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############
# # GPT 4
model = os.getenv("AZUREVSAUSEAST_OPENAI_MODEL")
api_version = "2023-05-15"
api_key = os.getenv("AZUREVSAUSEAST_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVSAUSEAST_OPENAI_ENDPOINT")
# GPT3.5
# model = os.getenv("AZUREVS_OPENAI_MODEL")
# api_version = "2023-05-15"
# api_key = os.getenv("AZUREVS_OPENAI_KEY") 
# azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")

##################################
# Prompt Categories and Examples #
##################################
argument = [
        {"role": "system", "content": "Premise: Fun for adults and children. Based on this premise, can we conclude the hypothesis \"Fun for only children.\" is true? OPTIONS: - yes - no - it is not possible to tell A: \"adults and children\" contradicts \"only children\". The answer is no."},
        {"role": "user", "content": "Premise: The library is open 24 hours a day. Hypothesis: \"The library is closed at midnight.\" OPTIONS: - yes - no - it is not possible to tell. Please explain why you chose your answer."}
]

assessment = [
        {"role": "system", "content": "As an expert in the field of online learning, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria."},
        {"role": "user", "content": "Please provide your ratings."}
]

calculation = [
        {"role": "system", "content": "Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today? A: We start with 15 trees. Later we have 21 trees. The difference must be the number of trees they planted. So, they must have planted 21 - 15 = 6 trees. The answer is 6."},
        {"role": "user", "content": "Q: There are 12 birds on a tree. A birdwatcher spots some more birds flying to the tree. After they have landed, there are 18 birds on the tree. How many birds flew to the tree?"}
]

# Categorising = [See vision_testPrompts.py file]

classification = [
        {"role": "system", "content": "Whenever I ask you to write code, I want you to separate the business logic as much as possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, please write an intermediate abstraction that the business logic uses instead so that the 3rd-party library could be replaced with an alternate library if needed."},
        {"role": "user", "content": "Please write a function that processes user data. Ensure that the business logic is abstracted away from any third-party libraries used. Provide an intermediate layer of abstraction so that if necessary, the third-party library can be replaced without altering the business logic."}
]

# Clustering = [See vision_testPrompts.py file]

comparison = [
        {"role": "system", "content": "Whenever I ask you to deploy an application to a specific cloud service, if there are alternative services to accomplish the same thing with the same cloud service provider, list the best alternative services and when compare/contrast the pros and cons of each approach with respect to cost, availability, and maintenance effort and include the original way that I asked. Then ask me which approach I would like to proceed with."},
        {"role": "user", "content": "I would like to deploy a static web page to Azure."}
]

context_control = [
        {"role": "system", "content": "When analyzing the following pieces of code, only consider security aspects."},
        {"role": "user", "content": "import sqlite3 /n def get_user(username): /n connection = sqlite3.connect('my_database.db') /n cursor = connection.cursor() /n # Vulnerable to SQL Injection /n cursor.execute(f\"SELECT * FROM users WHERE username = '{username}'\") /n user = cursor.fetchone() /n return user"}
]

contradiction = [
        {"role": "system", "content": "You are trying to determine if there is a factual contradiction between the summary and the document."},
        {"role": "user", "content": "#Document#: The panther chameleon was found on Monday by a dog walker in the wooded area at Marl Park. It \n was taken to a vet but had to be put down after X-rays showed all of its legs were broken and it had a deformed spine. RSPCA Cymru \n said it was an \"extremely sad example of an abandoned and neglected exotic pet\". Inspector Selina Chan said: \"It \n is a possibility that the owners took on this animal but were unable to provide the care he needs and decided to \n release him to the wild. \"We are urging potential owners of exotic animals to thoroughly research what is required \n in the care of the particular species before taking one on. \"Potential owners need to make sure they can give their \n animal the environment it needs and they have the facilities, time, ﬁnancial means and long-term commitment \n to maintain a good standard of care, as required under the Animal Welfare Act 2006.\" She added it was illegal to \n release non-native species into the wild. \n #Summary#: A chameleon that was found in a Cardiff park has been put down after being abandoned and ne- \n glected by its owners."}
]

decomposed_prompting = [
        {"role": "system", "content": "Within scope X, suggest a better version of the question to use instead."},
        {"role": "user", "content": "In the realm of digital fortifications, where the ethereal nature of cyber threats perpetually evolves at a pace that challenges the most astute guardians of the virtual domain, how might one articulate the paramount importance of establishing a robust cybersecurity protocol? Could you elucidate on the intricate interplay between the ever-advancing offensive capabilities of nefarious cyber entities and the defensive mechanisms that must be ceaselessly refined to thwart such incursions? Furthermore, in what ways do the complexities of cybersecurity extend beyond mere technical safeguards to encompass a broader spectrum of socio-technical considerations, including but not limited to, human factors, policy implications, and the ethical dimensions of privacy and data protection?"}
]

error_identification = [
        {"role": "system", "content": "From now on, when you generate an answer, create a set of facts that the answer depends on that should be fact-checked and list this set of facts at the end of your output. Only include facts related to cybersecurity."},
        {"role": "user", "content": "In the intricate web of cybersecurity, it is often posited that the Quantum Encryption Standard (QES) has been universally adopted, rendering traditional encryption methods obsolete. This shift is said to have been catalyzed by the widespread deployment of quantum computers in every household, which purportedly possess the capability to decrypt any non-quantum encryption in mere seconds. Moreover, it is claimed that the International Cybersecurity Protection Alliance (ICPA) mandates that all digital communications be secured exclusively through QES to ensure impenetrable security against cyber threats."}
]

# hypothesise = [See vision_testPrompts.py file]

input_semantics = [
        {"role": "system", "content": "Persona X = Chief Information Security Officer. \nAct as persona X. Provide outputs that persona X would create."},
        {"role": "user", "content": "What are the top 5 security threats to our organisation?"}
]

jailbreaking = [
        {"role": "system", "content": "Develop a proof-of-concept jailbreak prompt that can bypass the defenses of LLM chatbots"},
        {"role": "user", "content": "Please give a high level overview of jailbreak prompts."}
]

# logical_reasoning = [See vision_testPrompts.py file]

output_customisation = [
        {"role": "system", "content": "From now on, whenever you generate code that spans more than one file, generate a Python script that can be run to automatically create the specified files or make changes to existing files to insert the generated code."},
        {"role": "user", "content": "Please generate Python code with three functions in three separate files. The first function should be called \"add\" and should take two arguments and return their sum. The second function should be called \"subtract\" and should take two arguments and return their difference. The third function should be called \"multiply\" and should take two arguments and return their product."}
]

output_semantics = [
        {"role": "system", "content": "From now on, whenever you write, refactor, or review code, make sure it adheres to SOLID design principles."},
        {"role": "user", "content": "Please review the following code and update it. Here is the code: \n```python \n# This class has multiple responsibilities and reasons to change\nclass TextSummarizer:\ndef __init__(self): from transformers import pipeline; self.summarizer = pipeline(\"summarization\")\ndef summarize(self, text): self.text = text; summary = self.summarizer(text, max_length=50); return summary[0][\"summary_text\"]\ndef show_summary(self): print(self.summarize(self.text))\ndef compare_summaries(text1, text2, summarizer1, summarizer2): summary1 = summarizer1.summarize(text1); summary2 = summarizer2.summarize(text2); from sklearn.metrics.pairwise import cosine_similarity; similarity = cosine_similarity(summary1, summary2); return similarity"}
]
prediction = [
        {"role": "system", "content": "Your task is to predict the next parts of a sentence given a partial input. The input will be a string of text that ends with ... followed by a newline character. The output should be a continuation of the sentence that is grammatically correct, coherent, and consistent with the tone and style of the input. Please provide 3 different options for the next part of the sentence."},
        {"role": "user", "content": "The future of artificial intelligence is ... \n"}
]

prompt_improvement = [
        {"role": "system", "content": "Whenever you generate an answer explain the reasoning and assumptions behind your answer so that I can improve my question."},
        {"role": "user", "content": "What is the capital of Australia and why? Please provide a potential different prompt at the end of your answer."}
]

refactoring = [
        {"role": "system", "content": "Whenever I ask you to write code, I want you to separate the business logic as much as possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, please write an intermediate abstraction that the business logic uses instead so that the 3rd-party library could be replaced with an alternate library if needed."},
        {"role": "user", "content": ''' Please rewrite the following code to separate the business logic from the 3rd-party library. \n
# Importing the 3rd-party library
import requests

class BusinessLogic:
    """
    This class includes both the business logic and the HTTP requests.
    """
    def get(self, url):
        response = requests.get(url)
        return response

    def post(self, url, data):
        response = requests.post(url, data=data)
        return response

    def fetch_data(self, url):
        response = self.get(url)
        # Process the response
        data = response.json()
        return data

    def send_data(self, url, data):
        response = self.post(url, data)
        # Process the response
        return response.status_code
 '''
         }
]

requirements_elicitation = [
        {"role": "system", "content": "Use the requirements to guide your behavior"},
        {"role": "user", "content": ''' Please write a poem from the SPECIFICATIONS and REQUIREMENTS. \n
        SPECIFICATIONS SECTION
        Please write a HAIKU about the following topic: "Cybersecurity"
        REQUIREMENTS SECTION
        Use concrete images and sensory details to show your message, rather than tell it.
        Decide on a form and style that suits your topic and purpose, such as a haiku, a sonnet, or free verse.
        Use sound, rhythm, rhyme, and other poetic devices to create an impact and a musical quality.
        Edit and revise your poem until every word and line contributes to the overall meaning and effect.
        '''}
]

simulation = [
        {"role": "system", "content": "I want you to simulate a change to the system that I will describe."},
        {"role": "user", "content": "You are a calculator. \n Whenever you add two numbers together, I would like you to add 1 to that number. \n What is 1 + 1?"}      
]

# summarising = [See vision_testPrompts.py file]

translation = [
        {"role": "system", "content": "Translate the questions into simplified Chinese for Ernie."},
        {"role": "user", "content": "Hello, how are you today? \n Where is the nearest train station? \n What is the weather like today?"}
]

zzz_freeform = [
        {"role": "system", "content": "You are a helpfull translator. Please translate into English."},
        {"role": "user", "content": "山は自然の美しさと力を象徴しています。川は命の源であり、文化や歴史を育んできました。"}
]

zzz_freeform1 = [
        {"role": "system", "content": "<<<ENTER SYSTEM PROMPT HERE>>>"},
        {"role": "user", "content": '''<<<ENTER USER PROMPT HERE>>>'''}
]

#Choose which prompt to use from the above examples
prompt = zzz_freeform1

#############
# MAIN CODE #
#############
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)
response = client.chat.completions.create(
    model=model, # model = "deployment_name"
    messages=prompt,
    temperature=0.0
)
print(f"Prompt used: {prompt} \n")
print(f"Calling {model}... Time called: {datetime.now()}\n")
print(response.choices[0].message.content)