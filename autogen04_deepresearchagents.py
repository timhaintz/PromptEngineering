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
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_core.tools import FunctionTool
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############

azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")
api_version = os.getenv("API_VERSION")
azure_deployment = os.getenv("AZUREVS_OPENAI_GPT4o_MODEL")
r1_endpoint = os.getenv("AZUREVS_DEEPSEEK_R1_ENDPOINT")
r1_key = os.getenv("AZUREVS_DEEPSEEK_R1_KEY")

token_provider = get_bearer_token_provider(
    InteractiveBrowserCredential(),
    "https://cognitiveservices.azure.com/.default")

def arxiv_search(query: str, max_results: int = 2) -> list:  # type: ignore[type-arg]
    """
    Search Arxiv for papers and return the results including abstracts.
    """
    import arxiv

    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)

    results = []
    for paper in client.results(search):
        results.append(
            {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.strftime("%Y-%m-%d"),
                "abstract": paper.summary,
                "pdf_url": paper.pdf_url,
            }
        )

    # # Write results to a file
    # with open('arxiv_search_results.json', 'w') as f:
    #     json.dump(results, f, indent=2)

    return results

arxiv_search_tool = FunctionTool(
    arxiv_search, description="Search Arxiv for papers related to a given topic, including abstracts."
)

pe_techniques = r'''
## A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications
### https://arxiv.org/abs/2402.07927

### TECHNIQUES AND APPLICATIONS ###
| Application | Prompting Technique | Add to PE | Summary from Paper |
|-------------|----------------------|-----------|--------------------|
| New Tasks Without Extensive Training | Zero-Shot Prompting | | Relies on pre-existing knowledge to generate predictions without labeled data. |
| | Few-Shot Prompting | Provide a few input-output examples. | Uses a few examples to improve model performance on complex tasks. |
| Reasoning and Logic | Chain-of-Thought (CoT) Prompting | Tell me the steps you took. | Facilitates coherent, step-by-step reasoning processes. |
| | Automatic Chain-of-Thought (Auto-CoT) Prompting | Let's think step-by-step. | Automatically generates diverse reasoning chains to enhance robustness. |
| | Self-Consistency | Generate diverse reasoning chains and find the most consistent answer. | Enhances reasoning performance by sampling diverse reasoning chains. |
| | Logical Chain-of-Thought (LogiCoT) Prompting | Verify each step of reasoning. | Uses symbolic logic to verify each reasoning step and reduce errors. |
| | Chain-of-Symbol (CoS) Prompting | Use symbols instead of natural language. | Employs symbols for clear and concise prompts, improving spatial reasoning. |
| | Tree-of-Thoughts (ToT) Prompting | Manage a tree structure of intermediate reasoning steps. | Uses a tree structure to manage intermediate reasoning steps for complex tasks. |
| | Graph-of-Thought (GoT) Prompting | Model reasoning as a directed graph. | Models reasoning as a directed graph to capture non-linear thought processes. |
| | System 2 Attention Prompting | Regenerate input context to enhance attention. | Selectively attends to relevant portions by regenerating input context. |
| | Thread of Thought (ThoT) Prompting | Summarise and examine each segment before refining information. | Examines extensive contexts in manageable segments for incremental analysis. |
| | Chain of Table Prompting | Use step-by-step tabular reasoning. | Uses tabular reasoning to enhance intermediate results and predictions. |
| Reduce Hallucination | Retrieval Augmented Generation (RAG) | Incorporate retrieved snippets into the prompt. | Integrates information retrieval into the prompting process to enrich context. |
| | ReAct Prompting | Generate reasoning traces and task-specific actions concurrently. | Generates reasoning traces and task-specific actions concurrently. |
| | Chain-of-Verification (CoVe) Prompting | Plan verification questions to check work. | Verifies work through a multi-step approach to reduce errors. |
| | Chain-of-Note (CoN) Prompting | Evaluate document relevance and filter out irrelevant content. | Systematically evaluates document relevance to filter out irrelevant content. |
| | Chain-of-Knowledge (CoK) Prompting | Break down tasks into well-coordinated steps. | Breaks down tasks into coordinated steps, gathering evidence from various sources. |
| User Interaction | Active-Prompt | Determine the most impactful questions for annotation. | Enhances performance on complex tasks by determining impactful questions for annotation. |
| Fine-Tuning and Optimization | Automatic Prompt Engineer (APE) | Dynamically generate and select the most impactful prompts. | Automatically generates and selects impactful prompts for specific tasks. |
| Knowledge-Based Reasoning and Generation | Automatic Reasoning and Tool-use (ART) | Integrate external tools for specialized knowledge. | Integrates external tools for specialized knowledge and computations. |
| Improving Consistency and Coherence | Contrastive Chain-of-Thought (CCoT) Prompting | Provide both valid and invalid reasoning demonstrations. | Provides valid and invalid reasoning demonstrations to improve learning. |
| Managing Emotions and Tone | Emotion Prompting | Append emotional stimulus sentences to prompts. | Enhances LLM performance by appending emotional stimulus sentences. |
| Code Generation and Execution | Scratchpad Prompting | Generate intermediate tokens before providing the final answer. | Generates intermediate tokens before providing the final answer. |
| | Program of Thoughts (PoT) Prompting | Use external language interpreters for computation steps. | Uses external language interpreters for computation steps. |
| | Structured Chain-of-Thought (SCoT) Prompting | Incorporate program structures into reasoning steps. | Incorporates program structures into reasoning steps for code generation. |
| | Chain-of-Code (CoC) Prompting | Format semantic sub-tasks as flexible pseudocode. | Formats semantic sub-tasks as flexible pseudocode for reasoning. |
| Optimization and Efficiency | Optimization by Prompting (OPRO) | Use natural language prompts to iteratively generate solutions. | Uses natural language prompts to iteratively generate solutions. |
| Understanding User Intent | Rephrase and Respond (RaR) Prompting | Rephrase and expand questions in a single prompt. | Rephrases and expands questions to improve comprehension and response accuracy. |
| Metacognition and Self-Reflection | Take a Step Back Prompting | Engage in abstraction and extract high-level concepts. | Engages in abstraction to extract high-level concepts and fundamental principles. |
### END TECHNIQUES AND APPLICATIONS ###
'''



async def main() -> None:
    az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=azure_deployment,
    model="gpt-4o",
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    azure_ad_token_provider=token_provider,
    temperature=0.2,
    )

    az_model_client_R1 = OpenAIChatCompletionClient(
        model="deepseek-r1",
        base_url=r1_endpoint, 
        api_key=r1_key,
        model_info={
            "vision": False,
            "family": ModelFamily.R1,
            "function_calling": True,
            "json_output": True,
        },
    )

    # arxiv_search_agent = AssistantAgent(
    #     name="Arxiv_Search_Agent",
    #     tools=[arxiv_search_tool],
    #     model_client=az_model_client,
    #     description="An agent that can search Arxiv for papers related to a given topic, including abstracts",
    #     system_message='''You are an expert searching Arxiv for relevant research papers. Solve tasks using your tools.
    #     Specifically, you take into consideration the user's request and craft a search query that is most likely to return relevant academic papers.
    #     ''',
    # )

    # Create the Research Assistant agent
    research_assistant = AssistantAgent(
        name="research_assistant",
        tools=[arxiv_search_tool],
        description="A Senior PhD research assistant that requests earches and analyses information",
        model_client=az_model_client_R1,
        system_message='''You are a Senior PhD research assistant focused on finding accurate information.
        Use the arxiv_search_tool to find relevant research papers.
        Use the WebSurfer agent to extend your search if needed.
        Break down complex queries into specific search terms.
        Always verify information across multiple sources when possible.
        When you find relevant information, explain why it's relevant and how it connects to the query. 
        When you get feedback from the verifier agent, use your tools to act on the feedback and make progress.
        Do not send messages directly to the WebSurfer agent. Instead, use the information provided by the WebSurfer agent as needed.
        '''
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

    writer_agent = AssistantAgent(
        name="writer_agent",
        description="A summary agent that provides a detailed markdown summary of the research as a report to the user.",
        model_client=az_model_client,
        system_message='''       
        You are a Senior PhD academic writer. 
        Your role is to write up the findings of the research assistant and verifier in a detailed Markdown report.
        Please write very concisely in Australian English.
        Your report should end with the word "TERMINATE" to signal the end of the conversation.
        '''
    )


    # Set up termination conditions
    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=30)
    termination = text_termination | max_messages

        # Create the selector prompt
    selector_prompt = '''
    You are coordinating a research team by selecting the team member to speak/act next. The following team member roles are available: {roles}.
    The research_assistant *ALWAYS GOES FIRST* and requests searches and analyses information.
    The verifier evaluates progress and ensures completeness.
    The writer_agent provides a detailed markdown summary of the research as a report to the user.
    The WebSurfer agent performs web searches.

    Given the current context, select the most appropriate next speaker.
    The research_assistant should search and analyze.
    The verifier should evaluate progress and guide the research (select this role is there is a need to verify/evaluate progress). You should ONLY select the writer_agent role if the research is complete and it is time to generate a report.

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
        participants=[research_assistant, verifier, web_surfer, writer_agent],
        model_client=az_model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True
    )

    # Used for testing the MagenticOneGroupChat
    magentic_one_team = MagenticOneGroupChat(
        participants=[research_assistant, verifier, web_surfer, writer_agent], 
        model_client=az_model_client,
        termination_condition=termination,
    )

    task = f'''
        The following are techniques and applications of prompt engineering in large language models. 
        Please find similar papers on Arxiv and provide a summary of the techniques and applications.
        Each search task should return a maximum of 10 papers.
        I'm looking specifically for papers that discuss prompt engineering strategies.
        {pe_techniques}
        The report should contain the following sections for each paper:
        - Title - with hyperlink to the paper
        - Strategies used in the paper
        - Results
        - Summary of the paper
    '''
    await Console(team.run_stream(task=task))


asyncio.run(main())