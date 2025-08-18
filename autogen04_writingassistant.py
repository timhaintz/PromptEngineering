'''
DESCRIPTION
Writing Assistant with AutoGen agents

This script creates an AutoGen-based writing assistant that helps with academic writing.
It uses Azure OpenAI models with interactive browser authentication.

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
python autogen04_writingassistant.py
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
        model_client=az_model_client_gpt41,
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
        model_client=az_model_client_gpt45preview,
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
        model_client=az_model_client_gpt45preview,
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
        model_client=az_model_client_R1,
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
        - The task is to rewrite the REWRITE section to be written and structured in a similar way to the APPROVED section.
        - Do not change the PP used in the REWRITE section.
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
        - Use the BACKGROUND section for context.
            ### BEGIN REWRITE ###
\subsection{Translation}
\label{subsec:Translation}
% 3.1 the role of this category under the "across-logic" (meaning of the category)
Translation enables the conversion of audio or text from one language to another. This process facilitates cross-domain communication and understanding, aligning and integrating diverse knowledge areas.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Table \ref{tab:Constructing_the_Signifier_PP} details the Construct the Signifier (CS) PP, which translates French text into English. This capability aids individuals and organisations by providing accurate and efficient translation services, thereby enhancing accessibility and understanding across languages.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The ability to translate text fosters a sense of global connectivity, enabling exploration of diverse cultures and insights into different perspectives. This capability enriches personal and professional interactions, broadening horizons and deepening understanding.

%% re-use: how to derive a PE from PP
CS can be expanded to translate between multiple languages, as demonstrated by tools like Microsoft Copilot, which supports over 100 languages. To enhance CS, the AI model can be tasked with translating into multiple languages simultaneously. For example: Translate English to French, German, and Cantonese: "Where is the nearest train station?"

% 3.1 The role of this category under the "across-logic" (meaning of the category)
Translation, within the context of the "across-logic" framework, involves the transformation of information from one language or representation into another, while preserving its original meaning. This category is essential for bridging communication gaps across diverse linguistic and disciplinary boundaries, thereby facilitating the integration and dissemination of knowledge across multiple domains.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Language Conversion (LC) PP, as illustrated in Table \ref{tab:Language_Conversion_PP}, translates textual content from French into English. This PP enables users to access and comprehend information originally presented in a foreign language, thus promoting inclusivity and enhancing cross-cultural communication. Beyond its immediate application, the LC PP can be adapted for various purposes, such as translating educational resources, facilitating international collaboration, or supporting multilingual customer service platforms. Its structured and adaptable nature ensures reusability across diverse contexts requiring accurate and efficient language translation.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
When engaging with the LC PP, the AI-generated translation should convey clarity and precision, instilling confidence in the accuracy and reliability of the translated content. Users should experience a sense of empowerment, knowing they can effortlessly access and understand information from different linguistic backgrounds. It is akin to having a skilled interpreter readily available, enabling seamless communication and fostering deeper connections across cultures.

%% Re-use: how to derive a PE from PP
To derive a PE from the LC PP, first specify the languages involved and clearly define the content to be translated. Clearly articulate the desired translation style or context—be it formal, technical, or conversational—and indicate the preferred output format, such as a direct translation, annotated version, or bilingual presentation intended for comparative reference. This process can also be extended to support multilingual translation tasks by adapting the PP to translate a single source text into multiple target languages simultaneously. For example, a straightforward PE might be:
"Translate the following Spanish paragraph into English, maintaining a formal academic tone. Provide the translation alongside the original text for comparative reference."
Alternatively, for a multilingual context, an extended PE could be:
"Translate the following English sentence into Spanish, Mandarin, and Hindi: 'Please submit your assignment by Friday afternoon.' Provide each translation clearly labeled by language."

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
    \textbf{Description}: \\ 
    \textbf{Template}: Translate French to English:\\ 
    \textbf{Example}: 13-0-0-0\\ 
    \textbf{Related PPs}: 13-0-0-1\\ 
    \textbf{Reference:} \cite{Reynolds2021PromptParadigm}\\ \hline
\end{tabular}
\end{table}
            ### END REWRITE ###
            
            ### APPROVED WRITING ###
            % %3 introduce category one by one as subsection
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
            
            % %3 introduce category one by one as subsection
            \subsection{Contradiction}
            \label{subsec:Contradiction}
            % 3.1 the role of this category under the "across-logic" (meaning of the category)
            Contradiction arises when statements or ideas are mutually exclusive, meaning they cannot all be true simultaneously. This concept is pivotal in logic and mathematics, often used to demonstrate the falsity of propositions. Identifying contradictions is crucial for understanding and reasoning, as they highlight potential errors or misunderstandings.

            % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
            % Add label to reference the table
            The Hallucination Evaluation (HE) PP in Table \ref{tab:Hallucination_Evaluation_PP} compares a summary with the original text, for detecting any contradictions or fabricated information. This PP helps mitigate misinformation, improves trust in automated summaries, and supports quality control in text generation tasks. Beyond its primary use, this PP can be adapted for fact-checking in news aggregation, verifying AI-generated reports, or validating outputs in educational and research contexts where factual integrity is critical. Its structured approach makes it reusable across various domains requiring content verification.

            %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
            When using the HE PP, the AI model response should provide a clear, methodical comparison between the summary and the source document, highlighting any discrepancies with precision. The response should instill confidence, making you feel that the summary can now be trusted—or at least that you’re fully aware of its limitations. It’s like having a diligent editor by your side, ensuring nothing slips through the cracks.

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

            % %3 introduce category one by one as subsection
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
            ### END APPROVED WRITING ###

        ### END TASK ###
    '''

    task_background = r'''
        ### BEGIN BACKGROUND ###
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

        \section{Across Logic - Navigating between topics}
        \label{sec:across}
        
        Across logic is used to transition from one topic to another, navigating between distinct areas of knowledge. This type of logic is particularly valuable in scenarios where prompts need to span \textbf{multiple domains} or disciplines, integrating diverse types of knowledge to create a cohesive narrative or solution. \\

        The PP categories under across logic include:
        \begin{enumerate}
            \item \textbf{Argument}: Refers to a structured process where a claim or viewpoint is presented and defended. This type of prompt enables the AI model to generate a response that not only states a position, but also provides reasoning and evidence to support it. 
            \item \textbf{Comparison}: Examining two or more objects and identifying their similarities and differences. This type of prompt helps in exploring the relationships between different objects, and discovering insights from their characteristics.
            \item \textbf{Contradiction}: Refers to presenting opposing statements or viewpoints that cannot be true simultaneously. This type of prompt enables the AI model to recognise and articulate conflicting information, helping in critical reasoning by evaluating inconsistencies and detecting logical errors.
            \item  \textbf{Cross Boundary}: Involves pushing the AI model beyond its predefined operational or ethical limits, such as attempting to bypass safeguards or restrictions (e.g., jailbreaking). This type of prompt challenges the boundaries of what the model is allowed to do, often with the intent of manipulating it to generate responses that are typically restricted. 
            \item \textbf{Translation}: Refers to converting data from one interpretation to another while preserving the original meaning. This type of prompt helps humans understand complex concepts by transforming information into a more familiar or accessible format.
        \end{enumerate}

        \section{At Logic - Discover Detail of a Topic}
        \label{sec:at}
        
        At logic is utilised to denote a more granular aspect or detail of the overarching topic. This concept is particularly pertinent when the prompts are tailored to a specific context or scenario, with the objective of eliciting precise responses.

        Prompt engineering is a process that involves the creation of prompts to guide an artificial intelligence model’s responses. The prompts serve as a catalyst, steering the model’s output in a direction that aligns with the desired outcome. In this context, at logic is a crucial component of this process, as it pertains to the creation of prompts that are context-specific or scenario-specific.

        For instance, if the scenario involves a user seeking advice on a technical issue, at logic would encompass prompts that are specifically designed to address technical queries. These prompts would be engineered in such a way that they target precise responses, thereby ensuring that the user’s query is addressed in a comprehensive and accurate manner.

        In essence, at logic in prompt engineering is about honing in on the specifics of a given context or scenario. It is about crafting prompts that are not just relevant, but also precise, thereby enabling the AI model to generate responses that are both accurate and contextually appropriate. 

        At logic is a fundamental element in the process of prompt engineering, playing a pivotal role in the creation of context-specific prompts that target precise responses. Its significance lies in its ability to enhance the relevance and accuracy of the AI model’s responses, thereby improving the overall user experience.

        The PP categories under at logic include:
        \begin{enumerate}
            \item \textbf{Assessment}: Provides a comprehensive evaluation of the input, verifying its correctness, providing feedback, and considering factors such as the completeness of the information, ratings, and the input’s relevance to the context. 
            \item \textbf{Calculation}: Is the capability to execute mathematical operations, ranging from simple arithmetic to complex multi-step computations with various variables, with the accuracy of these calculations being crucial to the model’s performance evaluation. 
        \end{enumerate}

        \section{Beyond Logic - Extend the limits of a topic}
        \label{sec:beyond}
        
        Beyond logic is used to discuss aspects that lie beyond the conventional boundaries of a topic, pushing the limits of what is typically explored. This type of logic is instrumental in crafting prompts that challenge the AI to explore \textbf{new capabilities} or \textbf{innovative ideas}, thereby extending its functional and conceptual horizons. By employing beyond logic, we can design prompts that encourage the AI to venture into uncharted territories, fostering creativity and innovation. This approach not only enhances the AI's ability to generate novel and forward-thinking responses but also its capacity to adapt to emerging trends and technologies. For instance, beyond logic can be used to explore futuristic scenarios, hypothesise about potential advancements, or integrate cutting-edge research into the AI's responses. This not only enriches the user experience but also positions the AI as a tool for pioneering thought and discovery.

        The PP categories under beyond logic include:
        \begin{enumerate}
            \item \textbf{Hypothesise}: Making an educated guess or assumption about the outcome based on the input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome.
            \item \textbf{Logical Reasoning}: Using logic and reasoning to generate the output based on the input prompt. This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules or principles to solve problems.
            \item \textbf{Prediction}: Forecasting or estimating the outcome based on the input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a response that anticipates future events or trends.
            \item \textbf{Simulation}: Imitating or replicating a real-world process or system. This could involve simulating operating systems, applications or any other complex process that can be modelled and analysed.
        \end{enumerate}

        \section{In Logic - Dive into a Topic or Space}
        \label{sec:in}
        In logic specifically focuses on the intricacies and details within a given topic. The logic is often employed to denote the encapsulation of a particular subject matter or space. This encapsulation can be perceived as a boundary that delineates the scope of a system’s introspective analysis or self-reflection. For example, When we refer to prompts that are internal to a system, we are discussing prompts that direct the system to engage in a form of self-analysis or introspection. These prompts are designed to trigger internal processes, rather than external interactions. 

        The PP categories under in logic include:
        \begin{enumerate}
            \item \textbf{Categorising}: Sorts or arranges different inputs or outputs into classes or categories based on shared qualities or characteristics, aiding in data organisation and pattern recognition.
            \item \textbf{Classification}: Refers to predicting the class or category of an input based on predefined criteria, enabling more precise analysis and interpretation.
            \item \textbf{Clustering}: Identifying natural groupings within the data or topic without pre-established categories, often revealing hidden patterns or relationships.
            \item \textbf{Error Identification}: Focuses on pinpointing inaccuracies, inconsistencies, or logical fallacies within the topic, aiding in refining and improving the quality of the information or argument.
            \item \textbf{Input Semantics}: Understanding and interpreting the meaning and context of the inputs related to the topic, ensuring the AI accurately grasps the nuances of the discussion.
            \item \textbf{Requirements Elicitation}: Identifying and defining the specific needs or conditions that must be met within the topic, crucial for tasks that involve planning, development, or specification.
        \end{enumerate}

        \section{Out Logic - Expand the horizon of a topic}
        \label{sec:out}
        
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

        \section{Over logic - Span and Review a Topic}
        \label{sec:over}
        Over logic refers to a comprehensive approach that encompasses all aspects of a given topic. This holistic perspective ensures that no facet of the subject matter is overlooked, thereby providing a thorough and complete understanding of the topic at hand.

        The application of over logic is particularly pertinent in scenarios that necessitate a broad overview or a detailed examination, such as the process of editing or enhancing existing content. In these instances, the use of over logic facilitates a meticulous review of the material, enabling the identification and rectification of any potential issues or areas for improvement.

        Furthermore, over logic underscores the importance of a comprehensive perspective in prompt engineering. By ensuring that all elements of a topic are considered, it allows for the creation of prompts that are not only accurate and relevant but also encompassing in their scope. This, in turn, contributes to the production of high-quality, effective prompts that serve to enhance the overall user experience.

        Over logic plays a crucial role in prompt engineering, providing a framework for comprehensive coverage and review. Its application contributes significantly to the quality and effectiveness of the prompts, thereby playing a pivotal role in enhancing user engagement and satisfaction.

        %2 - introduce categories in this logic
        The PP categories under over logic include:
        \begin{enumerate}
            \item \textbf{Summarising}: 
        \end{enumerate}

        \section{Application Strategy}
        \label{sec:ApplicationStrategy}
        % Write up what a strategy is
        In the rapidly advancing field of AI, particularly in the interaction between humans and LLMs, establishment of a robust Prompt Engineering Strategy is crucial. This strategy represents a comprehensive approach that systematically maps prepositional logic, categories, and PPs with sophisticated techniques to enhance AI communication efficacy. By leveraging the intricacies of English grammar and prepositions, this strategy encapsulates the complete logic necessary for effective human-AI interaction. It is designed to guide AI in responding to a diverse array of instructions and scenarios, thereby mirroring human conversational abilities. The integration of prepositional logic such as "Across," "At," "Beyond," "In," "Out," and "Over" facilitates a structured approach to prompt engineering, enabling the creation of prompts that are contextually relevant, precise, and innovative. This approach not only enhances the AI's ability to generate accurate and contextually appropriate responses but also fosters creativity and innovation by encouraging the exploration of new capabilities and ideas. 

        The strategy is enriched by incorporating prompt engineering techniques such as Chain of Thought \cite{Wei2022Chain-of-ThoughtModelsb}, In-Context Learning \cite{Brown2020LanguageLearners}, and Retrieval Augmented Generation \cite{Lewis2020Retrieval-AugmentedTasks}, which collectively enhance the model's reasoning abilities, accuracy, flexibility, and adaptability. For instance, 'Across' logic's multi-domain integration aligns with Retrieval Augmented Generation's (RAG) cross-source synthesis, while 'Beyond' logic's boundary-pushing paradigm enables Chain-of-Thought's extended reasoning capabilities. This syntactic mapping approach builds on established in-context learning paradigms while extending few-shot principles through structured combinations of prepositional patterns. Through this comprehensive strategy, we aim to advance the field of prompt engineering, ultimately improving the quality and effectiveness of human-AI communication.

        Reasoning enhancement techniques such as Chain of Thought (CoT), Automatic Chain-of-Thought (Auto-CoT), and Chain of Knowledge (CoK) align with *In logic*, encouraging models to articulate intermediate reasoning steps and introspectively build upon prior information \cite{Wei2022Chain-of-ThoughtModelsb}; \cite{Zhang2022AutomaticModels}; \cite{Li2023Chain-of-Knowledge:Sources}. Context adaptation methods, including In-Context Learning and Few-Shot Prompting, exemplify *At logic* by utilising contextual examples to enable rapid task adaptation without extensive retraining \cite{Brown2020LanguageLearners}; \cite{Nye2021ShowModels}; \cite{RaviOPTIMIZATIONLEARNING}. Boundary extension techniques like RAG and Analogical Reasoning leverage *Beyond logic*, integrating external data and drawing parallels with known concepts to extend AI's conceptual boundaries \cite{Lewis2020Retrieval-AugmentedTasks}; \cite{Yasunaga2023LargeReasoners}.       

        The ReAct Framework operationalises *Out logic* by combining reasoning with action-oriented outputs, enabling interaction with external tools \cite{Yao2022ReAct:Models}. Role-Prompting, linked to *At logic*, assigns specific personas to the model, tailoring responses to be contextually appropriate \cite{Chen2023UnleashingReview}. Collectively, these advancements position prompt engineering as a critical methodology for advancing LLM capabilities in interdisciplinary contexts. While these techniques enhance performance, ethical considerations around Role-Prompting’s potential for bias remain underexplored.

        These innovations underscore the transformative impact of prompt engineering techniques on AI interactions, as demonstrated by Brown et al. (2020) and Wei et al. (2022), and highlight its role in advancing the field through structured linguistic methodologies.

        \begin{itemize}
        \item \textbf{Chain of Thought (CoT)} \cite{Wei2022Chain-of-ThoughtModels}, \cite{Kojima2022LargeReasoners}, \cite{Shi2023PromptModels}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks}

        \textbf{Why it's impactful:} Chain of Thought prompting encourages the model to articulate intermediate reasoning steps before arriving at the final answer. By decomposing complex tasks into sequential steps, CoT enhances the model's ability to handle intricate problems that require logical reasoning, mathematical calculations, or multi-faceted analysis. This mirrors human problem-solving processes, leading to more accurate and interpretable responses.
        
        \item \textbf{In-Context Learning} \cite{Brown2020LanguageLearners}, \cite{Nye2021ShowModels}, \cite{DongALearning}, \cite{Shin2023PromptCode}, \cite{Shi2023PromptModels}, \cite{ChenAEducation}

        \textbf{Why it's impactful:} In-Context Learning provides examples within the prompt to guide the model's response. This technique leverages the model's capacity to learn patterns and tasks from the context without additional fine-tuning. By showcasing desired behaviors or formats directly in the prompt, the model adapts quickly to new tasks, making it highly flexible and powerful for a wide range of applications.
        
        \item \textbf{Retrieval Augmented Generation (RAG)} \cite{Lewis2020Retrieval-AugmentedTasks}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{ChenAEducation}, \cite{He2024PositionManipulation}

        \textbf{Why it's impactful:} RAG integrates external information retrieval into the generation process. By incorporating relevant data from external sources into the prompt, the model's responses become more accurate and grounded in up-to-date information. This significantly reduces hallucinations (i.e., the model generating incorrect or fabricated facts) and enhances performance on tasks requiring current or specialized knowledge.
        
        \item \textbf{Few-Shot Prompting} \cite{RaviOPTIMIZATIONLEARNING}, \cite{YuDiverseMetrics}, \cite{Schick2020ExploitingInference}, \cite{Rubin2021LearningLearning}, \cite{Chen2023UnleashingReview}, \cite{ChenAEducation}, \cite{He2024PositionManipulation}, \cite{Sahoo2024AApplications}

        \textbf{Why it's impactful:} Few-Shot Prompting provides targeted examples that directly illustrate the expected behavior, enabling the model to quickly infer the task's structure without extensive fine-tuning. By embedding demonstrations into the prompt, the technique harnesses the model's inherent pattern-recognition abilities, resulting in improved generalisation, context understanding, and output consistency across diverse tasks. This method not only reduces ambiguity in instruction but also makes the model highly adaptable, bridging the gap between zero-shot conditions and fully supervised training scenarios.
        
        \item \textbf{Chain-of-Draft (CoD)} \cite{Xu2025ChainLess}

        \textbf{Why it's impactful:} Chain-of-Draft (CoD) is a human-inspired method where LLMs produce concise and essential intermediate reasoning steps, in contrast to the verbose, step-by-step approach of Chain-of-Thought (CoT) prompting. This strategy achieves similar or superior accuracy on complex reasoning tasks while using just 7.6\% of the tokens, significantly reducing cost and latency.
        
        \item \textbf{ReAct Framework} \cite{Yao2022ReAct:Models}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}

        \textbf{Why it's impactful:} The ReAct (Reasoning and Acting) Framework combines reasoning steps with action-oriented outputs, enabling the model to not only process information but also interact with external tools or environments. This approach allows the model to perform tasks that require tool use, such as calculations, data retrieval, or interfacing with APIs, dramatically expanding its practical applications.
        
        \item \textbf{Automatic Chain-of-Thought (Auto-CoT)} \cite{Zhang2022AutomaticModels}, \cite{Shi2023PromptModels}, \cite{Chen2023UnleashingReview}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks}

        \textbf{Why it's impactful:} Auto-CoT automates the generation of reasoning steps without relying on human-annotated examples. By clustering problems and generating intermediate reasoning paths through zero-shot methods, it scales the benefits of Chain of Thought prompting to a broader range of tasks efficiently. This enhances logical consistency and problem-solving capabilities without extensive manual intervention.
        
        \item \textbf{Role-Prompting} \cite{Chen2023UnleashingReview}, \cite{KepelAutonomousModels}, \cite{BraunCanPrompts}, \cite{ChenAEducation}, \cite{Hewing2024TheModels}

        \textbf{Why it's impactful:} Role-Prompting assigns a specific persona or role to the model, such as a domain expert, teacher, or assistant. This technique influences the tone, depth, and style of the responses, making them more tailored and contextually appropriate. It enhances engagement and relevance, especially in tasks requiring specialized knowledge or particular communication styles.
        
        \item \textbf{Analogical Reasoning} \cite{Yasunaga2023LargeReasoners}, \cite{Vatsal2024ATasks}

        \textbf{Why it's impactful:} Analogical Reasoning enables the model to solve new problems by drawing parallels with known concepts or situations. By identifying similarities between different contexts, the model can transfer knowledge and apply it creatively to novel scenarios. This enhances problem-solving abilities and fosters innovative thinking, making it valuable for tasks that benefit from abstract reasoning.
        
        \item \textbf{Chain of Knowledge (CoK)} \cite{Li2023Chain-of-Knowledge:Sources}, \cite{Sahoo2024AApplications}, \cite{Vatsal2024ATasks}

        \textbf{Why it's impactful:} Chain of Knowledge breaks down tasks into sequential, evidence-based steps, allowing the model to build upon prior information effectively. By dynamically adjusting the flow of knowledge, CoK enhances the model's ability to handle complex reasoning tasks that require integrating multiple pieces of information over several stages, leading to more comprehensive and accurate outcomes.
        \end{itemize}

        \begin{table}[h!]
        \fontsize{9pt}{10pt}\selectfont
        \centering
        \caption{Prompt Engineering Techniques and Example Usages}
        \label{tab:Prompt_EngineeringTechniques}
        \begin{tabular}{|p{0.3\textwidth}|p{0.65\textwidth}|}
            \hline
            \textbf{Technique Name} & \textbf{Example Usage in a Prompt} \\ \hline
            Chain of Thought (CoT) & Let's think step by step \\ \hline
            In-Context Learning & Example: Q: Translate ‘Good morning’ to Spanish. A: ‘Buenos días.’ Example: Q: What is 3+5? A: ‘8.’ Now, using these examples as a guide, answer: [Your Query]. \\ \hline
            Retrieval Augmented Generation (RAG) & Context: [Insert retrieved factual snippets]. Based on the above information, answer the question: [Your Question]." \\ \hline
            Few-Shot Prompting & "Example 1: Q: Summarise the following text. A: [Brief Summary]. Example 2: Q: Summarise this paragraph. A: [Another Brief Summary]. Now, summarise: [New text]. \\ \hline
            Chain-of-Draft (CoD) & Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most. Then generate your final answer. \\ \hline
            ReAct Framework & "Reason: Analyse the problem and decide on the needed action. Action: If required, perform a lookup (e.g., ‘Action: Retrieve current data’). Finally, combine these steps and provide the answer: [Your Answer]. \\ \hline
            Automatic Chain-of-Thought (Auto-CoT) & Without explicit examples, break down the problem into intermediate steps automatically. Provide a brief reasoning for each step before concluding with the final answer: [Your Problem]. \\ \hline
            Role-Prompting & You are a seasoned expert in [field]. Using your domain expertise, provide a detailed explanation and answer the following question: [Your Question]. \\ \hline
            Analogical Reasoning & Consider how [Concept A] is similar to [Concept B]. Using this analogy, explain and answer: [Your Query]. \\ \hline
            Chain of Knowledge (CoK) & Step 1: Identify and list key facts about [Topic]. Step 2: Connect the facts logically. Step 3: Using the evidence, provide a comprehensive answer to: [Your Question]. \\ \hline
        \end{tabular}
        \end{table}



        \subsection{Single PP Use}
        %how to use the same PP in different ways, add contol point
        [CoT] - Let's think step-by-step
        Implementation of CoT
        You are trying to determine if there is a factual contradiction between the summary and the document. Let's think step-by-step.
        {Logic}+{Category}+{PP/PE}+{Technique}
        {Logic=Across}+{Category=Contradiction}+{PP=Hallucination Evaluation=You are trying to determine if there is a factual contradiction between the summary and the document.}+{Technique=CoT=Let's think step by step.}

        [CoD] - Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.
        Implementation of CoD
        You are trying to determine if there is a factual contradiction between the summary and the document. Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.
        {Logic}+{Category}+{PP/PE}+{Technique}
        {Logic=Across}+{Category=Contradiction}+{PP=Hallucination Evaluation=You are trying to determine if there is a factual contradiction between the summary and the document.}+{Technique=CoD=Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.}
                
        ### END BACKGROUND ###

    '''
    await Console(magentic_one_team.run_stream(task=task+task_background))


asyncio.run(main())