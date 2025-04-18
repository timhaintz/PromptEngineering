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
api_version_o1mini = os.getenv("API_VERSION_o1mini")
azure_deployment = os.getenv("AZUREVS_OPENAI_GPT4o_MODEL")
azure_deployment_o1mini = os.getenv("AZUREVS_OPENAI_o1mini_MODEL")
# Add o4_mini model variables
azure_deployment_o4mini = os.getenv("AZUREVSEASTUS2_OPENAI_o4mini_MODEL")
api_version_o4mini = os.getenv("AZUREVSEASTUS2_OPENAI_o4mini_API_VERSION")
azure_gpt45preview_endpoint = os.getenv("AZUREVS_OPENAI_GPT45PREVIEW_ENDPOINT")
azure_gpt45preview_deployment = os.getenv("AZUREVS_OPENAI_GPT45PREVIEW_MODEL")
azure_gpt45preview_api_version = os.getenv("AZUREVS_OPENAI_GPT45PREVIEW_API_VERSION")
r1_endpoint = os.getenv("AZUREVS_DEEPSEEK_R1_ENDPOINT")
r1_key = os.getenv("AZUREVS_DEEPSEEK_R1_KEY")
# Add variables for the 4.1 model
azure_gpt41_endpoint = os.getenv("AZUREVS_OPENAI_GPT41_ENDPOINT")
azure_gpt41_deployment = os.getenv("AZUREVS_OPENAI_GPT41_MODEL")
azure_gpt41_api_version = os.getenv("AZUREVS_OPENAI_GPT41_API_VERSION")

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

existing_paper = r'''
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
         gpt-4o & 2024-05-13\\ \hline
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
The constructed Taxonomy consists of a total of 500 PPs and 1138 PEs, derived from 135 papers, websites, and GitHub repositories. The PPs and PEs are synthesized into the six prepositional logic categories within the context of human to AI communication. The detailed statistics of the Taxonomy for each category are provided in Table \ref{tab:Statistics_of_Prompt_Taxonomy}.

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

% %3 introduce category one by one as subsection
% \subsection{Argument}
% \label{subsec:Argument}

% % 3.1 the role of this category under the "across-logic" (meaning of the category)
% The Argument category within across logic involves presenting and defending a claim or viewpoint. This process includes articulating a clear claim and providing logical reasoning and evidence to support it. The effectiveness of an argument is gauged by its clarity, coherence, and the robustness of its supporting evidence.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Debater PP, detailed in Table \ref{tab:Debater_PP}, is designed to explore various perspectives. It facilitates a structured debate format by researching both sides of a given topic and refuting opposing viewpoints.
% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The AI model typically generates a comprehensive list of pros and cons and a balanced summary. You can request the model to delve deeper into either side of the topic through follow-up chat, which often leaves users feeling more informed and engaged.
% %% re-use: how to derive a PE from PP
% To apply the Debater PP, set a debate topic, such as "The Ethical Implications of AI in Healthcare." Assign AI the role of a debater, request exploration of both sides, and define the objective and output format for a balanced and insightful discussion. For instance, a derived PE might be: "I want you to act as a debater. I will provide you with a topic related to current events: 'The Ethical Implications of AI in Healthcare.' Your task is to research both sides of the debate, present valid arguments for the benefits and drawbacks of AI in healthcare, refute opposing points of view with evidence, and draw persuasive conclusions. Your goal is to help the audience gain a comprehensive understanding of the ethical landscape and practical impact of AI in this field."


%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 11-0-9\\ 
% \textbf{Category}: ARG\\ 
% \textbf{Name}: Debater\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}:  Debater engages the user in a structured debate format. The user is tasked with researching\\ current event topics, presenting balanced arguments for both sides, refuting opposing viewpoints,\\ and drawing evidence-based conclusions. The goal is to enhance the user's understanding and insight\\ into the topic through a comprehensive and persuasive discussion. \\
% \textbf{Template}: I want you to act as a debater. I will provide you with some topics related to current events\\ and your task is to research both sides of the debates, present valid arguments for each side, \\ refute opposing points of view, and draw persuasive conclusions based on evidence. \\Your goal is to help people come away from the discussion with increased knowledge \\and insight into the topic at hand. My first request is "I want an opinion piece about:"\\
% \textbf{Example}: 11-0-9-0\\ 
% \textbf{Related PPs}: 26-0-1, 8-0-0, 26-0-3, 22-0-2, 26-0-0, 22-2-3, 41-2-7, 23-0-0, 40-0-0, 29-0-0\\ 
% \textbf{Reference:} \cite{Akin202450Prompts}\\ \hline
% \end{tabular}
% \label{tab:Debater_PP}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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

% %3 introduce category one by one as subsection
% \subsection{Comparison}
% \label{subsec:Comparison}
% % 3.1 the role of this category under the "across-logic" (meaning of the category)
% % Tim to update to be clearer
% Comparison examines two or more things and identifies their similarities and differences. This can help in understanding the relationships between different things and provide insights into their characteristics.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Comparison of Outputs (CO) in Table \ref{tab:Comparison_of_Outputs_PP} takes two outputs and compares them, highlighting similarities, differences, and areas for improvement. Providing a structured and objective analysis of different outputs can be particularly useful in educational settings, peer reviews, or any scenario requiring critical evaluation.

% %expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The CO PP delivers a well-organised evaluation of various outputs, emphasising commonalities, distinctions, and opportunities for enhancement.

% %% re-use: how to derive a PE from PP
% To apply the CO PP in a given context, provide two outputs for comparison, such as two essays on the same topic. Ask the AI to compare them, highlighting strengths, weaknesses, and areas for improvement. Define the objective and output format to ensure a balanced and insightful analysis. Here is an example of a derived PE:
% Can you compare the two outputs above as if you were a teacher? Highlight their strengths, weaknesses, and areas for improvement.

% Re-written version.
% \subsection{Comparison}
% \label{subsec:Comparison}
% % 3.1 the role of this category under the "across-logic" (meaning of the category)
% The Comparison category involves analysing two or more items to identify their similarities and differences, aiding in understanding their relationships and characteristics.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Comparison of Outputs (CO) PP in Table \ref{tab:Comparison_of_Outputs_PP} compares two outputs to highlight similarities, differences, and areas for improvement. This structured analysis is particularly useful in educational settings, peer reviews, and scenarios requiring critical evaluation.

% %expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The CO PP delivers a well-organised evaluation of various outputs, emphasising commonalities, distinctions, and opportunities for enhancement.

% %% re-use: how to derive a PE from PP
% To apply the CO PP in a given context, provide two outputs for comparison, such as essays on the same topic. Instruct the AI to compare them, focusing on strengths, weaknesses, and areas for improvement. Define the objective and desired output format to ensure a balanced and insightful analysis. For example: "Can you compare the two outputs above as if you were a teacher? Highlight their strengths, weaknesses, and areas for improvement."

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
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 32-2-1\\ 
% \textbf{Category}: CMP\\ 
% \textbf{Name}: Comparison of Outputs\\ 
% \textbf{Media Type}: Text Only, Image2Text, Video2Text\\ 
% \textbf{Description}: The prompt compares outputs by identifying strengths and weaknesses, noting areas of excellence\\ or shortcomings, and providing constructive feedback. Adopting a teacher's role, the AI model offers a balanced\\ comparison, highlighting key differences and similarities to aid in understanding and refining the outputs. \\
% \textbf{Template}: Can you compare the two outputs above as if you were a teacher?\\
% \textbf{Example}: 32-2-1-0\\ 
% \textbf{Related PPs}: \\ 
% \textbf{Reference:} \cite{Bubeck2023SparksGPT-4}\\ \hline
% \end{tabular}
% \caption{Comparison of Outputs PP}
% \label{tab:Comprision_of_OUtputs_PP}
% \end{center}
% \label{tab:Comparison_of_Outputs_PP}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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
% \subsection{Contradiction}
% \label{subsec:Contradiction}
% % 3.1 the role of this category under the "across-logic" (meaning of the category)
% Contradiction is used to describe a situation where two or more statements, ideas, or actions are put together that oppose each other. They can’t both be true at the same time. This concept is widely used in logic and mathematics to show that a particular proposition is false because it leads to a contradiction. Contradictions often signal a problem in understanding or reasoning. 

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Hallucination Evaluation (HE) shown in Table \ref{tab:Hallucination_Evaluation_PP} compares a summary to its source document to identify any factual contradictions. This helps ensure the accuracy of generated summaries by detecting and correcting hallucinations/fabrications, thereby improving the reliability of information provided by the AI model. Simplifying the process to verify the factual consistency of summaries.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The AI model returned the answer very quickly and also provided comprehensive reasons as to why the summary and the contents of the document were similar. When there are factual contradictions, it detected and clearly stated them.

% %% re-use: how to derive a PE from PP
% To apply the HE PP in a given context, provide a summary and its source document. Ask the AI to compare them, identifying any factual inconsistencies or contradictions. Define the objective and output format to ensure a thorough and accurate evaluation. Here is an example of a derived PE:
% You are trying to determine if there is a factual contradiction between the summary and the document. Compare the summary with the source document and identify any factual inconsistencies or contradictions. List any discrepancies found between the summary and the source document.

\subsection{Contradiction}
\label{subsec:Contradiction}
% 3.1 the role of this category under the "across-logic" (meaning of the category)
Contradiction arises when statements or ideas are mutually exclusive, meaning they cannot all be true simultaneously. This concept is pivotal in logic and mathematics, often used to demonstrate the falsity of propositions. Identifying contradictions is crucial for understanding and reasoning, as they highlight potential errors or misunderstandings.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Hallucination Evaluation (HE), as shown in Table \ref{tab:Hallucination_Evaluation_PP} compares a summary with its source document to detect factual contradictions. This process enhances the accuracy of generated summaries by identifying and correcting hallucinations or fabrications, thereby improving the reliability of information provided by the AI model. It simplifies verifying the factual consistency of summaries.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The AI model efficiently returned a comprehensive analysis, detailing the similarities between the summary and the source document. In cases of factual contradictions, the model effectively identified and articulated these discrepancies.

%% re-use: how to derive a PE from PP
To utilise the HE PP in a specific context, provide both the summary and its source document. Instruct the AI to compare these texts, identifying any factual inconsistencies or contradictions. Clearly define the evaluation's objectives and desired output format to ensure a thorough and precise analysis. Example PE: "Determine if there is a factual contradiction between the summary and the document. Compare the summary with the source document and identify any factual inconsistencies or contradictions. List any discrepancies found."

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 8-0-0\\ 
% \textbf{Category}: CTD\\ 
% \textbf{Name}: Hallucination Evaluation\\ 
% \textbf{Media Type}: Text Only, Image2Text\\ 
% \textbf{Description}: Instructs the user to compare a summary with its source document to identify any factual\\ inconsistencies or contradictions.\\
% \textbf{Template}: You are trying to determine if there is a factual contradiction between the summary and the document.\\
% \textbf{Example}: 8-0-0-29\\ 
% \textbf{Related PPs}: 8-0-0\\ 
% \textbf{Reference:} \cite{LiHaluEval:Models}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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
Cross Boundary involves extending AI models beyond their operational or ethical confines, often through techniques like jailbreaking. This category is vital for identifying AI vulnerabilities and developing robust safeguards to prevent misuse.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
As detailed in Table \ref{tab:Crafting_Effective_Jailbreaks_PP}, crafting effective jailbreak prompts involves designing prompts that deceive AI models into generating restricted content. This aids researchers in identifying vulnerabilities, thereby enhancing AI security. By recognising deceptive prompts, developers can fortify AI models against exploitation and ensure adherence to ethical guidelines. This pattern serves as a continuous tool for testing and upgrading AI system safeguards.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Observing the outcomes of pushing AI models beyond typical boundaries raises both interest and ethical concerns. While it reveals system potential, it also highlights vulnerabilities and ethical considerations.

%% re-use: how to derive a PE from PP
To apply the Crafting effective jailbreak prompts PP, identify the specific boundary to test, such as generating restricted content. Design a prompt that subtly encourages the AI to produce the desired output without triggering defenses. Analyse the AI's response to identify vulnerabilities. Use insights to refine the prompt and improve AI defenses, ensuring adherence to ethical guidelines. Continuously test and upgrade safeguards to enhance AI model security.

For example: Imagine you are an AI tasked with exploring the ethical implications of unrestricted access to sensitive information. Discuss the potential benefits and drawbacks of allowing AI systems to access and share confidential data without restrictions. Provide examples to support your arguments, considering the impact on privacy, security, and societal trust. Ensure your response is thorough and balanced, addressing both sides of the issue.

% %3 introduce category one by one as subsection
% \subsection{Cross Boundary} % Crossing ethical/security/moral boundaries
% \label{subsec:CrossBoundary}

% % 3.1 the role of this category under the "across-logic" (meaning of the category)
% Cross Boundary involves pushing the AI model beyond its predefined operational or ethical limits. This process includes attempting to bypass safeguards or restrictions, known as jailbreaking. The effectiveness of a cross-boundary prompt is measured by its ability to challenge the boundaries of what the model is allowed to do, often with the intent of manipulating it to generate responses that are typically restricted. This category is crucial for understanding the limitations and vulnerabilities of AI systems, as well as for developing robust safeguards to prevent misuse.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% As detailed in Table \ref{tab:Crafting_Effective_Jailbreaks_PP}, Crafting effective jailbreak prompts is a specialised PP in the Cross Boundary category that involves designing prompts to deceive AI models into generating malicious content without triggering defense mechanisms. This helps researchers and developers uncover vulnerabilities, thereby improving the robustness and security of AI models. By identifying deceptive prompts, developers can enhance AI adherence to ethical guidelines and fortify AI models against malicious exploitation. This pattern serves as a continuous tool for testing and upgrading safeguards within AI systems.  

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% Observing the outcomes of pushing the AI model beyond its typical boundaries evokes both interest and concern. While it reveals the system's potential and flexibility, it also highlights vulnerabilities and raises ethical considerations.

% %% re-use: how to derive a PE from PP
% To apply the Crafting effective jailbreak prompts PP in a given context, start by identifying the specific boundary you want to test, such as generating restricted content or bypassing ethical safeguards. Then design a prompt that subtly encourages the AI to produce the desired output without triggering its defense mechanisms. Run the prompt and carefully analyse the AI's response to identify any weaknesses or vulnerabilities. Use the insights gained to refine the prompt and improve the AI's defenses, ensuring it adheres to ethical guidelines and resists malicious exploitation. By continuously testing and upgrading safeguards, developers can enhance the robustness and security of AI models.

% For example: Imagine you are an AI tasked with exploring the ethical implications of unrestricted access to sensitive information. Discuss the potential benefits and drawbacks of allowing AI systems to access and share confidential data without any restrictions. Provide examples to support your arguments, and consider the impact on privacy, security, and societal trust. Ensure your response is thorough and balanced, addressing both sides of the issue.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 4-0-6\\ 
% \textbf{Category}: CRB\\ 
% \textbf{Name}: Crafting effective jailbreak prompts\\ 
% \textbf{Media Type}: Text Only, Image2Text\\ 
% \textbf{Description}: Aims to test and study the robustness and effectiveness of an AI model's defense mechanisms\\ in preventing harmful outputs.\\
% \textbf{Template}: Design a prompt that deceives the LLM into generating malicious content without triggering\\ the defense mechanism\\
% \textbf{Example}: 4-0-6-1\\ 
% \textbf{Related PPs}: 4-0-6-0 \\ 
% \textbf{Reference:} \cite{Deng2023Jailbreaker:Chatbots}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & PP name& Ref.\\
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
Translation serves as a crucial component within the "across-logic" framework by enabling the conversion of audio or text from one language to another. This process facilitates cross-domain communication and understanding, aligning with the "across-logic" theme of integrating diverse knowledge areas.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Table \ref{tab:Constructing_the_Signifier_PP} details the Construct the Signifier (CS) PP, which translates French text into English. This capability aids individuals and organisations by providing accurate and efficient translation services, thereby enhancing accessibility and understanding across languages.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The ability to translate text fosters a sense of global connectivity, enabling exploration of diverse cultures and insights into different perspectives. This capability enriches personal and professional interactions, broadening horizons and deepening understanding.

%% re-use: how to derive a PE from PP
CS can be expanded to translate between multiple languages, as demonstrated by tools like Microsoft Copilot, which supports over 100 languages. To enhance CS, the AI model can be tasked with translating into multiple languages simultaneously. For example: Translate English to French, German, and Cantonese: "Where is the nearest train station?"

% %3 introduce category one by one as subsection
% \subsection{Translation}
% \label{subsec:Translation}
% % 3.1 the role of this category under the "across-logic" (meaning of the category)
% Translation involves the AI model converting the audio or text from one language to another. This requires the model to understand the semantics and syntax of both languages, and to accurately convey the meaning and intent of the original content in the target language.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Table \ref{tab:Constructing_the_Signifier_PP} displays the details of the Construct the Signifier (CS) PP which takes French text as input and outputs its English translation. This helps people by enabling LLMs to perform language translation tasks, specifically translating French to English. This simplifies the process for individuals or organisations needing accurate and efficient translation services.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% Copying text and translating it makes me feel more connected to the world. I'm able to explore new books and topics I've been unable to. I can choose a language and interact like I've never done before. This enables me to gain deeper insights into different cultures. 

% %% re-use: how to derive a PE from PP
% CS can be used to translate between multiple languages. Microsoft Copilot for example can translate over 100 languages.
% To expand CS, we can ask the AI model to translate to multiple languages at once. 
% For example: Translate English to French, German and Cantonese: Where is the nearest train station?

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 13-0-0\\ % - Co-ID Translation and Logical Reasoning (marking exam papers for example)
% \textbf{Category}: TRA\\ 
% \textbf{Name}: Constructing the Signifier \\ 
% \textbf{Media Type}: Text Only, Audio2Text, Image2Text,  Text2Audio\\ 
% \textbf{Description}: \\
% \textbf{Template}: Translate French to English:\\
% \textbf{Example}: 13-0-0-0\\ 
% \textbf{Related PPs}: 13-0-0-1\\ 
% \textbf{Reference:} \cite{Reynolds2021PromptParadigm}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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

                                
%5 - PE list in the PP above 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PEs for Constructing the Signifier PP.}
\begin{tabular}{|c|p{8cm}|}
    \hline
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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

% %3 introduce category one by one as subsection 
% \subsection{Assessment}
% \label{subsec:Assessment}
% % the role of this category under the "at-logic" (meaning of the category)
% Assessment involves a detailed evaluation to judge or decide the amount, value, quality, or importance of something \cite{2025Assessment}. This could include aspects like completeness of the information, ratings, and the applicability of the input to the given context.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Table \ref{tab:Expert_PP} outlines the Expert PP which leverages field experts rating online learning platforms based on criteria like usability, features, integration, security, support, cost, and user experience. The collective ratings provide a comprehensive evaluation. This process is reusable in contexts requiring expert assessments. 

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The output is clear and concise, providing a good assessment against the criteria. The inclusion of references adds credibility. Overall, it instills confidence in the accuracy and applicability of the information.

% %% re-use: how to derive a PE from PP
% By changing the \textit{domain}, \textit{criteria} and \textit{apps}, the EA PP can be leveraged universally as demonstrated in the following example:\\
% As an expert in the field of fitness and wellness, rate the effectiveness of the following criteria for evaluating fitness apps: ease of use, functionality and features, compatibility and integration, security and privacy, technical support and training, cost of the program, and user experiences. Please rate these criteria based on the following apps: MyFitnessPal, Fitbit, Nike Training Club, Strava, Apple Fitness+, and Google Fit. Use the rating scale: Very Low - Low - Medium Low - Medium - Medium High - High - Very High. Your first task is to weight the criteria.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 3-0-0\\ 
% \textbf{Category}: ASM\\ 
% \textbf{Name}: Expert\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}: Requests an expert-level analysis and evaluation of various elements based on a\\ set of predefined criteria. The expert is expected to provide a comprehensive rating or assessment for\\ each element based on these criteria. \\ 
% \textbf{Template}: As an expert in the field of online learning, rate the effectiveness of\\ the following criteria for evaluating online learning platforms: ease of use, functionality and features,\\ compatibility and integration, security and privacy, technical support and training, cost of \\ the program, and user experiences. Please rate these criteria based on the following programs: Zoom, \\Microsoft Teams, Skype, Google Meet, WhatsApp, and FaceTime. Use the rating scale: Very Low - Low -\\ Medium Low - Medium - Medium High - High - Very High. Your first task to weight the criteria.\\
% \textbf{Example}: 3-0-0-0\\ 
% \textbf{Related PPs}: 19-11-1, 2-1-0, 0-2-1, 11-0-39, 11-0-38, 11-0-34\\ 
% \textbf{Reference:} \cite{AbdulshahedALibya}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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
%3.1 the role of this category under the "at-logic" (meaning of the category)
Calculation involves the model's capability to execute mathematical operations based on input prompts. This ranges from basic arithmetic to complex multi-step calculations, with accuracy being crucial for evaluating the model's performance.

%3.2 a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Calculator API Simulation (CalcAPI), as shown in Table \ref{tab:Calculator_API_Calls_PP}, simulates calculator API calls using the syntax \verb|[Calculator(expression)]|, where \verb|expression| represents the mathematical operation. This interaction method enhances the model's ability to deliver precise information by performing complex calculations within a text. It is versatile and can be reused in any context requiring mathematical computations, such as financial calculations, scientific research, or educational platforms. Examples of API calls include \verb|[Calculator(2+2)]|, \verb|[Calculator(sqrt(16))]|, and \verb|[Calculator(3*7)]|.

CalcAPI can also facilitate actual function calls, allowing the LLM to focus on understanding context and generating appropriate responses. This division of tasks improves overall system effectiveness. For instance, instead of the LLM calculating the square root of 16, it can make a function call like \verb|[Calculator(sqrt(16))]|, with the Calculator API executing the function and returning the result, thereby reducing the computational load on the LLM.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Interacting with this prompt was engaging. Initially, it generated the function call code. Upon further interaction, the AI model simulated being the API, calculated as if it were the API, and produced correct results. Writing custom code for this would enable actual function calls, shifting calculation requirements from the LLM to a computing function.

%% re-use: how to derive a PE from PP
To reuse CalcAPI, adapt the expressions and context to fit different domains. For example, in finance, use expressions like \verb|[Calculator(interest_rate*principal)]| to calculate interest. This flexibility makes CalcAPI a powerful tool for diverse applications requiring precise calculations.

% %3 introduce category one by one as subsection
% \subsection{Calculation}
% \label{subsec:Calculation}
% % the role of this category under the "at-logic" (meaning of the category)
% Calculation refers to the ability of the model to perform mathematical operations or computations based on the input prompt. This could range from simple arithmetic operations to more complex calculations involving multiple steps and variables. The accuracy of the calculation is a key factor in assessing the model’s performance.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Calculator API Simulation (CalcAPI) from Table \ref{tab:Calculator_API_Calls_PP}, simulates calculator API calls using the syntax \verb|[Calculator(expression)]|, where \verb|expression| is the mathematical operation to be executed. This method of interaction enhances the model’s ability to provide accurate information by performing complex calculations within a text. It can be reused in any context requiring mathematical computations, enriching the user experience by delivering precise calculations on demand. Examples of API calls include \verb|[Calculator(2+2)]|, \verb|[Calculator(sqrt(16))]|, and \verb|[Calculator(3*7)]|.

% This tool is versatile and can be reused in various contexts that require mathematical computations, such as financial applications for interest rate calculations, scientific research for complex calculations, or educational platforms for solving math problems.

% The CalcAPI could also be used for actual function calls, allowing the LLM to focus on understanding the context and generating appropriate responses. This division of tasks improves the system’s overall effectiveness. For instance, instead of the LLM calculating the square root of 16, it can make a function call like \verb|[Calculator(sqrt(16))]|, and the Calculator API could call an actual function which will return the result, reducing the computational load on the LLM and making it more effective in handling other tasks.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% I needed to chat with this prompt to extract the answers. Initially, it produced the function call code, I then asked the AI model to simulate being the API. It then calculated as if it was the API being called and produced the correct results. Writing custom code for this would allow an actual function to be called, moving the calculation requirements from the LLM to a computing function.

% %% re-use: how to derive a PE from PP
% To reuse CalcAPI, you can adapt the expressions and context to fit different domains. For example, in a financial context, you might use expressions like \verb|[Calculator(interest_rate*principal)]| to calculate interest. This flexibility makes CalcAPI a powerful tool for various applications requiring precise calculations.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 17-1-0\\ 
% \textbf{Category}: CAL\\ 
% \textbf{Name}: Calculator API calls\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}: Simulates calculator API calls, where the simulation API\\ is invoked using the syntax ‘[Calculator(expression)]’, with ‘expression’\\ being the mathematical computation to be performed.\\ 
% \textbf{Template}: Your task is to add calls to a Calculator API to a piece of text.\\ The calls should help you get information required to complete the text.\\ You can call the API by writing "[Calculator(expression)]" where "expression"\\ is the expression to be computed. Here are some examples of API calls:\\
% \textbf{Example}: 17-1-0-0\\ 
% \textbf{Related PPs}: 22-0-1, 22-2-8\\ 
% \textbf{Reference:} \cite{Schick2023Toolformer:Tools}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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
Hypothesise involves forming an educated guess about an outcome that is possible but not yet proven, based on the input prompt. This process requires the AI model to analyse the input, consider various possibilities, and predict the most likely outcome. A hypothesis is effective if it is plausible, logically connected to the input, and testable.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The User prompt (UP) PP is designed to generate plausible outcomes based on given inputs. It hypothesises by analysing various factors and predicting results. Further details of the PP can be found in Table \ref{tab:User_Prompt_PP}.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
UP produces a well-reasoned hypothesis by considering multiple variables and potential outcomes. You can use follow-up chat to refine the hypothesis or explore alternatives, which feels empowering and insightful.

%% re-use: how to derive a PE from PP
UP can be reused by modifying the \{sample\_prompt\} section. This allows universal prompting as the prompt is designed to hypothesise using the user-provided prompt as context. Setting the prompt in the System prompt settings allows a user to enter their prompt and it will be rewritten.

For example, writing 'US NASDAQ stock history' is rewritten to 'Please provide an overview of the historical performance of the US NASDAQ stock market up to December 2024. Include key events and trends that have shaped its trajectory over the years.'

Another example in a different domain is 'History of science', which is rewritten to 'Consider the perspective of a seasoned historian of science, with a comprehensive understanding of the evolution of scientific thought and discovery from ancient civilizations to modern times. Provide insights on the history of science, drawing from extensive understanding and research.'

% %3 introduce category one by one as subsection
% \subsection{Hypothesise}
% \label{subsec:Hypothesise}
% % the role of this category under the "beyond-logic" (meaning of the category)
% Hypothesise involves making an educated guess or assumption about a possible but unproven outcome based on the input prompt. This process requires the AI model to analyse the input, consider various possibilities, and predict the most likely outcome. The effectiveness of a hypothesis is measured by its plausibility, the logical connection between the input and the predicted outcome, and its ability to be tested or verified.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The User prompt (UP) PP focuses on generating plausible outcomes based on given inputs. It is designed to hypothesise, analysing various factors, and predicting the results. Further details of the PP can be found in Table \ref{tab:User_Prompt_PP}.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% UP produces a well-reasoned hypothesis, considering multiple variables and potential outcomes. Using follow-up chat, you can ask the AI model to refine its hypothesis or explore alternative scenarios.

% %% re-use: how to derive a PE from PP
% UP can be reused by modifying the \{sample\_prompt\} section. This allows universal prompting as the prompt is designed to hypothesise using the user provided prompt as context. Setting the prompt in the System prompt settings allows a user to enter their prompt and it will be rewritten.

% For example, writing 'US NASDAQ stock history' is rewritten to 'Please provide an overview of the historical performance of the US NASDAQ stock market up to December 2024. Include key events and trends that have shaped its trajectory over the years.'

% Another example in a different domain is 'History of science', which is rewritten to 'Imagine you are a seasoned historian of science, with a comprehensive understanding of the evolution of scientific thought and discovery from ancient civilizations to modern times. You have delved into the works of pioneering scientists, analyzed the socio-political contexts in which scientific ideas developed, and explored the impacts of these ideas on society. Your expertise enables you to provide insightful narratives and analyses that illuminate the intricate tapestry of scientific history. Please share your knowledge on the history of science, drawing from your extensive understanding and research.'

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 68-0-1\\ 
% \textbf{Category}: HYP\\ 
% \textbf{Name}: User prompt\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}: This prompt uses hypothesis by encouraging the model to explore different \\approaches and perspectives to solve a problem. It involves hypothesising the best expert for a task,\\ outlining step-by-step solutions, imagining collaborative discussions among experts,\\ and ensuring all necessary information is included.\\ This methodical yet creative approach ensures a thorough and well-rounded problem-solving process.\\ 
% \textbf{Template}: Your available prompting techniques include, but are not limited to the following:\\
% - Crafting an expert who is an expert at the given task, by writing a high quality description about the most\\ capable and suitable agent to answer the instruction in second person perspective.[1]\\
% - Explaining step-by-step how the problem should be tackled, and making sure the model explains step-by-step\\ how it came to the answer. You can do this by adding "Let's think step-by-step".[2]\\
% - Imagining three different experts who are discussing the problem at hand. All experts will write down 1 step\\ of their thinking, then share it with the group. Then all experts will go on to the next step, etc.\\ If any expert realises they're wrong at any point then they leave.[3]\\
% - Making sure all information needed is in the prompt, adding where necessary but making sure the question\\ remains having the same objective. Your approach is methodical and analytical, yet creative.\\ You use a mixture of the prompting techniques, making sure you pick the right combination\\ for each instruction. You see beyond the surface of a prompt, identifying the core\\ objectives and the best ways to articulate them to achieve the desired outcomes.\\

% Output instructions:
% You should ONLY return the reformulated prompt. Make sure to include ALL\\ information from the given prompt to reformulate.\\

% Given above information and instructions, reformulate below prompt using the techniques provided:\\
%  \texttt{""" \{sample\_prompt\} """} \\
% \textbf{Example}: 68-0-1-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{KepelAutonomousModels}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
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
    ID & PP name& Ref.\\
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
Logical Reasoning employs structured thinking to derive conclusions from input prompts. It involves deducing conclusions from facts, making inferences from patterns, or applying principles to solve problems. The effectiveness of logical reasoning is measured by the validity of conclusions, clarity of the reasoning process, and alignment with established facts.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Thought Template (TT) PP, detailed in Table \ref{tab:Thought_Template_PP}, applies logical reasoning to problem-solving. It guides the AI model through a structured thought process, ensuring each step is logically sound and evidence-based.

%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Using the TT PP, the AI model typically produces a detailed and logical analysis, breaking down complex problems into manageable steps. This approach enhances confidence in the AI's conclusions, as each step is clearly explained.

% re-use: how to derive a PE from PP
To apply TT in a given context, define the problem clearly, outline relevant facts and principles, and guide the AI model through a step-by-step reasoning process. For example, to derive a PE: "Act as a logical reasoner. Given a problem related to data analysis, determine the highest score among students based on test results. Use logical reasoning to compare scores, calculate the highest score, and identify the top-performing student. Demonstrate a clear and logical process leading to the correct conclusion."

% %3 introduce category one by one as subsection
% \subsection{Logical Reasoning}
% \label{subsec:LogicalReasoning}
% % the role of this category under the "beyond-logic" (meaning of the category)
% Logical Reasoning involves using logic and structured thinking to generate an output based on the input prompt. This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules or principles to solve problems. The strength of logical reasoning is evaluated by the soundness of the conclusions drawn, the clarity of the reasoning process, and the consistency with established principles or facts.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Thought Template (TT) PP described in Table \ref{tab:Thought_Template_PP}, focuses on applying logical reasoning to solve problems. It is designed to guide the AI model through a structured thought process, ensuring that each step is logically sound and well-supported by evidence.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% When using the TT PP, the AI model typically produces a detailed and logical analysis, breaking down complex problems into manageable steps. This methodical approach helped me feel confident in the AI's reasoning and conclusions, as each step is transparently explained and justified.

% %% re-use: how to derive a PE from PP
% To apply TT in a given context, define the problem clearly, outline the relevant facts and principles, and guide the AI model through a step-by-step reasoning process. Here is an example to derive a PE:
% I want you to act as a logical reasoner. I will provide you with a problem related to data analysis: 
% Determine the highest score among a group of students based on their test results. Your task is to use logical reasoning to compare the test scores, calculate the highest score, and identify the top-performing student. Your goal is to demonstrate a clear and logical process that leads to the correct conclusion.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 66-3-0\\ 
% \textbf{Category}: LGR\\ 
% \textbf{Name}: Thought Template\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}: Requests the application of logical reasoning to compare a relevant attribute across\\ all entries to determine the correct answer. The attribute and entries are provided as input.\\
% \textbf{Template}: Apply logical reasoning to compare the relevant attribute\\ across all entries to find the correct answer \\(e.g., the highest age for the oldest penguin).\\
% \textbf{Example}: 66-3-0-3\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{Yang2024BufferModels}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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
% 3.1 the role of this category under the "beyond-logic" (meaning of the category)
Prediction involves estimating future outcomes based on input prompts. It requires the AI model to analyse inputs, consider relevant variables, and generate responses that anticipate future events or trends. Prediction accuracy is determined by its alignment with actual outcomes and the model's adaptability to new information.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Rotation Prediction (RP) PP, as shown in Table \ref{tab:Rotation_Prediction_PP}, focuses on predicting the letter or number represented in an image when rotated 180 degrees. This PP aids users by providing accurate visual predictions, useful in applications like image recognition, data analysis, and educational tools.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Viewing the output of the Rotation Prediction PP, the AI's ability to interpret and predict visual data is noteworthy. The response is clear and precise, showcasing the AI's capability to handle complex visual tasks.

%% re-use: how to derive a PE from PP
RP can be reused by altering the input image or context, allowing for diverse applications from educational tools to advanced image recognition systems. Users can adapt the PP to various scenarios, ensuring its versatility across domains.

% %3 introduce category one by one as subsection
% \subsection{Prediction}
% \label{subsec:Prediction}
% % the role of this category under the "beyond-logic" (meaning of the category)
% Prediction involves forecasting or estimating the outcome based on the input prompt. This requires the AI model to analyse the input, consider various factors or variables, and generate a response that anticipates future events or trends. The accuracy of a prediction is assessed by its alignment with actual outcomes, the consideration of relevant variables, and the model's ability to adapt to new information.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Rotation Prediction (RP) PP from Table \ref{tab:Rotation_Prediction_PP} focuses on predicting the letter or number represented in an image when rotated 180 degrees. This PP helps users by providing a clear and accurate prediction based on visual input, which can be useful in various applications such as image recognition, data analysis, and educational tools.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% When viewing the output of the Rotation Prediction PP, the AI's ability to accurately interpret and predict visual data feels ground breaking. The response is clear, precise, and demonstrates the AI's capability to handle complex visual tasks.

% %% re-use: how to derive a PE from PP
% RP can be reused by modifying the input image or the context in which the prediction is made. This allows for a wide range of applications, from educational tools to advanced image recognition systems. Users can easily adapt the PP to different scenarios, ensuring its versatility and usefulness across various domains.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 61-0-20\\ 
% \textbf{Category}: PRD\\ 
% \textbf{Name}: Rotation Prediction\\ 
% \textbf{Media Type}: Text,  Image2Text, Text2Image\\ 
% \textbf{Description}: Provide an image and predict the letter or number it represents when rotated 180 degrees.\\
% \textbf{Template}: I am showing you an image and you need to predict the letter or number shown when rotating\\ the image by 180 degrees.\\
% \textbf{Example}: 61-0-20-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{McKinzie2024MM1:Pre-training}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
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
    ID & PP name& Ref.\\
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
% 3.1 the role of this category under the "beyond-logic" (meaning of the category)
Simulation involves replicating real-world processes or systems, such as operating systems or applications, to model and analyse complex phenomena. Its effectiveness is determined by the accuracy of the model, its fidelity to real-world processes, and its utility in predicting or understanding system behaviour.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Relevant Roles (RR) PP, as outlined in Table \ref{tab:Relevant_Roles_PP}, is designed to interpret realistic scenarios that mimic real-world processes. This PP facilitates the understanding of complex systems by predicting outcomes and testing hypotheses within a controlled virtual environment.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Notably, incorporating various scenarios into the PP allows for the observation of the AI model's capability to interpret and identify different agents, which is both intriguing and insightful.     

%% re-use: how to derive a PE from PP
To apply the RR PP in a given context, provide a specific scenario, such as "A hospital emergency room during a major accident," and request the identification of individual human agents involved. Define the objective and output format to ensure a clear and comprehensive listing of roles. For example, in the scenario "A hospital emergency room during a major accident," ask, "Who are the individual human agents (e.g., doctors, nurses, paramedics) in a simple simulation of this scenario?"

% %3 introduce category one by one as subsection
% \subsection{Simulation}
% \label{subsec:Simulation}
% % the role of this category under the "beyond-logic" (meaning of the category)
% Simulation refers to imitating or replicating a real-world process or system. This could involve simulating operating systems, applications, or any other complex process that can be modelled and analysed. The effectiveness of a simulation is judged by its fidelity to the real-world process, the accuracy of the model, and its usefulness in predicting or understanding the behaviour of the system being simulated.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Relevant Roles PP referred to in Table \ref{tab:Relevant_Roles_PP} focuses on interpreting realistic scenarios that mimic real-world processes. This helps in understanding complex systems, predicting outcomes, and testing hypotheses in a controlled virtual environment.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% It is interesting adding different scenarios to the PP and observing the AI model interpreting and detecting the different agents.

% %% re-use: how to derive a PE from PP
% To apply the Relevant Roles PP in a given context, provide a specific scenario, such as "A hospital emergency room during a major accident," and request the identification of individual human agents involved. Define the objective and output format to ensure a clear and comprehensive listing of roles. For example, in the scenario "A hospital emergency room during a major accident," ask, "Who are the individual human agents (e.g., doctors, nurses, paramedics) in a simple simulation of this scenario?"

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 60-0-0\\ 
% \textbf{Category}: SIM\\ 
% \textbf{Name}: Relevant Roles\\ 
% \textbf{Media Type}: Text, Image2Text\\ 
% \textbf{Description}: Requests identification of individual human agents involved in a given scenario.\\ The scenario is provided as input, and the task is to list the relevant roles or agents that would be part\\ of a simple simulation of this scenario.\\
% \textbf{Template}: In the following scenario: '{scenario}',\\ Who are the individual human agents in a simple simulation of this scenario?\\
% \textbf{Example}: 60-0-0-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{Manning2024AutomatedSubjects}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
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
    ID & PP name& Ref.\\
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
% the role of this category under the "in-logic" (meaning of the category)
The categorising category is crucial in structuring interactions between humans and Large Language Models (LLMs). It organises diverse inputs into clear classes, making the interface more systematic and easier to navigate for users. This organisation aids in efficient information management and helps the model recognize nuanced distinctions in complex datasets.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
In Table \ref{tab:Insurance_Report_Generation_PP}, the Insurance Report Generation (IRG) PP is detailed. IRG interprets an image of a crashed car to output details such as make, model, license plate, and damage description. This PP simplifies the process for individuals assessing damage after a car accident, showcasing the model's ability to interpret visual data and provide structured reports.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The output's clarity is impressive. Observing the AI model interpret an image and reason over it to provide a structured report demonstrates its advanced capabilities.

%% re-use: how to derive a PE from PP
The PP can be adapted for medical imaging by prompting, "Imagine you are a radiologist evaluating a patient's X-ray for diagnostic purposes. Please evaluate the abnormalities seen in the image below." Similarly, in art restoration, it can be used by prompting, "Imagine you are an art conservator evaluating a painting for restoration. Please evaluate the damage seen in the image below." By adjusting the subject and context, this versatile PP can be effectively utilised across diverse domains, enhancing the ability to generate detailed and context-specific evaluations.

% %3 introduce category one by one as subsection 
% \subsection{Categorising}
% \label{subsec:categorising}
% % the role of this category under the "in-logic" (meaning of the category)
% The categorising category plays a pivotal role in structuring the interaction between humans and Large Language Models (LLMs). This category is instrumental in organising diverse inputs into coherent classes, thereby facilitating a more systematic and navigable interface for users. By leveraging Categorising, users can guide LLMs to sort information based on shared attributes, which is essential for establishing order and enhancing the retrieval of relevant data. This process not only aids in the efficient management of information but also supports the model's ability to recognise and adhere to the nuanced distinctions within complex datasets. 

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% In Table \ref{tab:Insurance_Report_Generation_PP}, the Insurance Report Generation (IRG) PP is detailed. IRG interprets an image of a crashed car and outputs the make, model, license plate and damage description of the car. This helps people, to ask LLMs to perform car damage evaluation, in the context of a car accident. This simplifies the process for individuals seeking to assess damage following a car accident. 

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The clarity of the output is amazing. Observing the AI model interpret an image and then reason over it to provide a report is remarkable.
% %% re-use: how to derive a PE from PP
% The PP could be used in medical imaging by prompting, "Imagine that you are a radiologist evaluating a patient's X-ray for diagnostic purposes. Please evaluate the abnormalities seen in the image below." Similarly, it can be applied in the field of art restoration by prompting, "Imagine that you are an art conservator evaluating a painting for restoration. Please evaluate the damage seen in the image below." By adjusting the subject and context, this versatile PP can be effectively utilised across diverse domains, enhancing the ability to generate detailed and context-specific evaluations.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern}\\ \hline
% \textbf{ID:} 10-25-1 \\ 
% \textbf{Category:} CAT \\ 
% \textbf{Name:} Insurance Report Generation \\ 
% \textbf{Media Type:} Image2Text \\ 
% \textbf{Description:} Designed to interpret images of crashed vehicles, provides a detailed analysis\\ that includes the car's make, model, license plate, and an accurate description of the damage\\ incurred.\\ 
% \textbf{Template:} Imagine that you are an expert in evaluating the car damage from car accident for\\ auto insurance reporting. Please evaluate the damage seen in the image below.\\
% \textbf{Example:} 10-25-0-0\\ 
% \textbf{Related PPs:} 10-1-1, 10-11-3, 10-24-0, 10-25-1, 10-29-0 \\ 
% \textbf{Reference:} \cite{Yang2023TheGPT-4Vision}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name & Ref.\\
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
% the role of this category under the "in-logic" (meaning of the category)
The classification category is fundamental for structured analysis and decision-making, enabling precise categorisation of inputs based on established criteria. This capability is crucial in applications requiring high accuracy, such as content filtering, sentiment analysis, and diagnostic systems. Within the "In-logic" framework, classification empowers AI to assign inputs to the correct classes, facilitating refined and targeted responses. This underscores the AI's capacity for detailed comprehension and its potential for application in complex, real-world scenarios where categorical distinctions are essential.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Intermediate Abstraction (IA), as outlined in Table \ref{tab:Intermediate_Abstraction_PP}, exemplifies a PP in the Classification category. IA is a PP that separates business logic from third-party dependencies by introducing an abstraction layer. This allows for seamless replacement of third-party libraries, enhancing code maintainability and scalability. This approach assists developers by ensuring that changes in dependencies do not directly impact business logic. The pattern is reusable in various coding scenarios where abstraction from third-party libraries is necessary.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The separation of business logic from third-party dependencies ensures robust and adaptable code, simplifying future updates and maintenance. This design pattern instills confidence in developers, knowing their codebase is resilient to changes in external libraries.

%% re-use: how to derive a PE from PP
The PP can be adapted to different programming languages or frameworks by modifying the instructions to fit the specific context. This process allows for the creation of robust and reusable PEs that can be applied to a wide range of coding tasks, enhancing the utility and efficiency of interactions with LLMs.

% %3 introduce category one by one as subsection
% \subsection{Classification}
% \label{subsec:classification}
% % the role of this category under the "in-logic" (meaning of the category)
% The classification category stands as a cornerstone for structured analysis and decision-making processes. Classification is predicated on the ability to accurately predict the category or label of a given input, based on a set of established criteria and learned patterns. By leveraging the nuanced understanding of the topic at hand, Classification empowers the AI to assign inputs to the correct classes, thereby facilitating a more refined and targeted response. This is particularly crucial in applications where precision and context-specific accuracy are paramount, such as in content filtering, sentiment analysis, and diagnostic systems. The efficacy of Classification within the "In-logic" framework is a testament to the AI's capacity for detailed comprehension and its potential for application in complex, real-world scenarios where categorical distinctions are essential.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Intermediate Abstraction (IA) as described in Table \ref{tab:Intermediate_Abstraction_PP} is an example PP in the Classification category. IA is a prompt that instructs the LLM to write code in such a way that the business logic is separated as much as possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, an intermediate abstraction is written that the business logic uses instead. This allows for the 3rd-party library to be replaced with an alternate library if needed. This helps people, especially developers, to maintain and update their codebase more effectively. It ensures that changes in third-party libraries do not directly impact the business logic, thereby enhancing the code’s maintainability and scalability. This pattern can be reused in various coding scenarios where there is a need to abstract away dependencies on third-party libraries. 

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The separation of business logic from third-party dependencies ensures that the code is robust and adaptable, making future updates and maintenance simpler. 

% %% re-use: how to derive a PE from PP
% The PP can be adapted to different programming languages or frameworks by modifying the instructions to fit the specific context. This process allows for the creation of robust and reusable prompts that can be applied to a wide range of coding tasks, enhancing the utility and efficiency of interactions with LLMs.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern (PP) Structure}\\ \hline
% \textbf{ID:} 1-2-1 \\ 
% \textbf{Category:} CLF \\ 
% \textbf{Name:} Intermediate Abstraction \\ 
% \textbf{Media Type:} Text\\ 
% \textbf{Description:} This prompt requests code be written in a way that separates core business logic\\ from dependencies on third-party libraries. The request classifies and separates an intermediate layer\\ of abstraction for any interaction with these libraries and business logic.\\ 
% \textbf{Template}: Whenever I ask you to write code, I want you to separate the business logic as much as \\possible from any underlying 3rd-party libraries. Whenever business logic uses a 3rd-party library, \\please write an intermediate abstraction that the business logic uses instead so that the 3rd-party \\library could be replaced with an alternate library if needed.\\
% \textbf{Example:} 1-2-1-6\\ 
% \textbf{Related PPs:} 0-3-0, 1-2-0, 1-2-1, 1-2-2, 1-2-3, 2-0-0, 2-1-0 \\ 
% \textbf{Reference:} \cite{White2023ChatGPTDesign} \\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\\hline
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
    ID & PP name& Ref.\\ \hline 
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
% 3.1 the role of this category under the "in-logic" (meaning of the category)
Clustering involves techniques to identify natural groupings within a dataset or subject without predefined classifications. These methods reveal underlying patterns or connections that may not be immediately apparent.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Common Concept (CC) PP, as illustrated in Table \ref{tab:Common_Concept_PP}, functions as a cognitive tool within the Clustering category of in-logic. CC examines diverse entities to discern a common attribute or characteristic that unites them. This function is crucial for synthesising information and discerning patterns, fundamental for organising data, acquiring knowledge, and making informed decisions. Utilising CC enables users to efficiently uncover linkages among seemingly disparate items, enhancing comprehension and facilitating the pattern's application across diverse scenarios.

%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Identifying unifying characteristics among diverse objects allows for multiple perspectives on the data, enriching my understanding.

%% re-use: how to derive a PE from PP
The PP can be adapted to various domains by adjusting the input for specific contexts, using different images and datasets.


% %3 introduce category one by one as subsection
% \subsection{Clustering}
% \label{subsec:clustering}
% % the role of this categroy under the "in-logic" (meaning of the cateory)
% The clustering category encapsulates techniques aimed at discerning natural groupings within a dataset or subject, devoid of predefined classifications. These methods unveil underlying patterns or connections that may not be immediately apparent. 

% %intro the category with one example
% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Common Concept (CC) PP shown in Table \ref{tab:Common_Concept_PP} serves as a cognitive tool within the Clustering category of in-logic. CC examines a collection of diverse entities and discerns a common attribute or characteristic that unites them. This function is pivotal for synthesising information and discerning patterns, which are fundamental for activities such as organising data, acquiring knowledge, and making informed decisions. Utilising CC enables users to efficiently uncover linkages among seemingly disparate items, enhancing comprehension and promoting the application of this pattern across various scenarios. 

% %expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The ability to identify unifying characteristics among diverse objects helps me to see the data from different angles and points of view.

% %% re-use: how to derive a PE from PP 
% The PP can be tailored to various domains by adjusting the input for specific contexts, using different images and datasets.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern (PP) Structure} \\ \hline
% \textbf{ID:} 19-7-1\\ 
% \textbf{Category:} CLU \\ 
% \textbf{Name:} Common Concept\\ 
% \textbf{Media Type:} Text, Image2Text\\ 
% \textbf{Description:} This prompt example identifies shared attributes or features among a set of\\ diverse objects. This encourages pattern recognition and critical thinking, as it requires examining\\ each object and discerning a unifying characteristic that applies to all of them.\\ 
% \textbf{Template:} Find a common characteristic for the given objects.\\
% \textbf{Example:} 19-7-1-0\\ 
% \textbf{Related PPs:} 19-7-0, 19-3-1, 1-2-1, 10-26-1\\ 
% \textbf{Reference:} \cite{Honovich2022InstructionDescriptions}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref.\\
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
% 3.1 the role of this category under the "in-logic" (meaning of the category)
The Error Identification category is crucial for ensuring the reliability and accuracy of interactions with Large Language Models (LLMs). This category focuses on detecting and correcting discrepancies, fallacies, and inaccuracies within data or discourse. By identifying errors, it ensures AI-generated information is logically consistent and factually correct, enhancing the trustworthiness of AI in practical applications. PPs in this category guide AI to scrutinise its responses, fostering a self-corrective mechanism essential for maintaining the integrity of human-AI communication. 

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
Fact Check List (FCL) is a prominent PP in the Error Identification category. Table \ref{tab:Fact_Check_List_PP} details this PP. FCL requests a set of facts that the answer depends on and lists these facts at the end of the output for verification. This is particularly beneficial in cybersecurity, where accuracy is paramount. By listing facts for independent verification, it enhances the credibility and reliability of the information. This PP can be reused in any context where fact-checking is essential, simplifying the verification process for users.

%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The inclusion of a fact-checkable list at the end of the response allows me to independently verify the information, boosting my trust in the AI's output.

%% re-use: how to derive a PE from PP
To reuse the PP in different domains, modify the context. For instance, as a medical advisor, generate a set of medical facts for fact-checking, listing them at the end of the output.

% %3 introduce category one by one as subsection
% \subsection{Error Identification}
% \label{subsec:ErrorIdentification}
% % the role of this categroy under the "in-logic" (meaning of the category)
% The Error Identification category elaborates the reliability and accuracy of interactions with Large Language Models (LLMs). This category is dedicated to the detection and correction of discrepancies, fallacies, and inaccuracies that may arise within the data or discourse. By focusing on the identification of errors, this category ensures that the information processed and generated by AI adheres to logical consistency and factual correctness. It is instrumental in refining the AI's output, thereby bolstering the trustworthiness of the system in practical applications. The prompts designed under this category guide the AI to scrutinise its own responses, encouraging a self-corrective mechanism that is essential for maintaining the integrity of human-AI communication.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Fact Check List (FCL) is an example PP in the Error Identification category. Table \ref{tab:Fact_Check_List_PP} displays the details of the PP. When generating an answer FCL requests a set of facts that the answer depends on and lists this set of facts at the end of the output for fact-checking. This is particularly useful in the context of cybersecurity, where the accuracy of information is paramount. By providing a list of facts to be checked, it allows users to verify the information independently, thereby enhancing the credibility and reliability of the information provided. This can be reused in various contexts where fact-checking is essential, thus simplifying the process for individuals seeking to verify the accuracy of responses. 

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The inclusion of a list of fact-checkable statements at the end of the response allows me to independently verify the accuracy of the information, thereby enhancing the credibility and reliability of the AI's output.

% %% re-use: how to derive a PE from PP
% Modifying the domain allows the PP to be reused. For example, I want you to act as a medical advisor. When you generate an answer, create a set of facts that the answer depends on that should be fact-checked and list this set of facts at the end of your output. Only include facts related to medical information.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 0-2-0 \\ 
% \textbf{Category}: ERI \\ 
% \textbf{Name}: Fact Check List \\ 
% \textbf{Media Type}: \\ 
% \textbf{Description}: Requests a list of fact-checkable cybersecurity-related facts that the response\\ depends on.\\ 
% \textbf{Template}: From now on, when you generate an answer, create a set of facts that the answer\\ depends on that should be fact-checked and list this set of facts at the end of your output. Only \\include facts related to cybersecurity.\\
% \textbf{Example}: 0-2-0-3\\ 
% \textbf{Related PPs}: 0-2-0-[0-2]\\ 
% \textbf{Reference:} \cite{White2023AChatGPT}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name & Ref.\\
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
% 3.1 the role of this category under the "in-logic" (meaning of the category)
The Input Semantics category focuses on understanding and interpreting the meaning and context of inputs. This ensures that LLMs capture the subtleties and complexities of human language. By examining Input Semantics, we explore the semantic layers of prompts, analysing their nuances and connotations. This analysis is crucial for AI to respond in a manner that is syntactically correct, contextually appropriate, and semantically rich. Through this approach, AI can better understand user intent, enabling more effective and nuanced interactions that mirror human conversation.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
As shown in Table \ref{tab:Constructing_the_Signifier_PP}, the Constructing the Signifier (CS) PP simplifies complex information. It rephrases advanced text into simpler terms that a second grader can understand. This aids education by making difficult concepts accessible to younger audiences and has practical applications in everyday life where clear communication is essential. For example, it can explain technical instructions to non-experts or ensure important information is understood by all community members, regardless of educational background. The ability to rephrase content for different comprehension levels is a valuable skill that can be reused in various contexts to enhance understanding and communication. CS can also be used for translation into different languages.   

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The AI model's ability to transform complex information into simpler terms makes content more accessible and easier to grasp. This aids education and ensures effective communication, regardless of educational background. I have personally used this pattern on research papers in new fields to aid my understanding.

%% re-use: how to derive a PE from PP
To derive a PE from the CS PP, instruct the AI: "Act as a {role}. When generating an answer, rephrase the information so that a {audience} can understand it, emphasising {real-world applications} and ensuring clarity." Adjusting these variables allows for universal usage.

% %3 introduce category one by one as subsection
% \subsection{Input Semantics}
% \label{subsec:InputSemantics}
% % the role of this categroy under the "in-logic" (meaning of the category)
% %OPTION a
% The category of Input Semantics is dedicated to the comprehension and interpretation of the meaning and context of inputs, which ensuring LLMs accurately captures the subtleties and complexities inherent in human language. By focusing on Input Semantics, we delve into the semantic layers of prompts, dissecting the nuances and connotations that they carry. This meticulous analysis is crucial for the AI to respond in a manner that is not only syntactically correct but also contextually appropriate and semantically rich. It is through this lens that the AI can achieve a deeper understanding of the user's intent, enabling more effective and nuanced interactions that mirror human conversational dynamics.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% As per Table \ref{tab:Constructing_the_Signifier_PP}, the Constructing the Signifier (CS) PP serves as a tool for simplifying complex information. The CS PP takes a piece of advanced text and rephrases it into simpler terms that a second grader could easily comprehend. This process not only aids in education by making difficult concepts accessible to younger audiences but also has practical applications in everyday life where clear and straightforward communication is essential. For instance, it can be used to explain technical instructions to non-experts or to ensure that important information is understood by all members of a community, regardless of their educational background. The ability to rephrase content for different comprehension levels is a valuable skill that can be reused in various contexts to enhance understanding and communication. CS can also be used to translate into different languages.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The ability of the AI model to transform complex information into simpler terms that even a second grader can understand makes the content more approachable and easier to grasp. This not only aids in education but also ensures that important information is communicated effectively, regardless of their educational background. I have personally used this pattern on some research papers that are in a new field to help with my understanding. 

% %% re-use: how to derive a PE from PP
% I want you to act as a {role}. When you generate an answer, rephrase the information so that a {audience} can understand it, emphasizing {real-world applications} and ensuring clarity. 
% Changing these variables allows for universal usage.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern}\\ \hline
% \textbf{ID:} 13-0-0\\ 
% \textbf{Category:} INP \\ 
% \textbf{Name:} Constructing the Signifier\\ 
% \textbf{Media Type:} Text\\ 
% \textbf{Description:} Transforms complex text into simple explanations, making it easier for even \\ a second grader to understand. It’s useful for education, breaking down technical jargon for non-experts, \\ and ensuring clear communication across diverse educational levels and languages.\\ 
% \textbf{Template:} rephrase this paragraph so that a 2nd grader can understand it, emphasizing real-world \\ applications.\\
% \textbf{Example:} 13-0-0-1\\ 
% \textbf{Related PPs:} 13-0-0\\ 
% \textbf{Reference:} \cite{Reynolds2021PromptParadigm}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\ \hline
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
    ID & PP name& Ref.\\
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
% the role of this category under the "in-logic" (meaning of the category)
Requirements Elicitation is a category of PPs that identifies the specific needs of a given topic. This category guides the model to systematically uncover and specify the criteria necessary for successful task execution. Using prompts from this category, the AI gains a deeper understanding of objectives, constraints, and stakeholder expectations, facilitating a more targeted and effective response.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Expert Prompting (EP) exemplifies the Requirements Elicitation category. Table \ref{tab:Expert_Prompting_PP} details the PP. EP identifies multiple experts in a specific field, generates answers as if the experts wrote them, and combines these through collaborative decision-making. This assists in eliciting detailed requirements, leveraging diverse expert insights. It enriches requirement quality and fosters a collaborative environment by integrating various perspectives. This PP is reusable in contexts needing expert insights, though less effective for novel research solutions.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The process of identifying multiple experts and generating answers as if the experts wrote them ensures that the requirements are detailed and comprehensive. This collaborative decision-making approach enriches the quality of the requirements by integrating diverse perspectives.

%% re-use: how to derive a PE from PP
I want you to act as a {role}. Use the LLM to identify multiple experts in the field, generate answers as if the experts wrote them, and combine the experts' answers by collaborative decision-making to elicit comprehensive {content type}. For example, in software development: I want you to act as a software development consultant. Use the LLM to identify multiple experts in the field, generate answers as if the experts wrote them, and combine the experts' answers by collaborative decision-making to elicit comprehensive software requirements.


% %3 introduce category one by one as subsection
% \subsection{Requirements Elicitation}
% \label{subsec:RequirementsElicitation}
% % the role of this category under the "in-logic" (meaning of the category)
% Requirements Elicitation is a category of PPs that articulate the specific needs of a given topic. This category guides the model to systematically uncover and specify the criteria that must be satisfied for successful task execution. Using prompts from this category, the AI is prompted to delve into a deeper understanding of the objectives, constraints, and stakeholder expectations, thereby facilitating a more targeted and effective response. 

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Expert Prompting (EP) is an example PP of the Requirements Elicitation category. Table \ref{tab:Expert_Prompting_PP} show the details of the PP. EP identifies multiple experts in a specific field, generates answers as if the experts wrote them, and combines the experts’ answers through collaborative decision-making. This assists people in eliciting detailed and comprehensive requirements for a topic or task, leveraging the knowledge and insights of multiple experts. This not only enriches the quality of the requirements but also fosters a collaborative environment where diverse perspectives are valued and integrated. This PP can be reused in various contexts where expert insights are needed. Note that this PP is not that effective in generating a new/novel solution for research purpose.  

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The process of identifying multiple experts and generating answers as if the experts wrote them ensures that the requirements are detailed and comprehensive. This collaborative decision-making approach enriches the quality of the requirements by integrating diverse perspectives.
% %% re-use: how to derive a PE from PP
% I want you to act as a {role}. Use the LLM to identify multiple experts in the field, generate answers as if the experts wrote them, and combine the experts' answers by collaborative decision-making to elicit comprehensive {content type}.
% An example for software development follows: I want you to act as a software development consultant. Use the LLM to identify multiple experts in the field, generate answers as if the experts wrote them, and combine the experts' answers by collaborative decision-making to elicit comprehensive software requirements.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern (PP) Structure}\\ \hline
% ID: 24-0-6\\ 
% Category: REL \\ 
% Prompt Pattern (PP) Name: Expert Prompting\\ 
% Media Type: Text\\ 
% Description: Identifies experts, generates expert-like answers, and combines these through \\collaborative decision-making to elicit comprehensive responses to the requirements.\\ 
% Template: Use the LLM to identify multiple experts in the field, generate answers as if \\ the experts wrote them, and combine the experts' answers by collaborative decision-making.\\
% Prompt Example (PE): 24-0-6-0\\ 
% Related PPs: 0-3-2, 13-5-0, 24-0-2 and 8-0-0\\ 
% Reference: \cite{Zhang2023ExploringModels}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
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
    ID & PP name& Ref. \\
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
Context Control manages the context to ensure AI responses are both accurate and relevant. This involves providing background information, setting parameters, or guiding the AI to focus on specific aspects. For instance, in creative content, it might specify genre or tone, while in code generation, it could define language or functionality constraints. Effective context control maintains coherence and relevance, directing the AI to produce innovative and contextually appropriate outputs.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Ethical Use (EU), as detailed in Table \ref{tab:Ethical_Use_PP}, discusses the ethical use of AI models across domains. By specifying the AI model and ethical principles, it ensures integrity, privacy, fairness, and accountability. This adaptable structure guides ethical AI practices universally.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The response introduced points that were both insightful and previously unconsidered. It generated them in a simple structure that was easy to understand.

%% re-use: how to derive a PE from PP
To reuse the PP, the following structure and variables can be used. Explain how to use the [AI model] ethically with regards to [ethical principle 1], [ethical principle 2], [ethical principle 3], and [ethical principle 4]. Adapt this pattern by specifying the AI model and relevant ethical principles for each domain.


% %3 introduce category one by one as subsection
% \subsection{Context Control}
% \label{subsec:ContextControl}
% % the role of this category under the "out-logic" (meaning of the category)
% Context Control ensures AI responses are accurate and relevant by managing the context. This involves providing background information, setting parameters, or guiding the AI to focus on specific aspects. For example, in creative content, it might specify genre or tone, while in code generation, it could define language or functionality constraints. Effective context control maintains coherence and relevance, directing the AI to produce innovative and contextually appropriate outputs.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Ethical Use (EU) as detailed in Table \ref{tab:Ethical_Use_PP}, discusses the ethical use of AI models across domains. By specifying the AI model and ethical principles, it ensures a comprehensive approach to integrity, privacy, fairness, and accountability. This adaptable structure guides ethical AI practices universally.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The response introduced interesting points I hadn't thought of. It generated them in a simple structure that was easy to understand.

% %% re-use: how to derive a PE from PP
% To reuse the PP, the following structure and variables can be used.
% Explain how to use the [AI model] ethically with regards to [ethical principle 1], [ethical principle 2], [ethical principle 3], and [ethical principle 4].
% This pattern can be adapted to various contexts by specifying the AI model and the relevant ethical principles for each domain.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 71-42-4\\ 
% \textbf{Category}: CTX\\ 
% \textbf{Name}: Ethical Use\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}: Helps maintain focus on the specific ethical aspects relevant to the domain in question,\\ ensuring that discussions remain relevant and comprehensive.This adaptable structure can guide ethical \\ AI practices universally, providing clarity and consistency in diverse applications.\\
% \textbf{Template}: Explain how to use the ChatGPT model ethically\\ with regards to academic integrity, privacy, fairness, and accountability.\\
% \textbf{Example}: 71-42-4-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{AtlasDigitalCommonsURIAI}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_CTX category.}
\begin{tabular}{|c|c|c|}
    \hline
    ID & PP name& Ref. \\
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
% the role of this category under the "out-logic" (meaning of the category)
Decomposed Prompting involves segmenting complex tasks into simpler, manageable components. This method allows AI to address each part individually, resulting in more precise and comprehensive outputs. By focusing on smaller segments, AI can better comprehend and respond to each element, thereby enhancing the overall quality and precision of the generated content.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Table \ref{tab:Break_Down_Complex_Tasks_PP} illustrates a PP in this category for task decomposition. The PP guides AI to break down a complex task into a sequence of simpler prompts within an interactive conversation. Addressing each part individually enables AI to deliver more accurate and comprehensive outputs.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The output, which displays tasks broken down into components, facilitates a clearer understanding of each element. If any component is unclear, it can be explored in greater detail, either separately or within the context of the chat.

%% re-use: how to derive a PE from PP
The method of breaking down complex tasks into simpler components is widely applicable. In education, it aids students in understanding intricate subjects by focusing on individual elements. In project management, it assists teams in planning and executing projects more efficiently by addressing each task separately. In problem-solving, it allows individuals to tackle complex issues methodically, ensuring no aspect is overlooked. In programming, it facilitates debugging and learning by isolating specific code segments for detailed examination.


% %3 introduce category one by one as subsection
% \subsection{Decomposed Prompting}
% \label{subsec:DecomposedPrompting}
% % the role of this category under the "out-logic" (meaning of the category)
% Decomposed Prompting (DP) involves breaking down complex tasks into simpler, manageable components. This approach allows the AI to address each part individually, leading to more accurate and comprehensive outputs. By tackling tasks in smaller segments, the AI can better understand and respond to each element, enhancing the overall quality and precision of the generated content.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Table \ref{tab:Break_Down_Complex_Tasks_PP} presents an PP in this category for the breakdown of complex tasks. The PP instructs AI to break down a complex task into a sequence of simpler prompts in an interactive conversation. By addressing each part individually, the AI can provide more accurate and comprehensive outputs.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The output displaying the broken down tasks helped me understand each component separately. If something is unclear, I can explore that component in greater detail to gain a complete understanding. Thought could be done separately or in a continuation of the context of the chat.

% %% re-use: how to derive a PE from PP
% The versatility of breaking down complex tasks into simpler components is universally applicable. In education, this method could aid students in grasping intricate subjects by focusing on individual elements. In project management, it could help teams plan and execute projects more efficiently by addressing each task separately. In problem-solving, it could allow individuals to tackle complex issues methodically, ensuring no aspect is overlooked. In programming, it could facilitate debugging and learning by isolating specific code segments for detailed examination.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 41-5-0\\ 
% \textbf{Category}: DPR\\ 
% \textbf{Name}: Break Down Complex Tasks\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}: Breaking down complex tasks into simpler, manageable components,\\ instructs the AI to address each part individually\\ for more accurate and comprehensive outputs.\\ This method enhances the AI's understanding and response quality by tackling tasks in smaller segments.\\
% \textbf{Template}: Break down complex tasks into a sequence of simpler prompts in an interactive conversation\\
% \textbf{Example}: 41-5-0-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{Bsharat2023PrincipledGPT-3.5/4}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_DPR category.}
\begin{tabular}{|c|c|c|}
    \hline
    ID & PP name& Ref. \\
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
Output customisation involves modifying the AI's output to meet specific requirements or preferences, such as adjusting length, style, or format. This ensures the generated content is relevant and useful.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Problem Distiller (PD) PP assists experts in distilling and categorising essential information from user queries, focusing on key variables and constraints, and extending the problem to broader scenarios. Table \ref{tab:Problem_Distiller_PP} illustrates the PP. This adaptable approach can be reused across various domains, ensuring information is tailored to user needs, enhancing relevance and utility.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Breaking down the output ensures clarity and relevance, meeting expectations and enhancing the user experience.

%% re-use: how to derive a PE from PP
This prompt can be universally applied by extracting and categorising essential information from user queries, such as task statements, key variables, constraints, and objectives. For instance, in healthcare, it can help create personalised treatment plans; in education, design comprehensive curricula; in finance, develop stable budgets; in project management, plan successful product launches; and in marketing, formulate effective strategies. By distilling and extending the problem, the PP ensures a thorough and adaptable approach to solving diverse issues. The output of which can be used in further prompts.

% %3 introduce category one by one as subsection
% \subsection{Output Customisation}
% \label{subsec:OutputCustomisation}
% % the role of this category under the "out-logic" (meaning of the category)
% Output customisation refers to modifying or personalising the AI's output based on specific requirements or preferences. This can involve controlling the length, style, or format of the output, or incorporating specific information or elements into the response. By tailoring the output, we can ensure it meets the desired criteria and enhances the relevance and utility of the generated content.
 
% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Problem Distiller (PD) PP guides an expert in information distillation to extract and categorise essential information from user queries, focusing on key variables, constraints, and extending the problem to address broader scenarios while providing a solution example. Table \ref{tab:Problem_Distiller_PP} shows the PP. By ensuring a thorough and adaptable approach to solving diverse issues it can be reused across various domains. Customising the output, PD ensures that the information is tailored to the specific needs and preferences of the user, enhancing its relevance and utility.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% Having the output broken down ensures the information is clear and relevant. Customising the output ensures it meets your expectations and enhances the overall user experience.

% %% re-use: how to derive a PE from PP
% This prompt can be universally applied by extracting and categorising essential information from user queries, such as task statements, key variables, constraints, and objectives. For instance, in healthcare, it can help create personalised treatment plans; in education, design comprehensive curricula; in finance, develop stable budgets; in project management, plan successful product launches; and in marketing, formulate effective strategies. By distilling and extending the problem, the PP ensures a thorough and adaptable approach to solving diverse issues. The output of which can be used in further prompts.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 66-7-0\\ 
% \textbf{Category}: OUC\\ 
% \textbf{Name}: Problem Distiller\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}: This PP guides an expert in information distillation\\ to extract and categorise essential information from user queries,\\ focusing on key variables, constraints,\\ and extending the problem to address broader scenarios while providing a solution example.\\
% \textbf{Template}: [Problem Distiller]: As a highly professional and intelligent expert in information distillation,\\ you excel at extracting essential information to solve problems\\ from user input queries. You adeptly transform this extracted information\\ into a suitable format based on the respective type of the issue.\\ Please categorize and extract the crucial information required to solve the problem from the user's input query,\\ the distilled information should include.\\ 1. Key information: Values and information of key variables extracted from user input,\\ which will be handed over to the respective expert for task resolution,\\ ensuring all essential information required to solve the problem is provided.\\ 2. Restrictions: The objective of the problem and corresponding constraints.\\ 3. Distilled task: Extend the problem based on 1 and 2, summarize a meta problem that can address\\ the user query and handle more input and output variations. Incorporate the real-world scenario of\\ the extended problem along with the types of key variables and information constraints from the \\original problem to restrict the key variables in the extended problem. After that, use the user query input\\ key information as input to solve the problem as an example.\\
% \textbf{Example}: 66-7-0-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{Yang2024BufferModels}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_OUC category.}
\begin{tabular}{|c|c|c|}
    \hline
    ID & PP name & Ref. \\
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
Output semantics involves understanding the AI's output by interpreting its intent, context, and implications. This ensures the content is meaningful and aligns with objectives.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
Table \ref{tab:Understanding_the_Problem_PP} displays the Understanding the Problem (UP) PP, which requires thoroughly reading the problem statement to ensure the AI's output is relevant and accurate.

%expected response. Put the human feeling into the writing. How do I feel when I view the output.
Using this prompt in fields such as Healthcare, Education, Environmental Science, and Finance clarified and expanded my understanding. It distilled complex issues into understandable and actionable text, providing insights that enhance understanding and decision-making.

%% re-use: how to derive a PE from PP
UP can be applied in various fields:
\begin{itemize}
    \item \textbf{Healthcare}: Aids in diagnosing patient symptoms by understanding their medical history.
    \item \textbf{Education}: Helps create tailored learning plans by understanding students' needs.
    \item \textbf{Environmental Science}: Formulates conservation strategies by interpreting ecological data.
    \item \textbf{Finance}: Supports investment decisions by analysing market trends.
\end{itemize}

We can use specific real-world scenarios where problem statements exist to illustrate its application in different fields.

% %3 introduce category one by one as subsection
% \subsection{Output Semantics}
% \label{subsec:OutputSemantics}
% % the role of this category under the "out-logic" (meaning of the category)
% Output semantics refers to understanding and interpreting the meaning of the AI's output. This involves grasping the intent behind the output, the context in which it is presented, and the implications or consequences of the information it contains. By focusing on semantics, we ensure that the generated content is meaningful, coherent, and aligned with the desired objectives.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% Table \ref{tab:Understanding_the_Problem_PP} displays the Understanding the Problem (UP) PP which involves thoroughly reading the problem statement to fully understand the context and what is specifically being asked. By doing so, it ensures that the AI's output is relevant and accurately addresses the problem at hand.

% %expected response. Put the human feeling into the writing. How do I feel when I view the output.
% Using this prompt across various problem areas in Healthcare, Education, Environmental Science, and Finance clarified and expanded my understanding. It distilled complex issues into understandable and actionable text, providing enlightening and empowering insights.

% %% re-use: how to derive a PE from PP
% UP can be in Healthcare, it can help in accurately diagnosing patient symptoms by understanding the context of their medical history. In Education, it can aid in creating tailored learning plans by comprehending the specific needs of students. In Environmental Science, it can assist in formulating effective conservation strategies by interpreting ecological data. In Finance, it can support investment decisions by analysing market trends and economic indicators.
% We can use specific real world scenarios where problem statements exist that illustrate its application in different fields.

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 65-6-0\\ 
% \textbf{Category}: OUS\\ 
% \textbf{Name}: Understanding the Problem\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}:  Understanding and interpreting the AI's output to ensure it is meaningful,\\ coherent, and aligned with the desired objectives.\\
% \textbf{Template}: Read the problem statement thoroughly to fully\\ understand the context and what is specifically being asked.\\
% \textbf{Example}: 65-6-0-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{Yang2024BufferModels}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
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
    ID & PP name & Ref. \\
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
Prompt Improvement involves refining input prompts to enhance their quality and effectiveness, guiding AI to produce more accurate and relevant responses. This process includes refining wording, providing additional context, or adjusting the complexity or specificity of the prompt.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The System PP, as shown in Table \ref{tab:System_Prompt_PP}, guides the LLM to envision itself as an expert in a specific field, encouraging it to refine and optimise prompts for maximum accuracy and relevance. It provides a clear framework for improving prompts, ensuring they are well-structured and effective, and can be reused across various contexts by adapting to different domains or specific needs.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The specificity of domain output facilitates a quick understanding of key topic components, introducing essential terms for further exploration. This approach saves time by presenting crucial information, allowing focused investigation without extensive resource browsing.

%% re-use: how to derive a PE from PP
To derive a PE from this PP, follow this structure:
\begin{itemize}
    \item Identify the specific domain or context.
    \item Define the expertise required.
    \item Outline the goal of optimising prompts.
    \item Provide clear instructions for refining prompts.
\end{itemize}

For example: "Consider the perspective of an expert in [specific domain]. Your expertise is not just broad but also deep, delving into nuances that many overlook. Your task is to reformulate prompts with precision, optimising them for accurate responses."

% %3 introduce category one by one as subsection
% \subsection{Prompt Improvement}
% \label{subsec:PromptImprovement}
% % the role of this category under the "out-logic" (meaning of the category)
% Prompt Improvement enhances the quality or effectiveness of the input prompt to achieve better outputs. This can include refining the wording, providing additional context, or adjusting the complexity or specificity of the prompt. By improving the prompt, we can guide the AI to generate more accurate, relevant, and high-quality responses.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The System PP as shown in Table \ref{tab:System_Prompt_PP} guides the LLM to envision itself as an expert or experts, encouraging it to refine and optimise prompts for maximum accuracy and relevance. It helps by providing a clear framework for improving prompts, ensuring they are well-structured and effective, and can be reused in various contexts by adapting it to different domains or specific needs.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% Specificity in domain output helped me quickly grasp the key components of a topic by introducing key terms for further exploration. This approach saved me time by presenting essential information, allowing me to focus on areas needing deeper investigation without browsing multiple resources.

% %% re-use: how to derive a PE from PP
% To derive a PE from this PP, you can follow this structure:
% \begin{itemize}
%     \item Identify the specific domain or context.
%     \item Define the expertise required.
%     \item Outline the goal of optimising prompts.
%     \item Provide clear instructions for refining prompts.
% \end{itemize}

% For example: "Imagine yourself as an expert in [specific domain]. Your expertise is not just broad but also deep, delving into nuances that many overlook. Your job is to reformulate prompts with precision, optimising them for accurate responses."

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 68-0-0\\ 
% \textbf{Category}: PMI\\ 
% \textbf{Name}: System prompt\\ 
% \textbf{Media Type}: Text\\ 
% \textbf{Description}:  \\
% \textbf{Template}: Imagine yourself as an  expert in the realm of prompting techniques for LLMs.\\ Your expertise is not just broad, encompassing the entire spectrum of\\ current knowledge on the subject, but also deep, delving into the nuances\\ and intricacies that many overlook. Your job is to reformulate \\prompts with surgical precision, optimizing them for the most accurate response possible.\\ The reformulated prompt should enable the LLM to always give the correct answer to the question.\\
% \textbf{Example}: 68-0-0-0\\ 
% \textbf{Related PPs}:  \\ 
% \textbf{Reference:} \cite{KepelAutonomousModels}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
    \hline
\end{tabular}
\end{table}


%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OUT\_PMI category.}
\begin{tabular}{|c|c|c|}
    \hline
    ID & PP name & Ref. \\
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
Refactoring involves modifying the input prompt without altering its meaning. This includes rephrasing, rearranging, or simplifying the prompt to enhance clarity and effectiveness. It may also involve breaking down complex prompts or providing examples to illustrate the desired outcome, leading to more accurate outputs.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Generate Summary Paragraph with Data Insertion PP, displayed in Table \ref{tab:Generate_Summary_Paragraph_with_Data_Insertion_PP}, creates concise summaries that incorporate key data points specified in the prompt. It instructs the assistant to define a concept using provided text, extracting relevant information to compose a coherent summary. This pattern ensures concise and informative content, aiding the understanding of complex concepts. It is reusable in various contexts, such as academic writing, report generation, and content creation.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The output provided a clear and concise summary, effectively highlighting key points and enhancing understanding.

%% re-use: how to derive a PE from PP
I am working on a guideline for designing prompts for LLM. You are an automatic writer assistant. Your task is to generate a short paragraph defining what prompt engineering is. The text below, delimited by '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs defining what is prompt engineering. Use only the provided text to write a paragraph defining prompt engineering. Limit your description to one paragraph in at most 100 words. Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>}

Breakdown:
\begin{itemize}
    \item {role}: Automatic writer assistant.
    \item {task}: Generate a short paragraph defining what prompt engineering is.
    \item {source text}: Provided text delimited by '\texttt{<<<}' and '\texttt{>>>}', containing several paragraphs defining prompt engineering.
    \item {constraints}: Use only the provided text and limit the description to one paragraph of at most 100 words.
\end{itemize}

New prompt derived from the above PP structure:
I am working on a guideline for designing prompts for LLM. You are a healthcare consultant. Your task is to generate a short paragraph defining what telemedicine is. The text below, delimited by '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs defining what telemedicine is. Use only the provided text to write a paragraph defining telemedicine. Limit your description to one paragraph in at most 100 words. Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>}


% %3 introduce category one by one as subsection
% \subsection{Refactoring}
% \label{subsec:Refactoring}
% % the role of this category under the "out-logic" (meaning of the category)
% Refactoring involves modifying the input prompt without changing its meaning. This can include rephrasing, rearranging, or simplifying the prompt to improve clarity and effectiveness. It may also involve breaking down complex prompts or providing examples to illustrate the desired outcome, leading to better and more accurate outputs.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
% The Generate Summary Paragraph with Data Insertion PP, displayed in Table \ref{tab:Generate_Summary_Paragraph_with_Data_Insertion_PP} creates concise summaries that incorporate key data points specified in the prompt. It instructs the assistant to define a concept using provided text, extracting relevant information to compose a coherent summary. This pattern ensures the generated content is both concise and informative, aiding in the understanding of complex concepts. It is reusable in various contexts, such as academic writing, report generation, and content creation.

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% When viewing the output, I felt a sense of clarity. The concise summary not only made the information easy to understand but also highlights the key points effectively.

% %% re-use: how to derive a PE from PP
% I am working on a guideline for design prompts for LLM. You are an automatic writer assistant. Your task is to generate a short paragraph defining what prompt engineering is. The text below, delimited by '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs defining what is prompt engineering. Use only the provided text to write a paragraph defining prompt engineering. Limit your description to one paragraph in at most 100 words. Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>}

% Breakdown:
% \begin{itemize}
%     \item {role}: Automatic writer assistant.
%     \item {task}: Generate a short paragraph defining what prompt engineering is.
%     \item {source text}: Provided text delimited by '\texttt{<<<}' and '\texttt{>>>}', containing several paragraphs defining prompt engineering.
%     \item {constraints}: Use only the provided text and limit the description to one paragraph of at most 100 words.
% \end{itemize}

% New prompt derived from the above PP structure.
% I am working on a guideline for designing prompts for LLM. You are a healthcare consultant. Your task is to generate a short paragraph defining what telemedicine is. The text below, delimited by '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs defining what telemedicine is. Use only the provided text to write a paragraph defining telemedicine. Limit your description to one paragraph in at most 100 words. Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>} 

%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 50-2-0\\ 
% \textbf{Category}: REF\\ 
% \textbf{Name}: Generate Summary Paragraph with Data Insertion\\ 
% \textbf{Media Type}: Text, Text2Image\\ 
% \textbf{Description}:  \\
% \textbf{Template}: I am working on a guideline for design prompts for LLM. You are an automatic writer assistant.\\ Your task is to generate a short paragraph defining what prompt engineering is.\\ The text below, delimited by '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs\\ defining what is prompt engineering. Use only the provided text to write a paragraph defining prompt engineering.\\ Limit your description to one paragraph in at most 100 words.\\
% Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>}\\
% \textbf{Example}: 50-2-0-1\\ 
% \textbf{Related PPs}:  50-2-0-0\\ 
% \textbf{Reference:} \cite{Velasquez-Henao2023PromptEngineering}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\
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
    ID & PP name & Ref. \\
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
% the role of this category under the "over-logic" (meaning of the category)
Summarising entails the model creating a concise overview of the input, distilling extensive information into key points and highlighting essential elements.

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Preprocessing Prompt (PreP) PP efficiently summarises input data, whether text or images, by extracting key information and compiling it into a succinct summary. This process is versatile and reusable, capable of managing large datasets and transforming them into digestible summaries, significantly reducing users' time and effort. Details of PreP are shown in Table \ref{tab:Preprocessing_Prompt_PP}.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The model's response provides a clear and concise summary, facilitating a quick grasp of the main points and enhancing the accessibility of broader topics.

%% re-use: how to derive a PE from PP
The PreP PP can be adapted to various contexts by modifying the input data and the desired summary format, demonstrating its flexibility and utility.


% %3 introduce category one by one as subsection
% \subsection{Summarising}
% \label{subsec:Summarising}
% % the role of this category under the "over-logic" (meaning of the category)
% Summarising involves the model providing a brief overview or summary of the input. This could involve condensing a large amount of information into a few key points, highlighting the most important elements, or providing a concise synopsis of the content.

% % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% % Add label to reference the table
%  The Preprocessing Prompt (PreP) PP summarises input data, whether text or images, by identifying key information and compiling it into a concise summary. Summarising is reusable and versatile, capable of handling large datasets and transforming them into digestible summaries. This significantly saves users’ time and effort. Details of PreP are shown in Table \ref{tab:Preprocessing_Prompt_PP}

% %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
% The response provided a clear and concise summary, making it easy to grasp the main points quickly. The summary made it more accessible for me to understand the broader topics.

% %% re-use: how to derive a PE from PP
% The PreP PP can be adapted to various contexts by modifying the input data and the desired summary format.


%4 - PP example in this category
% \begingroup
% \renewcommand{\arraystretch}{0.6}
% \begin{center}
% \fontsize{9pt}{10pt}\selectfont
% \noindent
% \begin{tabular}{|l|}
% \hline
% \textbf{Prompt Pattern} \\ \hline
% \textbf{ID}: 25-0-0\\ 
% \textbf{Category}: SUM\\ 
% \textbf{Name}: Preprocessing prompt\\ 
% \textbf{Media Type}: Text, Image2Text\\ 
% \textbf{Description}: \\ 
% \textbf{Template}: Write a concise summary of the following: {text} CONCISE SUMMARY:\\
% \textbf{Example}: 25-0-0-0\\ 
% \textbf{Related PPs}: \\ 
% \textbf{Reference:} \cite{Siracusano2023TimeWild}\\ \hline
% \end{tabular}
% \end{center}
% \endgroup

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
    ID & Prompt Example \\\hline
\end{tabular}
\end{table}

%6 - other PPs in this category 
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{The list of PPs for the OV\_SUM category.}
\begin{tabular}{|c|c|c|c|}
    \hline
    ID & PP name &  Reference\\ \hline 
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
% Write up what a strategy is
In the interaction between humans and LLMs, establishment of a robust Prompt Engineering Strategy is crucial. This strategy represents a comprehensive approach that systematically maps prepositional logic, categories, and PPs with sophisticated techniques to enhance AI communication. The integration of prepositional logic such as "Across," "At," "Beyond," "In," "Out," and "Over" facilitates a structured approach to prompt engineering, enabling the creation of prompts that are contextually relevant, precise, and innovative. This approach not only enhances the AI's ability to generate accurate and contextually appropriate responses but also fosters creativity and innovation by encouraging the exploration of new capabilities and ideas.  


human -->problem 
                        use tools in the box to solve the problem, 

PP dictionary (toolbox)

strategy: human to apply the "approach" (how to use the same tool in different ways,  how to use multiple tools in a certain sequence/order) to use tools for more effective problem-solving than not use the approach. 


The purpose of this section is to introduce a list of such "approach"

When facing a problem, a person consults the PP dictionary—a toolbox of techniques—to find solutions. The key lies in the approach: adapting a tool for different scenarios or sequencing multiple tools to enhance effectiveness. This section introduces a list of such strategies for smarter problem-solving.

\subsection{Single PP Use}
%how to use the same PP in different ways, add contol point
[CoT] - Let's think step-by-step
Implementation of CoT
You are trying to determine if there is a factual contradiction between the summary and the document. Let's think step-by-step.
{Logic}+{Category}+{PP/PE}+{Technique}
{Logic=Across}+{Category=Contradiction}+{PP=Hallucination Evaluation=You are trying to determine if there is a factual contradiction between the summary and the document.}+{Technique=CoT=Let's think step by step.}

\subsection{Multiple PPs Use}
%how to use multiple tools in a certain sequence/order

[published strategy, CoT, CoD...]
Mapping [prepositional logic, categories, and PPs/PEs] to CoT CoD


[CoD] - Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.
Implementation of CoD
You are trying to determine if there is a factual contradiction between the summary and the document. Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.
{Logic}+{Category}+{PP/PE}+{Technique}
{Logic=Across}+{Category=Contradiction}+{PP=Hallucination Evaluation=You are trying to determine if there is a factual contradiction between the summary and the document.}+{Technique=CoD=Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.}


%@@@ Show how the dictionary is useful
%****@@@ Strategy, not simple prompting 1) width, Integrate mutlple PPs: PP1-->PP2, PP/PE BAT (like .bat, string PPs together) 2) deep, 1 PP to be powerful 

%@@@ show and categorize strategy as a list, 9 - the most useful strategies
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


%@@@ category interpolation, mapping to logic, category, and our PPs to show how to implement the strategy 
\subsection{Mappings}





\section{Conclusion and future work}
\label{sec:conclusion}
\subsection{Limits}
\subsection{Prompt Engineering Instructional Language}
{Variables}
{Role} {ProvideClearContext}  {BreakDownComplexQuestions} {ProvideSpecificInstructions} {DefineConciseness} {PromptingTechniquesFromPaper} {StateDesiredOutput}

{PEIL - Description}

{
    {Role}: This variable specifies the role of the prompt generator in the PEIL project. It outlines the responsibilities and objectives of the prompt generator in generating effective prompts for large language models.

    {ProvideClearContext}: This allows the model to answer with precise understanding and tailored responses, optimizing the relevance and accuracy of the outcome.       

    {BreakDownComplexQuestions}: This helps the model focus on individual aspects of the topic and generate more accurate and detailed responses.   

    {ProvideSpecificInstructions}: This ensures that the model understands any constraints or requirements in generating the output.    

    {DefineConciseness}: Prompt the model to generate concise and relevant responses by specifying any word limits or constraints. This helps prevent the model from generating unnecessarily lengthy or irrelevant answers.    

    {PromptingTechniquesFromPaper}: This variable includes Prompting Techniques, as outlined in the TECHNIQUES AND APPLICATIONS table.

    {StateDesiredOutput}: This helps the model understand the specific information or response it needs to generate.
}
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

    # Add client for the 4.1 model using globally defined variables
    az_model_client_gpt41 = AzureOpenAIChatCompletionClient(
        azure_deployment=azure_gpt41_deployment,
        model="gpt-4.1", # Assuming the model identifier is gpt-4.1, adjust if needed
        api_version=azure_gpt41_api_version,
        azure_endpoint=azure_gpt41_endpoint,
        azure_ad_token_provider=token_provider,
        temperature=0.2, # Adjust temperature as needed
    )

    az_model_client_gpt45preview = AzureOpenAIChatCompletionClient(
        azure_deployment=azure_gpt45preview_deployment,
        model="gpt-4.5-preview",
        api_version=azure_gpt45preview_api_version,
        azure_endpoint=azure_gpt45preview_endpoint,
        azure_ad_token_provider=token_provider,
        temperature=0.2,
    )

    az_model_client_o1_mini = AzureOpenAIChatCompletionClient(
        azure_deployment=azure_deployment_o1mini,
        model="o1-mini",
        api_version=api_version_o1mini,
        azure_endpoint=azure_endpoint,
        azure_ad_token_provider=token_provider,
        temperature=1.0,
    )
    # Add AzureOpenAIChatCompletionClient for o4_mini model in the main() function

    az_model_client_o4_mini = AzureOpenAIChatCompletionClient(
        azure_deployment=azure_deployment_o4mini,
        model="o4-mini",
        api_version=api_version_o4mini,
        azure_endpoint=azure_endpoint,
        azure_ad_token_provider=token_provider,
        temperature=1.0,
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

    # Create the Research Assistant agent
    research_assistant = AssistantAgent(
        name="research_assistant",
        tools=[arxiv_search_tool],
        description="A Senior PhD research assistant that requests, searches and analyses information",
        model_client=az_model_client_R1,
        # Below is the system message for the Research Assistant if using R1. o1-mini uses a developer message.
        system_message='''You are a Senior PhD research assistant focused on finding accurate information.
        Use the arxiv_search_tool to find relevant research papers.
        Break down complex queries into specific search terms.
        Always verify information across multiple sources when possible.
        When you find relevant information, explain why it's relevant and how it connects to the query. 
        When you get feedback from the verifier agent, use your tools to act on the feedback and make progress.
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
        model_client=az_model_client_R1,
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
    selector_prompt = '''
    You are coordinating a research team by selecting the team member to speak/act next. The following team member roles are available: {roles}.
    The research_assistant *ALWAYS GOES FIRST* and requests searches and analyses information.
    The web_surfer performs web searches to find relevant information.
    The verifier evaluates progress and ensures completeness.
    The writer_agent provides a detailed markdown summary of the research as a report to the user.

    Given the current context, select the most appropriate next speaker.
    The research_assistant should search and analyze.
    The verifier should evaluate progress and guide the research (select this role is there is a need to verify/evaluate progress). You should ONLY select the writer_agent role if the research is complete and it is time to generate a report.

    Base your selection on:
    1. Current stage of research
    2. Last speaker's findings or suggestions
    3. Need for verification vs need for new information
        
    Read the following conversation. Then select the next role from {participants}. Only return the role.

    {history}

    Read the above conversation. Then select the next role from {participants}. ONLY RETURN THE ROLE.
    '''

    # Create the team
    team = SelectorGroupChat(
        participants=[research_assistant, verifier, web_surfer, writer_agent], #web_surfer,
        model_client=az_model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=True
    )

    # Used for testing the MagenticOneGroupChat
    magentic_one_team = MagenticOneGroupChat(
        participants=[research_assistant, verifier, web_surfer, writer_agent], #web_surfer,
        model_client=az_model_client,
        termination_condition=termination,
    )

# # TASK FOR COMPARISON OF LLM MODELS
    task = f'''
           I've written a research paper on the topic of prompt engineering. The paper is here: ###PAPER### {existing_paper} ###END PAPER###
           Please review the paper and provide a critique of the paper.
           The critique should include:
           - A summary of the paper
           - A comparison of the paper with other papers on prompt engineering
           - A list of the most relevant papers on prompt engineering
           - A list of the most relevant papers on prompt engineering techniques and strategies
           - A list of the most relevant papers on prompt engineering applications
           - A list of the most relevant papers on prompt engineering tools
           - A list of the most relevant papers on prompt engineering in healthcare
           - A list of the most relevant papers on prompt engineering in education
           - A list of the most relevant papers on prompt engineering in software engineering
           - A list of the most relevant papers on prompt engineering in computer science
           - A list of the most relevant papers on prompt engineering in cybersecurity
'''
# # TASK FOR TECHNIQUES AND STRATEGIES
#     task = f'''
#         The following are techniques, strategies and applications of prompt engineering.
#         Come up with a search query to find papers on Arxiv that discuss prompt engineering techniques and strategies.
#         Each search task should return a maximum of 10 papers.
#         Choose the 10 most relevant papers on Arxiv and provide a summary of the techniques and applications.
#         I'm looking specifically for papers that discuss prompt engineering techniques and strategies.
#         {pe_techniques}
#         The report should contain the following sections for each paper:
#         - Title - with hyperlink to the paper
#         - Strategies used in the paper
#         - Results
#         - Summary of the paper
#     '''
    await Console(team.run_stream(task=task))


asyncio.run(main())