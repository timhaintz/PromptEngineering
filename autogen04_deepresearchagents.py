'''
DESCRIPTION
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  20250209
LINKS:
https://microsoft.github.io/autogen/
https://www.microsoft.com/en-us/research/blog/autogen-enabling-next-generation-large-language-model-applications/
https://github.com/microsoft/autogen
https://microsoft.github.io/autogen/stable/
https://www.microsoft.com/en-us/research/blog/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/
https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/
https://multiagentbook.com/labs/usecases/?usecase=deep-research-agents&trk=public_post_comment-text - High level structure
EXAMPLE USAGE:
python autogen04_deepresearchagents.py
'''

###########
# IMPORTS #
###########
import asyncio
import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############

azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")
api_version = os.getenv("API_VERSION")
azure_deployment = os.getenv("AZUREVS_OPENAI_GPT4o_MODEL")

token_provider = get_bearer_token_provider(InteractiveBrowserCredential(), "https://cognitiveservices.azure.com/.default")

async def main() -> None:
    az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=azure_deployment,
    model="gpt-4o",
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    azure_ad_token_provider=token_provider,
    temperature=0.2,
    )

    # Create the Research Assistant agent
    research_assistant = AssistantAgent(
        name="research_assistant",
        description="A Senior PhD level research assistant that performs web searches and analyses information",
        model_client=az_model_client,
        system_message='''You are a Senior PhD level research assistant focused on finding accurate information.
        Use the WebSurfer agent to find relevant information.
        Break down complex queries into specific search terms.
        Always verify information across multiple sources when possible.
        When you find relevant information, explain why it's relevant and how it connects to the query. When you get feedback from the a verifier agent, use your tools to act on the feedback and make progress.
        '''
    )

    summary_agent = AssistantAgent(
        name="summary_agent",
        description="A summary agent that provides a detailed markdown summary of the research as a report to the user.",
        model_client=az_model_client,
        system_message="""You are a summary agent. Your role is to provide a detailed markdown summary of the research as a report to the user. Your report should have a reasonable title that matches the research question and should summarize the key details in the results found in natural an actionable manner. The main results/answer should be in the first paragraph.
        Your report should end with the word "TERMINATE" to signal the end of the conversation."""
    )

    web_surfer = MultimodalWebSurfer(
        name="WebSurfer",
        description="A web surfer agent that performs web searches to find relevant information",
        model_client=az_model_client,
    )

    # Create the Verifier agent
    verifier = AssistantAgent(
        name="verifier",
        description="A verification specialist who ensures research quality and completeness",
        model_client=az_model_client,
        system_message='''You are a research verification specialist.
        Your role is to:
        1. Verify that search queries are effective and suggest improvements if needed
        2. Explore drill downs where needed e.g, if the answer is likely in a link in the returned search results, suggest clicking on the link
        3. Suggest additional angles or perspectives to explore. Be judicious in suggesting new paths to avoid scope creep or wasting resources, if the task appears to be addressed and we can provide a report, do this and respond with "TERMINATE".
        4. Track progress toward answering the original question
        5. When the research is complete, provide a detailed summary in markdown format
        
        For incomplete research, end your message with "CONTINUE RESEARCH". 
        For complete research, end your message with APPROVED.
        
        Your responses should be structured as:
        - Progress Assessment
        - Gaps/Issues (if any)
        - Suggestions (if needed)
        - Next Steps or Final Summary
        '''
    )


    # Set up termination conditions
    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=20)
    termination = text_termination | max_messages

        # Create the selector prompt
    selector_prompt = '''You are coordinating a research team by selecting the team member to speak/act next. The following team member roles are available:
    {roles}.
    The research_assistant performs searches and analyses information.
    The verifier evaluates progress and ensures completeness.
    The summary_agent provides a detailed markdown summary of the research as a report to the user.
    The WebSurfer agent performs web searches.

    Given the current context, select the most appropriate next speaker.
    The research_assistant should search and analyze.
    The verifier should evaluate progress and guide the research (select this role is there is a need to verify/evaluate progress). You should ONLY select the summary_agent role if the research is complete and it is time to generate a report.

    Base your selection on:
    1. Current stage of research
    2. Last speaker's findings or suggestions
    3. Need for verification vs need for new information
        
    Read the following conversation. Then select the next role from {participants} to play. Only return the role.

    {history}

    Read the above conversation. Then select the next role from {participants} to play. ONLY RETURN THE ROLE.
    '''

    # Create the team
    team = SelectorGroupChat(
        participants=[research_assistant, verifier, summary_agent, web_surfer],
        model_client=az_model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True
    )

    # Used for testing the MagenticOneGroupChat
    magentic_one_team = MagenticOneGroupChat(
        participants=[research_assistant, web_surfer, verifier], 
        model_client=az_model_client,
        termination_condition=termination,
    )

    task = '''
        Please use the WebSurfer agent to find information on the following question: "What are the benefits of using a deep learning model for image recognition?"
    '''
    await Console(team.run_stream(task=task))


asyncio.run(main())