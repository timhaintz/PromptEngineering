'''
DESCRIPTION
Simple Categorisation Write-Up Generator

This script extracts the 4 core variables from the existing categorisation_write_up.py data
and generates a prompt for AI writeup generation using Azure OpenAI models.
It simplifies the complex categorisation system by focusing on the essential components:

#1[ ], which logic
#2[ ], the list of PP category under #1[ ]
#3[ ], the category you want AI to write up 
#4[ ], the latex table of the representative PP in #3[]

The script allows you to:
- Generate academic write-ups for specific prompt pattern categories
- Use various Azure OpenAI models for content generation
- Export results to LaTeX format for academic publications
- Debug variable hydration for testing

Version:        1.0
Author:         Tim Haintz
Creation Date:  20250710

LINKS
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity
https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
https://learn.microsoft.com/en-us/azure/ai-services/authentication-identity

EXAMPLE USAGE
# Basic writeup generation
python simple_categorisation_writeup.py -logic "Beyond" -category "prediction"

# With specific model and output file
python simple_categorisation_writeup.py -logic "Beyond" -category "prediction" -model "gpt-4.1" -output "beyond_prediction.tex"

# Debug variable hydration
python simple_categorisation_writeup.py -logic "Beyond" -category "prediction" -show_vars

# Show complete crafted prompt being sent to LLM
python simple_categorisation_writeup.py -logic "Beyond" -category "prediction" -show_crafted_prompt

# List available options
python simple_categorisation_writeup.py -list_logics
python simple_categorisation_writeup.py -list_categories "Beyond"
python simple_categorisation_writeup.py -list_categories

PROMPT PATTERN LOGIC STRUCTURE
The categorisation follows English language logic:
- Across: Multiple domains/disciplines integration
- At: Specific context/scenario targeting
- Beyond: Boundary-pushing capabilities/innovation
- In: Internal/self-reflection within systems
- Out: Output generation (creative/code)
- Over: Comprehensive coverage/oversight/review
'''

import argparse
import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from azure_models import get_model_client, get_available_models

# Load environment variables
load_dotenv()

# Import the existing data structures from the complex script

#############################################
# PROMPT PATTERN LOGIC DEFINITIONS         #
#############################################

LOGIC_DEFINITIONS = {
    "Across": {
        "description": "Signifies one topic from the other. Represents prompts that span multiple domains or disciplines, integrating diverse types of knowledge.",
        "focus": "Multiple domains/disciplines integration"
    },
    "At": {
        "description": "Refers to a more specific aspect or detail of the topic. Prompts that are specific to a certain context or scenario, targeting precise responses.",
        "focus": "Specific context/scenario targeting"
    },
    "Beyond": {
        "description": "Discusses aspects that are on the far side of a certain point or limit of a topic. Prompts that push the boundaries of what the AI can do, exploring new capabilities or innovative ideas.",
        "focus": "Boundary-pushing capabilities/innovation"
    },
    "In": {
        "description": "Indicates that something is contained within a topic or space. Prompts that are internal to a system, focusing on self-reflection or introspection.",
        "focus": "Internal/self-reflection within systems"
    },
    "Out": {
        "description": "Conveys the idea of expanding upon or moving beyond the general scope of a topic. Prompts that generate outputs, such as creative writing or code generation.",
        "focus": "Output generation (creative/code)"
    },
    "Over": {
        "description": "Describes elements that span the entirety of the topic, implying comprehensive coverage. Prompts that require oversight or review, such as editing or improving existing content.",
        "focus": "Comprehensive coverage/oversight/review"
    }
}


CATEGORY_TEMPLATES = {
    # Logic Layer: Across - Multiple domains/disciplines integration
    "Across": {
        "argument": {
            "latex_table": r"""
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
            """,
        },
        "comparison": {
            "latex_table": r"""
\begin{table}[h!]
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
\end{table}
            """,
        },
        "contradiction": {
            "latex_table": r"""
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
            """,
        },
        "cross_boundary": {
            "latex_table": r"""
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
            """,
        },
        "translation": {
            "latex_table": r"""
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
    \textbf{Description}: This process converts data from one representation (A) into another (B) by translating, rephrasing, \\or paraphrasing the original content. It ensures the core meaning remains intact while adapting the format \\for a different context or audience. \\ 
    \textbf{Template}: Translate/Paraphrase/rephrase  data representation A to representation B.\\ 
    \textbf{Example}: 13-0-0-0\\ 
    \textbf{Related PPs}: 13-0-0-1\\ 
    \textbf{Reference:} \cite{Reynolds2021PromptParadigm}\\ \hline
\end{tabular}
\end{table}
            """,
        }
    },

    # Logic Layer: At - Specific context/scenario targeting
    "At": {
        "assessment": {
            "latex_table": r"""
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
            """,
        },
        "calculation": {
            "latex_table": r"""
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
    \textbf{Description}: Simulates calculator API calls, where the simulation API\\ is invoked using the syntax '[Calculator(expression)]', with 'expression'\\ being the mathematical computation to be performed.\\ 
    \textbf{Template}: Your task is to add calls to a Calculator API to a piece of text.\\ The calls should help you get information required to complete the text.\\ You can call the API by writing "[Calculator(expression)]" where "expression"\\ is the expression to be computed. Here are some examples of API calls:\\
    \textbf{Example}: 17-1-0-0\\ 
    \textbf{Related PPs}: 22-0-1, 22-2-8\\ 
    \textbf{Reference:} \cite{Schick2023Toolformer:Tools}\\ \hline
\end{tabular}
\end{table}
            """,
        }
    },

    # Logic Layer: Beyond - Boundary-pushing capabilities/innovation
    "Beyond": {
        "hypothesise": {
            "latex_table": r"""
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
     \\texttt{\"\"\" \\{sample\\_prompt\\} \"\"\"} \\\\
    \\textbf{Example}: 68-0-1-0\\\\ 
    \\textbf{Related PPs}:  \\\\ 
    \\textbf{Reference:} \\cite{KepelAutonomousModels}\\\\ \\hline
\end{tabular}
\end{table}
            """,
        },
        "logical_reasoning": {
            "latex_table": r"""
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
            """,
        },
        "prediction": {
            "latex_table": r"""
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
            """,
        },
        "simulation": {
            "latex_table": r"""
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
            """,
        }
    },

    # Logic Layer: In - Internal/self-reflection within systems
    "In": {
        "categorising": {
            "latex_table": r"""
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
            """,
        },
        "classification": {
            "latex_table": r"""
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
            """,
        },
        "clustering": {
            "latex_table": r"""
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
            """,
        },
        "error_identification": {
            "latex_table": r"""
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
    \textbf{Media Type}: Text \\ 
    \textbf{Description}: Requests a list of fact-checkable cybersecurity-related facts that the response\\ depends on.\\ 
    \textbf{Template}: From now on, when you generate an answer, create a set of facts that the answer\\ depends on that should be fact-checked and list this set of facts at the end of your output. Only \\include facts related to cybersecurity.\\
    \textbf{Example}: 0-2-0-3\\ 
    \textbf{Related PPs}: 0-2-0-[0-2]\\ 
    \textbf{Reference:} \cite{White2023AChatGPT}\\ \hline
\end{tabular}
\end{table}
            """,
        },
        "input_semantics": {
            "latex_table": r"""
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Sentence Similarity PP}
\label{tab:Sentence_Similarity_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern}\\ \hline
    \textbf{ID:} 19-11-1\\ 
    \textbf{Category:} INP \\ 
    \textbf{Name:} Sentence Similarity\\ 
    \textbf{Media Type:} Image2Text, Text, Text2Image\\ 
    \textbf{Description:} Evaluates the semantic similarity between two input sentences. \\
    \textbf{Template:} Rate the semantic similarity of two input sentences on a scale of 0 - definitely not\\ to 5 - perfectly.\\
    \textbf{Example:} 19-11-1-0\\ 
    \textbf{Related PPs:} 19-11-0, 19-2-0, 60-0-8\\ 
    \textbf{Reference:} \cite{Honovich2022InstructionDescriptions}\\ \hline
\end{tabular}
\end{table}
            """,
        },
        "requirements_elicitation": {
            "latex_table": r"""
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
            """,
        }
    },
    
    # Logic Layer: Out - Output generation (creative/code)
    "Out": {
        "context_control": {
            "latex_table": r"""
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
            """,
        },
        "decomposed_prompting": {
            "latex_table": r"""
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
            """,
        },
        "output_customisation": {
            "latex_table": r"""
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
            """,
        },
        "output_semantics": {
            "latex_table": r"""
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
            """,
        },
        "prompt_improvement": {
            "latex_table": r"""
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
    \textbf{Description}:  Precision driven reformulation using the role of an expert.\\
    \textbf{Template}: Imagine yourself as an expert in the realm of prompting techniques for LLMs. Your expertise is not just broad,\\ encompassing the entire spectrum of current knowledge on the subject, but also deep, delving into the nuances and\\ intricacies that many overlook. Your job is to reformulate prompts with surgical precision, optimizing them for the most\\ accurate response possible. The reformulated prompt should enable the LLM to always give the correct answer to the\\ question.\\
    \textbf{Example}: 68-0-0-0\\ 
    \textbf{Related PPs}:  \\ 
    \textbf{Reference:} \cite{KepelAutonomousModels}\\ \hline
\end{tabular}
\end{table}
            """,
        },
        "refactoring": {
            "latex_table": r"""
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
    \textbf{Description}:  Automatic writing assistant that generates short paragraphs.\\
    \textbf{Template}: I am working on a guideline for design prompts for LLM. You are an automatic writer assistant.\\ Your task is to generate a short paragraph defining what prompt engineering is. The text below, delimited by\\ '\texttt{<<<}' and '\texttt{>>>}', provides several paragraphs defining what is prompt engineering. Use only the provided text to\\ write a paragraph defining prompt engineering. Limit your description to one paragraph in at most 100 words.\\
    Here is the text: \texttt{<<<} [Insert the text here] \texttt{>>>}\\
    \textbf{Example}: 50-2-0-1\\ 
    \textbf{Related PPs}:  50-2-0-0\\ 
    \textbf{Reference:} \cite{Velasquez-Henao2023PromptEngineering}\\ \hline
\end{tabular}
\end{table}
            """,
        }
    },
    
    # Logic Layer: Over - Comprehensive coverage/oversight/review
    "Over": {
        "summarising": {
            "latex_table": r"""
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
    \textbf{Description}: Summarises the data in a concise mannner\\ 
    \textbf{Template}: Write a concise summary of the following: {text} CONCISE SUMMARY:\\
    \textbf{Example}: 25-0-0-0\\ 
    \textbf{Related PPs}: \\ 
    \textbf{Reference:} \cite{Siracusano2023TimeWild}\\ \hline
\end{tabular}
\end{table}
            """,
        },
        "synthesis": {
            "latex_table": r"""
\begin{table}[h!]
\fontsize{9pt}{10pt}\selectfont
\centering
\caption{Ensuring Thorough Review and Validation}
\label{tab:Review_and_Validation_PP}
\begin{tabular}{|l|}
    \hline
    \textbf{Prompt Pattern} \\ \hline
    \textbf{ID}: 65-4-0\\ 
    \textbf{Category}: SYN\\ 
    \textbf{Name}: Ensuring Thorough Review and Validation\\ 
    \textbf{Media Type}: Text, Image2Text\\ 
    \textbf{Description}: Combine and refine all subanswers to create a precise and well-informed final response.\\ 
    \textbf{Template}: Synthesize all subanswers thoroughly to construct an accurate final answer to the main question.\\
    \textbf{Example}: 65-4-0-1\\ 
    \textbf{Related PPs}: \\ 
    \textbf{Reference:} \cite{Yang2024BufferModels}\\ \hline
\end{tabular}
\end{table}
            """,
        }
    }
}

def get_categories_list_latex(logic: str) -> str:
    """Generate LaTeX enumerated list of categories for a logic."""
    if logic not in CATEGORY_TEMPLATES:
        return "No categories found for this logic."
    
    categories = CATEGORY_TEMPLATES[logic]
    items = []
    for i, (cat_name, cat_data) in enumerate(categories.items(), 1):
        formatted_name = cat_name.replace('_', ' ').title()
        # 'description' key removed; skip or provide fallback
        items.append(f"    \\item \\textbf{{{formatted_name}}}")
    
    return "\\begin{enumerate}\n" + "\n".join(items) + "\n\\end{enumerate}"

def get_latex_table(logic: str, category: str) -> str:
    """Get the LaTeX table for a specific category."""
    if logic not in CATEGORY_TEMPLATES:
        return "[LaTeX table not found - logic not available]"
    
    category_lower = category.lower()
    if category_lower not in CATEGORY_TEMPLATES[logic]:
        return f"[LaTeX table not found - category '{category}' not available in '{logic}' logic]"
    
    latex_table = CATEGORY_TEMPLATES[logic][category_lower].get('latex_table', '')
    if not latex_table:
        return f"[LaTeX table not yet defined for '{category}' category]"
    
    return latex_table

def build_prompt(logic: str, category: str) -> str:
    """Build the complete prompt with hydrated variables."""
    
    # Variable #1: Logic name
    var1_logic = logic
    
    # Variable #2: List of PP categories under the logic
    var2_categories_list = get_categories_list_latex(logic)
    
    # Variable #3: The category for AI writeup
    var3_category = category
    
    # Variable #4: The LaTeX table of representative PP
    var4_latex_table = get_latex_table(logic, category)
    
    # Build the complete prompt
    prompt = f"""You are a world top ranking university PhD student in the field of AI application, conducting front edge research and writing a research paper on "The Way to Talk to AI: A Dictionary of Prompt Patterns to LLMs"

The proposed logic to construct the dictionary toward the best convenience and effectiveness of human to AI communication is to apply English language logic of in, out, over, across, beyond etc. to build a dictionary of prompt pattern (PP), each with multiple prompt examples (PEs)

As the result of English logic discovery, we have the full list logic summarized in latex
"\\begin{{itemize}}
    \\item \\textbf{{Across}} logic is used to signify one topic from the other. This could represent prompts that span \\textbf{{multiple domains}} or disciplines, integrating diverse types of knowledge.
    \\item \\textbf{{At}} logic is used to refer to a more specific aspect or detail of the topic. This might refer to prompts that are \\textbf{{specific}} to a certain context or scenario, targeting precise responses.
    \\item \\textbf{{Beyond}} logic is used to discuss aspects that are on the far side of a certain point or limit of a topic. This could indicate prompts that push the boundaries of what the AI can do, exploring \\textbf{{new capabilities}} or \\textbf{{innovative ideas}}.
    \\item \\textbf{{In}} logic is used to indicate that something is contained within a topic or space. This could represent prompts that are \\textbf{{internal}} to a system, focusing on self-reflection or introspection.
    \\item \\textbf{{Out}} logic is employed to convey the idea of expanding upon or moving beyond the general scope of a topic. This might be used for prompts that generate \\textbf{{outputs}}, such as creative writing or code generation.
    \\item \\textbf{{Over}} logic is used to describe elements that span the entirety of the topic, which implies comprehensive coverage. This could be associated with prompts that require \\textbf{{oversight}} or review, such as editing or improving existing content.
\\end{{itemize}}"

Thus the dictionary has logic layer, each logic has multiple categories of PP, and each PP has multiple PEs as example of PP applications

For {var1_logic} logic, it has the following category of PPs described in latex as "%2 - introduce categories in this logic
The PP categories under {var1_logic.lower()} logic include:

{var2_categories_list}

Please write to introduce the {var3_category} category, strictly follow the below criteria: 

IMPORTANT: Include the exact LaTeX comment structure as shown in the example. Each section must be preceded by its specific LaTeX comment heading.

1. give one paragraph to introduce over all the logic.
2. give one paragraph to cover: a) Introduce one representative PP of the category, b) what the PP did, and c) How the PP helps people and can be re-used. Reference the table that will appear at the end.
3. give one paragraph to introduce the expected response. Note to write out how a human feel when he/she views the output of this PP implementation.
4. give one paragraph on re-use of the PP, in other words to describe how to derive a PE from the PP
5. AFTER all paragraphs, place the LaTeX table at the very end of the output

REQUIRED LaTeX COMMENT STRUCTURE: You must include these exact comment headings before each corresponding paragraph:
- "% 3.1 the role of this category under the "{var1_logic.lower()}-logic" (meaning of the category)" before paragraph 1
- "% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used" and "% Add label to reference the table" before paragraph 2  
- "%expected response. Put the human feeling into the writing. How do I feel when I view the output." before paragraph 3
- "%% re-use: how to derive a PE from PP" before paragraph 4

STRUCTURE: Follow this exact order: subsection heading → paragraph 1 → paragraph 2 → paragraph 3 → paragraph 4 → LaTeX table at the end

The representative PP data for the table are:

{var4_latex_table} 

Here is an example latex writing for In logic, category: Argument:
"\\subsection{{Argument}}
\\label{{subsec:Argument}}

% 3.1 the role of this category under the "across-logic" (meaning of the category)
Argument involves presenting and defending a claim or viewpoint. This process includes stating a clear claim, providing logical reasoning and evidence to support/refute it. The effectiveness of an argument is measured by its clarity, coherence, and the strength of its supporting evidence. 

% 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and can be re-used
% Add label to reference the table
The Debater PP as described in Table \\ref{{tab:Debater_PP}} focuses on exploring various perspectives. It is designed to facilitate a structured debate format, researching both sides of a given topic and refuting opposing viewpoints. 

%expected response. Put the human feeling into the writing. How do I feel when I view the output.
The AI model typically generates a comprehensive list of pros and cons and a balanced summary. Through follow-up chat, you can request the model to explore either side of the topic in more detail. It is interesting being able to view both viewpoints in an argument, this provides a unique perspective that generates increased thought and depth of a topic.

%% re-use: how to derive a PE from PP
To apply the Debater PP in a given context, set a topic of debate, such as "The Ethical Implications of AI in Healthcare," assign AI the role of a debater, request exploration of both sides of the topic, and define the objective and output format to ensure a balanced and insightful discussion. Here is an example of derived PE:
I want you to act as a debater. I will provide you with a topic related to current events: "The Ethical Implications of AI in Healthcare." Your task is to research both sides of the debate, present valid arguments for the benefits and drawbacks of AI in healthcare, refute opposing points of view with evidence, and draw persuasive conclusions. Your goal is to help the audience gain a comprehensive understanding of the ethical landscape and practical impact of AI in this field."

\\begin{{table}}[h!]
\\fontsize{{9pt}}{{10pt}}\\selectfont
\\centering
\\caption{{Debater PP}}
\\label{{tab:Debater_PP}}
\\begin{{tabular}}{{|l|}}
    \\hline
    \\textbf{{Prompt Pattern}} \\\\ \\hline
    \\textbf{{ID}}: 11-0-9\\\\ 
    \\textbf{{Category}}: ARG\\\\ 
    \\textbf{{Name}}: Debater\\\\ 
    \\textbf{{Media Type}}: Text\\\\ 
    \\textbf{{Description}}:  Debater engages the user in a structured debate format. The user is tasked with researching\\\\ current event topics, presenting balanced arguments for both sides, refuting opposing viewpoints,\\\\ and drawing evidence-based conclusions. The goal is to enhance the user's understanding and insight\\\\ into the topic through a comprehensive and persuasive discussion. \\\\
    \\textbf{{Template}}: I want you to act as a debater. I will provide you with some topics related to current events\\\\ and your task is to research both sides of the debates, present valid arguments for each side, \\\\ refute opposing points of view, and draw persuasive conclusions based on evidence. \\\\Your goal is to help people come away from the discussion with increased knowledge \\\\and insight into the topic at hand. My first request is "I want an opinion piece about:"\\\\
    \\textbf{{Example}}: 11-0-9-0\\\\ 
    \\textbf{{Related PPs}}: 26-0-1, 8-0-0, 26-0-3, 22-0-2, 26-0-0, 22-2-3, 41-2-7, 23-0-0, 40-0-0, 29-0-0\\\\ 
    \\textbf{{Reference:}} \\cite{{Akin202450Prompts}}\\\\ \\hline
\\end{{tabular}}
\\end{{table}}"
"""
    
    return prompt

def generate_writeup(logic: str, category: str, model_version: str = "gpt-4.1") -> str:
    """Generate writeup using AI with the hydrated prompt."""
    
    # Validate inputs
    if logic not in LOGIC_DEFINITIONS:
        raise ValueError(f"Invalid logic '{logic}'. Available: {list(LOGIC_DEFINITIONS.keys())}")
    
    if logic not in CATEGORY_TEMPLATES:
        raise ValueError(f"No category templates available for logic '{logic}'")
    
    category_lower = category.lower()
    if category_lower not in CATEGORY_TEMPLATES[logic]:
        available_cats = list(CATEGORY_TEMPLATES[logic].keys())
        raise ValueError(f"Invalid category '{category}' for logic '{logic}'. Available: {available_cats}")
    
    # Build the prompt with hydrated variables
    prompt = build_prompt(logic, category)
    
    # Get AI response
    try:
        from azure_models import ModelRegistry
        client = get_model_client(model_version)
        model_config = ModelRegistry.get_model(model_version)
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Use model's default temperature if available and valid
        temperature = getattr(model_config, 'default_temperature', None)
        min_temp = getattr(model_config, 'min_temperature', None)
        max_temp = getattr(model_config, 'max_temperature', None)

        # Only set temperature if supported and valid, pass messages as positional
        if temperature is not None and (min_temp is None or max_temp is None or (min_temp <= temperature <= max_temp)):
            response = client.create_chat_completion(messages, temperature=temperature)
        else:
            response = client.create_chat_completion(messages)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {e}"

def show_variables(logic: str, category: str):
    """Show the 4 hydrated variables for debugging."""
    print("\n" + "="*80)
    print("VARIABLE HYDRATION DEBUG")
    print("="*80)
    
    print(f"\n#1[ ], which logic: {logic}")
    
    print(f"\n#2[ ], the list of PP category under #1[ ]:")
    categories_list = get_categories_list_latex(logic)
    print(categories_list)
    
    print(f"\n#3[ ], the category you want AI to write up: {category}")
    
    print(f"\n#4[ ], the latex table of the representative PP in #3[]:")
    latex_table = get_latex_table(logic, category)
    print(latex_table)
    
    print("\n" + "="*80)

def show_prompt(logic: str, category: str):
    """Show the complete crafted prompt being sent to the LLM."""
    print("\n" + "="*80)
    print("COMPLETE CRAFTED PROMPT FOR LLM")
    print("="*80)
    
    prompt = build_prompt(logic, category)
    print(prompt)
    
    print("\n" + "="*80)
    print(f"PROMPT LENGTH: {len(prompt)} characters")
    print("="*80)

def list_logics():
    """List available logics."""
    print("\nAvailable Logics:")
    print("=" * 50)
    for logic, data in LOGIC_DEFINITIONS.items():
        # 'description' key removed; skip or provide fallback
        print(f"• {logic}")
    print("=" * 50)

def list_categories(logic: Optional[str] = None):
    """List categories for a specific logic or all logics."""
    if logic:
        if logic not in CATEGORY_TEMPLATES:
            print(f"Invalid logic '{logic}' or no categories available.")
            return
        
        print(f"\nCategories for {logic} Logic:")
        print("=" * 50)
        for cat_name, cat_data in CATEGORY_TEMPLATES[logic].items():
            formatted_name = cat_name.replace('_', ' ').title()
            # 'description' key removed; skip or provide fallback
            print(f"• {formatted_name} ({cat_name})")
        print("=" * 50)
    else:
        print("\nAll Categories by Logic:")
        print("=" * 60)
        for logic_name in LOGIC_DEFINITIONS.keys():
            if logic_name in CATEGORY_TEMPLATES:
                print(f"\n{logic_name} Logic:")
                for cat_name, cat_data in CATEGORY_TEMPLATES[logic_name].items():
                    formatted_name = cat_name.replace('_', ' ').title()
                    # 'description' key removed; skip or provide fallback
                    print(f"  • {formatted_name} ({cat_name})")
        print("=" * 60)

def save_output(content: str, filename: Optional[str] = None) -> str:
    """Save content to file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"writeup_{timestamp}.tex"
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    parser = argparse.ArgumentParser(
        description="Simple Categorisation Write-Up Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate writeup
  python simple_categorisation_writeup.py -logic "Beyond" -category "prediction"
  
  # Generate writeup with output file
  python simple_categorisation_writeup.py -logic "Beyond" -category "prediction" -output "beyond_prediction.tex"
  
  # Show variable hydration (debug mode)
  python simple_categorisation_writeup.py -logic "Beyond" -category "prediction" -show_vars
  
  # Show complete crafted prompt being sent to LLM
  python simple_categorisation_writeup.py -logic "Beyond" -category "prediction" -show_crafted_prompt
  
  # List available logics
  python simple_categorisation_writeup.py -list_logics
  
  # List categories for a specific logic
  python simple_categorisation_writeup.py -list_categories "Beyond"
  
  # List all categories
  python simple_categorisation_writeup.py -list_categories

  # List available models
  python simple_categorisation_writeup.py -list_models
        """
    )
    parser.add_argument('-list_models', action='store_true', help='List available Azure OpenAI models')
    
    parser.add_argument('-logic', type=str, 
                       help='Logic layer (Across, At, Beyond, In, Out, Over)')
    parser.add_argument('-category', type=str,
                       help='PP category under the specified logic')
    parser.add_argument('-model', type=str, default='gpt-4.1',
                       help='Model version to use (default: gpt-4.1)')
    parser.add_argument('-output', type=str,
                       help='Output filename (optional)')
    parser.add_argument('-show_vars', action='store_true',
                       help='Show variable hydration (debug mode)')
    parser.add_argument('-show_crafted_prompt', action='store_true',
                       help='Show the complete crafted prompt being sent to LLM')
    parser.add_argument('-list_logics', action='store_true',
                       help='List available logics')
    parser.add_argument('-list_categories', type=str, nargs='?', const='all',
                       help='List categories (optional: specify logic)')
    
    args = parser.parse_args()
    
    # Handle utility functions
    if args.list_logics:
        list_logics()
        return

    if args.list_categories:
        if args.list_categories == 'all':
            list_categories()
        else:
            list_categories(args.list_categories)
        return

    if args.list_models:
        print("\nAvailable Azure OpenAI Models:")
        print("=" * 50)
        models = get_available_models()
        for model in models:
            print(f"- {model}")
        print("=" * 50)
        return
    
    # Validate required arguments
    if not args.logic or not args.category:
        print("Error: Both -logic and -category are required for writeup generation")
        parser.print_help()
        return
    
    # Show variables if requested
    if args.show_vars:
        show_variables(args.logic, args.category)
        return
    
    # Show prompt if requested
    if args.show_crafted_prompt:
        show_prompt(args.logic, args.category)
        return
    
    # Validate model
    available_models = get_available_models()
    if args.model not in available_models:
        print(f"Error: Model '{args.model}' not available. Available: {available_models}")
        return
    
    # Generate writeup
    print(f"Generating writeup for {args.logic} > {args.category}...")
    print(f"Using model: {args.model}")
    
    try:
        result = generate_writeup(args.logic, args.category, args.model)
        
        print("\n" + "="*60)
        print("GENERATED WRITEUP")
        print("="*60)
        print(result)
        print("="*60)
        
        # Save if requested
        if args.output:
            filepath = save_output(result, args.output)
            print(f"\n✓ Saved to: {filepath}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
