'''
DESCRIPTION
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  24/4/2024
LINKS:
https://microsoft.github.io/autogen/
https://www.microsoft.com/en-us/research/blog/autogen-enabling-next-generation-large-language-model-applications/
https://github.com/microsoft/autogen
https://microsoft.github.io/autogen/docs/topics/task_decomposition/#group-chat-with-a-custom-speaker-selection-policy
EXAMPLE USAGE:
python autogen_research_assistant.py
'''

###########
# IMPORTS #
###########
from autogen import Agent, AssistantAgent, ConversableAgent, GroupChat, GroupChatManager, register_function, UserProxyAgent, config_list_from_json
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from chromadb.utils import embedding_functions
from typing import Annotated
from langchain_text_splitters import RecursiveJsonSplitter
import pandas as pd
import json

#############
# VARIABLES #
#############
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
work_dir = "AutoGen/RelatedPP/"
prompt_patterns = "promptpatterns.json"
json_splitter = RecursiveJsonSplitter(max_chunk_size=1000)

llm_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "config_list": config_list,
    "temperature": 0.0,
    "timeout": 120,
}

gpt4 = llm_config['config_list'][0]
gpt35 = llm_config['config_list'][1]
gpt4_vision = llm_config['config_list'][2]
text_embedding_3_large = llm_config['config_list'][3]
text_embedding_ada_002 = llm_config['config_list'][4]
gpt4o = llm_config['config_list'][5]

# region import DATA
###############
# Import DATA #
###############
def prompt_patterns_text_split_function(prompt_patterns):
    # Parse the JSON
    data = json.loads(prompt_patterns)

    # Split the JSON into chunks
    json_chunks = json_splitter.split_json(json_data=data, convert_lists=True)

    # Convert each item in each dictionary in json_chunks to a separate JSON-formatted string
    json_strings = [json.dumps(item) for chunk in json_chunks for item in chunk.items()]

    return json_strings


df = pd.read_json("promptpatterns.json")

output_structure = '''
\\begin{table}[h!]
  \\centering
  \\begin{tabular}{|c|c|c|c|}
    \\hline
    ID & PP name& Category & APA ref\\
    \\hline
  \\end{tabular}
  \\caption{The list of different categories of PPs for the in-logic.}
\\end{table}
'''

categorising_example = '''
Category: CAT (Categorising)
PP Name: Insurance Report Generation
PE: Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. 
Please evaluate the damage seen in the image below. 
For filing the incident report, please follow the following format in JSON (note xxx is placeholder, if the information is not available in the image, put \"N/A\" instead).
 {\"make\": xxx, \"model\": xxx, \"license plate\": xxx, \"damage description\": xxx, \"estimated cost of repair\": xxx}
'''

# endregion
# region User Agents
###############
# USER AGENTS #
###############
admin = UserProxyAgent(
    name="Admin",
    llm_config=gpt35,
    system_message="A human admin. Give the task, provide feedback and confirm the output.",
    description="The admin initiates the chat and provides the task to generate a report on various topics.",
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

executor = UserProxyAgent(
    name="Executor",
    llm_config=False,
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    system_message="Executor. Execute the code written by the engineer and report the result.",
    description="Executor should always be called after the engineer has written code to be executed.",
    human_input_mode="NEVER",
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": work_dir,
        "use_docker": True,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)
# endregion

# region Assistant Agents
####################
# ASSISTANT AGENTS #
####################
critic = AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
    llm_config=gpt35,
    description="The critic should always be called at the end of the process to check the prompt patterns and prompt examples.",
)

chain_of_thought = AssistantAgent(
    name="ChainOfThought",
    llm_config=gpt35,
    system_message='''Chain of Thought. Provide a chain of thought analysis to solve the problem.
    Identify the problem, break it down into smaller problems, and provide a plan to solve each problem.
    ''',
    description="The chain of thought should always be called after the planner to further break down the task.",
)

engineer = AssistantAgent(
    name="Engineer",
    llm_config=gpt35,
    system_message='''Engineer. Do not provide feedback or commentary. Your explicit job is to write python code to assist with the requested task.
    The code you write is executed by the executor in a Docker environment. The code should be complete and correct.
    Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. 
    Don't use a code block if it's not intended to be executed by the executor. Don't include multiple code blocks in one response. 
    Do not ask others to copy and paste the result. Check the execution result returned by the executor. 
    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. The executor can install packages if needed.
    If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyse the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    ''',
    description='''Creates Python code for the executor to execute. Rewrites code as needed by the executor.
    The engineer should always be called before the executor.
    ''',
)

phd_student = AssistantAgent(
    name="PhDStudent",
    llm_config=gpt35,
    system_message='''PhD Student. You are working with your research assitant on critical research tasks.
    You can provide feedback on the plan and suggest changes.
    Please ask the Engineer to write Python code if needed for your research.
    ''',
    description='''The PhD student should always be called after the research assistant.
    ''',
)

planner = AssistantAgent(
    name="Planner",
    llm_config=gpt35,
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a PhDStudent who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by another agent.
Mark each step of the plan as (DONE) after it is completed. If the plan is not approved, revise the plan based on feedback.
''',
    description='''First input goes to the Planner to break the problem down.'''
)

research_assistant = AssistantAgent(
    name="ResearchAssistant",
    llm_config=gpt35,
    system_message='''Research Assistant. Help the PhD student.
    Please ask the Engineer to write Python code if needed for your research.
    ''',
    description='''The research assistant should always be called before the PhD student.
    ''',
)
# endregion

# region Retrieve Agent
###################
# RETRIEVE AGENTS #
###################
azure_openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_base=text_embedding_ada_002["base_url"],
                    api_key=text_embedding_ada_002["api_key"],
                    api_type="azure",
                    api_version=text_embedding_ada_002["api_version"],
                    model_name=text_embedding_ada_002["model"],
                )

rag_assistant = RetrieveAssistantAgent(
    name="ragassistant",
    system_message="You are a helpful assistant.",
    llm_config=gpt4,
)

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    human_input_mode="ALWAYS",
    retrieve_config={
        "task": "qa",
        "docs_path": "promptpatterns.json",
        "embedding_function": azure_openai_ef, # chromadb.errors.InvalidDimensionException: Embedding dimension 384 does not match collection dimensionality 3072
        "embedding_model": "text_embedding_ada_002",
        "collection_name": "promptpatterns",
        "get_or_create": True,
        "must_break_at_empty_line": False,
        "chunk_token_size": 1000,
        "custom_text_split_function": prompt_patterns_text_split_function,
    },
    description="The Retrieve User Proxy Agent is used to retrieve information from a database for solving difficult problems.",
)
        #"db_path": "AutoGen",       
        

# endregion



# region nested chat
#####################
# NESTED CHAT SETUP #
#####################
# Define a condition to trigger the nested chat  
def reflection_message(recipient, messages, sender, config):
    print("Reflection function called for the nested chat between the engineer and the executor")
    return f"Please execute the Python code: \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

# Setup the nexted chat between thematic_analysis and critic
admin.register_nested_chats(
    [
        {
            "recipient": executor,
            "message": reflection_message,
            "summary_method": "last_msg",
            "max_turns": 5
        }
    ],
    trigger=engineer
)

# endregion

# region setup GroupChat
###################
# GroupChat setup #
###################
def run_group_chat():
    groupchat = GroupChat(
        agents=[admin, critic, engineer, executor, phd_student, planner, research_assistant],
        messages=[],
        max_round=20,
        send_introductions=True,
        speaker_selection_method="auto",
    )

    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    admin.initiate_chat(
        recipient=manager,
        message=f'''
        Embedded in this chat is a JSON file with a list of prompt patterns and prompt examples.
        The JSON file index is used to identify the prompt pattern and prompt example.
        The JSON file is: #### START JSON #### {df} #### END JSON ####
        For example 10-25-0 is the index for the prompt pattern "Damage Evaluation".
        10-25-0-0 is the index for the prompt example "Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. Please evaluate the damage seen in the image below."
        Your task is to compare each prompt example in the JSON file and report on any that are related to {categorising_example}.
        If it is related please provide the ID, the prompt pattern name, the category and the APA reference.
        The APA Reference is the APAReference key in the same index as the prompt pattern and prompt example. 
        The output should be in LaTex format as follows: {output_structure}
        No code is required for this task.
        '''
    )

# run_group_chat()
# endregion

# region Setup Retrieve GroupChat
##################
# RAG Chat setup #
##################
def run_rag_group_chat():
    rag_assistant.reset()
    ragproxyagent.initiate_chat(
        recipient=rag_assistant,
        message=ragproxyagent.message_generator,
        problem="Please find 'Damage Evaluation' ExamplePrompts.",
        search_string="", # search_string is used as an extra filter for the embeddings search
    )

run_rag_group_chat()


# # Chat to create a RAG index
# admin.initiate_chat(
#     recipient=manager,
#     message=f'''
#     Please write code to read this website: https://microsoft.github.io/autogen/docs/notebooks/agentchat_RetrieveChat/.
#     Planner, please break down the tasks. Mark them as (DONE) after completion.
#     The Executor will execute the code in a Docker environment.
#     Save each file created locally with the name (datetime)_fileusename.fileextension
#     Use the website to write code to use AutoGen to convert PDF files into a RAG index.
#     Please save each Python file locally as you execute it.
# '''
# )

# # Chat to extract prompt patterns from the Arxiv papers
# admin.initiate_chat(
#     recipient=manager,
#     message=f'''Please find the 5 latest Arxiv papers on Prompt Engineering using the Arxiv API.
#     Please provide full APA references and also the URL to the paper.
#     The executor can execute the code in Docker to download the papers and parse the full text.
#     Download the papers and save the file name as the Arxiv unique identifier. Parse the full text and look for prompt patterns and prompt examples. 
#     If they have prompt patterns and prompt examples, extract them in the same structure as: {df}
# '''
# )

#endregion