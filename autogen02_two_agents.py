'''
DESCRIPTION
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  5/8/2024
LINKS:
https://microsoft.github.io/autogen/
https://www.microsoft.com/en-us/research/blog/autogen-enabling-next-generation-large-language-model-applications/
https://github.com/microsoft/autogen
https://microsoft.github.io/autogen/docs/topics/task_decomposition/#group-chat-with-a-custom-speaker-selection-policy
EXAMPLE USAGE:
python autogen_two_agents.py
python autogen_two_agents.py --prompt "Please tell me the latest news in AutoGen"
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
import argparse

#############
# VARIABLES #
#############
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
work_dir = "AutoGen/TwoAgents"

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

import autogen

from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
def parse_args():
    parser = argparse.ArgumentParser(description="Run AutoGen with Two Agents")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Please tell me the weather in Seattle",
        help="The prompt to send to the user proxy agent",
    )
    return parser.parse_args()

args = parse_args()

assistant = AssistantAgent("assistant", llm_config=gpt4o)
user_proxy = UserProxyAgent(
    "user_proxy", code_execution_config={"work_dir": work_dir, "use_docker": True}
)  # IMPORTANT: set to True to run code in docker, recommended
user_proxy.initiate_chat(assistant, message=args.prompt)