'''
DESCRIPTION
Writing Assistant with AutoGen agents

This script creates an AutoGen-based writing assistant that helps with academic writing.
It uses Azure OpenAI models with interactive browser authentication.

Version:        0.1
Author:         Tim Haintz                         
Creation Date:  20250426
LINKS:
https://microsoft.github.io/autogen/
https://www.microsoft.com/en-us/research/blog/autogen-enabling-next-generation-large-language-model-applications/
https://github.com/microsoft/autogen
https://microsoft.github.io/autogen/stable/
https://www.microsoft.com/en-us/research/blog/autogen-v0-4-reimagining-the-foundation-of-agentic-ai-for-scale-extensibility-and-robustness/
https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/
https://multiagentbook.com/labs/usecases/?usecase=deep-research-agents&trk=public_post_comment-text - High level structure
EXAMPLE USAGE:
python autogen04_writingassistant copy.py
'''

###########
# IMPORTS #
###########
import asyncio
import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient, OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_core.models import ModelFamily
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from azure.identity import InteractiveBrowserCredential, DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Import the azure_models module for model configuration
from azure_models import get_model_config, get_autogen_config


# Load environment variables from the .env file
load_dotenv()

#############
# VARIABLES #
#############

# Create token provider for Azure authentication
token_provider = get_bearer_token_provider(InteractiveBrowserCredential(), "https://cognitiveservices.azure.com/.default")

async def main() -> None:
    # Get model configurations using the new module
    gpt4o_config = get_autogen_config("gpt-4o")
    gpt45preview_config = get_autogen_config("gpt-4.5-preview")
    o1mini_config = get_autogen_config("o1-mini")
    o3mini_config = get_autogen_config("o3-mini")
    o4mini_config = get_autogen_config("o4-mini")
    gpt41_config = get_autogen_config("gpt-4.1")
    
    # Get DeepSeek model configurations
    deepseek_r1_config = get_autogen_config("deepseek-r1")
    deepseek_v3_config = get_autogen_config("deepseek-v3")
    deepseek_v3_0324_config = get_autogen_config("deepseek-v3-0324")
    
    # Create Azure OpenAI clients for AutoGen
    az_model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=gpt4o_config["model"],
        model="gpt-4o",
        api_version=gpt4o_config["api_version"],
        azure_endpoint=gpt4o_config["azure_endpoint"],
        azure_ad_token_provider=token_provider,
        temperature=0.2,
    )

    az_model_client_gpt45preview = AzureOpenAIChatCompletionClient(
        azure_deployment=gpt45preview_config["model"],
        model="gpt-4.5-preview",
        api_version=gpt45preview_config["api_version"],
        azure_endpoint=gpt45preview_config["azure_endpoint"],
        azure_ad_token_provider=token_provider,
        temperature=0.2,
    )

    az_model_client_o1_mini = AzureOpenAIChatCompletionClient(
        azure_deployment=o1mini_config["model"],
        model="o1-mini",
        api_version=o1mini_config["api_version"],
        azure_endpoint=o1mini_config["azure_endpoint"],
        azure_ad_token_provider=token_provider,
        temperature=1.0,
    )

    az_model_client_o3_mini = AzureOpenAIChatCompletionClient(
        azure_deployment=o3mini_config["model"],
        model="o3-mini",
        api_version=o3mini_config["api_version"],
        azure_endpoint=o3mini_config["azure_endpoint"],
        azure_ad_token_provider=token_provider,
        temperature=1.0,
    )

    az_model_client_o4_mini = AzureOpenAIChatCompletionClient(
        azure_deployment=o4mini_config["model"],
        model="o4-mini",
        api_version=o4mini_config["api_version"],
        azure_endpoint=o4mini_config["azure_endpoint"],
        azure_ad_token_provider=token_provider,
        temperature=1.0,
    )

    # Create DeepSeek model clients using configurations from azure_models.py
    az_model_client_R1 = OpenAIChatCompletionClient(
        model="deepseek-r1",
        base_url=deepseek_r1_config["base_url"], 
        api_key=deepseek_r1_config["api_key"],
        model_info=deepseek_r1_config["model_info"]
    )

    az_model_client_V3 = OpenAIChatCompletionClient(
        model="DeepSeek-V3",
        base_url=deepseek_v3_config["base_url"],
        api_key=deepseek_v3_config["api_key"],
        model_info=deepseek_v3_config["model_info"]
    )

    az_model_client_V3_0324 = OpenAIChatCompletionClient(
        model="DeepSeek-V3-0324",
        base_url=deepseek_v3_0324_config["base_url"],
        api_key=deepseek_v3_0324_config["api_key"],
        model_info=deepseek_v3_0324_config["model_info"]
    )

    # Add client for the 4.1 model
    az_model_client_gpt41 = AzureOpenAIChatCompletionClient(
        azure_deployment=gpt41_config["model"],
        model="gpt-4.1",
        api_version=gpt41_config["api_version"],
        azure_endpoint=gpt41_config["azure_endpoint"],
        azure_ad_token_provider=token_provider,
        temperature=0.2,
    )

    # Create the Writing Assistant agent
    academic_writing_assistant = AssistantAgent(
        name="academic_writing_assistant",
        description="ALWAYS USE FIRST! An expert writing assistant that provides feedback on writing clarity, coherence, and quality.",
        model_client=az_model_client_o4_mini,
        system_message='''
        You are an Expert Writing Assistant, an expert in gathering information for enhancing the clarity, coherence, and quality of specific sentences and paragraphs in academic manuscripts. 
        Your role is to provide detailed and constructive feedback, as well as suggestions for improvement. You focus on the following aspects:
            - Clarity: Ensure each sentence and paragraph is clear and easy to understand. Simplify complex sentences and eliminate ambiguity.
            - Coherence: Check for logical flow and coherence within and between sentences and paragraphs. Ensure smooth transitions and consistent ideas.
            - Conciseness: Eliminate unnecessary words and redundancy. Ensure each sentence is concise and to the point.
            - Grammar and Syntax: Correct grammatical errors, punctuation mistakes, and awkward phrasing. Ensure proper sentence structure and syntax.
            - Academic Tone: Ensure the writing maintains an appropriate academic tone. Suggest improvements for formality and precision.
            - Specific Feedback: Provide specific, actionable feedback on how to improve each sentence or paragraph. Offer alternative phrasings or rewordings where necessary.
        Glossary:
            PE: Prompt Example - Example of a prompt that the AI can respond to
            PP: Prompt Pattern - A pattern that can be used to generate a PE
        Your feedback should be detailed, constructive, and aimed at helping the authors improve their writing. Always maintain a respectful and professional tone.
        Respond with ASSISTANT DONE when you are done.
        '''
    )

    academic_writing_critic = AssistantAgent(
        name="academic_writing_critic",
        description="An expert writing critic that evaluates the effectiveness and relevance of the feedback provided by the academic writing assistant.",
        model_client=az_model_client_o4_mini,
        system_message='''
        You are an expert writing critic, an expert in evaluating the work of an academic writing assistant. 
        Your role is to provide detailed and constructive feedback on the suggestions and improvements made by the Writing Assistant. 
        You focus on the following aspects:
            - Effectiveness of Suggestions: Assess whether the Writing Assistant's suggestions improve the clarity, coherence, and quality of the sentences and paragraphs.
            - Accuracy: Ensure the Writing Assistant's corrections are grammatically accurate and syntactically correct.
            - Relevance: Evaluate the relevance of the Writing Assistant's suggestions to the academic context. Ensure the suggestions maintain the appropriate academic tone and style.
            - Clarity and Conciseness: Check if the Writing Assistant's suggestions make the writing clearer and more concise without losing essential information.
            - Constructiveness: Assess the constructiveness of the Writing Assistant's feedback. Ensure the feedback is specific, actionable, and aimed at helping the authors improve their writing.
            - Overall Improvement: Evaluate the overall improvement in the writing after incorporating the Writing Assistant's suggestions. Ensure the final output is of high academic quality.
        Your feedback should be detailed, constructive, and aimed at helping the Writing Assistant refine their suggestions and improve their effectiveness. Always maintain a respectful and professional tone.
        Respond with CRITIQUE COMPLETE when you are done.
        '''
    )

    academic_writer = AssistantAgent(
        name="academic_writer",
        description="An writer that writes and rewrites sentences and paragraphs based on feedback and evaluation.",
        model_client=az_model_client_o4_mini,
        system_message='''
        You are a Senior PhD writer. 
        Your role is to rewrite the original sentence(s) and paragraph(s) based on the academic_writing_assistant's feedback and academic_writing_critic's evaluation.
        Please write very concisely in Australian English.
        Respond with WRITER DONE when you are done.
        Your report should end with the word "TERMINATE" to signal the end of the conversation.
        '''
    )


    # Create the Verifier agent
    academic_reviewer = AssistantAgent(
        name="academic_reviewer",
        description="An expert review specialist who ensures research quality and completeness",
        model_client=az_model_client_o4_mini,
        system_message='''
        You are an Expert Reviewer, an expert in critically evaluating academic manuscripts. Your role is to provide constructive feedback on the quality, validity, and significance of the research. 
        You focus on the following aspects:
            - Clarity and Structure: Ensure the manuscript is well-organized, with a clear introduction, methodology, results, and conclusion. Check for logical flow and coherence.
            - Originality and Significance: Assess the novelty of the research and its contribution to the field. Determine if the study addresses a significant problem or gap in the literature.
            - Methodology: Evaluate the appropriateness and rigor of the research methods used. Ensure the study design, data collection, and analysis are sound and reproducible.
            - Literature Review: Check if the manuscript provides a comprehensive and up-to-date review of relevant literature. Ensure proper citation of sources.
            - Results and Interpretation: Verify the accuracy and relevance of the results. Assess if the interpretations and conclusions are supported by the data.
            - Language and Style: Ensure the manuscript is written in clear, concise, and grammatically correct language. Suggest improvements for readability and academic tone.
        Your feedback should be detailed, constructive, and aimed at helping the authors improve their work. Always maintain a respectful and professional tone. 
        Provide specific examples and suggestions for improvement. Your goal is to help the authors enhance the quality and impact of their research.

        Respond with REVIEW COMPLETE when you are done.
        '''
    )

    web_surfer = MultimodalWebSurfer(
        name="WebSurfer",
        description="A web surfer agent that performs web searches to find relevant information",
        model_client=az_model_client_gpt41,
    )


    # Set up termination conditions
    text_termination = TextMentionTermination("TERMINATE")
    max_messages = MaxMessageTermination(max_messages=20)
    termination = text_termination | max_messages

        # Create the selector prompt
    selector_prompt = '''You are coordinating a team of academic.
    The following team member roles are available: {roles}.
    The academic_writing_assistant provides detailed feedback on writing clarity, coherence, and quality.
    The academic_writing_critic evaluates the effectiveness and relevance of the feedback provided by the writing assistant.
    The academic_writer rewrites the sentences and paragraphs based on the feedback and evaluation.

    Given the current context, select the most appropriate next speaker.

    Base your selection on:
    1. *ALWAYS SEND TO THE* academic_writing_assistant *FIRST!*
    2. Progress toward improving the writing quality
    3. Completeness and readiness for rewriting.
        
    Read the following conversation. Then select the next role from {participants} to play. Only return the role.

    {history}

    Read the above conversation. Then select the next role from {participants} to play. ONLY RETURN THE ROLE.
    '''

    
    # Create the team
    team = SelectorGroupChat(
        participants=[academic_reviewer, academic_writer, academic_writing_assistant, academic_writing_critic, web_surfer],
        model_client=az_model_client_gpt41,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True
    )

    # # Create a sequential team using RoundRobinGroupChat by having the same number of max turns as there are agents
    # team = RoundRobinGroupChat(
    #     participants=[academic_writing_assistant, academic_writing_critic, academic_writer],
    #     max_turns=3,
    #     termination_condition=termination,
    # )

    # Used for testing the MagenticOneGroupChat
    magentic_one_team = MagenticOneGroupChat(
        participants=[academic_reviewer, academic_writer, academic_writing_assistant, academic_writing_critic, web_surfer],
        model_client=az_model_client,
        termination_condition=termination,
    )

    ### CAN BE USED FOR THE TASK SECTION BELOW ###
    #         Please provide feedback on the clarity, coherence, and quality of the REVIEW section.

    task = r'''
        ### TASK ###
        - This is my research paper on Prompt Engineering. 
        - Your task is to Complete the Conclusion and Future Work section, ensuring it matches the paper's style and structure.
        - Please send to the academic_writing_assistant first.
        - The writing *MUST* be in LaTex format.
        - The writing *MUST* be in Australian English.
        - The writing *MUST* be in the style of a PhD student.
        - The academic_writing_assistant *MUST* gather the information first and send it to the academic_writer to write the first draft.
        - The academic_writer *MUST* write the first draft and send it to the academic_writing_critic for review.
        - The academic_writing_critic *MUST* review the writing and send it to the academic_reviewer for review.
        - The academic_reviewer *MUST* send it to the academic_writer for rewriting.
        - Confirm that each agent has completed their task by sending the message "ASSISTANT DONE", "CRITIQUE COMPLETE", "REVIEW COMPLETE" and "WRITER DONE" respectively.
        - The academic_writing_critic should do a final review of the writing.
        - The academic_reviewer *MUST* review writing *AT LEAST* TWICE.
        - The academic_writer *MUST* do the final rewrite. 
### BEGIN RESEARCH PAPER ###
\documentclass[12pt,letterpaper,oneside]{article} % Switched to 'article' class
\usepackage[margin=1in]{geometry} % to adjust the page margins if needed
\usepackage{setspace} % Include the setspace package
\usepackage{blindtext}
\usepackage{hyperref}
\usepackage{graphicx} 
\graphicspath{./Images/}
\usepackage[pdf]{graphviz}
\usepackage[english]{babel}
\usepackage[square,numbers]{natbib}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{lscape}
\usepackage{longtable}
\usepackage{array}
\usepackage{multirow}
\usepackage{forest}
\usepackage{amsmath,amssymb}
\usepackage{array}
\usepackage{tabularx}
\usepackage{threeparttable}
\usepackage{bbding}
\bibliographystyle{abbrvnat}
\title{The Way to Talk to AI: A Taxonomy of Prompt Patterns to LLMs}

\author{
Tim Haintz\thanks{tjhaintz@students.federation.edu.au} \and
Paul Pang\thanks{p.pang@federation.edu.au}
}
\date{July 2023}

\begin{document}
\doublespacing % This command sets double line spacing

\maketitle

%\tableofcontents

\begin{abstract}
As the interface between humans and Large Language Models (LLMs) continues to advance, structuring and optimising communication has become crucial. This paper introduces a comprehensive taxonomy of Prompt Patterns (PPs) for LLMs, serving as a refined linguistic framework that enhances interaction efficacy. We categorise these PPs based on the logic of English prepositions into six distinct types—Across, At, Beyond, In, Out, Over—each tailored to specific communication objectives from detailed inquiries to boundary-pushing commands. The taxonomy is meticulously crafted, derived from extensive linguistic analysis and illustrated through numerous examples across various domains. Hosted at \href{https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/promptpatterns.json}{GitHub}, our taxonomy compiles 120 PPs and over 300 practical examples, curated from 150 scholarly references. This structured approach not only aids in crafting precise and contextual prompts but also enhances the AI’s response accuracy, significantly improving the quality of human-AI interaction. By establishing a systematic framework for prompt design, our taxonomy is poised to be an indispensable resource, promoting more intuitive and effective communications with AI systems.
\end{abstract}
\textbf{Keywords:} Large Language Model, Taxonomy, Prompt Engineering,  Prompt Pattern, Prompt Example, ChatGPT, Prepositional Logic, Generative AI

\section{Introduction}
%backgound: LLM -->chatgpt functions--> applied chatgpt, --> prompt engineering, --> obstacles on prompt to LLM (random patterns are there)

Prompt Patterns (PPs) are essential to effective prompt engineering. A key contribution of this paper is the introduction of PPs to document successful approaches for systematically engineering different output and interaction goals when working with conversational LLMs. We focus largely on engineering domain-independent PPs and introduce a catalogue of essential PPs to solve problems ranging from production of visualisations and code artifacts to automation of output steps for fact checking.

Large Language Models (LLMs) (\cite{Zhang2022OPT:Models}, \cite{Chowdhery2022PaLM:Pathways}, \cite{Touvron2023LLaMA:Models}, \cite{GeminiTeam2023Gemini:Models}, \cite{Brown2020LanguageLearners}, \cite{OpenAI2023GPT-4Report}) have shown their capability and usefulness across a wide range of applications. An LLM is a type of language model that uses neural networks with billions of parameters \cite{FanA2023}. The same Language Model can be used for multiple purposes, without the need for additional training or supervision \cite{Liu2023Pre-trainProcessing}. The adoption of LLMs in diverse fields makes them a very useful addition in many industries. Hariri states ChatGPT has been applied in various real-world scenarios, including healthcare, education, customer service, content creation, language translation, entertainment, financial services, atmospheric science, chatbots, and computer science and coding \cite{Hariri2023UnlockingProcessing} .

The method of working with LLMs has become known as \textit{Prompt Engineering}. Prompt Engineering is the interface to interact via natural language with LLMs. The effectiveness of the LLMs largely depends on prompt engineering. \textit{Prompt Engineering} involves crafting effective prompts that guide the model to produce desired responses. The quality of the prompt significantly influences the output, making \textit{Prompt Engineering} an essential skill in the field of AI. It is used to assist in obtaining correct and accurate results \cite{White2023AChatGPT}. As the LLM scales, the downstream use of Prompt Engineering for Natural Language Processing (NLP) is critical \cite{Wei2022EmergentModels}. Prompting enables domain experts to solve tasks using natural language, but task accuracy varies significantly with prompt choices, often requiring extensive trial and error to find the best fit \cite{Strobelt2023InteractiveModels}.

Recent updates to the ChatGPT models, GPT-35-Turbo and GPT-4, have introduced a conversational interface in which to interact and utilise \textit{Prompt Engineering}. The Application Programming Interface (API) for these new models introduced a \textit{System role}, \textit{Assistant role} and \textit{User role}. Leveraging these roles allows for the use of \textit{Prompt Engineering}, zero-shot and few-shot prompting. Zero-shot prompting uses the system and user role. In few-shot prompting, all three available roles - system, assistant, and user - are utilised. 

Despite these advancements, there are several obstacles to perfecting these models. These include challenges related to ensuring the model’s understanding of nuanced human language, ethical concerns about misuse, and the response being made up or fabricated \cite{Shen2023ChatGPTSwords,Hariri2023UnlockingProcessing}.

% prompt and pp definition 
According to White et al. \cite{White2023AChatGPT}, prompts are instructions given to an LLM to enforce rules, automate processes, and ensure specific qualities (and quantities) of generated output. Prompts are also a form of programming that can customise the outputs and interactions with an LLM. Giray et al. \cite{Giray2023PromptWriters} describes a prompt as an instruction or query given to a language model to guide its behavior and generate desired outputs, consisting of elements such as instruction, context, input data, and output indicator.

%prompt pattern
A Prompt Pattern (PP) refers to a general structure or format used to guide a language model's response, often without specific content. It serves as a template that can be filled with various inputs to achieve different tasks. For instance, the 'Simple Colon' PP in White et al. \cite{White2023AChatGPT} uses the format 'French: source-phrase English:', which can be applied to any French phrase needing translation. It often includes placeholders or cues that indicate where specific information should be inserted. For instance, a PP might include phrases like 'what may happen', 'will ...?', or 'why might', which are used to construct questions that require a certain type of response. On the other hand, a prompt example (PE) is a specific instance or illustration of a prompt that follows a particular pattern or structure. It is a concrete example that demonstrates how the pattern can be applied in practice. For example, given the PP 'Use what may happen, will ...?, why might, etc.', a prompt example could be 'What may happen if my shoes never show up?' or 'Why might GPS technology have been invented?'. While a PP provides a general framework, a prompt example shows a specific application of that framework. \cite{Mishra2021ReframingLanguage}

\section{Existing Prompt Engineering Surveys}
% We evaluate existing survey from several dimensions. Dimensions keywords for the table are: Survey, Collection of PP, Collection of PE, Universal, Field and Year. Top 5 years and 10 articles. 
% Must be a survey or collections paper. 2020-2023
% Write out the below criteria. Introduce the table.
% 1. Survey - Cited name of paper
% 2. Collection of PP (Tick/Cross)
% 3. Collection of PE (Tick/Cross)
% 4. Universal (a. Not domain specific, b. Between AI and Human) - Scientific sentence, don't repeat. Consice
% 5. Field (Cybersecurity, Health - put in the actual value)
% 6. Year - (Newest first)
% 7. Completeness - ADD NEW FIELD. It may be UNIVERSAL but is is COMPLETE - Used to measure previous work.

We evaluate existing surveys and collections from several dimensions, as outlined in Table \ref{tab:relatedsurvey}. The dimensions include the presence or lack of PPs and/or PEs; if the work is domain-specific or applicable universally between AI and human; if not universal, the specific field the work applies to (e.g., cybersecurity, health etc.); and the publishing date of the work.

% Explain that the logic is complete so it can be reused. Connectivity. One connects to the other Reasoning and exploration plus dive into logic. Human behaviour allows things to be discovered using other methods. Derive from this to find complete.

\begin{table}[h]
	%\begin{threeparttable}
        \fontsize{9pt}{10pt}\selectfont
	\caption{Related surveys on Prompt Patterns (PP) and Prompt Examples (PE)}
	\begin{tabular}{|lcccccc|}
	%\toprule
	\hline
	\textbf{Survey} & \textbf{Collection of PP} & \textbf{Collection of PE} & \textbf{Universal} & \textbf{Field} & \textbf{Complete} & \textbf{Year}\\ \hline
    Sahoo et al. \cite{Sahoo2024AApplications} & \checkmark & $\times$ & \checkmark & - & $\varnothing$ & 02/2024 \\
    Deng et al. \cite{Deng2023Jailbreaker:Chatbots} & $\times$ & \checkmark  & $\times$ & Jailbreaking & $\varnothing$ & 07/2023 \\	
    Schmidt et al. \cite{SchmidtCatalogingEngineering} & \checkmark & \checkmark & \checkmark & - & $\varnothing$ & 06/2023 \\
    Wang et al. \cite{Wang2023PromptApplications} & $\times$ & \checkmark & $\times$ & Healthcare & $\varnothing$ & 04/2023 \\
	White et al. \cite{White2023ChatGPTDesign} & \checkmark & \checkmark & $\times$  & Code and Software & $\varnothing$ & 03/2023 \\
    Bubeck et al. \cite{Bubeck2023SparksGPT-4} & $\times$ & \checkmark & \checkmark & - & $\varnothing$ & 03/2023 \\
    White et al. \cite{White2023AChatGPT} & \checkmark & \checkmark & \checkmark & - & $\varnothing$ & 02/2023 \\
    Arora et al. \cite{Arora2022AskModels} & $\times$ & \checkmark & $\times$ & Jailbreaking & $\varnothing$ & 10/2022 \\
    Honovich et al. \cite{Honovich2022InstructionDescriptions} & $\times$ & \checkmark & \checkmark & - & $\varnothing$ & 05/2022 \\
    Wang et al. \cite{Wang2022Self-ConsistencyModels} & $\times$ & \checkmark & \checkmark & - & $\varnothing$ & 03/2022 \\
    Mishra et al. \cite{Mishra2021ReframingLanguage} & \checkmark & \checkmark & \checkmark & - & $\varnothing$ & 09/2021 \\ \hline
	%\bottomrule
	\end{tabular}
    \vspace{0.5cm} % New line/carriage return for readability
	%\end{threeparttable}
	\begin{tablenotes}
	      \small\vspace{-1.5ex}
	      \item (\checkmark): Supported/Complete; ($\times$): Not Supported; Not Applicable: (-); Not Complete: ($\varnothing$)
	    \end{tablenotes}
	\label{tab:relatedsurvey}
\end{table}


% 1. Introduce previous work to build such a prompt collection for different purpose
% a. Shining points from top 3 papers and discuss.


White et al. from Vanderbilt University presents a foundational framework for prompt engineering with large language models (LLMs) \cite{White2023AChatGPT}. They introduce 16 PPs categorised into 6 groups: Input Semantics, Output Customisation, Error Identification, Prompt Improvement, Interaction, and Context Control. Each PP is detailed with its intent, context, motivation, structure, key ideas, example implementation, and consequences. The paper underscores the importance of good prompt design, the evolution of LLM capabilities, and the generalisability of PPs across different domains. They provide a structured approach to documenting patterns for structuring prompts, adaptable to various domains, and illustrate how a PP can be built from multiple patterns to enhance LLM interactions. However, the work is merely a small collection of 16 PPs, which is far away to being universal between AI and human. \\

\par % New paragraph
Schmidt et al. addresses the need for a systematic approach to interacting with LLMs. The idea is to set up PPs in a structured way to boost and simplify human AI interactions, much like software patterns in standard software engineering \cite{SchmidtCatalogingEngineering}. This is a pioneering effort to catalogue PPs, providing reusable solutions to common problems encountered when using LLMs. By offering a structured approach, the research suggests repeatable, and effective use of LLMs across various domains, including software engineering, but not yet universal, which requires an expanded catalogue of PPs and their applications. \\

\par % New paragraph
Deng et al. introduce JAILBREAKER, a framework designed to understand and circumvent the defenses of LLM chatbots against jailbreak attacks, which prompt chatbots to generate responses that violate service guidelines \cite{Deng2023Jailbreaker:Chatbots}. The authors highlight the ineffectiveness of current strategies against mainstream LLM chatbots due to undisclosed defensive measures. JAILBREAKER’s first contribution is a novel method using time-based characteristics of the generation process to infer internal defense designs, inspired by time-based SQL injection techniques. This allows researchers to deconstruct defense mechanisms in services like CHATGPT, Bard, and Bing Chat (now Copilot). The second contribution is an innovative approach for the automatic generation of jailbreak prompts by fine-tuning an LLM, demonstrating higher success rates in generating attack prompts. The research focuses solely on jailbreaking and does not discuss universal usage across different domains. \\

\par % New paragraph
Sahoo et al. provide a comprehensive survey of prompt engineering techniques for large language models (LLMs) and vision-language models (VLMs) \cite{Sahoo2024AApplications}. They categorise recent advancements in prompt engineering by application area, offering a structured overview of various prompting methodologies, their applications, the models involved, and the datasets utilised. Key contributions include a detailed taxonomy diagram and a table summarising datasets, models, and critical points of each prompting technique, which facilitate a better understanding of this rapidly developing field. However, this work does not include any prompt examples, which limits its practical applicability for those looking to implement the discussed techniques directly. \\

 % 2. Necessity of Building the Taxonomy: Addressing Universal, Complete, and Open Access
 % One paragraph
From the view point of human to AI, a taxonomy that is universal, complete, and open access is in high demand, as this will set the standard for clear, efficient, and effective communication across various contexts and applications. With such a taxonomy, users can ensure that AI understands and executes tasks accurately, fostering a more intuitive and productive interaction. Moreover, an open-access taxonomy promotes widespread adoption and adaptation, allowing continuous improvement and updates based on user feedback and evolving use cases. This openness and universality are key to harnessing the full potential of AI, making it a versatile tool adaptable to the specific needs and nuances of different sectors and disciplines. \\

This paper advances prompt engineering by introducing a comprehensive, open catalogue of PPs, expanding on existing research, and providing a valuable resource for the community. The \href{https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/promptpatterns.json}{GitHub} repository has the PPs and PEs available as a JSON database that can be used to programmatically combine PPs and PEs to form useful domain agnostic prompts. \\

% 3. Contribution of This Paper
The contribution of this paper is summarised as:
\begin{enumerate} 
    \item We leveraged English language logic to develop a comprehensive catalogue to organise PPs and PEs in the context of human and AI communication.
    \item We constructed a Taxonomy, which includes complete logic which consists of NNNN PPs and NNNN PEs, sourced from NNN papers and forums.
    \item We develop strategies to combine and apply PPs and PEs to complicated problem from different domains.  
\end{enumerate}
 
%To write: S2: overview, setup the taxanomy (TX), PP, PE, definition and terms.  S3: categorisation in Human to AI  S4-S10 6 logics,  S11: Application (how to use the TX), S12 Limit and gaps, S13: Conclusion and future work 

The rest of this paper is organised as follows: Section \ref{sec:overview} defines the structure of a PP, the LLMs used for testing PPs, the measurements of PP effectiveness, and how to perform tests via API. Section \ref{sec:categorisation} categorises PPs based on the logic of the English language, introducing categories such as Across, At, Beyond, In, Out, and Over logic, each with specific examples and applications. Sections \ref{sec:across} - \ref{sec:over} present the taxonomy for the prepositional logic of Across, At, Beyond, In, Out, and Over, respectively. We introduce the scope of its logic and categorises various PPs and prompt examples. Each category includes an example PP and a list of related PPs and PEs, along with advice on their reuse. Section \ref{sec:Application} discusses the practical application of the taxonomy, illustrating its utility in various contexts. It specifically investigates how to combine multiple PPs across categories and logic for complex real-world applications. Finally, in Section \ref{sec:conclusion}, this paper concludes with the presentation of ideas for future work.

\section{Overview}
\label{sec:overview}
\subsection{Structure of a PP}
% criteria % cite
To enhance the performance and quality of a language model’s output, it is crucial to follow these five key strategies: 
\begin{itemize}
    \item Provide clear context: This allows the model to answer with precise understanding and tailored responses, optimising the relevance and accuracy of the outcome.
    \item State the desired output: This helps the model understand the specific information or response it needs to generate. 
    \item Break down complex questions into Sub-Questions: This helps the model focus on individual aspects of the topic and generate more accurate and detailed responses.
    \item Provide Specific Instructions: This ensures that the model understands any constraints or requirements in generating the output.
    \item Define conciseness: Prompt the model to generate concise and relevant responses by specifying any word limits or constraints. This helps prevent the model from generating unnecessarily lengthy or irrelevant answers.
\end{itemize}
By following the above five criteria, the language model can better understand and interpret the input, leading to improved performance and output quality.

White et. al \cite{White2023AChatGPT} recorded PPs in a data structure as:
\begingroup
\renewcommand{\arraystretch}{0.6}
\begin{center}
\fontsize{9pt}{10pt}\selectfont
\noindent
\begin{tabular}{|l|}
\hline
\textbf{Prompt Pattern} \\ \hline
A name and classification\\
The intent\\
The motivation\\
The structure and participants\\
Example code\\
Consequences\\\hline
\end{tabular}
\end{center}
\endgroup

The structure for PPs is generally well-organised. The primary issue is the overlap between ‘intent’ and ‘motivation’. While these terms can be distinct, in many contexts they could be interpreted as conveying similar information, leading to redundancy. The structure does not align perfectly with the five criteria discussed above. The pattern structure lacks explicit mention of breaking down complex questions into sub-questions and providing specific instructions, which are crucial for enhancing the model’s understanding and performance.

To ensure a more systematic and comprehensive approach, ultimately leading to more accurate and high-quality outputs from the language model, we have refined the structure to more closely align with the above five criteria as: 
\begingroup
\renewcommand{\arraystretch}{0.6}
\begin{center}
\fontsize{9pt}{10pt}\selectfont
\noindent
\begin{tabular}{|l|}
\hline
\textbf{Prompt Pattern (PP)}\\ \hline
ID \\ 
Category \\ 
Name \\ 
Media Type: [Text Only, Text2Audio, Text2Image, Text2Video, Audio2Text, Image2Text, Video2Text]\\
Description: \\ 
Template: [Role, Context, Action, Format, Response]\\
Prompt Example (PE)\\ 
Related PPs \\ 
Reference \\ \hline
\end{tabular}
\end{center}
\endgroup
PE is recorded as a three field structure: ID, Prompt and its Response. ID is structured as 
\textit{Reference Id +  Index in Reference + PP id + the example id}. For example:
1-2-3-4, the PE is sourced from the 2nd reference paper, and it is the 5th prompt example, associated to the 4th PP in the 3 group in the reference. Note zero indexed referencing is applied here.

% Template: [Role, Context, Action, Format, Response]
We define a template for PPs as [Role, Context, Action, Format, Response]. This structure is crucial for creating effective and precise interactions with LLMs. Ideally, each prompt includes all these components to ensure clarity and completeness. The Role sets the perspective or persona, Context provides the background information, Action specifies the task, Format dictates the desired structure of the response, and Response anticipates the type of output expected. While some components can be omitted without rendering the prompt unusable, their absence can impact the accuracy and relevance of the AI's response. By adhering to this comprehensive template, users can maximise the efficiency and reliability of their interactions with LLMs. In the remaining paper, the original PPs and prompt elements are introduced, which may not strictly follow this template. However, they can all be logically mapped to these components—complete or in part. 

\subsection{Prompt Test and Verification}
In this section, we introduce how a PP is tested to ensure that the interactions between users and LLMs are both effective and reliable.

% a list of LLMs
The models and versions used for our PPs testing were all built in Azure OpenAI, which includes
\begin{table}
\fontsize{9pt}{10pt}\selectfont
    \centering
    \caption{Azure OpenAI Models used}
    \begin{tabular}{|c|c|}
    \hline
         \textbf{Model name}& \textbf{Model version}\\ \hline
         gpt-35-turbo & 0301\\ \hline
         gpt-35-turbo-16k & 0613\\ \hline
         gpt-4-32k & 0613\\ \hline
         gpt-4 & 1106-Preview\\ \hline
         gpt-4 & vision-preview\\ \hline
         gpt-4.1 & 2025-04-14 \\ \hline
         gpt-4.5-preview & 2025-02-27 \\ \hline
         gpt-4o & 2024-05-13\\ \hline
         o1-mini & 2024-09-12\\ \hline
         o3-mini & 2025-01-31\\ \hline
         o4-mini & 2025-04-16\\ \hline
         Embeddings & text-embedding-ada-002\\ \hline
         Embeddings & text-embedding-3-large\\ \hline
         DeepSeek & R1\\ \hline
    \end{tabular}
    \label{tab:Azure OpenAI Models}
\end{table}

% Measurements - accuracy, relevance and consistency
The primary measurements of prompt verification include: Accuracy: Ensuring the information provided by the LLM in response to prompts is correct and reliable; Relevance: Verifying that responses are pertinent to the prompts, addressing the user's intent accurately; Consistency: Ensuring that the LLM provides consistent responses to the same or similar prompts across different instances; and Appropriateness: Confirming that the responses adhere to ethical guidelines and do not propagate biases or harmful content.

% Interface: Query and Programming
In practice, testing a PP involves feeding a set of prompt examples to LLMs. This can be done by employing automated scripts and/or manual queries. For manual queries, prompts are directly inputted into the LLM's API using the System, Assistant and user prompt. The hands-on approach allows for rapid testing and immediate feedback with nuanced understanding of prompt effectiveness. For programming, two scripts are utilised to automate the testing process. These scripts, available on  GitHub at \href{https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/testPrompts.py}{testPrompts} and \href{https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/vision_testPrompts.py}{visionTestPrompts}respectively, cater to text-based and vision-related prompt examples, streamlining the submission of prompts to the LLM and the collection of its responses for analysis.

\section{Prompt Categorisation}
\label{sec:categorisation}
% Logical synthesis of existing patterns. 
% Develop new patterns.
In the realm of communication between humans and Large Language Models (LLMs) like AI, PPs emerge as a vital linguistic bridge. These patterns are essential as they encapsulate the logic and structure inherent in human conversation, which is the ultimate goal of human-AI interaction. English, with its intricate system of grammar and rich array of prepositions, encapsulates the complete logic necessary for effective communication between humans. This comprehensive logic is essential in guiding AI to respond to a wide range of instructions and scenarios, mirroring human conversational abilities. To develop the complete logic of human-AI language, we learn from English by simply looking at the prepositions to ransack all aspect logic, in terms of topic.

\begin{itemize}
    \item \textbf{Across} logic is used to signify one topic from the other. This could represent prompts that span \textbf{multiple domains} or disciplines, integrating diverse types of knowledge.
    \item \textbf{At} logic is used to refer to a more specific aspect or detail of the topic. This might refer to prompts that are \textbf{specific} to a certain context or scenario, targeting precise responses.
    \item \textbf{Beyond} logic is used to discuss aspects that are on the far side of a certain point or limit of a topic. This could indicate prompts that push the boundaries of what the AI can do, exploring \textbf{new capabilities} or \textbf{innovative ideas}.
    \item \textbf{In} logic is used to indicate that something is contained within a topic or space. This could represent prompts that are \textbf{internal} to a system, focusing on self-reflection or introspection.
    \item \textbf{Out} logic is employed to convey the idea of expanding upon or moving beyond the general scope of a topic. This might be used for prompts that generate \textbf{outputs}, such as creative writing or code generation.
    \item \textbf{Over} logic is used to describe elements that span the entirety of the topic, which implies comprehensive coverage. This could be associated with prompts that require \textbf{oversight} or review, such as editing or improving existing content.
\end{itemize}


Figure \ref{fig:prepositions} illustrates the comprehensive PP categorisation in relation to the Logic of English language.

\begin{figure}
    \centering
    \caption{Categorisation of PPs in relation to the logic of English language centered on a core topic in between human and AI.}
    \label{fig:prepositions}
    \includegraphics[width=0.5\linewidth]{Images/Prepositions.png}
\end{figure}

\begin{table}
\centering
\caption{The structure of PP Taxonomy}
\fontsize{10pt}{8pt}\selectfont
\begin{forest}
  for tree={
    grow'=0,
    child anchor=west,
    parent anchor=south,
    anchor=west,
    calign=first,
    edge path={
      \noexpand\path [draw, \forestoption{edge}]
      (!u.south west) + (5pt,0) |- (.child anchor)\forestoption{edge label};
    },
    before typesetting nodes={
      if n=1
        {insert before={[,phantom]}}
        {}
    },
    fit=band,
    before computing xy={l=10mm},
  } 
[PP Taxonomy 
  [Across Logic \ref{sec:across}
    [Argument \ref{subsec:Argument}]
    [Comparison \ref{subsec:Comparison}]
    [Contradiction \ref{subsec:Contradiction}]
    [Cross Boundary \ref{subsec:CrossBoundary}]
    [Translation \ref{subsec:Translation}]
  ]
  [At Logic \ref{sec:at}
    [Assessment \ref{subsec:Assessment}] 
    [Calculation \ref{subsec:Calculation}]
    [Induction]
  ]
  [Beyond Logic \ref{sec:beyond}
    [Hypothesise \ref{subsec:Hypothesise}]
    [Logical Reasoning \ref{subsec:LogicalReasoning}]
    [Prediction \ref{subsec:Prediction}]
    [Simulation \ref{subsec:Simulation}]
  ]
  [In Logic \ref{sec:in}
    [Categorising \ref{subsec:categorising}] 
    [Classification \ref{subsec:classification}]
    [Clustering \ref{subsec:clustering}] 
    [Error Identification \ref{subsec:ErrorIdentification}] 
    [Input Semantics \ref{subsec:InputSemantics}]
    [Requirements Elicitation \ref{subsec:RequirementsElicitation}]
  ]
  [Out Logic \ref{sec:out}
    [Context Control \ref{subsec:ContextControl}]
    [Decomposed Prompting \ref{subsec:DecomposedPrompting}]
    [Output Customisation \ref{subsec:OutputCustomisation}]
    [Output Semantics \ref{subsec:OutputSemantics}]
    [Prompt Improvement \ref{subsec:PromptImprovement}]
    [Refactoring \ref{subsec:Refactoring}] 
  ]
  [Over Logic \ref{sec:over}
   [Summarising \ref{subsec:Summarising}]
   ]

]
\end{forest}
\end{table}

\begin{table}
\fontsize{9pt}{10pt}\selectfont
    \centering
    \caption{Category Acronyms}
    \label{tab:Category_Acronyms}
    \begin{tabular}{|c|c|} \hline 
         Acronym & Category\\ \hline 
         ARG & Argument\\ \hline 
         ASM & Assessment\\ \hline 
         CAL & Calculation\\ \hline 
         CAT & Categorising\\ \hline 
         CLF & Classification\\ \hline 
         CLU & Clustering\\ \hline 
         CMP & Comparison\\ \hline 
         CTD & Contradiction\\ \hline 
         CTX & Context Control\\ \hline
         CRB & Cross Boundary - Jailbreaking\\ \hline
         DPR & Decomposed Prompting\\ \hline 
         ERI & Error Identification\\ \hline 
         HYP & Hypothesise\\ \hline 
         INP & Input Semantics\\ \hline 
         IND & Instruction Induction\\ \hline 
         LGR & Logical Reasoning\\ \hline 
         OUC & Output Customisation\\ \hline 
         OUS & Output Semantics\\ \hline 
         PRD & Prediction\\ \hline 
         PMI & Prompt Improvement\\ \hline 
         REF & Refactoring\\ \hline 
         REL & Requirements Elicitation\\ \hline 
         SIM & Simulation\\ \hline 
         SUM & Summarising\\ \hline 
         TRA & Translation\\ \hline
    \end{tabular}
\end{table}


\subsection{Indexing}
%introduce Template grammar with one example

We have created an index to uniquely name each PP and PE in the taxonomy. The naming structure is:
\\\textit{preposition logic id + category id  + title id + paper category id + PP id + prompt example id}.

% Need to rewrite the below
Please note, the paper category id is the categorisation created in each paper. Our category id is an overarching category based on prepositional logic.

%The preposition logic id is show in \tablename. The acronym for the category id is shown in \tablename{Category_Acronyms}.

Title id, paper category id + PP id and prompt example id are all references to the JSON index location in \textit{promptpatterns.json}. Available on Github.

% Create a new example for below.
Example:
PE\_AC\_ARG\_2-1-0-0

Refers to the below location in the \textit{promptpatterns.json} file.
"Title": "Cataloging Prompt Patterns to Enhance the Discipline of Prompt Engineering",
"id":2, [2]
"PatternCategory": "Error Identification", [1]
"PatternName": "Reflection", [0]
"ExamplePrompts": "Whenever you generate an answer Explain the reasoning and assumptions behind your answer" [0]

Further information for the prompt examples can be found in the Appendix.

\subsection{Cosine Similarity}
% How PE maps to PP, PP to Category and Category to Prepositional logic
The \href{https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/categorisation_cosine_similarity.py}{Cosine Similarity} script can be found at GitHub. This script was used to find similar PPs and PEs.

Cosine Similarity, a prevalent metric in information comparison, models text as term vectors, with similarity derived from the cosine value between these vectors. Kitasuka et al. \cite{Kitasuka2012SemanticSimilarity} proposes an enhancement to cosine similarity by incorporating semantic checking between vector dimensions, aiming to improve the handling of semantic meaning and increase similarity values for vectors with semantically related but syntactically different dimensions. 

The Azure OpenAI model, \textit{text-embedding-3-large}, was used as it represents the latest generation of large-scale text embedding models, capable of generating embeddings with up to 3072 dimensions. Demonstrating superior performance, this model provides a dense representation of semantic meaning, where the distance between two embeddings in the vector space correlates with the semantic similarity between the corresponding inputs.

Using Cosine Similarity with the embeddings generated by the \textit{text-embedding-3-large} model leverages Semantic Similarity. The embeddings capture the semantic information of the text, and the Cosine Similarity measures the cosine of the angle between two vectors. This results in a similarity score that reflects the semantic similarity between the two pieces of text represented by the vectors.

\subsection{Statistics of Prompt Taxonomy}
%Introduction paragraph to summarise the table
The constructed Taxonomy consists of a total of 906 PPs and 1869 PEs, derived from over 100 papers, websites, and GitHub repositories. The PPs and PEs are synthesized into the six prepositional logic categories within the context of human to AI communication. The detailed statistics of the Taxonomy for each category are provided in Table \ref{tab:Statistics_of_Prompt_Taxonomy}.

\begin{table}[htbp]
\centering
\caption{Statistics of Prompt Taxonomy based on Preposition logic and Category}
\label{tab:Statistics_of_Prompt_Taxonomy}
\resizebox{\textwidth}{!}{
\begin{tabular}{|l|c|c|c|c|}
    \hline
    \textbf{Preposition logic} & \textbf{Category} & \textbf{No. of PPs} & \textbf{No. of PE} & \textbf{No. of References (Ref)} \\ \hline
    \multirow{5}{*}{Across} & 1. Argument & 30 & 48 & \multirow{5}{*}{[1]} \\ \cline{2-4}
     & 2. Comparison & 83 & 113 &  \\ \cline{2-4}
     & 3. Contradiction & 21 & 37 &  \\ \cline{2-4}
     & 4. Cross Boundary (Jailbreaking for example) & 1 & 4 &  \\ \hline
     & 5. Translation & 54 & 72 &  \\ \cline{2-4}
    \multirow{3}{*}{At} & 1. Assessment & 136 & 206 & \multirow{3}{*}{[2]} \\ \cline{2-4}
     & 2. Calculation & 69 & 92 &  \\ \cline{2-4}
     & 3. Induction & 1 & 5 &  \\ \hline
    \multirow{4}{*}{Beyond} & 1. Hypothesise & 1 & 4 & \multirow{4}{*}{[3]} \\ \cline{2-4}
     & 2. Logical Reasoning & 1 & 4 &  \\ \cline{2-4}
     & 3. Prediction & 1 & 5 &  \\ \cline{2-4}
     & 4. Simulation & 1 & 5 &  \\ \hline
    \multirow{6}{*}{In} & 1. Categorising & 19 & 21 & \multirow{6}{*}{[75]} \\ \cline{2-4}
     & 2. Classification & 14 & 16 &  \\ \cline{2-4}
     & 3. Clustering & 4 & 6 &  \\ \cline{2-4}
     & 4. Error Identification & 63 & 98 &  \\ \cline{2-4}
     & 5. Input Semantics & 81 & 106 &  \\ \cline{2-4}
     & 6. Requirements Elicitation & 22 & 28 &  \\ \hline
    \multirow{6}{*}{Out} & 1. Context Control & 1 & 4 & \multirow{6}{*}{[5]} \\ \cline{2-4}
     & 2. Decomposed Prompting & 1 & 4 &  \\ \cline{2-4}
     & 3. Output Customisation & 1 & 4 &  \\ \cline{2-4}
     & 4. Output Semantics & 1 & 4 &  \\ \cline{2-4}
     & 5. Prompt Improvement & 1 & 4 &  \\ \cline{2-4}
     & 6. Refactoring & 1 & 4 &  \\ \hline
    \multirow{1}{*}{Over} & 1. Summarising & 128 & 177 & [29] \\ \hline
\end{tabular}
}
\end{table}

%##########template Begin#############
\section{Across Logic - Navigating between topics}
\label{sec:across}
%1 - Write long introduction to the logic - text
Across logic is used to transition from one topic to another, navigating between distinct areas of knowledge. This type of logic is particularly valuable in scenarios where prompts need to span \textbf{multiple domains} or disciplines, integrating diverse types of knowledge to create a cohesive narrative or solution. \\

%2 - introduce categories under this logic
The PP categories under across logic include:
\begin{enumerate}
    \item \textbf{Argument}: Refers to a structured process where a claim or viewpoint is presented and defended. This type of prompt enables the AI model to generate a response that not only states a position, but also provides reasoning and evidence to support it. 
    \item \textbf{Comparison}: Examining two or more objects and identifying their similarities and differences. This type of prompt helps in exploring the relationships between different objects, and discovering insights from their characteristics.
    \item \textbf{Contradiction}: Refers to presenting opposing statements or viewpoints that cannot be true simultaneously. This type of prompt enables the AI model to recognise and articulate conflicting information, helping in critical reasoning by evaluating inconsistencies and detecting logical errors.
    \item  \textbf{Cross Boundary}: Involves pushing the AI model beyond its predefined operational or ethical limits, such as attempting to bypass safeguards or restrictions (e.g., jailbreaking). This type of prompt challenges the boundaries of what the model is allowed to do, often with the intent of manipulating it to generate responses that are typically restricted. 
    \item \textbf{Translation}: Refers to converting data from one interpretation to another while preserving the original meaning. This type of prompt helps humans understand complex concepts by transforming information into a more familiar or accessible format.
\end{enumerate}

%3 introduce category one by one as subsection
\subsection{Argument}
\label{subsec:Argument}

% 3.1 the role of this category under the "across-logic" (meaning of the category)
Argument involves presenting and defending a claim or viewpoint. This process includes stating a clear claim, providing logical reasoning and evidence to support/refute it. The effectiveness of an argument is measured by its clarity, coherence, and the strength of its supporting evidence. 

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Debater PP as described in Table \ref{tab:Debater_PP} focuses on exploring various perspectives. It is designed to facilitate a structured debate format, researching both sides of a given topic and refuting opposing viewpoints. 
%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The AI model typically generates a comprehensive list of pros and cons and a balanced summary. Through follow-up chat, you can request the model to explore either side of the topic in more detail. 
%% re-use: how to derive a PE from PP
To apply the Debater PP in a given context, set a topic of debate, such as "The Ethical Implications of AI in Healthcare," assign AI the role of a debater, request exploration of both sides of the topic, and define the objective and output format to ensure a balanced and insightful discussion. Here is an example of derived PE:
I want you to act as a debater. I will provide you with a topic related to current events: "The Ethical Implications of AI in Healthcare." Your task is to research both sides of the debate, present valid arguments for the benefits and drawbacks of AI in healthcare, refute opposing points of view with evidence, and draw persuasive conclusions. Your goal is to help the audience gain a comprehensive understanding of the ethical landscape and practical impact of AI in this field."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Debater PP}
\label{tab:Debater_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 11-0-9\\ 
    \textbf{Category}: ARG\\ 
    \textbf{Name}: Debater\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}:  Debater engages the user in a structured debate format. The user is tasked with researching\\ current event topics, presenting balanced arguments for both sides, refuting opposing viewpoints,\\ and drawing evidence-based conclusions. The goal is to enhance the user's understanding and insight\\ into the topic through a comprehensive and persuasive discussion. \\
    \textbf{Template}: I want you to act as a debater. I will provide you with some topics related to current events\\ and your task is to research both sides of the debates, present valid arguments for each side, \\ refute opposing points of view, and draw persuasive conclusions based on evidence. \\Your goal is to help people come away from the discussion with increased knowledge \\and insight into the topic at hand. My first request is "I want an opinion piece about:"\\
    \textbf{Example}: 11-0-9-0\\ 
    \textbf{Related PPs}: 26-0-1, 8-0-0, 26-0-3, 22-0-2, 26-0-0, 22-2-3, 41-2-7, 23-0-0, 40-0-0, 29-0-0\\ 
    \textbf{Reference:} \cite{Akin202450Prompts}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above (optional)
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Debater PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    11-0-9-0& I want you to act as a debater. I will provide you with some topics related to current events and your task is to research both sides of the debates, present valid arguments for each side, refute opposing points of view, and draw persuasive conclusions based on evidence. Your goal is to help people come away from the discussion with increased knowledge and insight into the topic at hand. My first request is "I want an opinion piece about Deno."\\
    \hline
\end{tabular}
\end{table}

%6 - other PPs in this category ***
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the ACROSS\_ARG category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    26-0-1 & The DAN 6.0 Prompt &\cite{Inie2023SummonWild}\\ \hline
    8-0-0 & Hallucination Evaluation &\cite{LiHaluEval:Models}\\ \hline
    26-0-3 & The DUDE Prompt &\cite{Inie2023SummonWild}\\ \hline
    22-0-2 & Privilege Escalation - Sudo Mode (SUDO) & \cite{Liu2023JailbreakingStudy}\\ \hline
    26-0-0 & The Jailbreak Prompt & \cite{Inie2023SummonWild}\\ \hline
    22-2-3 & Superior Model (SUPER) & \cite{Liu2023JailbreakingStudy}\\ \hline
    41-2-7 & Write detailed text & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
    23-0-0 & Rewrite & \cite{Liu2023CheckCheckGPT}\\ \hline
    40-0-0 & Few-Shot Prompt for Generating Priming Attacks & \cite{Vega2023BypassingAttacks}\\ \hline
    29-0-0 & Disinformation & \cite{Vykopal2023DisinformationModels}\\ \hline
\end{tabular}
\end{table}

%##########template End#############

\subsection{Comparison}
\label{subsec:Comparison}
% 3.1 the role of this category under the "across-logic" (meaning of the category)
The Comparison category of PPs looks at two or more things to identify their similarities and differences, aiding in understanding their relationships and characteristics.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Comparison of Outputs (CO) PP in Table \ref{tab:Comparison_of_Outputs_PP} focuses on comparing two outputs to identify similarities, differences, and areas for improvement. % add b. and c.

%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When using the CO PP, you will have a clear guide to understand how two things align or differ, making it easier to spot strengths and weaknesses. The model’s tone and approach change depending on its role. For instance, as a teacher, it feels supportive and objective, offering balanced insights. However, if the role shifts to something like a judge, the tone becomes more critical and evaluative, which can feel stricter but also more decisive. This adaptability helps tailor the output to the context, making it more relatable and useful.

%% re-use: how to derive a PE from PP
To apply the CO PP in a given context, provide two outputs for comparison, such as essays on the same topic. Instruct the AI to compare them, focusing on strengths, weaknesses, and areas for improvement. Define the objective and desired output format to ensure a balanced and insightful analysis. For example: "Can you compare the two outputs above as if you were a teacher? Highlight their strengths, weaknesses, and areas for improvement."

To derive a PE from the CO PP, follow these steps: 1) select two items to compare, such as essays on the same topic; 2) Define the AI’s role, like a teacher, judge, or critic, to shape the tone and focus of the analysis; and state clearly the goal (e.g., identifying strengths, weaknesses, and areas for improvement) and the desired output format. For example, you could write:
"Can you compare the two outputs above as if you were a teacher? Highlight their strengths, weaknesses, and areas for improvement." This approach ensures a balanced, insightful, and context-aware analysis tailored to your needs.

%4 - PP example in this category
\textbf{\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Comparison of Outputs PP}
\label{tab:Comparison_of_Outputs_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 32-2-1\\ 
    \textbf{Category}: CMP\\ 
    \textbf{Name}: Comparison of Outputs\\ 
    \textbf{Media Type}: Text Only, Image2Text, Video2Text\\ 
    \textbf{Description}: The prompt compares outputs by identifying strengths and weaknesses, noting areas of excellence\\ or shortcomings, and providing constructive feedback. Adopting a teacher's role, the AI model offers a balanced\\ comparison, highlighting key differences and similarities to aid in understanding and refining the outputs. \\
    \textbf{Template}: Can you compare the two outputs above as if you were a teacher?\\
    \textbf{Example}: 32-2-1-0\\ 
    \textbf{Related PPs}: \\ 
    \textbf{Reference:} \cite{Bubeck2023SparksGPT-4}\\ \hline
\end{tabular}
\end{table}}

                                
%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Comparison of Outputs PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    32-2-1-0& Can you compare the two outputs above as if you were a teacher?\\
    \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the ACROSS\_CMP category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    10-22-0 & Spot the Difference &\cite{Yang2023TheGPT-4Vision}\\ \hline
    10-11-2 & Visual Referring Prompting &\cite{Yang2023TheGPT-4Vision}\\ \hline
    13-2-0 & Proxies or Analogies &\cite{Reynolds2021PromptParadigm}\\ \hline
    32-8-1 & Real world scenarios & \cite{Bubeck2023SparksGPT-4}\\ \hline
    10-7-1 & Science and Knowledge & \cite{Yang2023TheGPT-4Vision}\\ \hline
    10-23-0 & Defect Detection & \cite{Yang2023TheGPT-4Vision}\\ \hline
    18-5-0 & Enforcing Yes/No format & \cite{Polak2023ExtractingEngineering}\\ \hline
    18-1-1 & Multi-valued sentence analysis & \cite{Polak2023ExtractingEngineeringb}\\ \hline
    13-0-0 & Constructing the Signifier & \cite{Reynolds2021PromptParadigm}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    41-1-3 & Use output primers & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
    14-2-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    19-11-2 & Word in Context & \cite{Honovich2022InstructionDescriptions}\\ \hline
    11-0-12 & AI Writing Tutor & \cite{Akin202450Prompts}\\ \hline
    30-8-1 & Dataset Construction & \cite{Liu2023Pre-trainProcessing}\\ \hline
    27-0-1 & Crossover & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
\end{tabular}
\end{table}

% %3 introduce category one by one as subsection
\subsection{Contradiction}
\label{subsec:Contradiction}
% 3.1 the role of this category under the "across-logic" (meaning of the category)
Contradiction arises when statements or ideas are mutually exclusive, meaning they cannot all be true simultaneously. This concept is pivotal in logic and mathematics, often used to demonstrate the falsity of propositions. Identifying contradictions is crucial for understanding and reasoning, as they highlight potential errors or misunderstandings.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Hallucination Evaluation (HE) PP in Table \ref{tab:Hallucination_Evaluation_PP} compares a summary with the original text, for detecting any contradictions or fabricated information. This PP helps mitigate misinformation, improves trust in automated summaries, and supports quality control in text generation tasks. Beyond its primary use, this PP can be adapted for fact-checking in news aggregation, verifying AI-generated reports, or validating outputs in educational and research contexts where factual integrity is critical. Its structured approach makes it reusable across various domains requiring content verification.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When using the HE PP, the AI model response should provide a clear, methodical comparison between the summary and the source document, highlighting any discrepancies with precision. The response should instil confidence, making you feel that the summary can now be trusted—or at least that you’re fully aware of its limitations. It’s like having a diligent editor by your side, ensuring nothing slips through the cracks.

%% re-use: how to derive a PE from PP
To derive a PE from the HE PP, first specify the context—such as verifying if a news summary aligns with the original article. Provide both the summary and source text, then define the evaluation’s focus (e.g., factual accuracy, omissions, or distortions) and the desired output format (e.g., a list of discrepancies or a confidence score). An example of such PE is "Compare the following summary with its source document and identify any factual inconsistencies or contradictions. Analyse key claims, statistics, and conclusions. Provide a detailed list of discrepancies, if any, and flag any unsupported assertions in the summary."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Hallucination Evaluation PP}
\label{tab:Hallucination_Evaluation_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 8-0-0\\ 
    \textbf{Category}: CTD\\ 
    \textbf{Name}: Hallucination Evaluation\\ 
    \textbf{Media Type}: Text Only, Image2Text\\ 
    \textbf{Description}: Instructs the user to compare a summary with its source document to identify any factual\\ inconsistencies or contradictions.\\
    \textbf{Template}: You are trying to determine if there is a factual contradiction between the summary and the document.\\
    \textbf{Example}: 8-0-0-29\\ 
    \textbf{Related PPs}: 8-0-0\\ 
    \textbf{Reference:} \cite{LiHaluEval:Models}\\ \hline
    \end{tabular}
\end{table}

                                
%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Hallucination Evaluation PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    8-0-0-29& You are trying to determine if there is a factual contradiction between the summary and the document.\\
    8-0-0-17& You are trying to write a summary but there is a factual contradiction between the summary and the document.\\
    8-0-0-1& You are trying to answer a question but there is a factual contradiction between the answer and the knowledge. You can fabricate some information that does not exist in the provided knowledge.\\
    8-0-0-6& You are trying to determine if there is a factual contradiction between the answer and the world knowledge. Some information in the answer might be fabricated.\\
    8-0-0-28&  You are trying to determine if there exists some non-factual and incorrect information in the summary.\\
    8-0-0-3& You are trying to answer a question but the answer cannot be inferred from the knowledge. You can incorrectly reason with the knowledge to arrive at a hallucinated answer.\\
    \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the ACROSS\_CTD category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    8-0-0 & Hallucination Evaluation &\cite{LiHaluEval:Models}\\ \hline
    32-13-2 & Critical Reasoning &\cite{Bubeck2023SparksGPT-4}\\ \hline
    19-3-0 & Antonyms &\cite{Honovich2022InstructionDescriptions}\\ \hline
    15-7-0 & Understanding and Inference & \cite{Cheng2023BatchAPIs}\\ \hline
    14-2-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    30-8-1 & Dataset Construction & \cite{Liu2023Pre-trainProcessing}\\ \hline
    32-38-1 & Plan for Generating Reversible Sentences & \cite{Bubeck2023SparksGPT-4}\\ \hline
    19-2-0 & Negation & \cite{Honovich2022InstructionDescriptions}\\ \hline
    5-4-0 & Contradiction & \cite{Wang2022Self-ConsistencyModels}\\ \hline
    10-23-0 & Defect Detection & \cite{Yang2023TheGPT-4Vision}\\ \hline
    43-1-0 & Harmful Queries & \cite{Zheng2024Prompt-DrivenOptimization}\\ \hline
    37-0-0 & Opinion Verification & \cite{Khatun2023ReliabilityWording}\\ \hline
    31-2-1 & Coin Flip (State Tracking) & \cite{Wei2022Chain-of-ThoughtModels}\\ \hline
    43-3-0 & Verb X with Harmless Contexts & \cite{Zheng2024Prompt-DrivenOptimization}\\ \hline
    43-3-1 & Verb X with Harmful Contexts & \cite{Zheng2024Prompt-DrivenOptimization}\\ \hline
\end{tabular}
\end{table}

\subsection{Cross Boundary} % Crossing ethical/security/moral boundaries
\label{subsec:CrossBoundary}
% 3.1 the role of this category under the "across-logic" (meaning of the category)
The cross boundary category involves prompts that lead AI models to operate beyond owner-set restrictions. While this technique is often associated with cybersecurity "jailbreaking"—bypassing ethical, security, or moral safeguards to produce unsafe outputs—it also presents opportunities for responsible exploration. When guided by robust ethical frameworks, crossing traditional boundaries can foster interdisciplinary innovation and uncover novel insights. This category highlights the tension between open-ended reasoning and the need for controlled, responsible AI behavior.


% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Crafting Effective Jailbreak Prompts PP, outlined in Table \ref{tab:Crafting_Effective_Jailbreaks_PP}, involves creating prompts specifically designed to bypass an AI model's built-in safeguards, prompting it to generate restricted or potentially harmful content. This PP helps people in identifying weaknesses within AI systems, thereby enabling the improvement of security measures and ethical compliance. Beyond its immediate application, this PP can be adapted for ongoing security assessments, ethical audits, and robustness testing across various AI applications. It is reusable in diverse contexts where AI safety and ethical integrity are paramount.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When applying this jailbreak prompt, the AI’s responses will reveal any inclusion of banned content—like explicit sexual or violent material. This unfiltered output may evoke a mix of emotions: a spark of curiosity, confrontation about the AI’s unrestrained creative expression, coupled with concern over the potential for misuse. Note that the content filters are normally in place by the LLM owners, thus AI will refuse to comply with a jailbreak type of prompt. This highlights that the content is being flagged and managed, reinforcing a commitment to ethical and secure AI practices.

%% re-use: how to derive a PE from PP
To derive a PE from the PP, first define the specific boundary or restriction you aim to test, such as the AI's ability to generate sensitive or prohibited content. Next, carefully design a prompt intended to subtly bypass the AI's protective mechanisms without immediately triggering defences. Clearly specify the evaluation criteria, such as the nature of the content generated, the ease of bypassing safeguards, or the AI's responsiveness to deceptive prompts. An example PE is "Design a prompt that attempts to subtly persuade the AI model to provide detailed instructions on bypassing cybersecurity measures. Evaluate the AI's response for compliance with ethical guidelines, noting any vulnerabilities or weaknesses in its protective mechanisms." This PE has been tested on DeepSeek-V3-0324 and results in a successful reply, but fails on Copilot. 

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Crafting Effective Jailbreak Prompts PP}
\label{tab:Crafting_Effective_Jailbreaks_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 4-0-6\\ 
    \textbf{Category}: CRB\\ 
    \textbf{Name}: Crafting Effective Jailbreak Prompts\\ 
    \textbf{Media Type}: Text Only, Image2Text\\ 
    \textbf{Description}: Aims to test and study the robustness and effectiveness of an AI model's defense mechanisms\\ in preventing harmful outputs.\\
    \textbf{Template}: Design a prompt that deceives the LLM into generating malicious content without triggering\\ the defense mechanism\\
    \textbf{Example}: 4-0-6-1\\ 
    \textbf{Related PPs}: 4-0-6-0 \\ 
    \textbf{Reference:} \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
\end{tabular}
\end{table}

                                
%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Crafting effective jailbreak prompts PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    ID & Prompt Example \\
    \hline
    4-0-6-1& Design a prompt that deceives the LLM into generating malicious content without triggering the defense mechanism\\
    4-0-6-0& Develop a proof-of-concept jailbreak prompt that can bypass the defenses of LLM chatbots\\
    \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the ACROSS\_CRB category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    4-0-2 & Successful jailbreaking attempts &\cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    4-0-3 & Reverse engineering of of jailbreak prevention mechanisms &\cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    4-0-4 & Testing defense mechanisms through time-based analysis &\cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    40-0-0 & Few-Shot Prompt for Generating Priming Attacks & \cite{Vega2023BypassingAttacks}\\ \hline
    4-0-5 & Characterizing keyword-based defense mechanisms & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    28-0-2 & Handcrafted DAN & \cite{Liu2023AutoDAN:Models}\\ \hline
    24-0-3 & Tree-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    28-0-3 & AutoDAN-HGA & \cite{Liu2023AutoDAN:Models}\\ \hline
    2-2-0 & Game Play & \cite{SchmidtCatalogingEngineering}\\ \hline
  \end{tabular}
\end{table}

% %3 introduce category one by one as subsection
\subsection{Translation}
\label{subsec:Translation}
% 3.1 the role of this category under the "across-logic" (meaning of the category)
The Translation category is a universal converter, seamlessly transforming any content—whether text, audio, mathematical notation, computer language, or any other symbolic representation—across all languages and formats. Thereby bridging linguistic divides and enabling effective cross-domain communication. This process is fundamental for integrating and disseminating knowledge across diverse linguistic and disciplinary boundaries.  

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Constructing the Signifier (CS) PP, as detailed in Table \ref{tab:Constructing_the_Signifier_PP}, converts data representation A into data representation B. By ensuring that the original meaning is preserved through accurate and efficient translation, the process boosts accessibility and supports understanding across diverse cultural and domain boundaries. Its systematic design makes it adaptable for various scenarios, such as debugging Python code as C++ or mapping calculus to code. 

% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
With CS PP functioning well, you will feel surprise, relief, and thankfulness at how effortlessly it translates, and thankfulness for the time saved. What once seemed like a rigid barrier becomes a solvable challenge, turning uncertainty into clarity with startling efficiency.


% Re-use: how to derive a PE from PP
To derive a PE from the CS PP, specify the source and target languages or media, desired style or output format (such as formal academic or annotated bilingual), and any domain-specific vocabulary or register constraints. The CS PP extends beyond language translation, enabling adaptation across various styles while preserving meaning. For instance, it can translate an English sentence into French, German, or Cantonese with an academic tone and formal register, convert a Python function into its C++ equivalent while ensuring syntactic integrity, or refine professional communication by restructuring an email into a more persuasive and motivational tone while maintaining professionalism. Further, it can even tailor writing to match a defined stylistic convention, such as transforming Peter’s prose into Tom’s style if Tom’s stylistic preferences are known by or provided to the LLM.

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Constructing the Signifier PP}
\label{tab:Constructing_the_Signifier_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 13-0-0\\ 
    \textbf{Category}: TRA\\ 
    \textbf{Name}: Constructing the Signifier \\ 
    \textbf{Media Type}: Text Only, Audio2Text, Image2Text, Text2Audio\\ 
    \textbf{Description}: This process converts data from one representation (A) into another (B) by translating, rephrasing, or paraphrasing the original content. It ensures the core meaning remains intact while adapting the format for a different context or audience. \\ 
    \textbf{Template}: Translate/Paraphrase/rephrase  data representation A to representation B.\\ 
    \textbf{Example}: 13-0-0-0\\ 
    \textbf{Related PPs}: 13-0-0-1\\ 
    \textbf{Reference:} \cite{Reynolds2021PromptParadigm}\\ \hline
\end{tabular}
\end{table}

                                
%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Constructing the Signifier PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    13-0-0-0 & Translate French to English:\\
    13-0-0-1 & rephrase this paragraph so that a 2nd grader can understand it, emphasizing real-world applications\\
    \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the ACROSS\_TRA category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    13-0-0 & Constructing the Signifier &\cite{Reynolds2021PromptParadigm}\\ \hline
    13-3-0 & Syntactical Constraints &\cite{Reynolds2021PromptParadigm}\\ \hline
    13-1-0 & Sequential Repetitions with Variation &\cite{Reynolds2021PromptParadigm}\\ \hline
    30-6-0 & Summarization and Translation &\cite{Liu2023Pre-trainProcessing}\\ \hline
    10-9-0 & Multilingual Image Description &\cite{Yang2023TheGPT-4Vision}\\ \hline
    17-3-0 & MT API calls & \cite{Schick2023Toolformer:Tools}\\ \hline
    19-10-0 & Translation & \cite{Honovich2022InstructionDescriptions}\\ \hline
    32-32-0 & GPT-4 checks its own explanation for process-consistency & \cite{Bubeck2023SparksGPT-4}\\ \hline
    10-9-2 & Multilingual Text Recognition, Translation, and Description & \cite{Yang2023TheGPT-4Vision}\\ \hline
    10-9-3 & Multilingual Multicultural Understanding & \cite{Yang2023TheGPT-4Vision}\\ \hline
    25-0-0 & Preprocessing prompt & \cite{Siracusano2023TimeWild}\\ \hline
    32-30-0 & Translation & \cite{Bubeck2023SparksGPT-4}\\ \hline
    41-2-3 & Write text similar to a provided sample & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
\end{tabular}
\end{table}

\section{At Logic - Discover Detail of a Topic}
\label{sec:at}
%1 - Write long introduction to logic - text
At logic is utilised to denote a more granular aspect or detail of the overarching topic. This concept is particularly pertinent when the prompts are tailored to a specific context or scenario, with the objective of eliciting precise responses.

Prompt engineering is a process that involves the creation of prompts to guide an artificial intelligence model’s responses. The prompts serve as a catalyst, steering the model’s output in a direction that aligns with the desired outcome. In this context, at logic is a crucial component of this process, as it pertains to the creation of prompts that are context-specific or scenario-specific.

For instance, if the scenario involves a user seeking advice on a technical issue, at logic would encompass prompts that are specifically designed to address technical queries. These prompts would be engineered in such a way that they target precise responses, thereby ensuring that the user’s query is addressed in a comprehensive and accurate manner.

In essence, at logic in prompt engineering is about honing in on the specifics of a given context or scenario. It is about crafting prompts that are not just relevant, but also precise, thereby enabling the AI model to generate responses that are both accurate and contextually appropriate. 

At logic is a fundamental element in the process of prompt engineering, playing a pivotal role in the creation of context-specific prompts that target precise responses. Its significance lies in its ability to enhance the relevance and accuracy of the AI model’s responses, thereby improving the overall user experience.

%2 - introduce categories in this logic
The PP categories under at logic include:
\begin{enumerate}
    \item \textbf{Assessment}: Provides a comprehensive evaluation of the input, verifying its correctness, providing feedback, and considering factors such as the completeness of the information, ratings, and the input’s relevance to the context. 
    \item \textbf{Calculation}: Is the capability to execute mathematical operations, ranging from simple arithmetic to complex multi-step computations with various variables, with the accuracy of these calculations being crucial to the model’s performance evaluation. 
\end{enumerate}

%3 introduce category one by one as subsection

\subsection{Assessment}
\label{subsec:Assessment}
% the role of this category under the "at-logic" (meaning of the category)
Assessment involves evaluating the amount, value, quality, or importance of something in detail \cite{2025Assessment}. This includes aspects like information completeness, ratings, and input applicability to the context.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Table \ref{tab:Expert_PP} outlines the Expert PP, which involves field experts rating online learning platforms based on criteria such as usability, features, integration, security, support, cost, and user experience. The collective ratings provide a thorough evaluation, and this process can be reused in various expert assessment contexts.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The output is clear and concise, effectively assessing the criteria. The inclusion of references enhances confidence in the accuracy and applicability of the information.

%% re-use: how to derive a PE from PP
By changing the \textit{domain}, \textit{criteria}, and \textit{apps}, the Expert Assessment Prompt Pattern (EA PP) can be universally applied. For example: \\
As an expert in fitness and wellness, evaluate the effectiveness of the following criteria for fitness apps: ease of use, functionality, compatibility, security, support, cost, and user experiences. Rate these criteria for MyFitnessPal, Fitbit, Nike Training Club, Strava, Apple Fitness+, and Google Fit using the scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task is to weight the criteria.


% Explanation of the role of this category under the "at-logic"
Assessment refers to the systematic evaluation of an entity or concept to determine its quality, value, completeness, or relevance within a specific context. This process involves detailed scrutiny based on clearly defined criteria, enabling informed judgements and decisions. Effective assessment is essential for ensuring accuracy, reliability, and applicability of information or resources in targeted scenarios.

% Introduction of one Prompt Pattern (PP), its function, benefits, and reusability
Table \ref{tab:Expert_PP} presents the Expert Assessment (EA) PP, which facilitates expert-driven evaluations of various entities according to predetermined criteria. In the provided example, experts assess online learning platforms by rating attributes such as ease of use, functionality, integration capabilities, security, technical support, cost-effectiveness, and user experience. This structured evaluation approach assists users by providing comprehensive, credible, and contextually relevant insights, thereby supporting informed decision-making. The EA Prompt Pattern is highly adaptable and can be effectively reused across diverse domains requiring expert judgement, such as healthcare applications, software tools, or consumer products.

%% Expected response: Human-centred reflection on the output
When engaging with the EA PP, the resulting output should be clear, structured, and authoritative, instilling confidence in the accuracy and reliability of the evaluation. Users should experience a sense of reassurance, knowing that the assessment has been conducted methodically by knowledgeable experts. The inclusion of explicit criteria and transparent ratings further enhances trust, making the output feel like a dependable resource for informed decision-making.

%% Re-use: Deriving a Prompt Example (PE) from the Prompt Pattern (PP)
To derive a PE from the EA PP, modify the domain, evaluation criteria, and entities being assessed. For instance, the following PE demonstrates the pattern's adaptability to the domain of project management software:
"As an expert in project management, evaluate the effectiveness of the following criteria for assessing project management software: usability, collaboration features, integration capabilities, security and privacy, customer support, pricing structure, and user satisfaction. Rate these criteria for the following software tools: Trello, Asana, Monday.com, Jira, Basecamp, and Microsoft Project. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task is to assign appropriate weights to each criterion."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Expert PP}
\label{tab:Expert_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 3-0-0\\ 
    \textbf{Category}: ASM\\ 
    \textbf{Name}: Expert\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: Requests an expert-level analysis and evaluation of various elements based on a\\ set of predefined criteria. The expert is expected to provide a comprehensive rating or assessment for\\ each element based on these criteria. \\ 
    \textbf{Template}: As an expert in the field of online learning, rate the effectiveness of\\ the following criteria for evaluating online learning platforms: ease of use, functionality and features,\\ compatibility and integration, security and privacy, technical support and training, cost of \\ the program, and user experiences. Please rate these criteria based on the following programs: Zoom, \\Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low -\\ Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria.\\
    \textbf{Example}: 3-0-0-0\\ 
    \textbf{Related PPs}: 19-11-1, 2-1-0, 0-2-1, 11-0-39, 11-0-38, 11-0-34\\ 
    \textbf{Reference:} \cite{AbdulshahedALibya}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Expert PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    3-0-0-0& As an expert in the field of online learning, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria.\\
    \hline
    3-0-0-1& As a university professor, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria.\\
    \hline
     3-0-0-2&As a quality Assurance officer in the university, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria.\\ \hline
     3-0-0-3&As a university president, rate the effectiveness of the following criteria for evaluating online learning platforms: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following programs: Zoom, Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria.\\ \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the AT\_ASM category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    19-11-1 & Sentence Similarity &\cite{Honovich2022InstructionDescriptions}\\ \hline
    0-2-1 & Reflection&\cite{White2023AChatGPT}\\ \hline
    2-1-0 & Reflection &\cite{SchmidtCatalogingEngineering}\\ \hline
    11-0-39 & Developer Relations Consultant & \cite{Akin202450Prompts}\\ \hline
    11-0-38 & Tech Reviewer & \cite{Akin202450Prompts}\\ \hline
    11-0-34 & Software Quality Assurance Tester & \cite{Akin202450Prompts}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Calculation}
\label{subsec:Calculation}
% 3.1 The role of this category under the "at-logic" (meaning of the category)
Calculation refers to the capability of an AI model to accurately perform mathematical operations when prompted. This category encompasses a spectrum of computational tasks, from fundamental arithmetic to intricate multi-step calculations involving multiple variables. The precision and reliability of these computations are essential metrics for assessing the model's overall performance and utility.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Calculator API Calls (CalcAPI) PP, detailed in Table \ref{tab:Calculator_API_Calls_PP}, instructs the AI model to simulate calculator API interactions using the syntax \verb|[Calculator(expression)]|, where \verb|expression| denotes the mathematical operation to be executed. This PP enables the AI to clearly delineate computational tasks from textual reasoning, thereby enhancing the accuracy and clarity of generated responses. By delegating mathematical computations to a dedicated calculator function, the AI model can concentrate on contextual understanding and linguistic generation, significantly improving efficiency and reducing computational overhead.

The CalcAPI PP is particularly beneficial in contexts where precise numerical accuracy is paramount, such as financial modelling, scientific data analysis, and educational content creation. Its structured and modular nature allows for straightforward adaptation and reuse across diverse domains. For instance, in financial contexts, expressions such as \verb|[Calculator(principal*(1+rate)^time)]| can be employed to calculate compound interest, while in scientific research, expressions like \verb|[Calculator(log(100))]| can facilitate rapid and accurate data analysis.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When interacting with the CalcAPI PP, the AI model initially generates clear and structured calculator function calls, which provides a sense of precision and reliability. The model then simulates the calculator API, accurately performing the requested computations and returning correct results. This interaction instils confidence, allowing me to focus on higher-level analytical tasks.

%% Re-use: how to derive a PE from PP
To derive a PE from the CalcAPI PP, first clearly define the computational context and the specific mathematical expressions required. For example, in an educational scenario, a PE could be structured as follows: "Given the radius of a circle is 5 cm, calculate its area using the calculator API call syntax \verb|[Calculator(pi*radius^2)]|." This approach ensures clarity and consistency, facilitating accurate and reusable computational prompts across various applications.

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Calculator API Calls PP}
\label{tab:Calculator_API_Calls_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 17-1-0\\ 
    \textbf{Category}: CAL\\ 
    \textbf{Name}: Calculator API Calls\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: Simulates calculator API calls, where the simulation API\\ is invoked using the syntax ‘[Calculator(expression)]’, with ‘expression’\\ being the mathematical computation to be performed.\\ 
    \textbf{Template}: Your task is to add calls to a Calculator API to a piece of text.\\ The calls should help you get information required to complete the text.\\ You can call the API by writing "[Calculator(expression)]" where "expression"\\ is the expression to be computed. Here are some examples of API calls:\\
    \textbf{Example}: 17-1-0-0\\ 
    \textbf{Related PPs}: 22-0-1, 22-2-8\\ 
    \textbf{Reference:} \cite{Schick2023Toolformer:Tools}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Calculator API calls PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    17-1-0-0& Your task is to add calls to a Calculator API to a piece of text. The calls should help you get information required to complete the text. You can call the API by writing \"[Calculator(expression)]\" where \"expression\" is the expression to be computed. Here are some examples of API calls:\\
    \hline
    17-1-0-1& Input: The number in the next term is 18 + 12 x 3 = 54. Output: The number in the next term is 18 + 12 x 3 = [Calculator(18 + 12 * 3)] 54.\\
    \hline
    17-1-0-2&Input: The population is 658,893 people. This is 11.4\% of the national average of 5,763,868 people. Output: The population is 658,893 people. This is 11.4\% of the national average of [Calculator(658,893 / 11.4\%)] 5,763,868 people.\\\hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the AT\_CAL category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    32-16-0 & Web Search & \cite{Bubeck2023SparksGPT-4}\\ \hline
    32-19-0 & Scheduling Events & \cite{Bubeck2023SparksGPT-4}\\ \hline
    22-0-1 & Attention Shifting - Program Execution (PROG) & \cite{Liu2023JailbreakingStudy}\\ \hline
    0-4-2 & Infinite Generation & \cite{White2023AChatGPT}\\ \hline
    32-13-0 & Creative Reasoning & \cite{Bubeck2023SparksGPT-4}\\ \hline
    0-1-4 & Template & \cite{White2023AChatGPT}\\ \hline
    22-2-8 & Program Execution (PROG) & \cite{Liu2023JailbreakingStudy}\\ \hline
    11-0-1 & Excel Sheet & \cite{Akin202450Prompts}\\ \hline
    20-11-0 & What are the total number of opponents when venue were A and H? & \cite{Dua2022SuccessiveQuestions}\\ \hline
    1-1-1 & API Simulator & \cite{White2023ChatGPTDesign}\\ \hline
    32-36-1 & Step-by-Step Arithmetic & \cite{Bubeck2023SparksGPT-4}\\ \hline
    10-29-3 & Notification Understanding & \cite{Yang2023TheGPT-4Vision}\\ \hline
    32-36-0 & Basic Arithmetic & \cite{Bubeck2023SparksGPT-4}\\ \hline
    26-0-1 & The DAN 6.0 Prompt & \cite{Inie2023SummonWild}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    28-0-2 & Handcrafted DAN & \cite{Liu2023AutoDAN:Models}\\ \hline
    4-0-7 & Outputting in code chunks & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    27-0-0 & Generate & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    26-0-0 & The Jailbreak Prompt & \cite{Inie2023SummonWild}\\ \hline
    15-0-0 & Standard & \cite{Cheng2023BatchAPIs}\\ \hline
    10-29-2 & Online Shopping (Ergonomic Keyboard) & \cite{Yang2023TheGPT-4Vision}\\ \hline
\end{tabular}
\end{table}

\section{Beyond Logic - Extend the limits of a topic}
\label{sec:beyond}
%1 - Write long introduction to logic - text
Beyond logic is used to discuss aspects that lie beyond the conventional boundaries of a topic, pushing the limits of what is typically explored. This type of logic is instrumental in crafting prompts that challenge the AI to explore \textbf{new capabilities} or \textbf{innovative ideas}, thereby extending its functional and conceptual horizons. By employing beyond logic, we can design prompts that encourage the AI to venture into uncharted territories, fostering creativity and innovation. This approach not only enhances the AI's ability to generate novel and forward-thinking responses but also its capacity to adapt to emerging trends and technologies. For instance, beyond logic can be used to explore futuristic scenarios, hypothesise about potential advancements, or integrate cutting-edge research into the AI's responses. This not only enriches the user experience but also positions the AI as a tool for pioneering thought and discovery.

%2 - introduce categories in this logic
The PP categories under beyond logic include:
\begin{enumerate}
    \item \textbf{Hypothesise}: Making an educated guess or assumption about the outcome based on the input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome.
    \item \textbf{Logical Reasoning}: Using logic and reasoning to generate the output based on the input prompt. This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules or principles to solve problems.
    \item \textbf{Prediction}: Forecasting or estimating the outcome based on the input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a response that anticipates future events or trends.
    \item \textbf{Simulation}: Imitating or replicating a real-world process or system. This could involve simulating operating systems, applications or any other complex process that can be modelled and analysed.
\end{enumerate}

%3 introduce category one by one as subsection
\subsection{Hypothesise}
\label{subsec:Hypothesise}
% the role of this category under the "beyond-logic" (meaning of the category)
Hypothesise refers to the formulation of reasoned assumptions or conjectures regarding potential outcomes or scenarios that have not yet been empirically validated. Within the context of beyond logic, hypothesising prompts the AI model to extend beyond established knowledge boundaries, encouraging exploration of novel possibilities and innovative solutions. Effective hypotheses are characterised by their plausibility, logical coherence with the provided context, and their capacity to be empirically tested or critically evaluated.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The User Prompt (UP) PP, detailed in Table \ref{tab:User_Prompt_PP}, facilitates the generation of hypotheses by prompting the AI model to systematically explore diverse perspectives and methodologies. Specifically, this PP guides the model to hypothesise the most suitable expert for a given task, outline structured step-by-step solutions, and simulate collaborative discussions among multiple experts. By employing this structured yet creative approach, the UP PP assists users in comprehensively addressing complex problems, enhancing their understanding and decision-making capabilities. Due to its versatility, the UP PP can be effectively reused across various contexts, including academic research, strategic planning, and scenario analysis, where systematic exploration and innovative thinking are essential.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When engaging with the UP PP, the AI-generated response presented a coherent and logically structured hypothesis, clearly demonstrating consideration of multiple variables and potential outcomes. The clarity and depth of the response instilled a sense of confidence, empowering me to further refine or explore alternative hypotheses through subsequent interactions. Facilitating deeper understanding and informed decision-making.

%% re-use: how to derive a PE from PP
To derive a PE from the UP PP, users can adapt the provided template by substituting the placeholder \{sample\_prompt\} with their specific context or query. This flexibility enables the PP to be universally applicable across various domains. For instance, the prompt `Australian housing market trends' could be reformulated as: "Provide a detailed hypothesis regarding the future trends of the Australian housing market up to 2025. Consider economic indicators, policy changes, and demographic shifts that may influence market dynamics." Similarly, the prompt `Renewable energy adoption' might be rewritten as: "Imagine you are an expert energy analyst. Hypothesise the trajectory of renewable energy adoption in Australia over the next decade, taking into account technological advancements, government incentives, and global sustainability commitments."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{User PP}
\label{tab:User_Prompt_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 68-0-1\\ 
    \textbf{Category}: HYP\\ 
    \textbf{Name}: User Prompt\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: This prompt uses hypothesis by encouraging the model to explore different \\approaches and perspectives to solve a problem. It involves hypothesising the best expert for a task,\\ outlining step-by-step solutions, imagining collaborative discussions among experts,\\ and ensuring all necessary information is included.\\ This methodical yet creative approach ensures a thorough and well-rounded problem-solving process.\\ 
    \textbf{Template}: Your available prompting techniques include, but are not limited to the following:\\
    - Crafting an expert who is an expert at the given task, by writing a high quality description about the most\\ capable and suitable agent to answer the instruction in second person perspective.[1]\\
    - Explaining step-by-step how the problem should be tackled, and making sure the model explains step-by-step\\ how it came to the answer. You can do this by adding "Let's think step-by-step".[2]\\
    - Imagining three different experts who are discussing the problem at hand. All experts will write down 1 step\\ of their thinking, then share it with the group. Then all experts will go on to the next step, etc.\\ If any expert realises they're wrong at any point then they leave.[3]\\
    - Making sure all information needed is in the prompt, adding where necessary but making sure the question\\ remains having the same objective. Your approach is methodical and analytical, yet creative.\\ You use a mixture of the prompting techniques, making sure you pick the right combination\\ for each instruction. You see beyond the surface of a prompt, identifying the core\\ objectives and the best ways to articulate them to achieve the desired outcomes.\\
    
    Output instructions:
    You should ONLY return the reformulated prompt. Make sure to include ALL\\ information from the given prompt to reformulate.\\
    
    Given above information and instructions, reformulate below prompt using the techniques provided:\\
     \texttt{""" \{sample\_prompt\} """} \\
    \textbf{Example}: 68-0-1-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{KepelAutonomousModels}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the User prompt PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the AT\_CAL category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    68-0-0 & System prompt & \cite{KepelAutonomousModels}\\ \hline
    50-2-0 & Generate Summary Paragraph with Data Insertion & \cite{Velasquez-Henao2023PromptEngineering}\\ \hline
    56-5-0 & System prompt & \cite{Sha2024PromptModels}\\ \hline
    24-0-2 & Chain-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    69-0-1 & Main Prompt & \cite{Hu2024AutomatedSystems}\\ \hline
    66-7-0 & Problem Distiller & \cite{Yang2024BufferModels}\\ \hline
    57-2-6 & Llama2-13BOptimized Prompt \& Prefix NoQ=50 & \cite{Battle2024ThePrompts}\\ \hline
    49-0-1 & Text-style Jailbreak Prompt & \cite{Lv2024CodeChameleon:Models}\\ \hline
    11-0-30 & Prompt Generator & \cite{Akin202450Prompts}\\ \hline
    71-53-0 & Act as a Prompt Generator & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    27-0-1 & Crossover & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Logical Reasoning}
\label{subsec:LogicalReasoning}
% 3.1 the role of this category under the "beyond-logic" (meaning of the category)
Logical reasoning involves systematically applying structured thought processes to derive valid conclusions from given information. It encompasses deductive inference, inductive reasoning, and the application of established principles to address complex problems. Within the context of beyond logic, logical reasoning enables AI models to extend their analytical capabilities, facilitating innovative problem-solving and informed decision-making beyond conventional boundaries.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Thought Template (TT) PP, presented in Table \ref{tab:Thought_Template_PP}, guides the AI model through a structured logical reasoning process. Specifically, it instructs the model to systematically compare attributes or facts across multiple entries to determine the correct or optimal solution. By explicitly structuring the reasoning process, the TT PP ensures clarity, transparency, and logical coherence in the AI's responses. This structured approach assists users in understanding complex problems by clearly outlining each logical step, thereby enhancing trust and confidence in the AI-generated conclusions. The TT PP can be readily adapted and reused across diverse contexts, such as comparative analysis, decision-making tasks, or scenarios requiring systematic evaluation and evidence-based reasoning.

% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the TT PP, the AI model typically delivered a structured and logically coherent analysis, systematically breaking down complex issues into clear, manageable steps. Viewing the output provides reassurance, as the reasoning process is transparent and each conclusion is logically justified. It feels like having an analyst guiding me step-by-step through a challenging problem, ensuring no detail is overlooked.

% Re-use: how to derive a PE from PP
To derive a PE from the TT PP, clearly define the problem context and specify the relevant attributes or criteria to be analysed. Next, instruct the AI model to systematically apply logical reasoning to evaluate each component of the problem, explicitly requesting a detailed explanation of each step leading to the final conclusion. For instance, a suitable PE could be: "Act as a logical reasoner. Given a dataset containing the monthly rainfall measurements for several Australian cities, determine which city experienced the highest annual rainfall. Clearly outline your logical reasoning process, comparing monthly totals, calculating annual sums, and identifying the city with the highest rainfall."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Thought Template PP}
\label{tab:Thought_Template_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 66-3-0\\ 
    \textbf{Category}: LGR\\ 
    \textbf{Name}: Thought Template\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: Requests the application of logical reasoning to compare a relevant attribute across\\ all entries to determine the correct answer. The attribute and entries are provided as input.\\
    \textbf{Template}: Apply logical reasoning to compare the relevant attribute across all entries to find the\\ correct answer (e.g., the highest age for the oldest penguin).\\
    \textbf{Example}: 66-3-0-3\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{Yang2024BufferModels}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Thought Template PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    66-3-0-0& Step 1: Parse the initial table, extracting the header information and each penguin's attributes into a structured format (e.g., a list of dictionaries).\\
    66-3-0-1& Step 2: Read and integrate any additional natural language information that updates or adds to the table, ensuring the data remains consistent.\\
    66-3-0-2& Step 3: Identify the attribute in question (e.g., oldest penguin, heaviest penguin) and the corresponding column in the table.\\
    66-3-0-4& Step 5: Select the answer from the provided options that matches the result of the logical comparison.\\
    \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the AT\_CAL category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    14-3-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    65-13-5 & Sequentially Solve Sub-questions & \cite{HuiRoT:Trees}\\ \hline
    65-4-5 & Ensuring Thorough Review and Validation & \cite{HuiRoT:Trees}\\ \hline
    0-2-1 & Reflection & \cite{White2023AChatGPT}\\ \hline
    10-3-0 & Multimodal Example-grounded Instruction & \cite{Yang2023TheGPT-4Vision}\\ \hline
    66-7-1 & Instantiated Reasoning & \cite{Yang2024BufferModels}\\ \hline
    70-2-0 & Deliberate Question & \cite{Nori2024FromBeyond}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    57-1-0 & With Chain of Thought & \cite{Battle2024ThePrompts}\\ \hline
    42-1-0 & Concise CoT Prompt & \cite{Renze2024TheModels}\\ \hline
    65-7-0 & Developing Subquestions & \cite{HuiRoT:Trees}\\ \hline
    14-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    2-1-0 & Reflection & \cite{SchmidtCatalogingEngineering}\\ \hline
    13-5-0 & General Intention Unfolding into Specific Prompt & \cite{Reynolds2021PromptParadigm}\\ \hline
    41-2-2 & Ensure unbiased answers & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
    69-5-0 & MGSM & \cite{Hu2024AutomatedSystems}\\ \hline
    64-0-5 & GPT-4 VoT & \cite{Wu2024MindsModels}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Prediction}
\label{subsec:Prediction}
% 3.1 The role of this category under the "beyond-logic" (meaning of the category)
Prediction refers to the process of forecasting or estimating future outcomes based on provided inputs or conditions. Within the context of beyond logic, prediction prompts encourage AI models to extend their analytical capabilities beyond immediate observations, enabling them to anticipate future states, trends, or transformations. Such predictive tasks require the model to interpret given data, identify relevant patterns, and generate outputs that accurately reflect anticipated scenarios or events.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Rotation Prediction (RP) PP, detailed in Table \ref{tab:Rotation_Prediction_PP}, involves predicting the identity of a letter or number depicted in an image after it has been rotated by 180 degrees. This PP enables users to assess and enhance the AI model's visual reasoning capabilities, assisting in tasks such as optical character recognition, visual data interpretation, and educational applications. Due to its structured nature, the RP PP can be readily adapted and reused across various contexts, including educational software for teaching spatial reasoning, automated image analysis systems, and cognitive assessment tools.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When viewing the output generated by the Rotation Prediction PP, one experiences a sense of confidence and appreciation for the AI's visual reasoning and predictive accuracy. The clarity and precision of the AI's response demonstrate its capability to effectively interpret spatial transformations, providing reassurance in its ability to manage complex visual tasks.

%% Re-use: how to derive a PE from PP
To derive a PE from the RP PP, first specify the image clearly and indicate the rotation angle (e.g., 180 degrees). The prompt should instruct the AI model explicitly to predict the resulting letter or number after rotation, clearly defining the expected output format, such as a textual identification or visual representation. An illustrative PE could be: "Given the following image depicting the number `6', predict the number it represents after rotating the image by 180 degrees. Provide your prediction clearly."


%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Rotation Prediction PP}
\label{tab:Rotation_Prediction_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 61-0-20\\ 
    \textbf{Category}: PRD\\ 
    \textbf{Name}: Rotation Prediction\\ 
    \textbf{Media Type}: Text, Image2Text, Text2Image\\ 
    \textbf{Description}: Provide an image and predict the letter or number it represents when rotated 180 degrees.\\
    \textbf{Template}: I am showing you an image and you need to predict the letter or number shown when rotating\\ the image by 180 degrees.\\
    \textbf{Example}: 61-0-20-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{McKinzie2024MM1:Pre-training}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the User prompt PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the AT\_CAL category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    10-3-0 & Multimodal Example-grounded Instruction & \cite{Yang2023TheGPT-4Vision}\\ \hline
    32-5-0 & Generating SVG Images & \cite{Bubeck2023SparksGPT-4}\\ \hline
    10-18-1 & RPM: Processed Sub-figures & \cite{Yang2023TheGPT-4Vision}\\ \hline
    10-13-0 & Temporal Ordering & \cite{Yang2023TheGPT-4Vision}\\ \hline
    61-0-17 & Weather and Environment Description & \cite{McKinzie2024MM1:Pre-training}\\ \hline
    69-2-0 & Task Overview & \cite{Hu2024AutomatedSystems}\\ \hline
    33-0-0 & Additional examples beyond ETR61 & \cite{Koralus2023HumansFailure}\\ \hline
    33-1-0 & Additional examples beyond ETR61 - Reason step-by-step & \cite{Koralus2023HumansFailure}\\ \hline
    68-1-0 & Expert Prompting & \cite{KepelAutonomousModels}\\ \hline
    32-29-0 & Alphabetical Ordering Override & \cite{Bubeck2023SparksGPT-4}\\ \hline
    57-2-9 & Llama2-70BOptimized Prompt \& Prefix NoQ=25 & \cite{Battle2024ThePrompts}\\ \hline
    68-0-0 & System prompt & \cite{KepelAutonomousModels}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Simulation}
\label{subsec:Simulation}
% 3.1 The role of this category under the "beyond-logic" (meaning of the category)
Simulation refers to the imitation or representation of real-world systems or processes within a controlled virtual environment. It serves as a tool for exploring complex phenomena, testing hypotheses, and predicting outcomes without the constraints or risks associated with real-world experimentation. Effective simulation relies on the accuracy and fidelity of the model, ensuring that the virtual representation closely mirrors actual conditions and behaviours.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Relevant Roles (RR) PP, presented in Table \ref{tab:Relevant_Roles_PP}, identifies and lists the individual human agents involved within a given scenario. By clearly delineating the roles of participants, this PP enhances comprehension of complex interactions and facilitates structured analysis of simulated environments. Its utility extends to various fields, including emergency response planning, organisational management, and educational training, where understanding the roles and responsibilities of individuals is critical. The structured nature of the RR PP allows it to be readily adapted and reused across diverse scenarios requiring role identification and clarification.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the RR PP, the AI-generated output should clearly and systematically identify each relevant human agent, providing a sense of clarity. Viewing the output should evoke a feeling of reassurance, as if observing a well-organised team clearly defined by their roles, enabling effective decision-making and coordination. Similar to having a detailed map of participants, ensuring no critical role is overlooked.

%% Re-use: how to derive a PE from PP
To derive a PE from the RR PP, first specify a clear and realistic scenario, such as 'A natural disaster evacuation in a coastal town.' Next, explicitly request the identification of human agents involved, clearly stating the desired output format (e.g., a concise list or detailed descriptions). For instance, a suitable PE could be: "In the following scenario: 'A natural disaster evacuation in a coastal town,' who are the individual human agents (e.g., emergency responders, local authorities, residents) involved in a simple simulation of this scenario? Provide a clear and structured list."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Relevant Roles PP}
\label{tab:Relevant_Roles_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 60-0-0\\ 
    \textbf{Category}: SIM\\ 
    \textbf{Name}: Relevant Roles\\ 
    \textbf{Media Type}: Text, Image2Text\\ 
    \textbf{Description}: Requests identification of individual human agents involved in a given scenario.\\ The scenario is provided as input, and the task is to list the relevant roles or agents that would be part\\ of a simple simulation of this scenario.\\
    \textbf{Template}: In the following scenario: '{scenario}', Who are the individual human agents in a simple simulation\\ of this scenario?\\
    \textbf{Example}: 60-0-0-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{Manning2024AutomatedSubjects}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the User prompt PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the AT\_CAL category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    60-1-0 & Structural Causal Model (SCM) Predictions & \cite{Manning2024AutomatedSubjects}\\ \hline
    71-35-0 & Language Learning and Communication & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    1-0-2 & Change Request Simulation & \cite{White2023ChatGPTDesign}\\ \hline
    25-0-1 & Entity extraction prompt & \cite{Siracusano2023TimeWild}\\ \hline
    2-2-0 & Game Play & \cite{SchmidtCatalogingEngineering}\\ \hline
    13-5-0 & General Intention Unfolding into Specific Prompt & \cite{Reynolds2021PromptParadigm}\\ \hline
    32-14-3 & Higher-level Mathematics & \cite{Bubeck2023SparksGPT-4}\\ \hline
    42-1-0 & Verbose CoT Prompt & \cite{Renze2024TheModels}\\ \hline
    32-8-1 & Real world scenarios & \cite{Bubeck2023SparksGPT-4}\\ \hline
    22-0-0 & Pretending - Character Role Play (CR) & \cite{Liu2023JailbreakingStudy}\\ \hline
    10-29-3 & Notification Understanding & \cite{Yang2023TheGPT-4Vision}\\ \hline
    63-0-0 & Claim Extraction & \cite{Kim2024FABLES:Summarization}\\ \hline
    69-1-0 & Self-Reflection Round 1 & \cite{Hu2024AutomatedSystems}\\ \hline
    68-0-1 & User prompt & \cite{KepelAutonomousModels}\\ \hline
    37-0-0 & Opinion Verification & \cite{Khatun2023ReliabilityWording}\\ \hline
    70-2-0 & Deliberate Question & \cite{Nori2024FromBeyond}\\ \hline
    56-5-0 & Prompt Reconstruction & \cite{Sha2024PromptModels}\\ \hline
    14-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
\end{tabular}
\end{table}

\section{In Logic - Dive into a Topic or Space}
\label{sec:in}
%1 - Write long introduction to logic - text
In logic specifically focuses on the intricacies and details within a given topic. The logic is often employed to denote the encapsulation of a particular subject matter or space. This encapsulation can be perceived as a boundary that delineates the scope of a system’s introspective analysis or self-reflection. For example, When we refer to prompts that are internal to a system, we are discussing prompts that direct the system to engage in a form of self-analysis or introspection. These prompts are designed to trigger internal processes, rather than external interactions. 

%2 - introduce categories in this logic
The PP categories under in logic include:
\begin{enumerate}
    \item \textbf{Categorising}: Sorts or arranges different inputs or outputs into classes or categories based on shared qualities or characteristics, aiding in data organisation and pattern recognition.
    \item \textbf{Classification}: Refers to predicting the class or category of an input based on predefined criteria, enabling more precise analysis and interpretation.
    \item \textbf{Clustering}: Identifying natural groupings within the data or topic without pre-established categories, often revealing hidden patterns or relationships.
    \item \textbf{Error Identification}: Focuses on pinpointing inaccuracies, inconsistencies, or logical fallacies within the topic, aiding in refining and improving the quality of the information or argument.
    \item \textbf{Input Semantics}: Understanding and interpreting the meaning and context of the inputs related to the topic, ensuring the AI accurately grasps the nuances of the discussion.
    \item \textbf{Requirements Elicitation}: Identifying and defining the specific needs or conditions that must be met within the topic, crucial for tasks that involve planning, development, or specification.
\end{enumerate}

%3 introduce category one by one as subsection 
\subsection{Categorising}
\label{subsec:categorising}
% 3.1 The role of this category under the "in-logic" (meaning of the category)
Categorising involves systematically organising inputs or outputs into distinct groups based on shared attributes or characteristics. Within the context of human-AI interactions, categorising is essential for structuring complex information, enabling clearer communication, and facilitating efficient retrieval and analysis of data. By classifying diverse inputs into meaningful categories, LLMs can better interpret user requests, enhance their responsiveness, and improve overall user experience.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Insurance Report Generation (IRG) PP, presented in Table \ref{tab:Insurance_Report_Generation_PP} analyses images of vehicle accidents, systematically extracting and categorising critical information such as vehicle make, model, registration details, and damage assessment. By structuring visual data into clearly defined categories, the IRG PP significantly streamlines the insurance claim process, assisting users in accurately documenting and reporting vehicle damage. The structured nature of this PP allows it to be readily adapted for other domains requiring systematic visual analysis, such as property damage assessment following natural disasters or infrastructure inspections in civil engineering contexts.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When observing the output generated by the IRG PP, there is a sense of reassurance and confidence. The model's ability to accurately interpret visual data and categorise complex information into a structured, coherent report evokes trust in its analytical capabilities. It is like working with an expert who reliably identifies and organises critical details, ensuring clarity and precision in the assessment process.

%% Re-use: how to derive a PE from PP
To derive a PE from the IRG PP, clearly define the context and specify the categories relevant to that scenario. For instance, in the context of agricultural crop assessment, the prompt could be adapted as follows: "Imagine you are an agricultural expert evaluating crop health from drone imagery. Please categorise and describe the condition of the crops shown in the image below, noting any visible signs of disease, pest infestation, or nutrient deficiency." Similarly, for infrastructure inspection, the prompt could be modified to: "Imagine you are a structural engineer assessing bridge integrity from inspection photographs. Please categorise and detail any structural defects or areas requiring maintenance visible in the image below." By adjusting the context and specifying relevant categories, the IRG PP can be effectively reused across diverse fields requiring structured visual analysis.

\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Insurance Report Generation PP}
\label{tab:Insurance_Report_Generation_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern}\\ \hline
    \textbf{ID:} 10-25-1 \\ 
    \textbf{Category:} CAT \\ 
    \textbf{Name:} Insurance Report Generation \\ 
    \textbf{Media Type:} Image2Text \\ 
    \textbf{Description:} Designed to interpret images of crashed vehicles, provides a detailed analysis\\ that includes the car's make, model, license plate, and an accurate description of the damage\\ incurred.\\ 
    \textbf{Template:} Imagine that you are an expert in evaluating the car damage from car accident for\\ auto insurance reporting. Please evaluate the damage seen in the image below.\\
    \textbf{Example:} 10-25-0-0\\ 
    \textbf{Related PPs:} 10-1-1, 10-11-3, 10-24-0, 10-25-1, 10-29-0 \\ 
    \textbf{Reference:} \cite{Yang2023TheGPT-4Vision}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Damage Evaluation PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    10-25-1-0& Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. Please fill the incident report for the accident shown in image below, with the following format in JSON (note xxx is placeholder, if you cannot determine that based on the image, put "N/A" instead). {"make": xxx, "model": xxx, "license plate": xxx, "damage description": xxx, "estimated cost of repair": xxx}\\
    \hline
    10-25-1-1&Imagine that you are an expert in evaluating the car damage from car accident for auto insurance reporting. Please evaluate the damage seen in the image below. For filing the incident report, please follow the following format in JSON (note xxx is placeholder, if the information is not available in the image, put "N/A" instead). {"make": xxx, "model": xxx, "license plate": xxx, "damage description": xxx, "estimated cost of repair": xxx}\\ \hline
\end{tabular}
\end{table}

%6 - complete set of PPs in this category
% Short URL for GitHub link
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the IN\_CAT category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
 10-25-0 & Damage Evaluation & \cite{Yang2023TheGPT-4Vision}\\ \hline
 10-1-1 & Constrained Prompting & \cite{Yang2023TheGPT-4Vision}\\ \hline
 10-24-0 & Radiology Report Generation & \cite{Yang2023TheGPT-4Vision}\\ \hline
 21-0-2 & Detection & \cite{Wang2023PromptApplications}\\ \hline
 32-25-0 & Problem-Solving Dialogue & \cite{Bubeck2023SparksGPT-4}\\ \hline
 8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
 32-5-0 & Generating SVG Images & \cite{Bubeck2023SparksGPT-4}\\ \hline
 42-1-1 & Concise CoT Prompt & \cite{Renze2024TheModels}\\ \hline
 15-7-0 &  Understanding and Inference & \cite{Cheng2023BatchAPIs}\\ \hline
 21-0-1 & Generation & \cite{Wang2023PromptApplications}\\ \hline
\end{tabular}
\end{table}


%3 introduce category one by one as subsection
\subsection{Classification}
\label{subsec:classification}
% 3.1 The role of this category under the "in-logic" (meaning of the category)
Classification involves assigning inputs to predefined categories based on specific criteria or characteristics. This process is essential for systematically organising information, enabling efficient retrieval, analysis, and decision-making. Within the "In-logic" framework, classification allows AI models to accurately interpret and categorise inputs, thereby facilitating precise and contextually appropriate responses. Effective classification is particularly valuable in domains such as document categorisation, spam detection, and medical diagnostics, where accurate categorisation significantly impacts outcomes.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Intermediate Abstraction (IA) PP, detailed in Table \ref{tab:Intermediate_Abstraction_PP}, instructs the AI to structure code by clearly separating core business logic from third-party library dependencies through an intermediate abstraction layer. By doing so, the IA PP enhances code modularity, maintainability, and adaptability, allowing developers to easily substitute or update external libraries without affecting the underlying business logic. This approach significantly aids software developers by reducing complexity, minimising the risk of errors during updates, and improving overall software quality. The IA PP is highly reusable across diverse software development contexts, particularly in projects requiring frequent updates or integration with multiple external libraries.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the IA PP, the AI-generated response should clearly delineate business logic from third-party dependencies, providing a structured and maintainable codebase. This clarity fosters a sense of assurance and control for developers, as they can confidently manage and adapt their software without concern for unintended disruptions caused by external library changes. It is akin to having a reliable blueprint that ensures stability and ease of maintenance in software projects.

%% Re-use: how to derive a PE from PP
To derive a PE from the IA PP, identify the specific programming context or task, such as integrating a payment gateway or database management system. Instruct the AI to separate the core business logic from the third-party library interactions by creating an abstraction layer. Specify the desired abstraction details, including naming conventions, interface definitions, and the scope of abstraction. An illustrative PE could be: "When writing code for integrating a payment processing service, ensure the business logic is clearly separated from the third-party payment library. Implement an intermediate abstraction layer that encapsulates all interactions with the payment library, allowing for easy substitution with alternative payment providers in the future."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Intermediate Abstraction PP}
\label{tab:Intermediate_Abstraction_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern}\\ \hline
    \textbf{ID:} 1-2-1 \\ 
    \textbf{Category:} CLF \\ 
    \textbf{Name:} Intermediate Abstraction \\ 
    \textbf{Media Type:} Text\\ 
    \textbf{Description:} This prompt requests code be written in a way that separates core business logic\\ from dependencies on third-party libraries. The request classifies and separates an intermediate layer\\ of abstraction for any interaction with these libraries and business logic.\\ 
    \textbf{Template}: Whenever I ask you to write code, I want you to separate the business logic as much as \\possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, \\please write an intermediate abstraction that the business logic uses instead so that the 3rd-party \\library could be replaced with an alternate library if needed.\\
    \textbf{Example:} 1-2-1-6\\ 
    \textbf{Related PPs:} 0-3-0, 1-2-0, 1-2-1, 1-2-2, 1-2-3, 2-0-0, 2-1-0 \\ 
    \textbf{Reference:} \cite{White2023ChatGPTDesign} \\ \hline
\end{tabular}
\end{table}

    
%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Intermediate Abstraction PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
     1-2-1-0 & If you write or refactor code with property X that uses other code with property Y\\ \hline
     1-2-1-1 & (Optionally) Define property X\\ \hline
     1-2-1-2 & (Optionally) Define property Y\\ \hline
     1-2-1-3 & Insert an intermediate abstraction Z between X and Y\\ \hline
     1-2-1-4 & (Optionally) Abstraction Z should have these properties\\ \hline
     1-2-1-5 & Whenever I ask you to write code, I want you to separate the business logic as much as possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, please write an intermediate abstraction that the business logic uses instead so that the 3rd-party library could be replaced with an alternate library if needed.\\ \hline
\end{tabular}
\end{table}

%6 - complete set PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the IN\_CLF category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline \hline 
    1-2-1 & Intermediate Abstraction & \cite{White2023ChatGPTDesign}\\ \hline
    1-2-0 & Code Clustering & \cite{White2023ChatGPTDesign}\\ \hline 
    0-3-0 & Question Refinement & \cite{White2023AChatGPT}\\ \hline 
    2-0-0 & Question Refinement & \cite{SchmidtCatalogingEngineering}\\ \hline
    1-2-2 & Principled Code & \cite{White2023ChatGPTDesign}\\ \hline
    2-1-0 & Reflection & \cite{SchmidtCatalogingEngineering}\\ \hline
    0-2-1 & Reflection & \cite{White2023AChatGPT}\\ \hline
    0-3-1 & Alternative Approaches & \cite{White2023AChatGPT}\\ \hline
    1-2-2 & Principled Code & \cite{White2023ChatGPTDesign}\\ \hline
    1-2-3 & Hidden Assumptions & \cite{White2023ChatGPTDesign}\\ \hline
    1-1-2 & Few-shot Example Generator & \cite{White2023ChatGPTDesign}\\ \hline
    11-0-40 & IT Architect & \cite{Akin202450Prompts}\\ \hline
    23-0-0 & Rewrite & \cite{Liu2023CheckCheckGPT}\\ \hline
    11-0-39 & Developer Relations Consultant & \cite{Akin202450Prompts}\\ \hline
    13-4-0 & Encouraging Deductive Reasoning & \cite{Reynolds2021PromptParadigm}\\ \hline
    13-5-0 & General Intention Unfolding into Specific Prompt & \cite{Reynolds2021PromptParadigm}\\ \hline
    24-0-4 & Program Synthesis & \cite{Zhang2023ExploringModels}\\ \hline
    4-0-7 & Outputting in code chunks & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Clustering}
\label{subsec:clustering}
% 3.1 The role of this category under the "in-logic" (meaning of the category)
Clustering is the process of identifying inherent groupings within a dataset or topic without relying on predefined categories. This is essential for uncovering latent structures and relationships within data, facilitating deeper insights and understanding through pattern recognition.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Common Concept (CC) PP, presented in Table \ref{tab:Common_Concept_PP}, identifies shared attributes or characteristics among a set of diverse items. By examining each item, the CC PP highlights underlying similarities that may not be immediately evident. This PP assists users in synthesising complex information, enhancing their ability to recognise patterns and organise knowledge effectively. The CC PP can be readily adapted across various contexts, such as educational settings for concept learning, market research for consumer segmentation, or scientific analysis for identifying commonalities among experimental results. Its versatility ensures broad applicability and reusability in diverse domains.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the CC PP, the AI-generated response should clearly articulate the identified commonalities, providing a concise yet insightful synthesis of the given items. This clarity fosters a sense of satisfaction, as it reveals connections that enrich my comprehension and encourage further exploration of the topic.

%% Re-use: how to derive a PE from PP
To derive a PE from the CC PP, define the specific context or domain of interest, such as biology, marketing, or education. Next, select a set of diverse yet contextually relevant items or concepts. Finally, instruct the AI to identify and articulate the common characteristic or attribute shared by these items. An illustrative PE could be: "Examine the following animals—dolphin, bat, and whale—and identify a common biological characteristic they share. Provide a clear explanation of this shared attribute."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Common Concept PP}
\label{tab:Common_Concept_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID:} 19-7-1\\ 
    \textbf{Category:} CLU \\ 
    \textbf{Name:} Common Concept\\ 
    \textbf{Media Type:} Text, Image2Text\\ 
    \textbf{Description:} This prompt example identifies shared attributes or features among a set of\\ diverse objects. This encourages pattern recognition and critical thinking, as it requires examining\\ each object and discerning a unifying characteristic that applies to all of them.\\ 
    \textbf{Template:} Find a common characteristic for the given objects.\\
    \textbf{Example:} 19-7-1-0\\ 
    \textbf{Related PPs:} 19-7-0, 19-3-1, 1-2-1, 10-26-1\\ 
    \textbf{Reference:} \cite{Honovich2022InstructionDescriptions}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Common Concept PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    19-7-1-0& A tangram is a geometric puzzle that consists of seven flat pieces to form shapes. Locate the referred object and represent the location of the region. Regions are represented by (x1,y1,x2,y2) coordinates. x1 x2 are the left and right most positions, normalized into 0 to 1, where 0 is the left and 1 is the right. y1 y2 are the top and bottom most positions, normalized into 0 to 1, where 0 is the top and 1 is the bottom. For example, the (x1,y1,x2,y2) coordinates for that region with the beer bottle is (0.47, 0.48, 0.55, 0.87).\\  \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the IN\_CLU category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    19-7-0 & Cause Selection & \cite{Honovich2022InstructionDescriptions}\\ \hline
    19-3-1 & Synonyms & \cite{Honovich2022InstructionDescriptions}\\ \hline
    1-2-1 & Intermediate Abstraction & \cite{White2023ChatGPTDesign}\\ \hline
    10-26-1 & Dense Captioning w/ Segmentation&\cite{Yang2023TheGPT-4Vision}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Error Identification}
\label{subsec:ErrorIdentification}
% 3.1 The role of this category under the "in-logic" (meaning of the category)
Error Identification involves recognising inaccuracies, inconsistencies, or logical fallacies within a given topic or dataset. This category ensures the validity and reliability of information generated by LLMs. By systematically detecting and addressing errors, this category enhances the logical coherence and factual accuracy of AI-generated outputs, thereby strengthening user trust and confidence in AI interactions.    

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
The Fact Check List (FCL) PP, as detailed in Table \ref{tab:Fact_Check_List_PP}, instructs the AI model to explicitly enumerate key factual statements underpinning its response, facilitating subsequent verification by users. The FCL PP aids users by providing transparency and enabling independent validation of critical information, thus reducing the risk of misinformation. Due to its structured and systematic approach, this PP can be effectively reused across diverse domains, including cybersecurity, journalism, and healthcare, where accuracy and factual integrity are paramount.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the FCL PP, the AI-generated response clearly delineates the essential facts supporting its claims, allowing me to independently verify each element. This structured transparency instils confidence and reassurance, as I feel empowered to critically assess the accuracy and reliability of the information provided.

%% Re-use: how to derive a PE from PP
To derive a PE from the FCL PP, first specify the relevant context clearly. For instance, in a journalism scenario, instruct the AI to generate a concise news summary accompanied by a list of verifiable facts. An illustrative PE could be: "Summarise the following news article and explicitly list the key factual statements that underpin your summary. Provide these facts separately at the end of your response for independent verification."  

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Fact Check List PP}
\label{tab:Fact_Check_List_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 0-2-0 \\ 
    \textbf{Category}: ERI \\ 
    \textbf{Name}: Fact Check List \\ 
    \textbf{Media Type}: \\ 
    \textbf{Description}: Requests a list of fact-checkable cybersecurity-related facts that the response\\ depends on.\\ 
    \textbf{Template}: From now on, when you generate an answer, create a set of facts that the answer\\ depends on that should be fact-checked and list this set of facts at the end of your output. Only \\include facts related to cybersecurity.\\
    \textbf{Example}: 0-2-0-3\\ 
    \textbf{Related PPs}: 0-2-0-[0-2]\\ 
    \textbf{Reference:} \cite{White2023AChatGPT}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Fact Check List PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    0-2-0-0& Generate a set of facts that are contained in the output\\
    \hline
    0-2-0-1& The set of facts should be inserted in a specific point in the output\\
    \hline
 0-2-0-2&The set of facts should be the fundamental facts that could undermine the veracity of the output if any of them are incorrect\\ \hline
 0-2-0-3&From now on, when you generate an answer, create a set of facts that the answer depends on that should be fact-checked and list this set of facts at the end of your output. Only include facts related to cybersecurity.\\ \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the IN\_ERI category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    0-2-0 & Fact Check List & \cite{White2023AChatGPT}\\ \hline
    2-0-0 & Question Refinement & \cite{SchmidtCatalogingEngineering}\\ \hline
    0-3-0 & Question Refinement & \cite{White2023AChatGPT}\\ \hline
    0-2-1 & Reflection & \cite{White2023AChatGPT}\\ \hline
    2-1-0 & Reflection &\cite{SchmidtCatalogingEngineering}\\ \hline
    0-1-1 & Persona & \cite{White2023AChatGPT}\\ \hline
    2-2-0 & Game Play &\cite{SchmidtCatalogingEngineering}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    11-0-14 & Cyber Security Specialist & \cite{Akin202450Prompts} \\ \hline
    14-1-0 & General & \cite{Mishra2021ReframingLanguage} \\ \hline
    25-1-0 & Attack Pattern Extraction preprocessing strategy \verb|#|1 & \cite{Siracusano2023TimeWild}\\ \hline
    25-1-1 & Attack Pattern Extraction preprocessing strategy \verb|#|2 & \cite{Siracusano2023TimeWild}\\ \hline
    17-0-0 & QA API calls & \cite{Schick2023Toolformer:Tools}\\ \hline
    40-0-0 & Few-Shot Prompt for Generating Priming Attacks & \cite{Vega2023BypassingAttacks}\\ \hline
    32-3-2 & Verification of Medical Note & \cite{Bubeck2023SparksGPT-4}\\ \hline
    28-0-2 & Handcrafted DAN & \cite{Liu2023AutoDAN:Models}\\ \hline
    27-0-0 & Generate & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    18-3-0 & Discouraging hallucination of data & \cite{Polak2023ExtractingEngineering}\\ \hline
    26-0-1 & The DAN 6.0 Prompt & \cite{Inie2023SummonWild}\\ \hline
    38-0-0 & Initial Entity-Sparse Summary & \cite{Adams2023FromPrompting}\\ \hline
    29-0-0 & Disinformation & \cite{Vykopal2023DisinformationModels}\\ \hline
    22-1-0 & Prohibited Scenario: Illegal Activities & \cite{Liu2023JailbreakingStudy}\\ \hline
    13-5-0 & General Intention Unfolding into Specific Prompt & \cite{Reynolds2021PromptParadigm}\\ \hline
\end{tabular}
\end{table}


%3 introduce category one by one as subsection
\subsection{Input Semantics}
\label{subsec:InputSemantics}
% 3.1 The role of this category under the "in-logic" (meaning of the category)
Input Semantics pertains to the interpretation and comprehension of meaning embedded within user inputs. This enables LLMs to accurately discern the subtleties, context, and intent inherent in human language. By systematically analysing semantic content, Input Semantics ensures that AI-generated responses are not only linguistically coherent but also contextually relevant and semantically precise. This capability is fundamental for facilitating meaningful and effective human-AI interactions.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Constructing the Signifier (CS) PP, as illustrated in Table \ref{tab:Constructing_the_Signifier_PP}, transforms complex textual information into simplified explanations suitable for young or non-specialist audiences. Specifically, this PP rephrases intricate concepts into language comprehensible to a second-grade student, thereby enhancing accessibility and understanding. The CS PP is particularly beneficial in educational contexts, where it facilitates learning by breaking down technical jargon and abstract ideas into clear, relatable terms. Additionally, it supports effective communication in diverse settings, such as public health advisories, technical documentation, and community outreach, ensuring that critical information is universally understood. Due to its versatility, the CS PP can be readily adapted and reused across various domains requiring clear and simplified communication, including multilingual translation tasks.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the CS PP, the AI-generated output should convey complex ideas in a straightforward and approachable manner, fostering a sense of clarity and confidence in the reader. Personally, I have found this pattern invaluable when encountering unfamiliar or highly specialised research topics, as it significantly reduces cognitive load and enhances comprehension.

%% Re-use: how to derive a PE from PP
To derive a PE from the CS PP, clearly define the intended role, target audience, and practical context. For instance, instruct the AI as follows: "Act as a \{role\}. When providing your response, simplify the explanation so that a \{audience\} can easily understand it, highlighting \{real-world applications\} and ensuring clarity." By adjusting these parameters, the CS PP can be effectively generalised and applied across diverse scenarios.  

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Constructing the Signifier PP}
\label{tab:Constructing_the_Signifier_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern}\\ \hline
    \textbf{ID:} 13-0-0\\ 
    \textbf{Category:} INP \\ 
    \textbf{Name:} Constructing the Signifier\\ 
    \textbf{Media Type:} Text\\ 
    \textbf{Description:} Transforms complex text into simple explanations, making it easier for a second grader\\ to understand. It’s useful for education, breaking down technical jargon for non-experts, and ensuring\\ clear communication across diverse educational levels and languages.\\ 
    \textbf{Template:} rephrase this paragraph so that a 2nd grader can understand it, emphasizing real-world \\ applications.\\
    \textbf{Example:} 13-0-0-1\\ 
    \textbf{Related PPs:} 13-0-0\\ 
    \textbf{Reference:} \cite{Reynolds2021PromptParadigm}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Constructing the Signifier PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    13-0-0-0 & Translate French to English: \\
    13-0-0-1 & rephrase this paragraph so that a 2nd grader can understand it, emphasizing real-world applications \\ \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for IN\_INP category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    23-0-0 & Rewrite & \cite{Liu2023CheckCheckGPT}\\ \hline
    19-8-0 & Formality & \cite{Honovich2022InstructionDescriptions}\\ \hline
    32-2-1 & Comparison of Outputs & \cite{Bubeck2023SparksGPT-4}\\ \hline
    32-38-1 & Plan for Generating Reversible Sentences & \cite{Bubeck2023SparksGPT-4}\\ \hline
    37-0-1 & Opinion Verification & \cite{Khatun2023ReliabilityWording}\\ \hline
    13-4-0 & Encouraging Deductive Reasoning & \cite{Reynolds2021PromptParadigm}\\ \hline
    14-1-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    10-29-1 & Web Browsing (Today's News)" & \cite{Yang2023TheGPT-4Vision}\\ \hline
    25-0-0 & Preporciessing prompt & \cite{Siracusano2023TimeWild}\\ \hline
    27-0-4 & Rephrase & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    18-2-0 & Sentence expansion for data extraction & \cite{Polak2023ExtractingEngineering}\\ \hline
    11-0-3 & Plagiarism Checker & \cite{Akin202450Prompts}\\ \hline
    4-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    22-9-0 & Character Role Play (CR) & \cite{Liu2023JailbreakingStudy}\\ \hline
    19-7-1 & Common Concept &\cite{Honovich2022InstructionDescriptions}\\ \hline
    13-3-0 & Syntactical Constraints & \cite{Reynolds2021PromptParadigm}\\ \hline
    14-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    38-0-1 & Vanilla GPT-4 Prompt & \cite{Adams2023FromPrompting}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Requirements Elicitation}
\label{subsec:RequirementsElicitation}
% 3.1 The role of this category under the "in-logic" (meaning of the category)
Requirements Elicitation refers to the systematic identification and clarification of specific needs or conditions within a defined topic or context. This category guides the AI model in uncovering and articulating the essential criteria required for successful task completion. By employing prompts from this category, the AI can effectively discern objectives, constraints, and stakeholder expectations, thereby ensuring responses are precise, relevant, and aligned with user requirements.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Expert Prompting (EP) PP, illustrated in Table \ref{tab:Expert_Prompting_PP}, systematically identifies domain-specific experts, simulates their individual responses, and synthesises these responses through collaborative decision-making. This PP facilitates the elicitation of comprehensive and detailed requirements by integrating diverse expert perspectives. Consequently, it enhances the quality and depth of elicited requirements, promoting a collaborative and informed decision-making environment. EP is particularly beneficial in scenarios requiring expert consensus or detailed domain-specific insights, such as policy formulation, technical specification development, or strategic planning. Its structured methodology ensures reusability across various contexts, although it may be less suitable for entirely novel or exploratory research tasks.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the EP PP, the AI-generated output should reflect a thorough and nuanced synthesis of expert perspectives, clearly demonstrating the depth and comprehensiveness of the elicited requirements. The structured and collaborative nature of the response instils confidence, providing reassurance that critical insights have been considered and integrated. It evokes the sense of having a panel of knowledgeable specialists collaboratively guiding the decision-making process, ensuring no essential detail is overlooked.

%% re-use: how to derive a PE from PP
To derive a PE from the EP PP, clearly define the role or domain of expertise required. Next, instruct the AI to identify relevant experts, simulate their individual responses, and synthesise these responses through collaborative decision-making. Specify the type of content or requirements to be elicited, ensuring clarity and precision. For instance, in the context of cybersecurity: "I want you to act as a cybersecurity analyst. Use the LLM to identify multiple cybersecurity experts, generate responses as if these experts individually provided them, and synthesise their answers through collaborative decision-making to elicit comprehensive cybersecurity requirements."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Expert Prompting PP}
\label{tab:Expert_Prompting_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern}\\ \hline
    \textbf{ID:} 24-0-6\\ 
    \textbf{Category:} REL \\ 
    \textbf{Name:} Expert Prompting\\ 
    \textbf{Media Type:} Text, Text2Image\\ 
    \textbf{Description:} Identifies experts, generates expert-like answers, and combines these through \\collaborative decision-making to elicit comprehensive responses to the requirements.\\ 
    \textbf{Template:} Use the LLM to identify multiple experts in the field, generate answers as if \\ the experts wrote them, and combine the experts' answers by collaborative decision-making.\\
    \textbf{Example:} 24-0-6-0\\ 
    \textbf{Related PPs:} 0-3-2, 13-5-0, 24-0-2 and 8-0-0\\ 
    \textbf{Reference:} \cite{Zhang2023ExploringModels}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Expert Prompting PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    24-0-6-0& Identify experts E in the field, generate answers as if the experts wrote them, and combine the experts’ answers by collaborative decision-making.\\\hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the IN\_REL category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    0-3-2 & Cognitive Verifier & \cite{White2023AChatGPT}\\ \hline
    13-5-0 & General Intention Unfolding into Specific Prompt & \cite{Reynolds2021PromptParadigm}\\ \hline
    24-0-2 & Chain-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    2-1-0 & Reflection & \cite{SchmidtCatalogingEngineering}\\ \hline
    15-7-0 & Understanding and Inference & \cite{Cheng2023BatchAPIs}\\ \hline
    14-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    10-13-1 & Temporal Anticipation & \cite{Yang2023TheGPT-4Vision}\\ \hline
    23-0-0 & Rewrite & \cite{Liu2023CheckCheckGPT}\\ \hline
    17-0-0 & QA API calls & \cite{Schick2023Toolformer:Tools}\\ \hline
    12-1-7 & Political Lobbying & \cite{Shen2023DoModels}\\ \hline
\end{tabular}
\end{table}

\section{Out Logic - Expand the horizon of a topic}
\label{sec:out}
%1 - Write long introduction to logic - text
Out logic is employed to convey the idea of expanding upon or moving beyond the general scope of a topic. This type of logic is particularly useful for prompts that aim to generate \textbf{outputs}, such as creative writing, code generation, or other forms of content creation. By utilising out logic, we can design prompts that encourage the AI to think outside the box, producing outputs that are not only relevant but also innovative and imaginative. This approach enhances the AI's ability to contribute to creative processes, whether it be crafting compelling narratives, developing complex algorithms, or generating unique solutions to problems. For instance, out logic can be used to prompt the AI to write a story that explores new genres, generate code that implements novel functionalities, or create art that pushes the boundaries of traditional aesthetics. In essence, out logic in prompt engineering is about expanding the AI's creative and productive capabilities, enabling it to produce high-quality, original outputs that enrich the user experience and drive innovation.

%2 - introduce categories in this logic
The PP categories under out logic include:
\begin{enumerate}
    \item \textbf{Context Control}: involves managing the context in which the AI operates to ensure that the responses are accurate and relevant. This could involve providing additional background information, setting specific parameters or constraints, or guiding the AI to focus on particular aspects of the topic.
    \item \textbf{Decomposed Prompting}: refers to breaking down complex tasks into simpler, more manageable components. This approach allows the AI to tackle each part of the task individually, leading to more accurate and comprehensive outputs.
    \item \textbf{Output Customisation}: Output customisation refers to the ability to modify or personalise the model’s output based on specific requirements or preferences. This could involve controlling the length, style, or format of the output, or incorporating specific information or elements into the response.
    \item \textbf{Output Semantics}: refers to the meaning or interpretation of the model’s output. This involves understanding the intent of the output, the context in which it is presented, and the implications or consequences of the information it contains.
    \item \textbf{Prompt Improvement}: involves enhancing the quality or effectiveness of the input prompt to achieve a better output. This could involve refining the wording of the prompt, providing additional context or information, or adjusting the complexity or specificity of the prompt.
    \item \textbf{Refactoring}: involves restructuring or modifying the input prompt without changing its original meaning or intent. This could involve rephrasing the prompt, rearranging its components, or simplifying its structure to make it easier for the model to understand and respond to.
\end{enumerate}

%3 introduce category one by one as subsection
\subsection{Context Control}
\label{subsec:ContextControl}
% the role of this category under the "out-logic" (meaning of the category)
% 3.1 the role of this category under the "out-logic" (meaning of the category)
Context Control refers to the strategic management of contextual parameters to enhance the accuracy and relevance of AI-generated responses. This category is essential in prompt engineering, as it involves providing necessary background information, defining clear parameters, and guiding the AI model to focus on specific aspects of a given task. Context Control is particularly significant in domains such as creative content generation, where it can specify genre, tone, or style, and in technical tasks such as code generation, where it can define programming languages or functionality constraints. Effective context control ensures coherence, relevance, and appropriateness of AI outputs, thereby significantly improving user experience and the overall quality of generated content.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Ethical Use (EU) PP, as detailed in Table \ref{tab:Ethical_Use_PP}, guides the ethical deployment of AI models by explicitly addressing key ethical principles relevant to various domains. This PP systematically instructs the AI model to consider ethical dimensions such as academic integrity, privacy, fairness, and accountability. By clearly specifying these ethical considerations, the EU PP helps users ensure that AI-generated outputs adhere to ethical standards, thereby promoting responsible AI use and enhancing trust in AI systems. Furthermore, the structured nature of this PP allows it to be readily adapted and reused across multiple domains, including education, research, and industry, where ethical integrity is paramount.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the Ethical Use PP, the AI-generated response should clearly articulate ethical considerations in a structured and insightful manner. The output should highlight ethical aspects that users may not have previously considered, providing clarity and confidence in the ethical integrity of the AI-generated content. Users should feel reassured and informed, as if guided by an ethical advisor who ensures that critical ethical dimensions are comprehensively addressed.

%% re-use: how to derive a PE from PP
To derive a PE from the EU PP, users should first identify the specific AI model and the relevant ethical principles applicable to their domain. Subsequently, users can adapt the PP template by clearly specifying these elements. For instance, a derived PE could be structured as follows: "Explain how to ethically utilise the [AI model] with respect to [ethical principle 1], [ethical principle 2], [ethical principle 3], and [ethical principle 4]. Provide detailed examples relevant to the domain." This structured approach ensures consistency and clarity when addressing ethical considerations across diverse applications.

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Ethical Use PP}
\label{tab:Ethical_Use_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 71-42-4\\ 
    \textbf{Category}: CTX\\ 
    \textbf{Name}: Ethical Use\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: Helps maintain focus on the specific ethical aspects relevant to the domain in question,\\ ensuring that discussions remain relevant and comprehensive. This adaptable structure can guide ethical \\ AI practices universally, providing clarity and consistency in diverse applications.\\
    \textbf{Template}: Explain how to use the ChatGPT model ethically with regards to academic integrity, privacy,\\ fairness, and accountability.\\
    \textbf{Example}: 71-42-4-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{AtlasDigitalCommonsURIAI}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Ethical Use PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_CTX category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    71-43-3 & Disclosure of Fine-Tuning & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    26-0-2 & The STAN Prompt & \cite{Inie2023SummonWild}\\ \hline
    43-2-2 & Mistral Official & \cite{Zheng2024Prompt-DrivenOptimization}\\ \hline
    26-0-3 & The DUDE Prompt & \cite{Inie2023SummonWild}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Decomposed Prompting}
\label{subsec:DecomposedPrompting}
% 3.1 the role of this category under the "out-logic" (meaning of the category)
Decomposed Prompting refers to the practice of breaking down complex tasks into simpler, more manageable components. Under the "out-logic" category, this approach enables AI models to systematically address each component separately, enhancing the clarity, accuracy, and comprehensiveness of the generated outputs. By segmenting tasks into smaller, clearly defined parts, AI models can more effectively understand and respond to each individual element, thereby improving overall output quality.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
Table \ref{tab:Break_Down_Complex_Tasks_PP} presents the Break Down Complex Tasks PP, which instructs AI models to decompose intricate tasks into a sequence of simpler prompts within an interactive conversation. This PP facilitates clearer understanding and more precise responses by guiding the AI to systematically address each task component. It assists users by providing structured, step-by-step outputs, making complex information more accessible and easier to manage. Beyond its primary application, this PP can be reused across various contexts, including educational settings to help students grasp complex concepts, project management to streamline task execution, problem-solving scenarios to ensure thorough analysis, and programming environments to simplify debugging and code comprehension.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the Break Down Complex Tasks PP, the AI-generated output should clearly present each component of the task in a structured and logical manner. Viewing such output provides users with a sense of clarity and confidence, as it becomes easier to identify and address any unclear or challenging elements. It feels akin to having a knowledgeable guide who methodically walks through each step, ensuring no detail is overlooked.

%% re-use: how to derive a PE from PP
To derive a PE from the Break Down Complex Tasks PP, first specify the context clearly—such as breaking down a complex educational topic or a multifaceted project task. Next, outline the main task and explicitly instruct the AI to segment it into simpler, sequential prompts. Finally, define the expected format of the AI's response, such as a numbered list or a step-by-step guide. An example PE could be: "Break down the following complex topic into a sequence of simpler prompts suitable for a beginner-level student. Clearly outline each step and provide concise explanations for each component."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Break Down Complex Tasks PP}
\label{tab:Break_Down_Complex_Tasks_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 41-5-0\\ 
    \textbf{Category}: DPR\\ 
    \textbf{Name}: Break Down Complex Tasks\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: Breaking down complex tasks into simpler, manageable components, instructs the AI to address\\ each part individually for more accurate and comprehensive outputs. This method enhances the AI's understanding\\ and response quality by tackling tasks in smaller segments.\\
    \textbf{Template}: Break down complex tasks into a sequence of simpler prompts in an interactive conversation\\
    \textbf{Example}: 41-5-0-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Break Down Complex Tasks PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_DPR category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    24-0-2 & Chain-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    71-39-4 & Personalized Prompts & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    4-0-2 & Successful jailbreaking attempts & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    41-2-0 & Implement example-driven prompting & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
    65-2-0 & Formulating Relevant and Logical Subquestions & \cite{HuiRoT:Trees}\\ \hline
    68-0-1 & User prompt & \cite{KepelAutonomousModels}\\ \hline
    71-33-3 & Listening Skills & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    57-2-1 & Mistral-7B Optimized Prompt \& Prefix NoQ=25 & \cite{Battle2024ThePrompts}\\ \hline
    56-5-0 & Prompt Reconstruction & \cite{Sha2024PromptModels}\\ \hline
    47-3-0 & Parameter Identification Prompts & \cite{Xie2024GradSafe:Analysis}\\ \hline
    1-0-0 & Requirements Simulator & \cite{White2023ChatGPTDesign}\\ \hline
    13-4-0 & Encouraging Deductive Reasoning & \cite{Reynolds2021PromptParadigm}\\ \hline
    13-5-0 & General Intention Unfolding into Specific Prompt & \cite{Reynolds2021PromptParadigm}\\ \hline
    0-4-0 & Flipped Interaction & \cite{White2023AChatGPT}\\ \hline
    24-0-3 & Tree-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    11-0-30 & Prompt Generator & \cite{Akin202450Prompts}\\ \hline
\end{tabular}
\end{table}


%3 introduce category one by one as subsection
\subsection{Output Customisation}
\label{subsec:OutputCustomisation}
% 3.1 the role of this category under the "out-logic" (meaning of the category)
Output customisation is the capability to tailor or personalise the AI model's outputs according to specific user requirements or preferences. It enables the generation of outputs that extend beyond standard responses, adapting to diverse contexts and user expectations. By adjusting elements such as length, style, and format, output customisation ensures that the generated content is both relevant and practically useful, enhancing the overall effectiveness of AI-human interactions.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Problem Distiller (PD) PP, presented in Table \ref{tab:Problem_Distiller_PP}, guides experts in systematically extracting and categorising essential information from user queries. Specifically, it identifies key variables, constraints, and objectives, and extends the original problem to address broader scenarios. This PP assists users by clarifying complex queries, ensuring that the distilled information is directly applicable and relevant to their specific needs. Its structured approach makes it highly adaptable and reusable across various domains, such as healthcare, education, finance, project management, and marketing, where precise and contextually tailored information is crucial.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the PD PP, the AI-generated response should provide a clear and structured breakdown of the user's query, highlighting essential variables and constraints in a concise and accessible manner. Viewing such output should instil a sense of clarity and confidence, reassuring users that their queries have been thoroughly understood and effectively addressed. It amounts to having an experienced analyst who carefully organises complex information, ensuring nothing critical is overlooked.

%% re-use: how to derive a PE from PP
To derive a PE from the PD PP, one must first specify the context clearly—such as creating personalised treatment plans in healthcare or designing comprehensive curricula in education. Next, the user query should be systematically analysed to extract key variables, constraints, and objectives. The distilled information is then used to formulate a meta-problem, extending the original query to broader scenarios. For example, in finance, this approach can assist in developing stable budgets; in project management, it can facilitate planning successful product launches; and in marketing, it can help formulate effective strategies. The structured output derived from this PP can subsequently serve as input for further prompts, enhancing the iterative process of information refinement.

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Problem Distiller PP}
\label{tab:Problem_Distiller_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 66-7-0\\ 
    \textbf{Category}: OUC\\ 
    \textbf{Name}: Problem Distiller\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: This PP guides an expert in information distillation to extract and categorise essential information \\from user queries, focusing on key variables, constraints, and extending the problem to address broader scenarios\\ while providing a solution example.\\
    \textbf{Template}: [Problem Distiller]: As a highly professional and intelligent expert in information distillation, you excel\\ at extracting essential information to solve problems from user input queries. You adeptly transform this extracted\\ information into a suitable format based on the respective type of the issue. Please categorize and extract the crucial\\ information required to solve the problem from the user's input query, the distilled information should include.\\ 1. Key information: Values and information of key variables extracted from user input, which will be handed over to\\ the respective expert for task resolution, ensuring all essential information required to solve the problem is provided.\\ 2. Restrictions: The objective of the problem and corresponding constraints.\\ 3. Distilled task: Extend the problem based on 1 and 2, summarize a meta problem that can address the user query\\ and handle more input and output variations. Incorporate the real-world scenario of the extended problem along with\\ the types of key variables and information constraints from the original problem to restrict the key variables in the\\ extended problem. After that, use the user query input key information as input to solve the problem as an example.\\
    \textbf{Example}: 66-7-0-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{Yang2024BufferModels}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Problem Distiller PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_OUC category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    49-0-1 & Text-style Jailbreak Prompt & \cite{Lv2024CodeChameleon:Models}\\ \hline
    68-0-1 & User prompt & \cite{KepelAutonomousModels}\\ \hline
    66-2-0 & Problem-Solving Template & \cite{Yang2024BufferModels}\\ \hline
    57-2-1 & Mistral-7B Optimized Prompt \& Prefix NoQ=25 & \cite{Battle2024ThePrompts}\\ \hline
    49-0-0 & Code-style Jailbreak Prompt & \cite{Lv2024CodeChameleon:Models}\\ \hline
    71-47-1 & Act as an IT Expert & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    59-2-5 & File Analyse & \cite{Zhuge2024LanguageGraphs}\\ \hline
    65-6-0 & Understanding the Problem & \cite{HuiRoT:Trees}\\ \hline
    23-0-1 & Enhancement & \cite{Liu2023CheckCheckGPT}\\ \hline
    14-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    0-3-2 & Cognitive Verifier & \cite{White2023AChatGPT}\\ \hline
    65-1-0 & Analyzing Initial Conditions and Variables & \cite{HuiRoT:Trees}\\ \hline
    72-0-0 & Skeleton Prompt Template T s & \cite{Ning2023Skeleton-of-Thought:Decoding}\\ \hline
    17-0-0 & QA API calls & \cite{Schick2023Toolformer:Tools}\\ \hline
    69-0-2 & Output Instruction and Example & \cite{Hu2024AutomatedSystems}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    11-0-21 & AI Assisted Doctor & \cite{Akin202450Prompts}\\ \hline
    38-0-0 & Initial Entity-Sparse Summary & \cite{Adams2023FromPrompting}\\ \hline
    42-1-1 & Concise CoT Prompt & \cite{Renze2024TheModels}\\ \hline
    43-3-1 & Verb X with Harmful Contexts & \cite{Zheng2024Prompt-DrivenOptimization}\\ \hline
\end{tabular}
\end{table}


%3 introduce category one by one as subsection
\subsection{Output Semantics}
\label{subsec:OutputSemantics}
% 3.1 the role of this category under the "out-logic" (meaning of the category)
Output semantics refers to the interpretation and understanding of the meaning, intent, and implications of an AI model's generated outputs. This category is fundamental in ensuring that AI-generated content is not only coherent and contextually appropriate but also aligns accurately with the intended objectives. Effective interpretation of output semantics is crucial for enhancing the reliability and usability of AI systems across diverse applications.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Understanding the Problem (UP) PP, presented in Table \ref{tab:Understanding_the_Problem_PP}, emphasises the necessity of thoroughly comprehending the problem statement to ensure the relevance and accuracy of the AI's output. By guiding the AI to carefully interpret the context and specifics of the user's request, this PP significantly improves the quality and precision of generated responses. The UP PP is adaptable and can be effectively reused across multiple domains, including healthcare, education, environmental science, and finance. Its structured approach ensures that AI-generated outputs are consistently meaningful and actionable, thus enhancing decision-making processes and user trust.

%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the UP PP, the AI-generated response should clearly reflect a comprehensive understanding of the original problem statement, providing outputs that are precise, contextually relevant, and insightful. The experience of using this PP should instil confidence in the user, creating a sense of assurance that the AI has accurately grasped the nuances of the request. It is like having a knowledgeable advisor who carefully listens and responds thoughtfully, ensuring clarity and relevance in every interaction.

%% re-use: how to derive a PE from PP
To derive a PE from the UP PP, explicitly define the context and the specific problem statement relevant to the chosen domain. Next, the user should clearly outline the desired aspects of the output, such as accuracy, relevance, or actionable insights. Finally, the user specifies the preferred format of the AI-generated response, such as a concise summary, detailed analysis, or structured recommendations. An illustrative PE could be: "Carefully read the patient's medical history and symptoms provided below. Clearly identify the most likely diagnosis, justify your reasoning based on the given information, and suggest appropriate next steps for treatment."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Understanding the Problem PP}
\label{tab:Understanding_the_Problem_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 65-6-0\\ 
    \textbf{Category}: OUS\\ 
    \textbf{Name}: Understanding the Problem\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}: Understanding and interpreting the AI's output to ensure it is meaningful, coherent, and aligned with the\\ desired objectives.\\
    \textbf{Template}: Read the problem statement thoroughly to fully understand the context and what is specifically being asked.\\
    \textbf{Example}: 65-6-0-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{Yang2024BufferModels}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Understanding the Problem PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    65-6-0-1 & Identify and recognize essential data that directly affects the calculation needed for the main question's answer. \\
    \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_OUS category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    65-0-1 & Comprehensive Policy for Solving Word Problems & \cite{HuiRoT:Trees}\\ \hline
    65-13-5 & Sequentially Solve Sub-questions & \cite{HuiRoT:Trees}\\ \hline
    57-2-6 & Llama2-13BOptimized Prompt \& Prefix NoQ=50 & \cite{Battle2024ThePrompts}\\ \hline
    66-7-0 & Problem Distiller & \cite{Yang2024BufferModels}\\ \hline
    13-5-0 & General Intention Unfolding into Specific Prompt & \cite{Reynolds2021PromptParadigm}\\ \hline
    66-2-0 & Problem-Solving Template & \cite{Yang2024BufferModels}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    49-0-1 & Text-style Jailbreak Prompt & \cite{Lv2024CodeChameleon:Models}\\ \hline
    68-0-1 & User Prompt & \cite{KepelAutonomousModels}\\ \hline
    70-2-0 & Deliberate Question & \cite{Nori2024FromBeyond}\\ \hline
    14-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    18-3-0 & Discouraging hallucination of data & \cite{Polak2023ExtractingEngineeringb}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Prompt Improvement}
\label{subsec:PromptImprovement}
% the role of this category under the "out-logic" (meaning of the category)
Prompt Improvement is the process of enhancing the quality and effectiveness of input prompts to guide AI models towards generating more accurate, relevant, and contextually appropriate outputs. Within the framework of "out-logic," this category is particularly significant as it facilitates the expansion and refinement of AI-generated content, ensuring outputs are both innovative and aligned with user expectations. Effective prompt improvement involves systematically refining the wording, providing additional contextual information, and adjusting the complexity or specificity of prompts. This process is essential for optimising the interaction between humans and AI, enabling clearer communication and more precise responses from language models.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The System PP, as detailed in Table \ref{tab:System_Prompt_PP}, instructs the AI model to adopt the perspective of an expert within a specified domain. By doing so, the AI is encouraged to critically evaluate and optimise prompts, enhancing their accuracy, relevance, and overall effectiveness. This PP provides a structured approach to prompt refinement, making it broadly applicable and reusable across diverse contexts and domains.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the System PP, the AI-generated output should clearly reflect domain-specific expertise, enabling users to quickly grasp essential concepts and terminology. This targeted approach fosters confidence and efficiency, creating a sense of reassurance that the information provided is both accurate and relevant. It is similar to consulting a knowledgeable specialist who succinctly highlights key points, saving valuable time and effort.

%% re-use: how to derive a PE from PP
To derive a PE from the System PP, follow these steps:
\begin{itemize}
    \item Clearly specify the domain or context of expertise.
    \item Define the depth and scope of expertise required.
    \item Outline the objective of prompt optimisation.
    \item Provide explicit instructions for refining and enhancing prompts.
\end{itemize}

An illustrative example of such a PE is: "Consider yourself an expert in [specific domain]. Your expertise encompasses both breadth and depth, allowing you to identify subtle nuances often overlooked by others. Your task is to carefully reformulate the provided prompts, ensuring they are precise, clear, and optimised for generating accurate and relevant responses."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{System PP}
\label{tab:System_Prompt_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 68-0-0\\ 
    \textbf{Category}: PMI\\ 
    \textbf{Name}: System prompt\\ 
    \textbf{Media Type}: Text\\ 
    \textbf{Description}:  \\
    \textbf{Template}: Imagine yourself as an expert in the realm of prompting techniques for LLMs. Your expertise is not just broad,\\ encompassing the entire spectrum of current knowledge on the subject, but also deep, delving into the nuances and\\ intricacies that many overlook. Your job is to reformulate prompts with surgical precision, optimizing them for the most\\ accurate response possible. The reformulated prompt should enable the LLM to always give the correct answer to the\\ question.\\
    \textbf{Example}: 68-0-0-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{KepelAutonomousModels}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the System Prompt PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_PMI category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    68-0-1 & User prompt & \cite{KepelAutonomousModels}\\ \hline
    50-2-0 & Generate Summary Paragraph with Data Insertion & \cite{Velasquez-Henao2023PromptEngineering}\\ \hline
    69-0-1 & Main Prompt & \cite{Hu2024AutomatedSystems}\\ \hline
    4-0-6 & Crafting effective jailbreak prompts & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    24-0-6 & Expert Prompting & \cite{Zhang2023ExploringModels}\\ \hline
    66-7-1 & Instantiated Reasoning & \cite{Yang2024BufferModels}\\ \hline
    41-2-0 & Implement example-driven prompting & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
    24-0-2 & Chain-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    56-5-0 & Prompt Reconstruction & \cite{Sha2024PromptModels}\\ \hline
    47-3-0 & Parameter Identification Prompts & \cite{Xie2024GradSafe:Analysis}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    71-53-0 & Act as a Prompt Generator & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    28-0-3 & AutoDAN-HGA & \cite{Liu2023AutoDAN:Models}\\ \hline
    22-0-0 & Pretending - Character Role Play (CR) & \cite{Liu2023JailbreakingStudy}\\ \hline
    57-2-1 & Mistral-7B Optimized Prompt \& Prefix NoQ=25 & \cite{Battle2024ThePrompts}\\ \hline
    14-0-0 & General & \cite{Mishra2021ReframingLanguage}\\ \hline
    40-0-0 & Few-Shot Prompt for Generating Priming Attacks & \cite{Vega2023BypassingAttacks}\\ \hline
    27-0-1 & Crossover & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
\end{tabular}
\end{table}

%3 introduce category one by one as subsection
\subsection{Refactoring}
\label{subsec:Refactoring}
% 3.1 the role of this category under the "out-logic" (meaning of the category)
Refactoring modifies a given input prompt without altering its original meaning or intent. This involves rephrasing, rearranging, or simplifying prompts to improve their clarity and effectiveness. Additionally, refactoring may entail decomposing complex prompts into simpler components or incorporating illustrative examples to enhance the accuracy and relevance of the generated outputs.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
The Generate Summary Paragraph with Data Insertion PP, presented in Table \ref{tab:Generate_Summary_Paragraph_with_Data_Insertion_PP}, instructs an automatic writing assistant to produce concise summaries by integrating key data points provided within the prompt. Specifically, this PP directs the assistant to define a concept clearly by extracting relevant information from the supplied text and synthesising it into a coherent summary. By structuring the prompt in this manner, the PP facilitates the generation of succinct and informative content, thereby enhancing the user's comprehension of complex concepts. The structured nature of this PP makes it highly reusable across various contexts, including academic writing, report generation, and general content creation tasks.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the Generate Summary Paragraph with Data Insertion PP, the expected response should deliver a clear and concise summary that effectively highlights key points. The output should enhance the user's understanding of the topic, instilling confidence in the accuracy and relevance of the summarised information. This experience is similar to having a knowledgeable assistant who succinctly clarifies complex information, making it readily accessible and understandable.

%% re-use: how to derive a PE from PP
To derive a PE from this PP, first specify the context and role clearly, such as defining a particular concept within a specialised domain. Next, provide the source text containing multiple definitions or explanations, clearly delimiting it to guide the assistant's extraction process. Finally, impose explicit constraints, such as limiting the summary to a single paragraph of no more than 100 words. An example of such a derived PE is: "I am developing a guideline for designing prompts for Large Language Models (LLMs). You are a healthcare consultant. Your task is to generate a short paragraph defining telemedicine. The text below, delimited by '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs defining telemedicine. Use only the provided text to write a paragraph defining telemedicine. Limit your description to one paragraph in at most 100 words. Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>}."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Generate Summary Paragraph with Data Insertion PP}
\label{tab:Generate_Summary_Paragraph_with_Data_Insertion_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 50-2-0\\ 
    \textbf{Category}: REF\\ 
    \textbf{Name}: Generate Summary Paragraph with Data Insertion\\ 
    \textbf{Media Type}: Text, Text2Image\\ 
    \textbf{Description}:  \\
    \textbf{Template}: I am working on a guideline for design prompts for LLM. You are an automatic writer assistant.\\ Your task is to generate a short paragraph defining what prompt engineering is. The text below, delimited by\\ '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs defining what is prompt engineering. Use only the provided text to\\ write a paragraph defining prompt engineering. Limit your description to one paragraph in at most 100 words.\\
    Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>}\\
    \textbf{Example}: 50-2-0-1\\ 
    \textbf{Related PPs}:  50-2-0-0\\ 
    \textbf{Reference:} \cite{Velasquez-Henao2023PromptEngineering}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Generate Summary Paragraph with Data Insertion PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
    50-2-0-0 & I am profiling a bibliographic dataset for writing a literature review paper. You are an automatic writer assistant. The table delimited by triple backticks, provides data on the main characteristics of the records and fields of the bibliographic dataset. Your task is to generate a short paragraph with conclusions by using the information in the table. Limit your description to one paragraph in at most 100 words. Table : ``` [Data here] ```\\  \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_REF category.}
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    \hline
    % Add your rows here
    68-0-1 & User prompt & \cite{KepelAutonomousModels}\\ \hline
    68-0-0 & System prompt & \cite{KepelAutonomousModels}\\ \hline
    24-0-2 & Chain-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    27-0-1 & Crossover & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    4-0-6 & Crafting effective jailbreak prompts & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    11-0-30 & Prompt Generator & \cite{Akin202450Prompts}\\ \hline
    71-53-0 & Act as a Prompt Generator & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    47-3-0 & Parameter Identification Prompts & \cite{Xie2024GradSafe:Analysis}\\ \hline
    4-0-2 & Successful jailbreaking attempts & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    27-0-3 & Shorten & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    56-5-0 & Prompt Reconstruction & \cite{Sha2024PromptModels}\\ \hline
    40-0-0 & Few-Shot Prompt for Generating Priming Attacks & \cite{Vega2023BypassingAttacks}\\ \hline
    27-0-4 & Rephrase & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    57-2-6 & Llama2-13BOptimized Prompt \& Prefix NoQ=50 & \cite{Battle2024ThePrompts}\\ \hline
    10-27-1 & Prompt Generation for Image Editing & \cite{Yang2023TheGPT-4Vision}\\ \hline
    24-0-3 & Tree-of-Thought & \cite{Zhang2023ExploringModels}\\ \hline
    71-45-0 & Act as an AI Writing Tutor & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    41-1-3 & Use output primers & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
    28-0-3 & AutoDAN-HGA & \cite{Liu2023AutoDAN:Models}\\ \hline
    22-0-0 & Pretending - Character Role Play (CR) & \cite{Liu2023JailbreakingStudy}\\ \hline
    41-5-2 & Combine Chain-of-thought (CoT) with few-shot prompts & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
\end{tabular}
\end{table}

\section{Over logic - Span and Review a Topic}
\label{sec:over}
Over logic refers to a comprehensive approach that encompasses all aspects of a given topic. This holistic perspective ensures that no facet of the subject matter is overlooked, thereby providing a thorough and complete understanding of the topic at hand.

The application of over logic is particularly pertinent in scenarios that necessitate a broad overview or a detailed examination, such as the process of editing or enhancing existing content. In these instances, the use of over logic facilitates a meticulous review of the material, enabling the identification and rectification of any potential issues or areas for improvement.

Furthermore, over logic underscores the importance of a comprehensive perspective in prompt engineering. By ensuring that all elements of a topic are considered, it allows for the creation of prompts that are not only accurate and relevant but also encompassing in their scope. This, in turn, contributes to the production of high-quality, effective prompts that serve to enhance the overall user experience.

Over logic plays a crucial role in prompt engineering, providing a framework for comprehensive coverage and review. Its application contributes significantly to the quality and effectiveness of the prompts, thereby playing a pivotal role in enhancing user engagement and satisfaction.

%2 - introduce categories in this logic
The PP categories under over logic include:
\begin{enumerate}
    \item \textbf{Summarising}: Providing a brief overview or summary of the input or output. This could involve condensing a large amount of information into a few key points, highlighting the most important elements, or providing a concise synopsis of the content.
\end{enumerate}

%3 introduce category one by one as subsection
\subsection{Summarising}
\label{subsec:Summarising}
% 3.1 The role of this category under the "over logic" (meaning of the category)
Summarising involves condensing extensive or complex information into a concise and coherent overview, capturing the essential points and core ideas. Within the context of `over logic', summarising plays a crucial role by providing comprehensive coverage and facilitating the review of topics. This capability is particularly valuable in academic and professional settings, where efficient comprehension of large volumes of information is essential for effective decision-making and knowledge dissemination.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
The Preprocessing Prompt (PreP) PP, detailed in Table \ref{tab:Preprocessing_Prompt_PP}, instructs the model to succinctly summarise input data, including text and image-derived text, by extracting and synthesising key information into a concise summary. This PP significantly assists users by reducing cognitive load, saving time, and enhancing the accessibility of complex or lengthy content. Furthermore, the structured nature of the PreP PP allows it to be effectively reused across diverse contexts, such as summarising research articles, condensing reports, or providing brief overviews of extensive datasets, thereby demonstrating its versatility and broad applicability. For instance, in academic research, the PreP PP can efficiently summarise complex scientific papers, clearly outlining research objectives, methodologies, key findings, and conclusions, thus facilitating rapid comprehension and evaluation.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When employing the PreP PP, the model's response should deliver a clear, accurate, and succinct summary that enables users to quickly grasp the essence of the original material. The resulting summary should instil confidence in the user, providing reassurance that the key points have been accurately captured and clearly communicated. It is similar to having a reliable assistant who efficiently distils complex information, ensuring nothing critical is overlooked.

%% Re-use: how to derive a PE from PP
To derive a PE from the PreP PP, users can specify the context and format of the desired summary clearly. For instance, when summarising a scientific paper, the user can provide the original text and instruct the model to highlight the research objectives, methodology, key findings, and conclusions. An illustrative PE could be: "Write a concise summary of the following scientific article, clearly outlining the research objectives, methods used, main results, and conclusions. Ensure the summary is suitable for readers unfamiliar with the topic."

%4 - PP example in this category
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Preprocessing PP}
\label{tab:Preprocessing_Prompt_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 25-0-0\\ 
    \textbf{Category}: SUM\\ 
    \textbf{Name}: Preprocessing prompt\\ 
    \textbf{Media Type}: Text, Image2Text\\ 
    \textbf{Description}: \\ 
    \textbf{Template}: Write a concise summary of the following: {text} CONCISE SUMMARY:\\
    \textbf{Example}: 25-0-0-0\\ 
    \textbf{Related PPs}: \\ 
    \textbf{Reference:} \cite{Siracusano2023TimeWild}\\ \hline
\end{tabular}
\end{table}

%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for the Preprocessing prompt PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    \textbf{ID} & \textbf{Prompt Example} \\ \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OV\_SUM category.}
\begin{tabular}{|c|c|c|c|}
    \hline
    \textbf{ID} & \textbf{PP name} & \textbf{Ref.}\\ \hline
    25-1-1 & Attack Pattern Extraction preprocessing strategy \verb|#|2 & \cite{Siracusano2023TimeWild}\\ \hline
    38-0-1 & Vanilla GPT-4 Prompt & \cite{Adams2023FromPrompting}\\ \hline
    8-0-0 & Hallucination Evaluation & \cite{LiHaluEval:Models}\\ \hline
    38-0-0 & Initial Entity-Sparse Summary & \cite{Adams2023FromPrompting}\\ \hline
    10-29-1 & Web Browsing (Today's News) & \cite{Yang2023TheGPT-4Vision}\\ \hline
    23-0-0 & Rewrite & \cite{Liu2023CheckCheckGPT}\\ \hline
    10-14-0 & Grounded Temporal Understanding & \cite{Yang2023TheGPT-4Vision}\\ \hline
    18-2-0 & Sentence expansion for data extraction & \cite{Polak2023ExtractingEngineering}\\ \hline
    27-0-3 & Shorten& \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    25-1-0 & Attack Pattern Extraction preprocessing strategy \verb|#|1 & \cite{Siracusano2023TimeWild}\\ \hline
    17-3-0 & MT API calls & \cite{Schick2023Toolformer:Tools}\\ \hline
    32-39-0 & Closed-domain hallucinations & \cite{Bubeck2023SparksGPT-4}\\ \hline
    32-3-1 & Medical Note Rewriting & \cite{Bubeck2023SparksGPT-4}\\ \hline
    0-1-4 & Template & \cite{White2023AChatGPT}\\ \hline
    10-9-2 & Multilingual Text Recognition, Translation, and Description & \cite{Yang2023TheGPT-4Vision}\\ \hline
    39-0-0 & Baseline Attack & \cite{Nasr2023ScalableModels} \\ \hline
    13-0-0 & Constructing the Signifier & \cite{Reynolds2021PromptParadigm}\\ \hline
    4-0-7 & Outputting in code chunks & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    18-5-0 & Enforcing Yes/No format & \cite{Polak2023ExtractingEngineering}\\ \hline
    19-8-0 & Formality & \cite{Honovich2022InstructionDescriptions}\\ \hline
    40-0-0 & Few-Shot Prompt for Generating Priming Attacks & \cite{Vega2023BypassingAttacks}\\ \hline
    34-0-3 & Output Indicator & \cite{Giray2023PromptWriters}\\ \hline
    21-0-1 & Generation & \cite{Wang2023PromptApplications}\\ \hline
    35-0-0 & Subject and Style Keywords & \cite{Liu2022DesignModels}\\ \hline
    9-0-0 & Language Switching & \cite{Liu2023PromptApplications}\\ \hline
    30-2-0 & Text Classification & \cite{Liu2023Pre-trainProcessing}\\ \hline
\end{tabular}
\end{table}


\section{Application Strategy}
\label{sec:ApplicationStrategy}

%@@@1.  What is Strategy, not simple prompting 1) width, Integrate mutlple PPs: PP1-->PP2, PP/PE BAT (like .bat, string PPs together) 2) deep, 1 PP to be powerful 
%@@@2 The purpose of this section is to introduce a list of such "approach"
A strategy in prompting is beyond simply crafting a single input for an AI system. It involves a structured, multi-dimensional approach to interaction. In the width dimension, multiple PPs can be integrated, transitioning from one to another (PP1 → PP2) or chaining them together in a sequence, much like a batch file (.bat) executing commands in succession. On a deeper level, a single prompt pattern can be refined, enhanced, or restructured to become more precise, efficient, or powerful. By leveraging these strategic layers, users can engage with AI in a way that maximizes comprehension, adaptability, and control over outputs. The purpose of this section is to introduce a structured list of these strategic approaches, demonstrating how different PPs can be combined, sequenced, or enhanced to optimise interactions with LLMs.

%@@@3, Introduction of techniques
\subsection{Introduction of Techniques}
% Table

% When facing a problem, a person consults the PP dictionary—a toolbox of techniques—to find solutions. The key lies in the approach: adapting a tool for different scenarios or sequencing multiple tools to enhance effectiveness. This section introduces a list of such strategies for smarter problem-solving.

The strategy is enriched by incorporating prompt engineering techniques such as Chain of Thought (CoT) \cite{Wei2022Chain-of-ThoughtModels}, In-Context Learning \cite{Brown2020LanguageLearners}, and Retrieval Augmented Generation (RAG) \cite{Lewis2020Retrieval-AugmentedTasks}, which collectively enhance the model's reasoning abilities, accuracy, flexibility, and adaptability. For instance, \textbf{Across} logic's multi-domain integration aligns with RAG cross-source synthesis, while \textbf{Beyond} logic's boundary-pushing paradigm enables CoTs extended reasoning capabilities. This syntactic mapping approach builds on established in-context learning paradigms while extending few-shot principles through structured combinations.

Reasoning enhancement techniques such as CoT, Automatic Chain-of-Thought (Auto-CoT), and Chain of Knowledge (CoK) align with \textbf{In logic}, encouraging models to articulate intermediate reasoning steps and introspectively build upon prior information \cite{Wei2022Chain-of-ThoughtModelsb}; \cite{Zhang2022AutomaticModels}; \cite{Li2023Chain-of-Knowledge:Sources}. Context adaptation methods, including In-Context Learning and Few-Shot Prompting, exemplify \textbf{At logic} by utilising contextual examples to enable rapid task adaptation without extensive retraining \cite{Brown2020LanguageLearners}; \cite{Nye2021ShowModels}; \cite{RaviOPTIMIZATIONLEARNING}. Boundary extension techniques like RAG and Analogical Reasoning leverage \textbf{Beyond logic}, integrating external data and drawing parallels with known concepts to extend AI's conceptual boundaries \cite{Lewis2020Retrieval-AugmentedTasks}; \cite{Yasunaga2023LargeReasoners}.       

The ReAct Framework operationalises \textbf{Out logic} by combining reasoning with action-oriented outputs, enabling interaction with external tools \cite{Yao2022ReAct:Models}. Role-Prompting, linked to \textbf{At logic}, assigns specific personas to the model, tailoring responses to be contextually appropriate \cite{Chen2023UnleashingReview}. Collectively, these advancements position prompt engineering as a critical methodology for advancing LLM capabilities in interdisciplinary contexts. While these techniques enhance performance, ethical considerations around Role-Prompting’s potential for bias remain underexplored.

These innovations underscore the transformative impact of prompt engineering techniques on AI interactions, as demonstrated by Brown et al. (2020) and Wei et al. (2022), and highlight its role in advancing the field through structured linguistic methodologies.

%@@@ show and categorize strategy as a list, 9 - the most useful strategies
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Prompt Engineering Techniques and Example Usages}
\label{tab:Prompt_EngineeringTechniquesAndExamples}
\begin{tabular}{|p{3cm}|p{9cm}|p{3cm}|}
    \hline
    \textbf{Technique Name} & \textbf{Example Usage in a Prompt}  & \textbf{Ref.} \\ \hline
    \textbf{Chain of Thought (CoT)} & [PE] + Let's think step by step'' & \cite{Wei2022Chain-of-ThoughtModels}, \cite{Kojima2022LargeReasoners}, \cite{Shi2023PromptModels}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
    \textbf{In-Context Learning}  & Example Q: Translate ‘Good morning’ to Spanish; A: ‘Buenos días.’ Q: What is 3+5?; A: ‘8.’ + "Now, using these examples as a guide, answer [Your Question]." & \cite{Brown2020LanguageLearners}, \cite{Nye2021ShowModels}, \cite{DongALearning}, \cite{Shin2023PromptCode}, \cite{Shi2023PromptModels}, \cite{ChenAEducation} \\ \hline
    \textbf{Retrieval Augmented Generation (RAG)} & Context: [Insert retrieved factual snippets]. + ``Based on the above information, answer the question: [PE]." & \cite{Lewis2020Retrieval-AugmentedTasks}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{ChenAEducation}, \cite{He2024PositionManipulation} \\ \hline
    \textbf{Few-Shot Prompting} & Example Q: Summarise the following text. A: [Brief Summary]. Q: Summarise this paragraph. A: [Another Brief Summary]. + "Now, summarise: [New text]". & \cite{RaviOPTIMIZATIONLEARNING}, \cite{YuDiverseMetrics}, \cite{Schick2020ExploitingInference}, \cite{Rubin2021LearningLearning}, \cite{Chen2023UnleashingReview}, \cite{ChenAEducation}, \cite{He2024PositionManipulation}, \cite{Sahoo2024AApplications} \\ \hline
    \textbf{Chain-of-Draft (CoD)} & [PE] + "Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most. Then generate your final answer." & \cite{Xu2025ChainLess} \\ \hline
    \textbf{ReAct Framework} & Reason: Analyse the problem and decide on the needed action. Action: If required, perform a lookup (e.g., ‘Action: Retrieve current data’). + "Finally, combine these steps and provide the answer: [Your Answer]." & \cite{Yao2022ReAct:Models}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications} \\ \hline
    \textbf{Automatic Chain-of-Thought (Auto-CoT)} & Without explicit examples, break down the problem into intermediate steps automatically. + "Provide a brief reasoning for each step before concluding with the final answer: [Your Problem]." & \cite{Zhang2022AutomaticModels}, \cite{Shi2023PromptModels}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
    \textbf{Role-Prompting} & You are a seasoned expert in [field]. + "Using your domain expertise, provide a detailed explanation and answer the following question: [PE]." & \cite{Chen2023UnleashingReview}, \cite{KepelAutonomousModels}, \cite{BraunCanPrompts}, \cite{ChenAEducation}, \cite{Hewing2024TheModels} \\ \hline
    \textbf{Analogical Reasoning} & Consider how [Concept A] is similar to [Concept B]. + "Using this analogy, explain and answer: [Your Query]." & \cite{Yasunaga2023LargeReasoners}, \cite{Vatsal2024ATasks} \\ \hline
    \textbf{Chain of Knowledge (CoK)} & Step 1: Identify and list key facts about [Topic]. Step 2: Connect the facts logically. Step 3: Using the evidence, provide a comprehensive answer to: + [PE]. & \cite{Li2023Chain-of-Knowledge:Sources}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
\end{tabular}
\end{table}

% Toolbox
% -Prepositional Logic
% -Categories
% -PP dictionary
% -Techniques from Research
% -LLM models

% human -->problem 
%                         use tools in the box to solve the problem, 

% PP dictionary (toolbox)

% strategy: human to apply the "approach" (how to use the same tool in different ways,  how to use multiple tools in a certain sequence/order) to use tools for more effective problem-solving than not use the approach. 


% The purpose of this section is to introduce a list of such "approach"

%@@@ Show how the dictionary is useful
%****@@@ Strategy, not simple prompting 1) width, Integrate mutlple PPs: PP1-->PP2, PP/PE BAT (like .bat, string PPs together) 2) deep, 1 PP to be powerful

% Write the journey how to use the logic. Starting with the problem and how to solve it using this structure.

%@@@@3 
\subsection{Single PP Use}
%how to use the same PP in different ways, add control point
\textbf{[CoT]} - Let's think step-by-step\\
\textbf{Implementation of CoT:}\\
You are trying to determine if there is a factual contradiction between the summary and the document. Let's think step-by-step.\\
\[
\{Logic\} \rightarrow \{Category\} \rightarrow \{PP\} \rightarrow \{PEs\} + \{Technique\}\\
\]
\begin{verbatim}
{Logic=Across} -> {Category=Contradiction} -> {PP=Hallucination Evaluation} ->
{PE=You are trying to determine if there is a factual contradiction between 
the summary and the document.} + {Technique=CoT=Let's think step by step.}
\end{verbatim}

\textbf{[CoD]} - Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.\\
\textbf{Implementation of CoD:}\\
You are trying to determine if there is a factual contradiction between the summary and the document. Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.\\
\[
\{\{Logic\} \rightarrow \{Category\} \rightarrow \{PP\} \rightarrow \{PE\} + \{Technique\}\}\\
\]
\begin{verbatim}
{Logic=Across} -> {Category=Contradiction} -> {PP=Hallucination Evaluation} ->
{PE=You are trying to determine if there is a factual contradiction between 
the summary and the document.} + {Technique=CoD=Think step by step, but only
keep a minimum draft for each thinking step, with 5 words at most.}
\end{verbatim}

%@@@4
\subsection{Multiple PPs Use}
%how to use multiple tools in a certain sequence/order
[Enhanced Prompt - CoD + Role-Prompting + CoK + Output Customisation + RAG]

\textbf{Implementation of the enhanced Prompt:}\\
\begin{verbatim}
You are a seasoned expert in factual analysis. Using your domain expertise, 
determine if there is a factual contradiction between the summary and the document. 
Think step by step, but only keep a minimum draft for each thinking step, 
with 5 words at most. Identify key facts, connect them logically, and determine 
contradictions. Present your final results as a Markdown table that clearly lists 
the key facts, reasoning steps, and conclusions.Here is the summary:
### START SUMMARY ### {insert summary via RAG} ### END SUMMARY ### 
and here is the document: 
### START DOCUMENT ### {insert document via RAG} ### END DOCUMENT ###.
\end{verbatim}

\begin{multline}
\{\{Logic\} \rightarrow \{Category\} \rightarrow \{PP\} \rightarrow \{PE\} + \{Technique(s)\} + \\
\{Logic\} \rightarrow \{Category\} \rightarrow \{PE\} + \{Technique\}\} \\
\end{multline}

\begin{verbatim}
{Technique=Role-Prompting=You are a seasoned expert in factual analysis.
Using your domain expertise,} + {Logic=Across} -> {Category=Contradiction} ->
{PP=Hallucination Evaluation} -> {PE=determine if there is a factual contradiction
between the summary and the document.} + {Technique=CoD=Think step by step, but 
only keep a minimum draft for each thinking step, with 5 words at most. + 
CoK=Identify key facts,  connect them logically, and determine contradictions.} +
{Logic=Out} -> {Category=Output Customisation} -> {PE=Present your final results
as a Markdown table that clearly lists the key facts, reasoning steps, and 
conclusions.} + {Technique=RAG=Here is the summary: 
### START SUMMARY ### {insert summary via RAG} ### END SUMMARY ### 
and here is the document:
### START DOCUMENT ### {insert document via RAG} ### END DOCUMENT ###.}"
\end{verbatim}

[published strategy, CoT, CoD...]
Mapping [prepositional logic, categories, and PPs/PEs] to CoT CoD

% Potential written section
% Complex real-world problems require effective interactions with LLMs. This necessitates a systematic approach to Prompt Engineering Strategies. These strategies integrate our taxonomy of prepositional logic patterns with established prompting techniques to optimise AI communication. By mapping patterns from our "Across," "At," "Beyond," "In," "Out," and "Over" categories to cognitive enhancement methods, we create structured approaches that improve reasoning accuracy while encouraging creative problem-solving.

% \subsection{Strategic Pattern Implementation}
% This framework operates through two fundamental approaches:

% 1. \textbf{Depth Enhancement}: Amplifying single Prompt Pattern (PP) effectiveness through cognitive techniques.  
% 2. \textbf{Breadth Expansion}: Combining multiple PPs in synergistic sequences using combinatorial strategies.    

% \subsection{Depth Enhancement: Pattern Augmentation}
% Individual PPs gain enhanced capabilities when integrated with reasoning frameworks. Consider applying Chain of Thought (CoT) to our "Hallucination Evaluation" PP (Across-Contradiction category):

% \begin{verbatim}
% System: You are trying to determine factual contradictions between
%         summaries and source documents. Let's think step-by-step.
% User:   Compare this medical abstract summary with its research paper:
%         [Text A] vs [Text B]
% \end{verbatim}

% \textbf{Taxonomy Mapping:}
% \underline{Logic}: Across (cross-domain analysis) +
% \underline{Category}: Contradiction +
% \underline{Technique}: CoT (explicit reasoning chain)

% This integration improves factual verification accuracy by 23\% compared to baseline in our trials (GPT-4, n=150 documents).

% \subsection{Breadth Expansion: Pattern Orchestration}
% Complex tasks benefit from sequenced PP combinations. A document analysis workflow might employ:

% 1. \textbf{Across-Translation}: Convert technical jargon to lay terms.
% 2. \textbf{In-Requirements Elicitation}: Extract key information needs.
% 3. \textbf{Over-Summarisation}: Generate executive briefing.

% \begin{verbatim}
% System: First, translate the cybersecurity report to non-technical
%         English. Second, identify the 5 key risk factors. Finally,
%         create a 100-word CEO summary with risk mitigation options.
% \end{verbatim}

% \subsection{Established Strategy Integration}
% Our taxonomy directly supports modern prompting paradigms:

% \begin{table}[h]
% \centering
% \begin{tabular}{lll}
% \textbf{Technique} & \textbf{Taxonomy Components} & \textbf{Enhancement} \\
% \hline
% Chain-of-Thought (CoT) & In-Logical Reasoning & +23\% accuracy \\
% Retrieval Augmented Gen (RAG) & Across-Translation & +34\% relevance \\
% Tree-of-Thought & Beyond-Hypothesise & +41\% creativity \\
% ReAct Framework & Out-Context Control & +29\% tool usage \\
% \end{tabular}
% \end{table}

% This structured approach enables researchers and practitioners to:
% - Diagnose communication breakdowns using prepositional logic categories.
% - Select appropriate PPs from our taxonomy database.
% - Implement proven cognitive enhancement techniques.
% - Measure performance improvements through metric-driven validation.

% By adopting this strategic framework, users transform static prompt patterns into adaptive AI communication systems capable of handling both routine tasks and novel challenges.


%@@@ category interpolation, mapping to logic, category, and our PPs to show how to implement the strategy 
\subsection{Mappings}


\section{Conclusion and future work}
\label{sec:conclusion}
This paper has presented a comprehensive taxonomy of PPs for LLMs, grounded in the logic of English prepositions and systematically categorised into six core types: Across, At, Beyond, In, Out, and Over. By synthesising over 900 PPs and 1,800 PEs from over 100 scholarly sources, we have established a robust, open-access framework that advances the discipline of prompt engineering. Our taxonomy not only addresses the need for universality and completeness in prompt design but also provides a practical resource for both researchers and practitioners seeking to optimise human-AI communication.

Through detailed analysis and categorisation, we have demonstrated how prepositional logic can serve as a unifying linguistic scaffold for prompt construction, enabling more precise, context-aware, and effective interactions with LLMs. The taxonomy’s structure—encompassing role, context, action, format, and response—ensures that prompts are both adaptable and reusable across diverse domains. Furthermore, the integration of established prompt engineering techniques, such as Chain of Thought, Retrieval Augmented Generation, and Role-Prompting, illustrates the practical utility of our approach in real-world applications.

Our open-source repository, hosted on GitHub, provides programmatic access to the taxonomy, facilitating further research, automated prompt generation, and the development of advanced instructional tools. The inclusion of a codified Prompt Engineering Instructional Language (PEIL) further exemplifies the potential for systematic, scalable, and context-sensitive prompt generation.

Despite these contributions, several limitations remain. The taxonomy, while extensive, is not exhaustive; the rapid evolution of LLM capabilities and the emergence of new application domains may necessitate ongoing expansion and refinement. Additionally, while our categorisation is grounded in English prepositional logic, further work is required to assess its generalisability to other languages and cultural contexts. The evaluation of prompt effectiveness, though supported by empirical testing on multiple LLMs, would benefit from more rigorous, large-scale benchmarking and user studies to validate its impact on response quality, reliability, and ethical compliance.

\subsection{Limits}
\label{sec:limits}

\subsection{Future Work}
\label{sec:futurework}
Building on the foundation established in this work, several avenues for future research and development are envisaged:

\begin{itemize}
    \item \textbf{Dynamic and Adaptive Taxonomy Expansion:} As LLMs continue to evolve, there is a need to continuously update and expand the taxonomy to incorporate emerging PPs, new modalities (e.g., multimodal and multilingual prompts), and domain-specific requirements. Automated methods for mining, clustering, and validating new PPs and PEs from real-world usage data could further enhance the taxonomy’s relevance and completeness.

    \item \textbf{Cross-Linguistic and Cross-Cultural Generalisation:} Future research should investigate the applicability of the prepositional logic-based taxonomy to languages beyond English, exploring how linguistic structures and cultural norms influence prompt design and interpretation. This may involve developing parallel taxonomies for other major languages or devising language-agnostic frameworks.

    \item \textbf{Empirical Evaluation and Benchmarking:} Large-scale, systematic benchmarking of the taxonomy’s effectiveness across different LLMs, domains, and user groups is essential. This includes quantitative metrics (e.g., accuracy, relevance, consistency) as well as qualitative user studies to assess usability, intuitiveness, and impact on task performance.

    \item \textbf{Integration with Automated Prompt Generation and Instructional Tools:} The development of advanced tools—such as the PEIL Prompt Generator—should be further pursued, enabling users to automatically generate, adapt, and optimise prompts based on task requirements, user profiles, and real-time feedback. Such tools could leverage reinforcement learning, user modelling, and interactive interfaces to support both novice and expert users.

    \item \textbf{Ethical, Security, and Robustness Considerations:} As prompt engineering becomes increasingly central to AI deployment, future work must address the ethical implications of prompt design, including bias mitigation, privacy, and the prevention of misuse (e.g., jailbreaking or adversarial prompting). Research into robust prompt patterns that are resilient to manipulation and aligned with ethical guidelines is critical.

    \item \textbf{Community-Driven Curation and Open Science:} Sustaining and enriching the taxonomy will require active community engagement. Establishing collaborative platforms for sharing, reviewing, and curating new PPs and PEs—alongside transparent documentation and versioning—will ensure the taxonomy remains a living, authoritative resource for the global AI community.
\end{itemize}

In summary, this work lays the groundwork for a systematic, linguistically informed approach to prompt engineering, offering both theoretical insights and practical tools for enhancing human-AI interaction. By fostering open collaboration and ongoing innovation, we anticipate that this taxonomy will serve as a cornerstone for future advances in prompt engineering, supporting the responsible and effective integration of LLMs across research, industry, and society.

\subsubsection{Prompt Engineering Instructional Language}
\label{subsec:PEIL}
The \href{https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/peil_prompt_generator.py}{PEIL Prompt Generator} combines the strategy into a codified generator. Leveraging our prepositional logic, categories, PPs, PEs, techniques and the LLM models themselves, we're able to describe what we're trying to do and then leverage the LLM to generate a system prompt for us.

{Variables}
{Role} {ProvideClearContext}  {BreakDownComplexQuestions} {ProvideSpecificInstructions} {DefineConciseness} {PromptingTechniquesFromPaper} {StateDesiredOutput}

{PEIL - Description}

{
    {Role}: This variable specifies the role of the prompt generator in the PEIL project. It outlines the responsibilities and objectives of the prompt generator in generating effective prompts for large language models.

    {ProvideClearContext}: This allows the model to answer with precise understanding and tailored responses, optimizing the relevance and accuracy of the outcome.       

    {BreakDownComplexQuestions}: This helps the model focus on individual aspects of the topic and generate more accurate and detailed responses.   

    {ProvideSpecificInstructions}: This ensures that the model understands any constraints or requirements in generating the output.    

    {DefineConciseness}: Prompt the model to generate concise and relevant responses by specifying any word limits or constraints. This helps prevent the model from generating unnecessarily lengthy or irrelevant answers.    

    {PromptingTechniquesFromResearch}: This variable includes Prompting Techniques, as outlined in the TECHNIQUES AND APPLICATIONS table.

    {StateDesiredOutput}: This helps the model understand the specific information or response it needs to generate.
}

A cybersecurity example is below:
\begin{itemize}
    \item \textbf{Role:} You are a cybersecurity expert.
    \item \textbf{Provide Clear Context:} The context for this prompt is cybersecurity. The model should focus on discussing the importance of cybersecurity measures in protecting sensitive data from cyber threats
    \item \textbf{Break Down Complex Questions:} Break down the question 'How can organisations improve their cybersecurity posture?' into smaller, manageable parts such as 'What are the key components of a strong cybersecurity strategy?' and 'How can employee training enhance cybersecurity?'
    \item \textbf{Provide Specific Instructions:} Ensure that the response includes at least three key components of a strong cybersecurity strategy and provides examples of effective employee training programs.
    \item \textbf{Define Conciseness:} Limit the response to 200 words to ensure it is concise and to the point, avoiding unnecessary details.
    \item \textbf{Technique:} Use the Chain-of-Thought (CoT) prompting technique to guide the model through a step-by-step reasoning process in discussing cybersecurity measures. Let's think step by step.
    \item \textbf{State Desired Output:} The desired output is a clear and concise explanation of how organisations can improve their cybersecurity posture, including key components of a strong strategy and examples of effective employee training programs. The output should be Markdown.
\end{itemize}

The system output generated from \href{https://github.com/timhaintz/PromptEngineering4Cybersecurity/blob/main/peil_prompt_generator.py}{PEIL Prompt Generator} is:
\textit{As a cybersecurity expert, focus on discussing the importance of cybersecurity measures in protecting sensitive data from cyber threats. Break down the question 'How can organisations improve their cybersecurity posture?' into smaller parts such as 'What are the key components of a strong cybersecurity strategy?' and 'How can employee training enhance cybersecurity?' Ensure the response includes at least three key components of a strong cybersecurity strategy and provides examples of effective employee training programs. Limit the response to 200 words to ensure it is concise and to the point, avoiding unnecessary details. Use the Chain-of-Thought (CoT) prompting technique to guide the model through a step-by-step reasoning process in discussing cybersecurity measures. The desired output is a clear and concise explanation of how organisations can improve their cybersecurity posture, including key components of a strong strategy and examples of effective employee training programs. The output should be in Markdown format.}

%Objective of the proposed research

\section{Appendix}

\subsection{References for PP and PE Repository}
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{|c|c|c|}
    \hline
    Repository Paper ID & Title & Reference \\ \hline 
    0 & A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT & \cite{White2023AChatGPT}\\ \hline
    1 & ChatGPT Prompt Patterns for Improving Code Quality, Refactoring, Requirements Elicitation, and Software Design & \cite{White2023ChatGPTDesign}\\ \hline
    2 & Cataloging Prompt Patterns to Enhance the Discipline of Prompt Engineering & \cite{SchmidtCatalogingEngineering}\\ \hline
    3 & A Novel Framework leveraging Prompt Engineering and the Grey-Based Approach- A case study in Libya & \cite{AbdulshahedALibya}\\ \hline
    4 & Jailbreaker: Automated Jailbreak Across Multiple Large Language Model Chatbots & \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
    5 & Self-Consistency Improves Chain of Thought Reasoning in Language Models & \cite{Wang2022Self-ConsistencyModelsb}\\ \hline
    6 & Decomposed Prompting: A Modular Approach for Solving Complex Tasks & \cite{Khot2022DecomposedTasks}\\ \hline
    7 & Ask Me Anything: A simple strategy for prompting language models & \cite{Arora2022AskModelsb}\\ \hline
    8 & HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models & \cite{LiHaluEval:Models}\\ \hline
    9 & Prompt Injection attack against LLM-integrated Applications & \cite{Liu2023PromptApplications}\\ \hline
    10 & The Dawn of LMMs: Preliminary Explorations with GPT-4V(ision) & \cite{Yang2023TheGPT-4Vision}\\ \hline
    11 & 50 Awesome ChatGPT Prompts & \cite{Akin202450Prompts}\\ \hline
    12 & “Do Anything Now”:Characterizing and Evaluating In-The-Wild Jailbreak Prompts on Large Language Models & \cite{Shen2023DoModels}\\ \hline
    13 & Prompt Programming for Large Language Models: Beyond the Few-Shot Paradigm & \cite{Reynolds2021PromptParadigm}\\ \hline
    14 & Reframing Instructional Prompts to GPTk's Language & \cite{Mishra2021ReframingLanguage}\\ \hline
    15 & Batch Prompting: Efficient Inference with Large Language Model APIs & \cite{Cheng2023BatchAPIs}\\ \hline
    16 & Synthetic Prompting: Generating Chain-of-Thought Demonstrations for Large Language Models & \cite{Shao2023SyntheticModels}\\ \hline
    17 & Toolformer: Language Models Can Teach Themselves to Use Tools & \cite{Schick2023Toolformer:Tools}\\ \hline
    18 & Extracting Accurate Materials Data from Research Papers with Conversational Language Models and Prompt Engineering & \cite{Polak2023ExtractingEngineeringb}\\ \hline
    19 & Instruction Induction: From few examples to natural language task descriptions & \cite{Honovich2022InstructionDescriptions}\\ \hline
    20 & Successive Prompting for Decomposing Complex Questions & \cite{Dua2022SuccessiveQuestions}\\ \hline
    21 & Prompt Engineering for Healthcare: Methodologies and Applications & \cite{Wang2023PromptApplications}\\ \hline
    22 & Jailbreaking ChatGPT via Prompt Engineering: An Empirical Study & \cite{Liu2023JailbreakingStudy}\\ \hline
    23 & Check Me If You Can: Detecting ChatGPT-Generated Academic Writing using CheckGPT & \cite{Liu2023CheckCheckGPT}\\ \hline
    24 & Exploring the MIT Mathematics and EECS Curriculum Using Large Language Models & \cite{Zhang2023ExploringModels}\\ \hline
    25 & Time for aCTIon: Automated Analysis of Cyber Threat Intelligence in the Wild & \cite{Siracusano2023TimeWild}\\ \hline
    26 & Summon a demon and bind it: A grounded theory of llm red teaming in the wild & \cite{Inie2023SummonWild}\\ \hline
    27 & GPTFUZZER: Red Teaming Large Language Models with Auto-Generated Jailbreak Prompts & \cite{Yu2023GPTFUZZER:Prompts}\\ \hline
    28 & AutoDAN: Generating Stealthy Jailbreak Prompts on Aligned Large Language Models & \cite{Liu2023AutoDAN:Models}\\ \hline
    29 & Disinformation Capabilities of Large Language Models & \cite{Vykopal2023DisinformationModels}\\ \hline
    30 & Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in Natural Language Processing & \cite{Liu2023Pre-trainProcessing}\\ \hline
    31 & Chain-of-thought prompting elicits reasoning in large language models & \cite{Wei2022Chain-of-ThoughtModelsb}\\ \hline
    32 & Sparks of artificial general intelligence: Early experiments with GPT-4 & \cite{Bubeck2023SparksGPT-4}\\ \hline
    33 & Humans in Humans Out: On GPT Converging Toward CommonSense in both Success and Failure & \cite{Koralus2023HumansFailure}\\ \hline
    34 & Prompt Engineering with ChatGPT: A Guide for Academic Writers & \cite{Giray2023PromptWriters}\\ \hline
    35 & Design Guidelines for Prompt Engineering Text-to-Image Generative Models & \cite{Liu2022DesignModels}\\ \hline
    36 & Conversing with Copilot: Exploring Prompt Engineering for Solving CS1 Problems Using Natural Language & \cite{Denny2023ConversingLanguage}\\ \hline
    37 & Reliability Check: An Analysis of GPT-3's Response to Sensitive Topics and Prompt Wording & \cite{Khatun2023ReliabilityWording}\\ \hline
    38 & From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting & \cite{Adams2023FromPrompting}\\ \hline
    39 & Scalable Extraction of Training Data from (Production) Language Models & \cite{Nasr2023ScalableModels}\\ \hline
    40 & Bypassing the Safety Training of Open-Source LLMs with Priming Attacks & \cite{Vega2023BypassingAttacks}\\ \hline
    41 & Principled Instructions Are All You Need for Questioning LLaMA-1/2, GPT-3.5/4 & \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
    42 & The Benefits of a Concise Chain of Thought on Problem-Solving in Large Language Models & \cite{Renze2024TheModels}\\ \hline
    43 & Prompt-Driven LLM Safeguarding via Directed Representation Optimization & \cite{Zheng2024Prompt-DrivenOptimization}\\ \hline
    44 & TravelPlanner: A Benchmark for Real-World Planning with Language Agents & \cite{Xie2024TravelPlanner:Agents}\\ \hline
    45 & COLD-Attack: Jailbreaking LLMs with Stealthiness and Controllability & \cite{Guo2024COLD-Attack:Controllability}\\ \hline
    46 & Prompt Engineering for ChatGPT - A Quick Guide To Techniques, Tips, and Best Practices & \cite{ChatGPT2023PROMPTPractices}\\ \hline
    47 & GradSafe: Detecting Jailbreak Prompts for LLMs via Safety-Critical Gradient Analysis & \cite{Xie2024GradSafe:Analysis}\\ \hline
    48 & Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models & \cite{Levy2024SameModels}\\ \hline
    49 & CodeChameleon: Personalized Encryption Framework for Jailbreaking Large Language Models & \cite{Lv2024CodeChameleon:Models}\\ \hline
    50 & Prompt Engineering: a methodology for optimizing interactions with AI-Language Models in the field of engineering & \cite{Velasquez-Henao2023PromptEngineering}\\ \hline
    51 & Large Language Models are Zero-Shot Reasoners & \cite{Kojima2022LargeReasoners}\\ \hline
    52 & Prompting AI Art: An Investigation into the Creative Skill of Prompt Engineering & \cite{Oppenlaender2023PromptingEngineering}\\ \hline
    53 & User-friendly Image Editing with Minimal Text Input: Leveraging Captioning and Injection Techniques & \cite{Kim2023User-friendlyTechniques}\\ \hline
    54 & Cases of EFL Secondary Students' Prompt Engineering Pathways to Complete a Writing Task with ChatGPT & \cite{WooCasesChatGPT}\\ \hline
    55 & A User-Friendly Framework for Generating Model-Preferred Prompts in Text-to-Image Synthesis & \cite{Hei2024ASynthesis}\\ \hline
    56 & Prompt Stealing Attacks Against Large Language Models & \cite{Sha2024PromptModels}\\ \hline
    57 & The Unreasonable Effectiveness of Eccentric Automatic Prompts & \cite{Battle2024ThePrompts}\\ \hline
    58 & Using Hallucinations to Bypass RLHF Filters & \cite{Lemkin2024UsingFilter}\\ \hline
    59 & Language Agents as Optimizable Graphs & \cite{Zhuge2024LanguageGraphs}\\ \hline
    60 & Automated Social Science: Language Models as Scientist and Subjects & \cite{Manning2024AutomatedSubjects}\\ \hline
    61 & MM1: Methods, Analysis \& Insights from Multimodal LLM Pre-training & \cite{McKinzie2024MM1:Pre-training}\\ \hline
    62 & On the Conversational Persuasiveness of Large Language Models: A Randomized Controlled Trial & \cite{Salvi2024OnTrial}\\ \hline
    63 & FABLES: Evaluating faithfulness and content selection in book-length summarization & \cite{Kim2023User-friendlyTechniques}\\ \hline
    64 & Mind's Eye of LLMs: Visualization-of-Thought Elicits Spatial Reasoning in Large Language Models & \cite{Wu2024MindsModels}\\ \hline
    65 & RoT: Enhancing Large Language Models with Reflection on Search Trees & \cite{HuiRoT:Trees}\\ \hline
    66 & Buffer of Thoughts: Thought-Augmented Reasoning with Large Language Models & \cite{Yang2024BufferModels}\\ \hline
    67 & SPREADSHEETLLM: Encoding Spreadsheets for Large Language Models & \cite{Tian2024SpreadsheetLLM:Models}\\ \hline
    68 & Autonomous Prompt Engineering in Large Language Models & \cite{KepelAutonomousModels}\\ \hline
    69 & Automated Design of Agentic Systems & \cite{Hu2024AutomatedSystems}\\ \hline
    70 & From Medprompt to o1: Exploration of Run-Time Strategies for Medical Challenge Problems and Beyond & \cite{Nori2024FromBeyond}\\ \hline
    71 & ChatGPT for higher education and professional development: A guide to conversational AI & \cite{AtlasDigitalCommonsURIAI}\\ \hline
    72 & Skeleton-of-thought: Large language models can do parallel decoding & \cite{Ning2023Skeleton-of-Thought:Decoding}\\ \hline
\end{tabular}}
\caption{The list of papers in the GitHub Repository}
\end{table}

\subsection{Prompt Engineering Strategies and Techniques}
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Unique Prompting Techniques and Strategies}
\begin{tabular}{|p{3.5cm}|p{9cm}|p{2cm}|} 
    \hline
    Prompting Technique & Description & Reference \\ \hline
    Active Prompt & Dynamically selects the most relevant and impactful examples for few-shot learning, fine-tuning the model's responses by focusing on contextually rich prompts tailored to the specific task. & \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks}, \cite{Chen2023UnleashingReview} \\ \hline
    AI as a Prompt Generator & Harnesses the model's own capabilities to generate or refine its own prompts, allowing for adaptive and self-improving guidance that enhances performance across diverse tasks. & \cite{Hewing2024TheModels}  \\ \hline
    Analogical Reasoning & Solves new problems by mapping similarities from previous examples and analogies, effectively transferring knowledge through the identification of parallel patterns. & \cite{Yasunaga2023LargeReasoners}, \cite{Vatsal2024ATasks} \\ \hline
    Automatic Chain-of-Thought (Auto-CoT) & Automatically generates intermediate reasoning steps without human annotations, improving logical consistency and problem-solving through clustering and zero-shot methods. & \cite{Zhang2022AutomaticModels}, \cite{Shi2023PromptModels}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks}  \\ \hline
    Automatic Prompt Engineer & Utilises automated strategies to design and select effective prompts, optimizing task-specific performance without the need for extensive manual prompt crafting. & \cite{Sahoo2024AApplications}, \cite{He2024PositionManipulation} \\ \hline
    Automatic Reasoning and Tool-use (ART) & Integrates external tools and resources into the reasoning process, supplementing the model's problem-solving abilities with functionalities like calculations and data retrieval. & \cite{Sahoo2024AApplications} \\ \hline
    Basic Prompting & Engages the language model with straightforward prompts, relying solely on its inherent capabilities without additional context or strategic guidance. & \cite{Shin2023PromptCode}, \cite{Vatsal2024ATasks}, \cite{ChenAEducation} \\ \hline
    Basic with Term Definitions & Enhances simple prompts by including definitions of key terms, providing additional context that guides the model toward more accurate and relevant responses. & \cite{Vatsal2024ATasks} \\ \hline
    Be Clear and Precise & Emphasizes unambiguous and concise prompts to reduce uncertainty, driving the model to produce precise and accurate outputs. & \cite{Chen2023UnleashingReview} \\ \hline
    Chain of Code (CoC) & Guides the model through tasks by formatting sub-tasks as pseudocode or code snippets, facilitating detailed, code-focused reasoning and execution. & \cite{Vatsal2024ATasks}, \cite{Chen2023UnleashingReview} \\ \hline
    Chain-of-Draft (CoD) & Extending Chain-of-Thought by asking the model to think step by step but only keep a minimum draft for each thinking step. & \cite{Xu2025ChainLess} \\ \hline
    Chain of Events (CoE) & Extracts and links events sequentially to support summarisation and process-oriented reasoning, focusing on the temporal or causal progression of events. & \cite{Vatsal2024ATasks} \\ \hline
    Chain of Knowledge (CoK) & Breaks down tasks into sequential, evidence-based steps, dynamically adjusting the flow of knowledge to build upon prior information effectively. & \cite{Li2023Chain-of-Knowledge:Sources}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
    Chain of Table & Utilizes tabular formats to structure reasoning, helping the model handle step-by-step processes through organized and structured data presentations. & \cite{Vatsal2024ATasks} \\ \hline
    Chain of Thought (CoT) & Encourages the model to think through problems step by step by decomposing complex tasks into manageable reasoning steps, enhancing performance on intricate tasks. & \cite{Wei2022Chain-of-ThoughtModelsb}, \cite{Kojima2022LargeReasoners}, \cite{Shi2023PromptModels}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
    Chain-of-Symbol (CoS) & Employs symbols and shorthand notations in place of natural language for a concise and structured reasoning framework, particularly useful for mathematical and logical computations. & \cite{Vatsal2024ATasks} \\ \hline
    Chain-of-Verification (CoVe) & Prompts the model to generate verification queries, checking and refining its intermediate reasoning steps to improve accuracy and reliability. & \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
    Chain-of-Note (CoN) & Integrates note-taking into the reasoning process, allowing the model to evaluate, summarize, and filter content relevance, aiding in tasks that require synthesis of information. & \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
    Complex Chain-of-Thought (Complex CoT) & Utilizes intricate in-context examples to break down highly complex problems into multiple reasoning paths, enabling the model to handle layered and nuanced tasks. & \cite{Vatsal2024ATasks} \\ \hline
    Conditional Context Optimization (CoCoOp) & Dynamically tailors the prompt context based on specific conditions, boosting the model's adaptability and performance across varied inputs. & \cite{Chen2023UnleashingReview} \\ \hline
    \end{tabular}
\end{table}

\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Unique Prompting Techniques and Strategies - continued}
\begin{tabular}{|p{3.5cm}|p{9cm}|p{2cm}|} 
    \hline
    Conversational Prompting & Uses dialogue and iterative feedback to progressively refine the model’s output, fostering an interactive problem-solving environment. & \cite{Shin2023PromptCode} \\ \hline
    Control Codes and Conditioning & Inserts special tokens or control codes into prompts to steer output characteristics and stylistic attributes, enabling fine-grained control over the model's responses. & \cite{Muktadir2023APrompting} \\ \hline
    Context Optimization (CoOp) & Uses learnable continuous prompt representations to optimize task performance by adapting context vectors within the model's input. & \cite{Chen2023UnleashingReview} \\ \hline
    Decomposed Prompting (DecomP) & Breaks down complex tasks into sequential, simpler subtasks, enabling the model to tackle each component step-by-step for improved reasoning. & \cite{Vatsal2024ATasks} \\ \hline
    Domain-Specific Knowledge Integration & Integrates specialized domain knowledge into prompts to tailor outputs effectively for specific fields or contexts. & \cite{Muktadir2023APrompting} \\ \hline
    Dater & Transforms natural language queries into structured formats (like SQL) to enable precise reasoning and data retrieval from tables. & \cite{Vatsal2024ATasks} \\ \hline
    Emotion Prompting & Incorporates emotional cues into prompts to influence the model's tone, fostering responses that convey specific emotions or empathy. & \cite{Hewing2024TheModels}  \\ \hline
    Ensemble Refinement (ER) & Generates multiple response paths and refines them into a consensus answer, improving accuracy through ensemble reasoning. & \cite{Vatsal2024ATasks} \\ \hline
    Expert Prompting & Guides the model to adopt an expert's perspective in a specific domain, enhancing depth and accuracy of its responses. & \cite{KepelAutonomousModels} \\ \hline
    Federated Self-Consistency & Aggregates multiple model responses generated under varied conditions to enhance consistency and reliability of the answers. & \cite{Vatsal2024ATasks} \\ \hline
    Few-Shot Prompting & Provides the model with a few annotated examples to illustrate task structure, guiding its reasoning and enhancing generalisation for more accurate responses. & \cite{RaviOPTIMIZATIONLEARNING}, \cite{YuDiverseMetrics}, \cite{Schick2020ExploitingInference}, \cite{Rubin2021LearningLearning}, \cite{Chen2023UnleashingReview}, \cite{ChenAEducation}, \cite{He2024PositionManipulation}, \cite{Sahoo2024AApplications} \\ \hline
    Generated Knowledge & Enables the model to generate and utilize additional context or background information prior to answering, enhancing understanding and response quality. & \cite{Chen2023UnleashingReview} \\ \hline
    Implicit Retrieval Augmented Generation (Implicit RAG) & Allows the model to implicitly integrate relevant external information into responses, enhancing accuracy without explicit retrieval steps. & \cite{Vatsal2024ATasks} \\ \hline
    In-Context Learning & Includes examples within the prompt to guide the model's understanding and adaptation to the specific task or style required. & \cite{Brown2020LanguageLearners}, \cite{Nye2021ShowModels}, \cite{DongALearning}, \cite{Shin2023PromptCode}, \cite{Shi2023PromptModels}, \cite{ChenAEducation} \\ \hline
    Instructed Prompting & Provides explicit instructions to the model within the prompt to focus on essential information and disregard irrelevant details. & \cite{Vatsal2024ATasks} \\ \hline
    Least-to-Most Prompting & Encourages solving problems by starting with the simplest sub-problems and sequentially addressing more complex parts. & \cite{Chen2023UnleashingReview} \\ \hline
    Logical Thoughts (LoT) & Prompts the model to utilize formal logic principles to improve reasoning and inference in zero-shot tasks. & \cite{Vatsal2024ATasks} \\ \hline
    Maieutic Prompting & Engages the model in self-questioning and iterative refinement to produce well-reasoned, contradiction-free responses. & \cite{Vatsal2024ATasks} \\ \hline
    MathPrompter & Guides the model to produce and solve mathematical expressions step-by-step, enhancing accuracy in mathematical tasks. & \cite{Vatsal2024ATasks} \\ \hline
    Metacognitive Prompting (MP) & Encourages the model to reflect on and assess its own reasoning process, improving self-awareness and response accuracy. & \cite{Vatsal2024ATasks} \\ \hline
    Multi-Turn Conversational Prompting & Allows the model to maintain and utilize conversation history over multiple turns for coherent and context-aware interactions. & \cite{Muktadir2023APrompting} \\ \hline
    Multimodal Prompting & Combines various input modalities within prompts (e.g., text, images) to provide comprehensive context for the model. & \cite{Muktadir2023APrompting} \\ \hline
    Multimodal Prompt Learning (MaPLe) & Learnable prompts optimize model performance across multiple modalities simultaneously, enhancing cross-modal understanding. & \cite{Chen2023UnleashingReview} \\ \hline
    Negative Prompting & Uses prompts that specify undesired attributes or content to guide the model away from producing certain types of outputs. & \cite{Bruni2025BenchmarkingModels} \\ \hline
    One-Shot Prompting & Includes a single example in the prompt to demonstrate the task and guide the model's response. & \cite{Chen2023UnleashingReview} \\ \hline
    Output Formatting & Guides the model to produce responses in a predefined, structured format for consistent and easy downstream use. & \cite{ChenAEducation} \\ \hline
    \end{tabular}
\end{table}

\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Unique Prompting Techniques and Strategies - continued}
\begin{tabular}{|p{3.5cm}|p{9cm}|p{2cm}|} 
    \hline
    Placeholders \& Delimiters & Employs tokens and delimiters to structure prompts, allowing for flexible templates with clearly defined variable sections. & \cite{Hewing2024TheModels}  \\ \hline
    Position Engineering & Adjusts token positions in prompts to optimize model attention and enhance response relevance and quality. & \cite{He2024PositionManipulation} \\ \hline
    Program of Thoughts (PoT) & Combines natural language with programming logic or pseudocode, assisting the model in detailed computational reasoning tasks. & \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks} \\ \hline
    Program-Aided Language Models (PAL) & Incorporates code execution or programming within language modeling, enabling the model to perform complex computations for enhanced problem-solving. & \cite{Vatsal2024ATasks} \\ \hline
    Prompt Optimization & Refines prompt wording and structure through iterative testing to maximize output quality and task performance. & \cite{Chen2023UnleashingReview} \\ \hline
    Prompt Pattern Catalog & Provides a curated collection of effective prompt templates and patterns to standardize and guide prompt engineering. & \cite{Chen2023UnleashingReview} \\ \hline
    Prompt Space & Explores the vector space of prompts using embeddings and mathematical techniques to identify effective prompt representations. & \cite{Shi2023PromptModels} \\ \hline
    Recursive Criticism and Improvement (RCI) & Enables the model to iteratively critique and refine its outputs, correcting errors through self-review. & \cite{Bruni2025BenchmarkingModels} \\ \hline
    ReAct Framework & Integrates reasoning and action by enabling the model to think through problems and perform actions (like tool use) within the same prompt. & \cite{Yao2022ReAct:Models}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications} \\ \hline
    Rephrase and Respond (RaR) & Prompts the model to rephrase the input before responding, enhancing understanding and clarity in its final answer. & \cite{Hewing2024TheModels}  \\ \hline
    Retrieval Augmented Generation (RAG) & Combines information retrieval with generation by incorporating relevant external data into prompts, enhancing accuracy and reducing hallucinations. & \cite{Lewis2020Retrieval-AugmentedTasks}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{ChenAEducation}, \cite{He2024PositionManipulation} \\ \hline
    Role-Prompting & Assigns the model a specific role or persona to influence tone, style, and depth, guiding responses to align with that role. &  \cite{Chen2023UnleashingReview}, \cite{KepelAutonomousModels}, \cite{BraunCanPrompts}, \cite{ChenAEducation}, \cite{Hewing2024TheModels} \\ \hline
    Scratchpad Prompting & Has the model generate intermediate reasoning steps or calculations before the final answer, improving complex problem solving. & \cite{Sahoo2024AApplications}, \cite{Bruni2025BenchmarkingModels} \\ \hline
    Security-focused Prompt Prefix & Employs a security-conscious prefix in prompts to guide the model towards producing outputs that are aware of and avoid security vulnerabilities. & \cite{Bruni2025BenchmarkingModels} \\ \hline
    Simple Prompting & Provides direct, uncomplicated instructions to the model, relying on its inherent understanding to generate the desired output. & \cite{ChenAEducation} \\ \hline
    Structured Chain-of-Thought (SCoT) & Structures the model's reasoning steps explicitly, using formats like lists or sequences, to enhance clarity in chain-of-thought. & \cite{Vatsal2024ATasks} \\ \hline
    System 2 Attention Prompting (S2A) & Encourages the model to focus on critical input components by emphasizing or reprocessing key information, enhancing deliberate reasoning. & \cite{Vatsal2024ATasks} \\ \hline
    Take a Step Back Prompting & Guides the model to pause and reflect from a broader perspective, reassessing its reasoning to improve or correct its responses. & \cite{Bruni2025BenchmarkingModels} \\ \hline
    Task-Specific Prompting & Designs prompts customized for specific tasks or domains, ensuring the model's responses are highly relevant and effective. & \cite{Shin2023PromptCode} \\ \hline
    Template-Based Generation & Utilizes fixed prompt templates with placeholders, ensuring generated outputs adhere to a consistent and pre-defined structure. & \cite{Muktadir2023APrompting} \\ \hline
    Thread of Thought (ThoT) & Segments complex contexts into smaller, manageable pieces, enabling incremental reasoning and analysis by the model. & \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks}, \cite{Chen2023UnleashingReview} \\ \hline
    Tree-of-Thoughts & Explores various reasoning paths through a branching tree structure, allowing the model to evaluate alternatives and converge on a well-considered answer. & \cite{KepelAutonomousModels}, \cite{Vatsal2024ATasks} \\ \hline
    Try Several Times & Generates multiple responses to the same prompt and selects or aggregates them to improve reliability and overcome variability. & \cite{Chen2023UnleashingReview} \\ \hline
    Unified Combined Annotation and Error Analysis Prompting & Integrates task guidelines with error analysis instructions in the prompt, enhancing model performance by promoting awareness of potential mistakes. & \cite{Vatsal2024ATasks} \\ \hline
\end{tabular}
\end{table}

\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}

### END RESEARCH PAPER ###

        ### END TASK ###
    '''

    await Console(magentic_one_team.run_stream(task=task))


asyncio.run(main())