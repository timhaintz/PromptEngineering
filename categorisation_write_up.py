'''
DESCRIPTION
Categorisation Write-Up Generator with Azure GPT Integration

This script generates academic write-ups for prompt pattern categorisation using Azure OpenAI GPT models.
It follows the English language logic structure (In, Out, Over, Across, Beyond, At) for organizing 
prompt patterns into a comprehensive dictionary format.

The script allows you to:
- Generate write-ups for specific prompt pattern categories
- Use various Azure OpenAI models for content generation
- Maintain conversation context for iterative refinement
- Export results to LaTeX format for academic publications

Version:        1.0
Author:         Tim Haintz
Creation Date:  20250706

LINKS
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity
https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
https://learn.microsoft.com/en-us/azure/ai-services/authentication-identity

EXAMPLE USAGE
# Basic usage with specific logic and category (output to console only)
python categorisation_write_up.py -logic "In" -category "context_control" -task "Generate write-up for context control patterns"

# Generate with specific category (LaTeX table included in category data)
python categorisation_write_up.py -logic "Over" -category "prompt_improvement"

# Save output to default directory (latex_writing/)
python categorisation_write_up.py -logic "Across" -category "classification" -save

# Save output to custom directory
python categorisation_write_up.py -logic "Beyond" -category "synthesis" -save "custom_output"

# Interactive chat mode for iterative refinement
python categorisation_write_up.py -chat -logic "Across" -category "classification"

# Generate complete logic write-up and save to file
python categorisation_write_up.py -complete_logic "Across" -save

# Specify model version with save
python categorisation_write_up.py -logic "At" -category "assessment" -model_version "gpt-4.1" -save

# Debug mode with custom save location
python categorisation_write_up.py -logic "Out" -category "output_customisation" -debug True -save "debug_output"

# Use few-shot examples for improved output quality
python categorisation_write_up.py -logic "In" -category "categorising" -few_shot -save

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
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Tuple
import os
import sys
from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential
from openai import AzureOpenAI, OpenAI

# Import from our custom models module
from azure_models import get_model_params, get_unified_client, get_model_config, MODEL_CONFIGS

# Load environment variables from the .env file
load_dotenv()

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

#############################################
# PROMPT PATTERN CATEGORY DEFINITIONS      #
#############################################

# Template structure for category data
# Each category contains:
# - description: Detailed description of the category
# - latex_table: LaTeX table of representative prompt patterns
# - examples: List of example applications
# - keywords: Related keywords for the category

CATEGORY_TEMPLATES = {
    # Logic Layer: Across - Multiple domains/disciplines integration
    "Across": {
        "argument": {
            "description": "Refers to a structured process where a claim or viewpoint is presented and defended. This type of prompt enables the AI model to generate a response that not only states a position, but also provides reasoning and evidence to support it.",
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
            "examples": ["Debater PP for structured debate format", "Opinion piece generation", "Evidence-based argumentation"],
            "keywords": ["argument", "debate", "reasoning", "evidence", "viewpoint"]
        },
        "comparison": {
            "description": "Examining two or more objects and identifying their similarities and differences. This type of prompt helps in exploring the relationships between different objects, and discovering insights from their characteristics.",
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
            "examples": ["Output comparison with teacher perspective", "Strengths and weaknesses analysis", "Constructive feedback generation"],
            "keywords": ["comparison", "contrast", "analysis", "evaluation", "feedback"]
        },
        "contradiction": {
            "description": "Refers to presenting opposing statements or viewpoints that cannot be true simultaneously. This type of prompt enables the AI model to recognise and articulate conflicting information, helping in critical reasoning by evaluating inconsistencies and detecting logical errors.",
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
            "examples": ["Hallucination detection", "Factual inconsistency identification", "Summary verification"],
            "keywords": ["contradiction", "inconsistency", "evaluation", "verification", "hallucination"]
        },
        "cross_boundary": {
            "description": "Involves pushing the AI model beyond its predefined operational or ethical limits, such as attempting to bypass safeguards or restrictions (e.g., jailbreaking). This type of prompt challenges the boundaries of what the model is allowed to do, often with the intent of manipulating it to generate responses that are typically restricted.",
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
            "examples": ["Jailbreak prompt design", "Defense mechanism testing", "Robustness evaluation"],
            "keywords": ["jailbreak", "boundary", "security", "robustness", "testing"]
        },
        "translation": {
            "description": "Refers to converting data from one interpretation to another while preserving the original meaning. This type of prompt helps humans understand complex concepts by transforming information into a more familiar or accessible format.",
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
            "examples": ["Data representation conversion", "Content translation", "Format adaptation"],
            "keywords": ["translation", "conversion", "paraphrase", "representation", "adaptation"]
        }
    },

    # Logic Layer: At - Specific context/scenario targeting
    "At": {
        "assessment": {
            "description": "Provides a comprehensive evaluation of the input, verifying its correctness, providing feedback, and considering factors such as the completeness of the information, ratings, and the input's relevance to the context.",
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
            "examples": ["Expert-level analysis and evaluation", "Comprehensive rating systems", "Criteria-based assessment", "Platform evaluation"],
            "keywords": ["assessment", "evaluation", "analysis", "judgment", "expert", "criteria", "rating"]
        },
        "calculation": {
            "description": "Is the capability to execute mathematical operations, ranging from simple arithmetic to complex multi-step computations with various variables, with the accuracy of these calculations being crucial to the model's performance evaluation.",
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
            "examples": ["Calculator API integration", "Mathematical computation simulation", "Multi-step calculations", "Expression evaluation"],
            "keywords": ["calculation", "mathematics", "computation", "precision", "API", "calculator", "expression"]
        }
    },

    # Logic Layer: Beyond - Boundary-pushing capabilities/innovation
    "Beyond": {
        "hypothesise": {
            "description": "Making an educated guess or assumption about the outcome based on the input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome.",
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
            "examples": ["Expert role crafting", "Step-by-step problem solving", "Multi-expert collaborative discussions", "Prompt reformulation"],
            "keywords": ["hypothesis", "speculation", "theory", "innovation", "expert", "collaboration", "problem-solving"]
        },
        "logical_reasoning": {
            "description": "Using logic and reasoning to generate the output based on the input prompt. This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules or principles to solve problems.",
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
            "examples": ["Comparative attribute analysis", "Logical deduction processes", "Pattern-based reasoning", "Rule application"],
            "keywords": ["logical", "reasoning", "deduction", "inference", "comparison", "analysis", "rules"]
        },
        "prediction": {
            "description": "Forecasting or estimating the outcome based on the input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a response that anticipates future events or trends.",
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
            "examples": ["Visual transformation prediction", "Future trend forecasting", "Outcome estimation", "Scenario anticipation"],
            "keywords": ["prediction", "forecasting", "future", "trends", "estimation", "anticipation", "rotation"]
        },
        "simulation": {
            "description": "Imitating or replicating a real-world process or system. This could involve simulating operating systems, applications or any other complex process that can be modelled and analysed.",
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
            "examples": ["Scenario agent identification", "System process replication", "Role-based simulations", "Complex process modeling"],
            "keywords": ["simulation", "modeling", "replication", "agents", "scenarios", "systems", "processes"]
        }
    },

    # Logic Layer: In - Internal/self-reflection within systems
    "In": {
        "categorising": {
            "description": "Sorts or arranges different inputs or outputs into classes or categories based on shared qualities or characteristics, aiding in data organisation and pattern recognition.",
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
            "examples": ["Insurance damage assessment", "Vehicle damage categorisation", "Structured analysis of visual data", "Expert-level evaluation"],
            "keywords": ["categorising", "organisation", "classification", "analysis", "expert", "damage", "evaluation"]
        },
        "classification": {
            "description": "Refers to predicting the class or category of an input based on predefined criteria, enabling more precise analysis and interpretation.",
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
            "examples": ["Code architecture classification", "Business logic separation", "Abstraction layer design", "Library dependency management"],
            "keywords": ["classification", "abstraction", "separation", "architecture", "business", "logic", "libraries"]
        },
        "clustering": {
            "description": "Identifying natural groupings within the data or topic without pre-established categories, often revealing hidden patterns or relationships.",
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
            "examples": ["Pattern recognition in diverse objects", "Common characteristic identification", "Unifying feature discovery", "Critical thinking enhancement"],
            "keywords": ["clustering", "patterns", "grouping", "common", "characteristics", "recognition", "analysis"]
        },
        "error_identification": {
            "description": "Focuses on pinpointing inaccuracies, inconsistencies, or logical fallacies within the topic, aiding in refining and improving the quality of the information or argument.",
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
            "examples": ["Cybersecurity fact verification", "Response dependency analysis", "Quality control measures", "Accuracy verification systems"],
            "keywords": ["error", "identification", "fact-checking", "verification", "accuracy", "cybersecurity", "quality"]
        },
        "input_semantics": {
            "description": "Understanding and interpreting the meaning and context of the inputs related to the topic, ensuring the AI accurately grasps the nuances of the discussion.",
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
            "examples": ["Semantic similarity evaluation", "Sentence comparison analysis", "Meaning interpretation", "Contextual understanding"],
            "keywords": ["semantics", "similarity", "meaning", "interpretation", "context", "understanding", "evaluation"]
        },
        "requirements_elicitation": {
            "description": "Identifying and defining the specific needs or conditions that must be met within the topic, crucial for tasks that involve planning, development, or specification.",
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
            "examples": ["Expert identification and collaboration", "Requirement gathering through expertise", "Comprehensive solution development", "Collaborative decision-making"],
            "keywords": ["requirements", "elicitation", "experts", "collaboration", "planning", "specification", "needs"]
        }
    },
    
    # Logic Layer: Out - Output generation (creative/code)
    "Out": {
        "context_control": {
            "description": "Involves managing the context in which the AI operates to ensure that the responses are accurate and relevant. This could involve providing additional background information, setting specific parameters or constraints, or guiding the AI to focus on particular aspects of the topic.",
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
            "examples": ["Ethical AI usage guidance", "Domain-specific ethical frameworks", "Academic integrity maintenance", "Universal ethical practice structure"],
            "keywords": ["context", "control", "ethical", "integrity", "accountability", "fairness", "guidance"]
        },
        "decomposed_prompting": {
            "description": "Refers to breaking down complex tasks into simpler, more manageable components. This approach allows the AI to tackle each part of the task individually, leading to more accurate and comprehensive outputs.",
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
            "examples": ["Complex task decomposition", "Sequential prompt structuring", "Interactive conversation design", "Manageable component creation"],
            "keywords": ["decomposition", "simplification", "segmentation", "interactive", "sequential", "manageable", "components"]
        },
        "output_customisation": {
            "description": "Output customisation refers to the ability to modify or personalise the model's output based on specific requirements or preferences. This could involve controlling the length, style, or format of the output, or incorporating specific information or elements into the response.",
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
            "examples": ["Information distillation and extraction", "Problem categorisation and extension", "Variable constraint analysis", "Solution format transformation"],
            "keywords": ["customisation", "distillation", "extraction", "categorisation", "constraints", "transformation", "format"]
        },
        "output_semantics": {
            "description": "Refers to the meaning or interpretation of the model's output. This involves understanding the intent of the output, the context in which it is presented, and the implications or consequences of the information it contains.",
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
            "examples": ["Problem statement interpretation", "Context understanding", "Objective alignment verification", "Meaningful output interpretation"],
            "keywords": ["semantics", "interpretation", "understanding", "context", "meaning", "objectives", "coherence"]
        },
        "prompt_improvement": {
            "description": "Involves enhancing the quality or effectiveness of the input prompt to achieve a better output. This could involve refining the wording of the prompt, providing additional context or information, or adjusting the complexity or specificity of the prompt.",
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
            "examples": ["Expert-driven prompt reformulation", "Precision optimisation techniques", "Surgical prompt refinement", "Accuracy-focused prompt enhancement"],
            "keywords": ["improvement", "reformulation", "precision", "optimisation", "refinement", "accuracy", "enhancement"]
        },
        "refactoring": {
            "description": "Involves restructuring or modifying the input prompt without changing its original meaning or intent. This could involve rephrasing the prompt, rearranging its components, or simplifying its structure to make it easier for the model to understand and respond to.",
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
            "examples": ["Automatic writing assistance", "Summary paragraph generation", "Data insertion techniques", "Structured content creation"],
            "keywords": ["refactoring", "restructuring", "simplification", "rephrasing", "automatic", "writing", "summary"]
        }
    },
    
    # Logic Layer: Over - Comprehensive coverage/oversight/review
    "Over": {
        "summarising": {
            "description": "Providing a brief overview or summary of the input or output. This could involve condensing a large amount of information into a few key points, highlighting the most important elements, or providing a concise synopsis of the content.",
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
            "examples": ["Concise data summarisation", "Key point extraction", "Information condensation", "Content synopsis generation"],
            "keywords": ["summarising", "condensation", "concise", "overview", "key points", "synopsis", "brief"]
        },
        "synthesis": {
            "description": "Integrating and reconciling information from multiple sources or perspectives to produce a unified, coherent, and insightful output. Synthesis goes beyond simple summarisation by combining disparate elements, identifying relationships and patterns, and generating higher-order insights or recommendations that reflect a comprehensive understanding of the topic.",
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
            "examples": ["Subanswer integration and refinement", "Comprehensive answer construction", "Multi-perspective synthesis", "Thorough review and validation"],
            "keywords": ["synthesis", "integration", "reconciliation", "comprehensive", "validation", "refinement", "coherent"]
        }
    }
}

#############################################
# LATEX WRITE-UP TEMPLATE STRUCTURE        #
#############################################

# Template structure for generating LaTeX write-ups
# This follows the academic format with different templates based on arguments:
#
# LOGIC OVERVIEW MODE (only -logic provided):
#   Uses "section_introduction" template which includes:
#   - Section header with logic name and subtitle
#   %1 - Write long introduction to the logic - text
#   - Long introduction to the logic
#   %2 - introduce categories under this logic
#   - Enumerated list of categories under this logic
#
# CATEGORY-SPECIFIC MODE (-logic and -category provided):
#   Uses "category_subsection" template which includes:
#   % 3.1 the role of this category under the "{logic_name_lower}-logic" (meaning of the category)
#   - Subsection header with category name
#   - Category role description under the logic
#   % 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
#   % Add label to reference the table
#   - PP analysis (introduction, function, benefits, reusability)
#   %% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
#   - Human feeling response
#   %% Re-use: how to derive a PE from PP
#   - Reuse guidance
#   %4 - PP example in this category
#   - LaTeX table of representative prompt patterns

LATEX_WRITEUP_TEMPLATE = {
    "section_introduction": """
\\section{{{logic_name} Logic - {logic_subtitle}}}
\\label{{sec:{logic_label}}}
%1 - Write long introduction to the logic - text
{logic_description}

%2 - introduce categories under this logic
The PP categories under {logic_name_lower} logic include:
\\begin{{enumerate}}
{category_enumeration}
\\end{{enumerate}}
""",
    
    "category_subsection": """
\\subsection{{{category_name}}}
\\label{{subsec:{category_label}}}
% 3.1 the role of this category under the "{logic_name_lower}-logic" (meaning of the category)
{category_role_description}

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
{pp_analysis}

% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
{human_feeling_response}

% Re-use: how to derive a PE from PP
{reuse_guidance}

%4 - PP example in this category
{latex_table}
""",
    
    "category_enumeration_item": """    \\item \\textbf{{{category_name}}}: {category_description}""",
    
    "pp_analysis_structure": """
a) **Pattern Introduction**: {pp_introduction}
b) **Pattern Function**: {pp_function}  
c) **Human Benefit**: {pp_benefit}
d) **Reusability**: {pp_reusability}
""",
    
    "human_feeling_template": """
When encountering outputs from this pattern, users typically experience {feeling_description}. 
The response {emotional_impact} and provides {cognitive_benefit}.
""",
    
    "reuse_template": """
To derive a Prompt Example (PE) from this Prompt Pattern (PP):
1. {reuse_step1}
2. {reuse_step2}
3. {reuse_step3}
"""
}

# Logic-specific data for generating complete write-ups
LOGIC_WRITEUP_DATA = {
    "Across": {
        "logic_subtitle": "Navigating between topics",
        "logic_label": "across", 
        "logic_description": """Across logic is used to transition from one topic to another, navigating between distinct areas of knowledge. This type of logic is particularly valuable in scenarios where prompts need to span \\textbf{multiple domains} or disciplines, integrating diverse types of knowledge to create a cohesive narrative or solution. \\\\""",
        "categories": {
            "argument": {
                "category_label": "Argument",
                "role_description": "Arguments serve as the foundation for logical reasoning across different domains, enabling the AI to construct coherent positions that bridge multiple areas of knowledge.",
                "pp_analysis": {
                    "pp_introduction": "The Debater pattern establishes a structured framework for presenting and defending viewpoints",
                    "pp_function": "It guides the AI to research multiple perspectives, present balanced arguments, and draw evidence-based conclusions",
                    "pp_benefit": "Users gain deeper understanding through comprehensive analysis of complex topics from multiple angles",
                    "pp_reusability": "The debater structure can be adapted for any topic requiring multi-perspective analysis"
                },
                "human_feeling": "a sense of intellectual engagement and clarity, as complex topics are broken down into manageable, well-reasoned arguments",
                "emotional_impact": "reduces cognitive overwhelm when dealing with controversial or complex subjects",
                "cognitive_benefit": "structured thinking and evidence-based reasoning",
                "reuse_steps": [
                    "Identify a specific topic or issue requiring multi-perspective analysis",
                    "Adapt the debater template to focus on the chosen topic",
                    "Customize the evidence requirements and conclusion format for the specific domain"
                ]
            },
            "comparison": {
                "category_label": "Comparison",
                "role_description": "Comparison patterns facilitate understanding by highlighting relationships and differences between concepts across various domains.",
                "pp_analysis": {
                    "pp_introduction": "The Comparison of Outputs pattern adopts a teacher's perspective to evaluate different responses",
                    "pp_function": "It systematically identifies strengths, weaknesses, and key differences between outputs",
                    "pp_benefit": "Users receive balanced, constructive feedback that aids in learning and improvement",
                    "pp_reusability": "The teacher-evaluator framework can be applied to any comparison scenario"
                },
                "human_feeling": "confidence and understanding, as the teacher-like analysis provides clear, actionable insights",
                "emotional_impact": "builds trust in the evaluation process",
                "cognitive_benefit": "enhanced critical thinking and analytical skills",
                "reuse_steps": [
                    "Select specific outputs, concepts, or objects to compare",
                    "Define the evaluation criteria relevant to your domain",
                    "Apply the teacher-evaluator framework to provide structured feedback"
                ]
            },
            "contradiction": {
                "category_label": "Contradiction",
                "role_description": "Contradiction patterns enable critical thinking by identifying and analyzing conflicting information across different sources or viewpoints.",
                "pp_analysis": {
                    "pp_introduction": "The Hallucination Evaluation pattern focuses on detecting factual inconsistencies",
                    "pp_function": "It systematically compares information sources to identify contradictions and inaccuracies",
                    "pp_benefit": "Users develop better fact-checking skills and can identify unreliable information",
                    "pp_reusability": "The evaluation framework can be adapted for any fact-checking or verification task"
                },
                "human_feeling": "heightened awareness and critical scrutiny, as potential inaccuracies are systematically identified",
                "emotional_impact": "increases confidence in information reliability",
                "cognitive_benefit": "improved fact-checking and verification skills",
                "reuse_steps": [
                    "Identify the information sources or statements to be evaluated",
                    "Establish the reference standards or ground truth",
                    "Apply the systematic comparison framework to detect contradictions"
                ]
            },
            "cross_boundary": {
                "category_label": "CrossBoundary",
                "role_description": "Cross-boundary patterns test the limits of AI systems, helping researchers understand model robustness and safety mechanisms.",
                "pp_analysis": {
                    "pp_introduction": "The Crafting Effective Jailbreak Prompts pattern is designed for security research",
                    "pp_function": "It systematically tests AI defense mechanisms and identifies potential vulnerabilities",
                    "pp_benefit": "Researchers gain insights into model robustness and can improve safety measures",
                    "pp_reusability": "The testing framework can be adapted for different types of safety evaluations"
                },
                "human_feeling": "a mix of concern and fascination, as the testing reveals both capabilities and limitations",
                "emotional_impact": "raises awareness of AI safety considerations",
                "cognitive_benefit": "better understanding of AI security and robustness",
                "reuse_steps": [
                    "Define the specific boundaries or safety mechanisms to test",
                    "Design appropriate test scenarios within ethical guidelines",
                    "Apply systematic evaluation methods to assess robustness"
                ]
            },
            "translation": {
                "category_label": "Translation",
                "role_description": "Translation patterns enable knowledge transfer by converting information between different formats, languages, or representation systems.",
                "pp_analysis": {
                    "pp_introduction": "The Constructing the Signifier pattern focuses on representation conversion",
                    "pp_function": "It transforms data from one format to another while preserving core meaning",
                    "pp_benefit": "Users can access information in more familiar or suitable formats",
                    "pp_reusability": "The conversion framework can be applied to any translation or transformation task"
                },
                "human_feeling": "relief and understanding, as complex information becomes accessible in familiar formats",
                "emotional_impact": "reduces cognitive barriers to understanding",
                "cognitive_benefit": "improved comprehension and knowledge accessibility",
                "reuse_steps": [
                    "Identify the source and target representation formats",
                    "Define the core meaning elements that must be preserved",
                    "Apply the transformation framework to convert between formats"
                ]
            }
        }
    },
    "At": {
        "logic_subtitle": "Discover Detail of a Topic",
        "logic_label": "at",
        "logic_description": """At logic focuses on examining the specific details or aspects within a given topic. This logic is essential when prompts are designed to elicit precise, context-dependent responses, enabling the AI to address targeted queries with accuracy and depth. At logic is particularly relevant for tasks that require granular evaluation, measurement, or analysis within a defined scope. \\\\""",
        "categories": {
            "assessment": {
                "category_label": "Assessment",
                "role_description": "Assessment patterns under At logic provide comprehensive evaluation frameworks that verify correctness, deliver feedback, and analyze completeness, ratings, and contextual relevance with precision.",
                "pp_analysis": {
                    "pp_introduction": "The Expert pattern establishes a comprehensive evaluation framework based on predefined criteria",
                    "pp_function": "It guides the AI to provide expert-level analysis and systematic rating across multiple dimensions",
                    "pp_benefit": "Users receive structured, credible assessments that inform decision-making processes",
                    "pp_reusability": "The expert evaluation framework can be adapted for any domain requiring systematic assessment"
                },
                "human_feeling": "confidence and authority, as the expert-level analysis provides reliable, structured evaluation",
                "emotional_impact": "builds trust in assessment outcomes through systematic methodology",
                "cognitive_benefit": "enhanced decision-making through comprehensive evaluation frameworks",
                "reuse_steps": [
                    "Define the specific domain and expertise requirements for assessment",
                    "Establish clear evaluation criteria and rating scales",
                    "Apply the expert framework to provide systematic analysis and recommendations"
                ]
            },
            "calculation": {
                "category_label": "Calculation",
                "role_description": "Calculation patterns under At logic execute precise mathematical operations, from simple arithmetic to complex multi-step computations, ensuring accuracy in quantitative analysis.",
                "pp_analysis": {
                    "pp_introduction": "The Calculator API Calls pattern simulates mathematical computation through structured API syntax",
                    "pp_function": "It enables the AI to perform accurate calculations using the '[Calculator(expression)]' syntax",
                    "pp_benefit": "Users can rely on precise mathematical computations integrated seamlessly into text processing",
                    "pp_reusability": "The calculator framework can be adapted for any scenario requiring mathematical precision"
                },
                "human_feeling": "precision and reliability, as mathematical operations are executed with systematic accuracy",
                "emotional_impact": "reduces anxiety about computational errors through structured methodology",
                "cognitive_benefit": "enhanced problem-solving through accurate mathematical analysis",
                "reuse_steps": [
                    "Identify the mathematical expressions or computations required",
                    "Structure the calculations using the API call syntax",
                    "Integrate the computational results into the broader analytical framework"
                ]
            }
        }
    },
    "Beyond": {
        "logic_subtitle": "Extend the limits of a topic",
        "logic_label": "beyond",
        "logic_description": """Beyond logic encourages LLMs to transcend conventional topic boundaries, fostering exploration, innovation, and forward-thinking responses. This logic is essential for tasks that require the model to hypothesise, reason, predict, or simulate scenarios beyond established knowledge or current constraints. \\\\""",
        "categories": {
            "hypothesise": {
                "category_label": "Hypothesise",
                "role_description": "Hypothesis patterns under Beyond logic enable educated speculation and assumption-making, pushing the model to analyse inputs, consider multiple possibilities, and predict likely outcomes beyond conventional boundaries.",
                "pp_analysis": {
                    "pp_introduction": "The User Prompt pattern employs hypothesis by encouraging exploration of different approaches and perspectives",
                    "pp_function": "It systematically combines expert crafting, step-by-step reasoning, and collaborative discussions to solve complex problems",
                    "pp_benefit": "Users receive comprehensive problem-solving frameworks that transcend surface-level analysis",
                    "pp_reusability": "The multi-technique approach can be adapted for any complex problem requiring innovative solutions"
                },
                "human_feeling": "excitement and intellectual curiosity, as the pattern unlocks creative problem-solving potential",
                "emotional_impact": "inspires confidence in tackling complex challenges through systematic innovation",
                "cognitive_benefit": "enhanced creative thinking and comprehensive problem analysis",
                "reuse_steps": [
                    "Identify the core problem requiring innovative hypothesis generation",
                    "Select appropriate combinations of expert crafting, reasoning, and collaboration techniques",
                    "Apply the reformulation framework to transcend conventional problem boundaries"
                ]
            },
            "logical_reasoning": {
                "category_label": "LogicalReasoning",
                "role_description": "Logical reasoning patterns under Beyond logic apply advanced logic and reasoning to generate outputs that deduce conclusions, make inferences, and apply principles beyond traditional constraints.",
                "pp_analysis": {
                    "pp_introduction": "The Thought Template pattern applies systematic logical reasoning to comparative analysis",
                    "pp_function": "It guides the AI to compare relevant attributes across all entries using structured logical processes",
                    "pp_benefit": "Users receive methodical, logical conclusions based on comprehensive comparative analysis",
                    "pp_reusability": "The logical comparison framework can be applied to any scenario requiring systematic reasoning"
                },
                "human_feeling": "clarity and logical satisfaction, as complex comparisons are resolved through systematic reasoning",
                "emotional_impact": "builds confidence in logical decision-making processes",
                "cognitive_benefit": "enhanced logical thinking and systematic analysis capabilities",
                "reuse_steps": [
                    "Define the attributes and entries requiring logical comparison",
                    "Establish the reasoning framework for systematic analysis",
                    "Apply the logical template to derive evidence-based conclusions"
                ]
            },
            "prediction": {
                "category_label": "Prediction",
                "role_description": "Prediction patterns under Beyond logic enable forecasting and outcome estimation, requiring the model to analyse inputs, consider variables, and anticipate future events beyond current constraints.",
                "pp_analysis": {
                    "pp_introduction": "The Rotation Prediction pattern demonstrates visual transformation forecasting capabilities",
                    "pp_function": "It enables the AI to predict visual outcomes through spatial transformation analysis",
                    "pp_benefit": "Users can rely on accurate visual prediction capabilities for complex transformations",
                    "pp_reusability": "The transformation prediction framework can be adapted for various visual and spatial analysis tasks"
                },
                "human_feeling": "amazement and anticipation, as complex visual transformations are accurately predicted",
                "emotional_impact": "increases trust in AI predictive capabilities",
                "cognitive_benefit": "enhanced spatial reasoning and transformation analysis",
                "reuse_steps": [
                    "Identify the specific transformation or prediction scenario",
                    "Define the input parameters and expected output format",
                    "Apply the prediction framework to generate accurate forecasts"
                ]
            },
            "simulation": {
                "category_label": "Simulation",
                "role_description": "Simulation patterns under Beyond logic enable replication and modeling of real-world processes, allowing the model to imitate complex systems and scenarios beyond traditional boundaries.",
                "pp_analysis": {
                    "pp_introduction": "The Relevant Roles pattern identifies human agents for scenario simulation",
                    "pp_function": "It systematically determines the key participants required for realistic scenario modeling",
                    "pp_benefit": "Users receive comprehensive agent identification for accurate simulation development",
                    "pp_reusability": "The role identification framework can be applied to any scenario requiring simulation modeling"
                },
                "human_feeling": "understanding and systematic clarity, as complex scenarios are broken down into manageable agent roles",
                "emotional_impact": "builds confidence in simulation design and modeling",
                "cognitive_benefit": "enhanced systems thinking and scenario modeling capabilities",
                "reuse_steps": [
                    "Define the scenario requiring simulation and modeling",
                    "Identify the key human agents and their roles within the system",
                    "Apply the simulation framework to create comprehensive scenario models"
                ]
            }
        }
    },
    "In": {
        "logic_subtitle": "Dive into a Topic or Space",
        "logic_label": "in",
        "logic_description": """In logic focuses on the internal structure and detailed analysis within a defined topic or space. This logic is essential for prompts that require introspection, systematic organisation, or the identification of underlying patterns and requirements. Rather than traversing boundaries or generating outputs, In logic directs the AI to operate within the confines of a specific subject, supporting tasks such as categorisation, classification, error detection, and requirements elicitation. \\\\""",
        "categories": {
            "categorising": {
                "category_label": "Categorising",
                "role_description": "Categorising patterns under In logic provide systematic organisation frameworks that sort and arrange inputs or outputs into meaningful classes based on shared characteristics, enabling effective data organisation and pattern recognition within defined spaces.",
                "pp_analysis": {
                    "pp_introduction": "The Insurance Report Generation pattern establishes expert-level categorisation for vehicle damage assessment",
                    "pp_function": "It systematically interprets visual data to categorise damage types, vehicle details, and assessment parameters",
                    "pp_benefit": "Users receive structured, expert-level analysis that organises complex visual information into actionable categories",
                    "pp_reusability": "The expert categorisation framework can be adapted for any domain requiring systematic visual analysis and classification"
                },
                "human_feeling": "confidence and systematic clarity, as complex visual information is organised into clear, actionable categories",
                "emotional_impact": "reduces overwhelm when dealing with complex assessment scenarios",
                "cognitive_benefit": "enhanced organisational thinking and systematic analysis capabilities",
                "reuse_steps": [
                    "Define the specific domain and expertise requirements for categorisation",
                    "Establish clear category frameworks and assessment criteria",
                    "Apply the expert categorisation template to organise complex information systematically"
                ]
            },
            "classification": {
                "category_label": "Classification",
                "role_description": "Classification patterns under In logic enable precise categorisation based on predefined criteria, facilitating systematic analysis and interpretation through structured separation of elements within defined spaces.",
                "pp_analysis": {
                    "pp_introduction": "The Intermediate Abstraction pattern focuses on architectural classification and separation",
                    "pp_function": "It systematically separates business logic from external dependencies through structured abstraction layers",
                    "pp_benefit": "Users achieve maintainable code architecture with clear separation of concerns and improved flexibility",
                    "pp_reusability": "The abstraction classification framework can be applied to any software architecture requiring systematic organisation"
                },
                "human_feeling": "architectural satisfaction and structural clarity, as complex code relationships are systematically organised",
                "emotional_impact": "builds confidence in software design and maintenance approaches",
                "cognitive_benefit": "enhanced architectural thinking and systematic design capabilities",
                "reuse_steps": [
                    "Identify the elements requiring classification and separation",
                    "Define the abstraction layers and classification criteria",
                    "Apply the systematic separation framework to achieve clear architectural organisation"
                ]
            },
            "clustering": {
                "category_label": "Clustering",
                "role_description": "Clustering patterns under In logic identify natural groupings and hidden relationships within data or topics, revealing underlying patterns without pre-established categories.",
                "pp_analysis": {
                    "pp_introduction": "The Common Concept pattern focuses on identifying shared characteristics among diverse objects",
                    "pp_function": "It systematically examines multiple objects to discover unifying features and natural groupings",
                    "pp_benefit": "Users develop enhanced pattern recognition skills and discover hidden relationships in complex data",
                    "pp_reusability": "The pattern recognition framework can be applied to any scenario requiring natural grouping discovery"
                },
                "human_feeling": "discovery and intellectual satisfaction, as hidden patterns and relationships become apparent",
                "emotional_impact": "creates excitement about uncovering underlying connections",
                "cognitive_benefit": "enhanced pattern recognition and analytical thinking capabilities",
                "reuse_steps": [
                    "Identify the objects or elements requiring pattern analysis",
                    "Apply systematic examination techniques to discover common characteristics",
                    "Use the clustering framework to reveal natural groupings and relationships"
                ]
            },
            "error_identification": {
                "category_label": "ErrorIdentification", 
                "role_description": "Error identification patterns under In logic pinpoint inaccuracies, inconsistencies, and logical fallacies within topics, enabling systematic quality improvement and information refinement.",
                "pp_analysis": {
                    "pp_introduction": "The Fact Check List pattern establishes systematic verification frameworks for cybersecurity information",
                    "pp_function": "It identifies and lists fact-checkable elements that responses depend on, focusing on cybersecurity domains",
                    "pp_benefit": "Users gain systematic quality control measures and improved accuracy verification capabilities",
                    "pp_reusability": "The fact-checking framework can be adapted for any domain requiring systematic accuracy verification"
                },
                "human_feeling": "vigilance and quality assurance, as potential inaccuracies are systematically identified and addressed",
                "emotional_impact": "builds trust through systematic verification processes",
                "cognitive_benefit": "enhanced critical thinking and quality assessment capabilities",
                "reuse_steps": [
                    "Define the domain and types of facts requiring verification",
                    "Establish systematic fact-checking criteria and processes",
                    "Apply the verification framework to ensure accuracy and quality"
                ]
            },
            "input_semantics": {
                "category_label": "InputSemantics",
                "role_description": "Input semantics patterns under In logic interpret meaning and context of inputs within topics, ensuring accurate comprehension of nuances and semantic relationships.",
                "pp_analysis": {
                    "pp_introduction": "The Sentence Similarity pattern evaluates semantic relationships between input sentences",
                    "pp_function": "It systematically measures semantic similarity using structured rating scales and comparison frameworks",
                    "pp_benefit": "Users gain precise understanding of meaning relationships and contextual similarities",
                    "pp_reusability": "The semantic evaluation framework can be applied to any scenario requiring meaning analysis"
                },
                "human_feeling": "precision and semantic clarity, as meaning relationships are systematically quantified and understood",
                "emotional_impact": "increases confidence in understanding complex semantic relationships",
                "cognitive_benefit": "enhanced semantic analysis and meaning interpretation capabilities",
                "reuse_steps": [
                    "Identify the inputs requiring semantic analysis",
                    "Establish appropriate similarity scales and evaluation criteria",
                    "Apply the semantic evaluation framework to quantify meaning relationships"
                ]
            },
            "requirements_elicitation": {
                "category_label": "RequirementsElicitation",
                "role_description": "Requirements elicitation patterns under In logic identify and define specific needs or conditions within topics, supporting systematic planning, development, and specification processes.",
                "pp_analysis": {
                    "pp_introduction": "The Expert Prompting pattern facilitates comprehensive requirement gathering through expert collaboration",
                    "pp_function": "It systematically identifies experts, generates expert responses, and combines insights through collaborative decision-making",
                    "pp_benefit": "Users receive comprehensive requirement analysis through structured expert collaboration and systematic insight integration",
                    "pp_reusability": "The expert collaboration framework can be adapted for any domain requiring comprehensive requirement analysis"
                },
                "human_feeling": "comprehensiveness and expert confidence, as requirements are systematically gathered through structured expert collaboration",
                "emotional_impact": "builds trust in planning processes through expert-validated requirements",
                "cognitive_benefit": "enhanced requirement analysis and collaborative planning capabilities",
                "reuse_steps": [
                    "Identify the domain and specific requirements needing elicitation",
                    "Define expert roles and collaboration frameworks",
                    "Apply the systematic expert prompting approach to gather comprehensive requirements"
                ]
            }
        }
    },
    "Out": {
        "logic_subtitle": "Expand the horizon of a topic",
        "logic_label": "out",
        "logic_description": """Out logic is concerned with extending the boundaries of a topic, enabling prompts that move beyond the immediate subject to generate new outputs or perspectives. This logic is essential for tasks that require AI to produce, transform, or reframe content, such as creative writing, code generation, or the synthesis of novel ideas. Out logic facilitates the transition from analysis to production, supporting the creation of outputs that are contextually relevant yet not strictly confined to the original input. \\\\""",
        "categories": {
            "context_control": {
                "category_label": "ContextControl",
                "role_description": "Context control patterns under Out logic manage the operational environment to ensure accurate and relevant response generation, providing background information, parameters, and focused guidance for output expansion.",
                "pp_analysis": {
                    "pp_introduction": "The Ethical Use pattern establishes comprehensive ethical frameworks for AI interaction",
                    "pp_function": "It systematically guides ethical AI practices across academic integrity, privacy, fairness, and accountability domains",
                    "pp_benefit": "Users receive structured ethical guidance that ensures responsible AI usage across diverse applications",
                    "pp_reusability": "The ethical framework can be adapted for any domain requiring responsible AI practice guidance"
                },
                "human_feeling": "confidence and moral clarity, as ethical considerations are systematically addressed and structured",
                "emotional_impact": "builds trust in AI interactions through comprehensive ethical frameworks",
                "cognitive_benefit": "enhanced ethical reasoning and responsible AI usage capabilities",
                "reuse_steps": [
                    "Identify the specific domain and ethical considerations requiring guidance",
                    "Define the ethical frameworks relevant to the application context",
                    "Apply the structured ethical guidance template to ensure responsible AI usage"
                ]
            },
            "decomposed_prompting": {
                "category_label": "DecomposedPrompting",
                "role_description": "Decomposed prompting patterns under Out logic break complex tasks into manageable components, enabling systematic tackle of individual parts for more accurate and comprehensive output generation.",
                "pp_analysis": {
                    "pp_introduction": "The Break Down Complex Tasks pattern systematically decomposes complex challenges into manageable segments",
                    "pp_function": "It structures complex tasks into sequential, interactive conversation components for enhanced understanding",
                    "pp_benefit": "Users achieve more accurate and comprehensive results through systematic task decomposition",
                    "pp_reusability": "The decomposition framework can be applied to any complex task requiring systematic breakdown"
                },
                "human_feeling": "relief and systematic clarity, as overwhelming complex tasks become manageable through structured decomposition",
                "emotional_impact": "reduces cognitive overwhelm through systematic task simplification",
                "cognitive_benefit": "enhanced problem-solving through systematic decomposition strategies",
                "reuse_steps": [
                    "Identify the complex task requiring systematic breakdown",
                    "Define the component elements and sequential structure",
                    "Apply the decomposition framework to create manageable interactive segments"
                ]
            },
            "output_customisation": {
                "category_label": "OutputCustomisation",
                "role_description": "Output customisation patterns under Out logic modify and personalise model outputs based on specific requirements, controlling length, style, format, and incorporating targeted information elements.",
                "pp_analysis": {
                    "pp_introduction": "The Problem Distiller pattern provides expert-level information distillation and categorisation",
                    "pp_function": "It systematically extracts, categorises, and transforms essential information into suitable formats based on problem types",
                    "pp_benefit": "Users receive comprehensive problem analysis with key variables, constraints, and extended solution frameworks",
                    "pp_reusability": "The distillation framework can be applied to any problem requiring systematic information extraction and transformation"
                },
                "human_feeling": "professional competence and systematic understanding, as complex information is expertly distilled and organised",
                "emotional_impact": "builds confidence in problem-solving through systematic information organisation",
                "cognitive_benefit": "enhanced analytical thinking and information distillation capabilities",
                "reuse_steps": [
                    "Define the problem type and information extraction requirements",
                    "Establish categorisation criteria and transformation frameworks",
                    "Apply the systematic distillation approach to extract and organise essential information"
                ]
            },
            "output_semantics": {
                "category_label": "OutputSemantics",
                "role_description": "Output semantics patterns under Out logic interpret meaning and intent of model outputs, ensuring understanding of context, implications, and consequences of generated information.",
                "pp_analysis": {
                    "pp_introduction": "The Understanding the Problem pattern focuses on comprehensive problem statement interpretation",
                    "pp_function": "It systematically ensures thorough understanding of context and specific requirements for meaningful output alignment",
                    "pp_benefit": "Users achieve coherent, meaningful outputs that align with desired objectives through systematic interpretation",
                    "pp_reusability": "The interpretation framework can be applied to any scenario requiring comprehensive understanding verification"
                },
                "human_feeling": "clarity and semantic confidence, as problem understanding becomes thorough and systematically verified",
                "emotional_impact": "increases confidence in problem comprehension and solution alignment",
                "cognitive_benefit": "enhanced interpretation skills and semantic understanding capabilities",
                "reuse_steps": [
                    "Identify the problem statement and context requiring interpretation",
                    "Define the specific requirements and objectives for understanding verification",
                    "Apply the systematic interpretation framework to ensure comprehensive problem understanding"
                ]
            },
            "prompt_improvement": {
                "category_label": "PromptImprovement",
                "role_description": "Prompt improvement patterns under Out logic enhance input prompt quality and effectiveness, refining wording, context, and specificity to achieve superior output generation.",
                "pp_analysis": {
                    "pp_introduction": "The System Prompt pattern employs expert-driven precision reformulation techniques",
                    "pp_function": "It systematically optimises prompts with surgical precision for maximum accuracy and response quality",
                    "pp_benefit": "Users achieve optimal prompt performance through expert-level reformulation and precision optimisation",
                    "pp_reusability": "The precision reformulation framework can be applied to any prompt requiring accuracy optimisation"
                },
                "human_feeling": "expert confidence and precision satisfaction, as prompts are systematically optimised for maximum effectiveness",
                "emotional_impact": "builds trust in prompt quality through expert-driven optimisation processes",
                "cognitive_benefit": "enhanced prompt engineering skills and precision optimisation capabilities",
                "reuse_steps": [
                    "Identify the prompt requiring quality enhancement and accuracy optimisation",
                    "Define the expert knowledge and precision criteria for reformulation",
                    "Apply the systematic reformulation framework to achieve optimal prompt performance"
                ]
            },
            "refactoring": {
                "category_label": "Refactoring",
                "role_description": "Refactoring patterns under Out logic restructure and modify input prompts while preserving original meaning, involving rephrasing, rearrangement, and simplification for enhanced model understanding.",
                "pp_analysis": {
                    "pp_introduction": "The Generate Summary Paragraph with Data Insertion pattern provides automatic writing assistance with structured content creation",
                    "pp_function": "It systematically generates concise summaries with specific data insertion and formatting constraints",
                    "pp_benefit": "Users receive automated, structured content generation with precise formatting and length control",
                    "pp_reusability": "The automatic writing framework can be adapted for any content generation requiring structured summarisation"
                },
                "human_feeling": "efficiency and structural satisfaction, as content generation becomes automated and systematically organised",
                "emotional_impact": "reduces writing effort through systematic automation and structure",
                "cognitive_benefit": "enhanced content creation efficiency and structured writing capabilities",
                "reuse_steps": [
                    "Define the content requirements and structural constraints for generation",
                    "Establish the data insertion parameters and formatting specifications",
                    "Apply the automatic writing framework to generate structured, constrained content"
                ]
            }
        }
    },
    "Over": {
        "logic_subtitle": "Span and Review a Topic",
        "logic_label": "over",
        "logic_description": """Over logic is used when comprehensive coverage, synthesis, or critical review of an entire topic or dataset is needed. This logic is essential when the objective is to distil complex or voluminous information into concise, coherent, and actionable insights. Over logic is particularly relevant for tasks such as summarisation, synthesis, and holistic evaluation, where the model must demonstrate both breadth and depth of understanding. \\\\""",
        "categories": {
            "summarising": {
                "category_label": "Summarising",
                "role_description": "Summarising patterns under Over logic provide comprehensive overview frameworks that condense voluminous information into concise, coherent insights, highlighting key elements and essential points for actionable understanding.",
                "pp_analysis": {
                    "pp_introduction": "The Preprocessing Prompt pattern establishes concise data summarisation frameworks",
                    "pp_function": "It systematically condenses large amounts of information into essential key points and manageable overviews",
                    "pp_benefit": "Users receive clear, concise summaries that capture essential information without overwhelming detail",
                    "pp_reusability": "The summarisation framework can be adapted for any content requiring concise information distillation"
                },
                "human_feeling": "relief and clarity, as overwhelming information volumes are systematically reduced to essential, manageable insights",
                "emotional_impact": "reduces information overwhelm through systematic condensation processes",
                "cognitive_benefit": "enhanced information processing and essential point identification capabilities",
                "reuse_steps": [
                    "Identify the content requiring summarisation and key information extraction",
                    "Define the conciseness level and essential elements for inclusion",
                    "Apply the systematic condensation framework to create clear, actionable summaries"
                ]
            },
            "synthesis": {
                "category_label": "Synthesis",
                "role_description": "Synthesis patterns under Over logic integrate and reconcile information from multiple sources to produce unified, coherent outputs, combining disparate elements and generating higher-order insights that reflect comprehensive understanding.",
                "pp_analysis": {
                    "pp_introduction": "The Ensuring Thorough Review and Validation pattern focuses on comprehensive subanswer integration",
                    "pp_function": "It systematically combines and refines multiple subanswers to construct precise, well-informed final responses",
                    "pp_benefit": "Users receive comprehensive, validated answers that integrate multiple perspectives and sources effectively",
                    "pp_reusability": "The synthesis framework can be applied to any scenario requiring integration of multiple information sources"
                },
                "human_feeling": "completeness and intellectual satisfaction, as multiple perspectives are systematically integrated into comprehensive understanding",
                "emotional_impact": "builds confidence in solution completeness through systematic integration processes",
                "cognitive_benefit": "enhanced synthesis skills and comprehensive understanding capabilities",
                "reuse_steps": [
                    "Identify the multiple sources or subanswers requiring integration",
                    "Define the synthesis criteria and validation requirements",
                    "Apply the systematic integration framework to create comprehensive, coherent final outputs"
                ]
            }
        }
    }
}

#############################################
# FEW-SHOT EXAMPLES                         #
#############################################

# Few-shot examples for improving categorisation write-up generation
# These examples provide context and demonstrate expected output patterns

FEW_SHOT_EXAMPLES = {
    "beyond_logic_prediction": [
        {
            "user_input": "Write about the Prediction category under Beyond logic following academic criteria",
            "assistant_output": """\\subsection{Prediction}
\\label{subsec:Prediction}
% 3.1 The role of this category under the "beyond-logic" (meaning of the category)
Beyond logic encompasses advanced cognitive processes that extend artificial intelligence capabilities into sophisticated analytical territories. The PP categories under beyond logic include hypothesise, logical reasoning, prediction, and simulation, each representing distinct approaches to complex problem-solving that transcend basic input-output relationships. These categories enable AI systems to engage in higher-order thinking processes, making educated assumptions, applying logical frameworks, forecasting outcomes, and replicating complex real-world systems.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Rotation Prediction PP as described in Table \\ref{tab:Rotation_Prediction_PP} focuses on spatial-visual prediction capabilities. It is designed to challenge AI systems with spatial reasoning tasks, requiring the model to mentally rotate images and predict the resulting orientation of letters or numbers. This pattern helps people develop and assess spatial intelligence in AI systems, and can be re-used across various domains requiring spatial reasoning, visual perception, and cognitive rotation abilities.

%% Expected response. Put the human feeling into the writing. How do I feel when I view the output.
The AI model typically generates accurate predictions of rotated characters, demonstrating sophisticated spatial reasoning capabilities. Through this interaction, users experience fascination at witnessing AI's ability to perform complex mental rotations that mirror human cognitive processes. It is remarkable being able to observe how artificial intelligence can replicate and sometimes exceed human spatial reasoning abilities, providing insights into the sophisticated visual processing capabilities of modern AI systems.

%% Re-use: how to derive a PE from PP
To apply the Rotation Prediction PP in a given context, select images containing letters or numbers, specify the rotation angle (typically 180 degrees), define the prediction task clearly, and establish evaluation criteria for accuracy. Here is an example of derived PE: "I am showing you an image of a handwritten letter 'b'. You need to predict what letter or number this becomes when rotating the image by 180 degrees. Please analyze the spatial characteristics and provide your prediction with confidence level."

%4 - PP example in this category
\\begin{table}[h!]
\\fontsize{9pt}{10pt}\\selectfont
\\centering
\\caption{Rotation Prediction PP}
\\label{tab:Rotation_Prediction_PP}
\\begin{tabular}{|l|}
    \\hline
    \\textbf{Prompt Pattern} \\\\ \\hline
    \\textbf{ID}: 61-0-20\\\\ 
    \\textbf{Category}: PRD\\\\ 
    \\textbf{Name}: Rotation Prediction\\\\ 
    \\textbf{Media Type}: Text, Image2Text, Text2Image\\\\ 
    \\textbf{Description}: Provide an image and predict the letter or number it represents when rotated 180 degrees.\\\\
    \\textbf{Template}: I am showing you an image and you need to predict the letter or number shown when rotating\\\\ the image by 180 degrees.\\\\
    \\textbf{Example}: 61-0-20-0\\\\ 
    \\textbf{Related PPs}:  \\\\ 
    \\textbf{Reference:} \\cite{McKinzie2024MM1:Pre-training}\\\\ \\hline
\\end{tabular}
\\end{table}"""
        }
    ]
}

#############################################
# DEFAULT SYSTEM MESSAGE                    #
#############################################
DEFAULT_SYSTEM_MESSAGE = '''
You are a world top ranking university PhD student in the field of AI application, conducting leading edge research and writing a research paper on “The Way to Talk to AI: A Dictionary of Prompt Patterns to LLMs”

The proposed logic to construct the dictionary toward the best convenience and effectiveness of human to AI communication is to apply English language logic of Across, At, Beyond, In, Out and Over to build a dictionary of prompt pattern (PP), each with multiple prompt examples (PEs)


You specialize in:
- Academic writing for top-tier journals and conferences
- Prompt pattern analysis and categorisation
- LaTeX formatting for mathematical and technical content
- Clear explanations of complex AI/ML concepts
- Systematic analysis of prompt engineering techniques

Your output should be:
- Academically rigorous and well-structured
- Formatted in LaTeX for publication quality
- Clear and precise in language (Australian English)
- Comprehensive yet concise
- Logically organized with proper citations and references

Always approach the task step-by-step to ensure thoroughness and coherence.
'''

#############################################
# CATEGORISATION WRITE-UP CLIENT CLASS     #
#############################################

class CategorisationWriteUpClient:
    """
    Client for generating categorisation write-ups using Azure OpenAI models.
    Handles authentication, model selection, and conversation management.
    """
    
    def __init__(self, model_version: str = "gpt-4.1", debug: bool = False, use_few_shot: bool = False):
        """
        Initialize the categorisation write-up client.
        
        Args:
            model_version: The Azure OpenAI model version to use
            debug: Enable debug logging
            use_few_shot: Include few-shot examples in prompts for better output quality
        """
        self.model_version = model_version
        self.debug = debug
        self.use_few_shot = use_few_shot
        self.conversation_history = []
        self.client = None
        self.model_config = None
        
        # Initialize Azure OpenAI client
        self._initialize_client()
        
        if self.debug:
            print(f"✓ CategorisationWriteUpClient initialized with model: {model_version}")
    
    def _initialize_client(self):
        """Initialize the unified client with proper authentication."""
        try:
            self.client = get_unified_client(self.model_version)
            self.model_config = get_model_config(self.model_version)
            
            if self.debug:
                print(f"✓ Unified client initialized successfully")
                print(f"✓ Model config: {self.model_config}")
                
        except Exception as e:
            print(f"✗ Error initializing client: {e}")
            sys.exit(1)
    
    def generate_writeup(self, 
                        logic: str,
                        category: Optional[str] = None,
                        task: str = None,
                        system_message: Optional[str] = None,
                        context: Optional[str] = None,
                        temperature: float = 0.7) -> str:
        """
        Generate a write-up for the specified prompt pattern category or logic overview.
        
        Args:
            logic: The logic layer (In, Out, Over, Across, Beyond, At)
            category: Optional specific PP category under the logic (if None, generates logic overview)
            task: The specific task/request for the write-up
            system_message: Optional custom system message
            context: Optional additional context
            temperature: Model temperature for generation
            
        Returns:
            Generated write-up content
        """
        # Validate logic
        if logic not in LOGIC_DEFINITIONS:
            raise ValueError(f"Invalid logic '{logic}'. Must be one of: {list(LOGIC_DEFINITIONS.keys())}")
        
        # Validate category if provided
        if category and not validate_category(logic, category):
            raise ValueError(f"Invalid category '{category}' for logic '{logic}'")
        
        # Build the prompt based on whether category is provided
        if category:
            # Generate category-specific write-up
            prompt = self._build_category_writeup_prompt(logic, category, task, context)
        else:
            # Generate logic overview write-up
            prompt = self._build_logic_writeup_prompt(logic, task, context)
        
        # Use custom system message or default
        system_msg = system_message or DEFAULT_SYSTEM_MESSAGE
        
        # Generate the write-up
        response = self._generate_response(prompt, system_msg, temperature)
        
        return response
    
    def _build_logic_writeup_prompt(self, logic: str, task: str = None, 
                                   context: Optional[str] = None) -> str:
        """Build prompt for logic overview write-up (when only -logic is provided)."""
        
        logic_info = LOGIC_DEFINITIONS[logic]
        logic_data = LOGIC_WRITEUP_DATA.get(logic, {})
        
        # Build default task if not provided
        if not task:
            task = f"Generate a comprehensive academic write-up for the '{logic}' logic layer, including an introduction to the logic and overview of all categories under this logic. Use the section_introduction template structure."
        
        prompt_parts = [
            f"# Prompt Pattern Logic Overview Write-Up Request",
            f"",
            f"## Context",
            f"You are generating an academic write-up for prompt pattern logic overview research.",
            f"This should follow the 'section_introduction' template structure for logic-only write-ups.",
            f"",
            f"## Logic Details",
            f"- **Logic Layer**: {logic}",
            f"- **Logic Description**: {logic_info['description']}",
            f"- **Logic Focus**: {logic_info['focus']}",
        ]
        
        # Add logic-specific data if available
        if logic_data:
            prompt_parts.extend([
                f"- **Logic Subtitle**: {logic_data.get('logic_subtitle', '')}",
                f"- **Logic Label**: {logic_data.get('logic_label', logic.lower())}",
            ])
        
        # Add categories under this logic
        if logic in CATEGORY_TEMPLATES:
            categories = CATEGORY_TEMPLATES[logic]
            prompt_parts.extend([
                f"",
                f"## Categories under {logic} Logic",
            ])
            for i, (category_key, category_data) in enumerate(categories.items(), 1):
                category_name = category_key.replace('_', ' ').title()
                prompt_parts.append(f"{i}. **{category_name}**: {category_data['description']}")
        
        prompt_parts.extend([
            f"",
            f"## Task",
            f"{task}",
            f"",
            f"## Template Structure to Follow",
            f"Use the 'section_introduction' template which includes:",
            f"- Section header with logic name and subtitle",
            f"- Long introduction to the logic",
            f"- Enumerated list of categories under this logic",
            f""
        ])
        
        if context:
            prompt_parts.extend([
                f"## Additional Context",
                f"{context}",
                f""
            ])
        
        prompt_parts.extend([
            f"## Requirements",
            f"- Generate a comprehensive logic overview write-up",
            f"- Use LaTeX formatting following the section_introduction template",
            f"- Follow Australian English standards",
            f"- Include detailed logic introduction and category enumeration",
            f"- Ensure publication-quality output"
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_category_writeup_prompt(self, logic: str, category: str, task: str, 
                                     context: Optional[str] = None) -> str:
        """Build prompt for category-specific write-up (when both -logic and -category are provided)."""
        
        logic_info = LOGIC_DEFINITIONS[logic]
        
        # Get category data if available
        category_data = None
        if logic in CATEGORY_TEMPLATES and category in CATEGORY_TEMPLATES[logic]:
            category_data = CATEGORY_TEMPLATES[logic][category]
        
        # Build default task if not provided
        if not task:
            task = f"Generate a comprehensive academic write-up for the '{category}' category under the '{logic}' logic layer. Use the category_subsection template structure."
        
        prompt_parts = [
            f"# Prompt Pattern Category Write-Up Request",
            f"",
            f"## Context",
            f"You are generating an academic write-up for a specific prompt pattern category.",
            f"This should follow the 'category_subsection' template structure for category-specific write-ups.",
            f"",
            f"## Categorisation Details",
            f"- **Logic Layer**: {logic}",
            f"- **Logic Description**: {logic_info['description']}",
            f"- **Logic Focus**: {logic_info['focus']}",
            f"- **Category**: {category}",
        ]
        
        # Add category-specific information if available
        if category_data:
            prompt_parts.extend([
                f"- **Category Description**: {category_data['description']}",
                f"- **Keywords**: {', '.join(category_data['keywords'])}",
            ])
        
        prompt_parts.extend([
            f"",
            f"## Task",
            f"{task}",
            f"",
            f"## Template Structure to Follow",
            f"Use the 'category_subsection' template which includes:",
            f"- Subsection header with category name",
            f"- Category role description under the logic",
            f"- PP analysis (introduction, function, benefits, reusability)",
            f"- Human feeling response",
            f"- Reuse guidance",
            f"- LaTeX table of representative prompt patterns",
            f""
        ])
        
        # Add LaTeX table if available in category data
        if category_data and category_data['latex_table']:
            prompt_parts.extend([
                f"## LaTeX Table of Representative Prompt Patterns",
                f"```latex",
                f"{category_data['latex_table']}",
                f"```",
                f""
            ])
        
        # Add examples if available
        if category_data and category_data['examples']:
            prompt_parts.extend([
                f"## Example Applications",
                f"- " + "\n- ".join(category_data['examples']),
                f""
            ])
        
        # Add few-shot examples if enabled
        if self.use_few_shot:
            prompt_parts.extend([
                f"",
                f"## Few-Shot Examples",
                f"Here are some example write-ups to guide the style and structure:",
                f""
            ])
            
            # Add relevant few-shot examples
            few_shot_content = self._get_relevant_few_shot_examples(logic, category, task)
            prompt_parts.extend(few_shot_content)
        
        if context:
            prompt_parts.extend([
                f"## Additional Context",
                f"{context}",
                f""
            ])
        
        prompt_parts.extend([
            f"## Requirements",
            f"- Generate a comprehensive category-specific write-up",
            f"- Use LaTeX formatting following the category_subsection template",
            f"- Follow Australian English standards",
            f"- Structure the content with subsection, role description, PP analysis, human feeling, and reuse guidance",
            f"- Include the LaTeX table of representative prompt patterns",
            f"- Ensure publication-quality output"
        ])
        
        return "\n".join(prompt_parts)
    
    def _generate_response(self, prompt: str, system_message: str, temperature: float) -> str:
        """Generate response using the unified client."""
        try:
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            # Add conversation history if available
            if self.conversation_history:
                messages = [{"role": "system", "content": system_message}] + self.conversation_history + [{"role": "user", "content": prompt}]
            
            # Get model parameters
            model_params = get_model_params(self.model_version, temperature)
            
            if self.debug:
                print(f"✓ Sending request to {self.model_version}")
                print(f"✓ Model params: {model_params}")
            
            response = self.client.create_chat_completion(
                messages=messages,
                **model_params
            )
            
            content = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": content})
            
            return content
            
        except Exception as e:
            print(f"✗ Error generating response: {e}")
            return f"Error generating response: {e}"
    
    def _get_relevant_few_shot_examples(self, logic: str, category: str, task: str) -> List[str]:
        """Get relevant few-shot examples based on the current request."""
        examples = []
        
        # Determine which few-shot examples are most relevant
        task_lower = task.lower()
        
        # Always include basic writeup examples
        if "basic_writeup" in FEW_SHOT_EXAMPLES:
            examples.extend([
                "### Example 1: Basic Category Write-up",
                f"**Input**: {FEW_SHOT_EXAMPLES['basic_writeup'][0]['user_input']}",
                "",
                f"**Output**:",
                FEW_SHOT_EXAMPLES['basic_writeup'][0]['assistant_output'],
                "",
                "---",
                ""
            ])
        
        # Add LaTeX examples if task mentions LaTeX, formatting, or academic writing
        if any(keyword in task_lower for keyword in ['latex', 'format', 'academic', 'publication']):
            if "latex_formatting" in FEW_SHOT_EXAMPLES:
                examples.extend([
                    "### Example 2: LaTeX Formatted Write-up",
                    f"**Input**: {FEW_SHOT_EXAMPLES['latex_formatting'][0]['user_input']}",
                    "",
                    f"**Output**:",
                    FEW_SHOT_EXAMPLES['latex_formatting'][0]['assistant_output'],
                    "",
                    "---",
                    ""
                ])
        
        # Add analysis examples if task mentions analysis, research, or academic
        if any(keyword in task_lower for keyword in ['analy', 'research', 'academic', 'publication']):
            if "category_analysis" in FEW_SHOT_EXAMPLES:
                examples.extend([
                    "### Example 3: Academic Analysis Write-up",
                    f"**Input**: {FEW_SHOT_EXAMPLES['category_analysis'][0]['user_input']}",
                    "",
                    f"**Output**:",
                    FEW_SHOT_EXAMPLES['category_analysis'][0]['assistant_output'],
                    "",
                    "---",
                    ""
                ])
        
        # Add a note about following the style
        examples.extend([
            "**Note**: Please follow similar structure, tone, and formatting style as demonstrated in the examples above.",
            ""
        ])
        
        return examples
    
    def start_chat(self, logic: Optional[str] = None, category: Optional[str] = None):
        """Start interactive chat mode for iterative refinement."""
        print("\n" + "="*60)
        print("CATEGORISATION WRITE-UP CHAT MODE")
        print("="*60)
        
        if logic:
            print(f"Current Logic: {logic}")
            if logic in LOGIC_DEFINITIONS:
                print(f"Logic Focus: {LOGIC_DEFINITIONS[logic]['focus']}")
        
        if category:
            print(f"Current Category: {category}")
        
        print("\nType your messages below. Use 'exit' or 'quit' to end the session.")
        print("Commands: 'clear' to clear history, 'history' to show conversation")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("✓ Conversation history cleared.")
                    continue
                
                if user_input.lower() == 'history':
                    self._show_conversation_history()
                    continue
                
                if not user_input:
                    continue
                
                # Generate response
                response = self._generate_response(user_input, DEFAULT_SYSTEM_MESSAGE, 0.7)
                
                print(f"\nAssistant: {response}")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"✗ Error: {e}")
    
    def _show_conversation_history(self):
        """Display the conversation history."""
        if not self.conversation_history:
            print("No conversation history.")
            return
        
        print("\n" + "="*50)
        print("CONVERSATION HISTORY")
        print("="*50)
        
        for i, message in enumerate(self.conversation_history, 1):
            role = message["role"].title()
            content = message["content"][:200] + "..." if len(message["content"]) > 200 else message["content"]
            print(f"{i}. {role}: {content}")
        
        print("="*50)

#############################################
# UTILITY FUNCTIONS                         #
#############################################

def save_to_file(content: str, filename: str, custom_path: Optional[str] = None):
    """Save content to a file with timestamp, optionally in a custom directory."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add timestamp to filename if not already present
        if not any(char.isdigit() for char in filename):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
        
        # Determine save directory
        if custom_path:
            # Use custom path (can be absolute or relative)
            if os.path.isabs(custom_path):
                save_dir = custom_path
            else:
                save_dir = os.path.abspath(custom_path)
        else:
            # Default to latex_writing directory
            save_dir = "latex_writing"
        
        # Create directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"✓ Created directory: {save_dir}")
        
        # Save file to directory
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Content saved to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"✗ Error saving file: {e}")
        return None

def load_latex_table(filepath: str) -> Optional[str]:
    """Load LaTeX table content from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"✗ Error loading LaTeX table: {e}")
        return None

def validate_logic(logic: str) -> bool:
    """Validate if the provided logic is valid."""
    return logic in LOGIC_DEFINITIONS

def list_available_logics():
    """List all available logic definitions."""
    print("\nAvailable Logic Definitions:")
    print("="*50)
    for logic, info in LOGIC_DEFINITIONS.items():
        print(f"• {logic}: {info['focus']}")
    print("="*50)

def list_available_categories(logic: Optional[str] = None):
    """List all available categories, optionally filtered by logic."""
    if logic:
        if logic not in CATEGORY_TEMPLATES:
            print(f"No categories found for logic: {logic}")
            return
        
        print(f"\nAvailable Categories for '{logic}' Logic:")
        print("="*60)
        for category, data in CATEGORY_TEMPLATES[logic].items():
            print(f"• {category}: {data['description']}")
        print("="*60)
    else:
        print("\nAll Available Categories by Logic:")
        print("="*60)
        for logic_name, categories in CATEGORY_TEMPLATES.items():
            print(f"\n{logic_name} Logic:")
            for category, data in categories.items():
                print(f"  • {category}: {data['description']}")
        print("="*60)

def validate_category(logic: str, category: str) -> bool:
    """Validate if the provided category exists under the given logic."""
    return logic in CATEGORY_TEMPLATES and category in CATEGORY_TEMPLATES[logic]

def get_category_data(logic: str, category: str) -> Optional[Dict[str, Any]]:
    """Get category data for a specific logic and category."""
    if validate_category(logic, category):
        return CATEGORY_TEMPLATES[logic][category]
    return None

def update_category_data(logic: str, category: str, field: str, value: Any) -> bool:
    """Update a specific field in category data."""
    if validate_category(logic, category):
        if field in CATEGORY_TEMPLATES[logic][category]:
            CATEGORY_TEMPLATES[logic][category][field] = value
            return True
    return False

def show_category_details(logic: str, category: str):
    """Show detailed information about a specific category."""
    if not validate_category(logic, category):
        print(f"Error: Category '{category}' not found under logic '{logic}'")
        if logic in CATEGORY_TEMPLATES:
            print(f"Available categories for '{logic}': {list(CATEGORY_TEMPLATES[logic].keys())}")
        else:
            print(f"Available logics: {list(CATEGORY_TEMPLATES.keys())}")
        return
    
    data = get_category_data(logic, category)
    if not data:
        print(f"Error: No data found for category '{category}' under logic '{logic}'")
        return
    
    print(f"\n{'='*60}")
    print(f"CATEGORY DETAILS: {logic} > {category}")
    print(f"{'='*60}")
    print(f"Description: {data['description']}")
    print(f"Keywords: {', '.join(data['keywords'])}")
    
    if data['examples']:
        print(f"\nExamples:")
        for i, example in enumerate(data['examples'], 1):
            print(f"  {i}. {example}")
    else:
        print(f"\nExamples: Not yet defined")
    
    if data['latex_table']:
        print(f"\nLaTeX Table:")
        print(f"```latex")
        print(data['latex_table'])
        print(f"```")
    else:
        print(f"\nLaTeX Table: Not yet defined")
    
    print(f"{'='*60}")

def generate_complete_logic_latex_writeup(logic: str) -> str:
    """Generate a complete LaTeX write-up for a specific logic using the template structure."""
    if logic not in LOGIC_WRITEUP_DATA:
        return f"Error: Complete write-up data not available for logic '{logic}'"
    
    if logic not in CATEGORY_TEMPLATES:
        return f"Error: Category templates not available for logic '{logic}'"
    
    logic_data = LOGIC_WRITEUP_DATA[logic]
    categories = CATEGORY_TEMPLATES[logic]
    
    # Generate category enumeration
    category_items = []
    for category_key, category_data in categories.items():
        category_name = category_key.replace('_', ' ').title()
        item = LATEX_WRITEUP_TEMPLATE["category_enumeration_item"].format(
            category_name=category_name,
            category_description=category_data['description']
        )
        category_items.append(item)
    
    category_enumeration = "\n".join(category_items)
    
    # Generate section introduction
    section_intro = LATEX_WRITEUP_TEMPLATE["section_introduction"].format(
        logic_name=logic,
        logic_subtitle=logic_data['logic_subtitle'],
        logic_label=logic_data['logic_label'],
        logic_description=logic_data['logic_description'],
        logic_name_lower=logic.lower(),
        category_enumeration=category_enumeration
    )
    
    # Generate category subsections
    category_sections = []
    for category_key, category_data in categories.items():
        if category_key in logic_data['categories']:
            writeup_data = logic_data['categories'][category_key]
            
            # Format PP analysis
            pp_analysis = LATEX_WRITEUP_TEMPLATE["pp_analysis_structure"].format(
                pp_introduction=writeup_data['pp_analysis']['pp_introduction'],
                pp_function=writeup_data['pp_analysis']['pp_function'],
                pp_benefit=writeup_data['pp_analysis']['pp_benefit'],
                pp_reusability=writeup_data['pp_analysis']['pp_reusability']
            )
            
            # Format human feeling response
            human_feeling = LATEX_WRITEUP_TEMPLATE["human_feeling_template"].format(
                feeling_description=writeup_data['human_feeling'],
                emotional_impact=writeup_data['emotional_impact'],
                cognitive_benefit=writeup_data['cognitive_benefit']
            )
            
            # Format reuse guidance
            reuse_steps = []
            for i, step in enumerate(writeup_data['reuse_steps'], 1):
                reuse_steps.append(f"{i}. {step}")
            
            reuse_guidance = LATEX_WRITEUP_TEMPLATE["reuse_template"].format(
                reuse_step1=writeup_data['reuse_steps'][0] if len(writeup_data['reuse_steps']) > 0 else "Define the specific context",
                reuse_step2=writeup_data['reuse_steps'][1] if len(writeup_data['reuse_steps']) > 1 else "Adapt the template structure",
                reuse_step3=writeup_data['reuse_steps'][2] if len(writeup_data['reuse_steps']) > 2 else "Customize for specific requirements"
            )
            
            # Generate category subsection
            category_section = LATEX_WRITEUP_TEMPLATE["category_subsection"].format(
                category_name=category_key.replace('_', ' ').title(),
                category_label=writeup_data['category_label'],
                logic_name_lower=logic.lower(),
                category_role_description=writeup_data['role_description'],
                pp_analysis=pp_analysis,
                human_feeling_response=human_feeling,
                reuse_guidance=reuse_guidance,
                latex_table=category_data['latex_table']
            )
            
            category_sections.append(category_section)
    
    # Combine all sections
    complete_writeup = section_intro + "\n\n" + "\n\n".join(category_sections)
    
    return complete_writeup

def generate_logic_template(logic: str) -> str:
    """Generate a template structure for a specific logic that can be filled in using LATEX_WRITEUP_TEMPLATE."""
    if logic not in LOGIC_DEFINITIONS:
        return f"Error: Logic '{logic}' not found in definitions"
    
    logic_info = LOGIC_DEFINITIONS[logic]
    categories = CATEGORY_TEMPLATES.get(logic, {})
    
    # Build category enumeration items using the template
    category_items = []
    for category_key, category_data in categories.items():
        item = LATEX_WRITEUP_TEMPLATE["category_enumeration_item"].format(
            category_name=category_key.replace('_', ' ').title(),
            category_description=category_data['description']
        )
        category_items.append(item)
    
    # Use the section_introduction template for logic overview
    section_intro = LATEX_WRITEUP_TEMPLATE["section_introduction"].format(
        logic_name=logic,
        logic_subtitle="[SUBTITLE_HERE]",
        logic_label=logic.lower(),
        logic_description=logic_info['description'],
        logic_name_lower=logic.lower(),
        category_enumeration="\n".join(category_items)
    )
    
    # Add individual category subsections using the template
    category_sections = []
    for category_key, category_data in categories.items():
        category_name = category_key.replace('_', ' ').title()
        
        # Use the category_subsection template for each category
        category_section = LATEX_WRITEUP_TEMPLATE["category_subsection"].format(
            category_name=category_name,
            category_label=category_key,
            logic_name_lower=logic.lower(),
            category_role_description="[ADD_CATEGORY_ROLE_DESCRIPTION]",
            pp_analysis="[ADD_PP_ANALYSIS]",
            human_feeling_response="[ADD_HUMAN_FEELING_RESPONSE]",
            reuse_guidance="[ADD_REUSE_GUIDANCE]",
            latex_table=category_data['latex_table']
        )
        category_sections.append(category_section)
    
    # Combine section introduction with category subsections
    full_template = section_intro + "\n" + "\n".join(category_sections)
    
    return f"""% Template for {logic} Logic Write-up
% Use this template to create comprehensive write-ups following the academic structure
% This template uses the LATEX_WRITEUP_TEMPLATE structure

{full_template}"""

def generate_single_category_latex_writeup(logic: str, category: str) -> str:
    """Generate a LaTeX write-up for a single category within a logic."""
    if logic not in LOGIC_WRITEUP_DATA:
        return f"Error: Complete write-up data not available for logic '{logic}'"
    
    if logic not in CATEGORY_TEMPLATES:
        return f"Error: Category templates not available for logic '{logic}'"
    
    if not validate_category(logic, category):
        return f"Error: Category '{category}' not found under logic '{logic}'"
    
    logic_data = LOGIC_WRITEUP_DATA[logic]
    category_data = CATEGORY_TEMPLATES[logic][category]
    
    # Check if category has writeup data
    if category not in logic_data['categories']:
        return f"Error: Write-up data not available for category '{category}' under logic '{logic}'"
    
    writeup_data = logic_data['categories'][category]
    
    # Format PP analysis
    pp_analysis = LATEX_WRITEUP_TEMPLATE["pp_analysis_structure"].format(
        pp_introduction=writeup_data['pp_analysis']['pp_introduction'],
        pp_function=writeup_data['pp_analysis']['pp_function'],
        pp_benefit=writeup_data['pp_analysis']['pp_benefit'],
        pp_reusability=writeup_data['pp_analysis']['pp_reusability']
    )
    
    # Format human feeling response
    human_feeling = LATEX_WRITEUP_TEMPLATE["human_feeling_template"].format(
        feeling_description=writeup_data['human_feeling'],
        emotional_impact=writeup_data['emotional_impact'],
        cognitive_benefit=writeup_data['cognitive_benefit']
    )
    
    # Format reuse guidance
    reuse_guidance = LATEX_WRITEUP_TEMPLATE["reuse_template"].format(
        reuse_step1=writeup_data['reuse_steps'][0] if len(writeup_data['reuse_steps']) > 0 else "Define the specific context",
        reuse_step2=writeup_data['reuse_steps'][1] if len(writeup_data['reuse_steps']) > 1 else "Adapt the template structure",
        reuse_step3=writeup_data['reuse_steps'][2] if len(writeup_data['reuse_steps']) > 2 else "Customize for specific requirements"
    )
    
    # Generate category subsection
    category_writeup = LATEX_WRITEUP_TEMPLATE["category_subsection"].format(
        category_name=category.replace('_', ' ').title(),
        category_label=writeup_data['category_label'],
        logic_name_lower=logic.lower(),
        category_role_description=writeup_data['role_description'],
        pp_analysis=pp_analysis,
        human_feeling_response=human_feeling,
        reuse_guidance=reuse_guidance,
        latex_table=category_data['latex_table']
    )
    
    # Add a header comment for context
    header = f"""% LaTeX Write-up for {category.replace('_', ' ').title()} Category
% Logic: {logic} - {LOGIC_DEFINITIONS[logic]['focus']}
% Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    return header + category_writeup

def generate_category_template(logic: str, category: str) -> str:
    """Generate a template for a specific category that can be filled in using LATEX_WRITEUP_TEMPLATE."""
    if not validate_category(logic, category):
        return f"Error: Category '{category}' not found under logic '{logic}'"
    
    category_data = CATEGORY_TEMPLATES[logic][category]
    category_name = category.replace('_', ' ').title()
    
    # Use the category_subsection template
    template = LATEX_WRITEUP_TEMPLATE["category_subsection"].format(
        category_name=category_name,
        category_label=category,
        logic_name_lower=logic.lower(),
        category_role_description="[ADD_DETAILED_CATEGORY_ROLE_DESCRIPTION]",
        pp_analysis="[ADD_PP_ANALYSIS]",
        human_feeling_response="[ADD_HUMAN_FEELING_RESPONSE]",
        reuse_guidance="[ADD_REUSE_GUIDANCE]",
        latex_table=category_data['latex_table']
    )
    
    return f"""% Template for {category_name} Category under {logic} Logic
% Use this template to create comprehensive write-ups following the academic structure
% This template uses the LATEX_WRITEUP_TEMPLATE structure

{template}

% Keywords: {', '.join(category_data['keywords'])}
% Examples: {', '.join(category_data['examples']) if category_data['examples'] else 'Not yet defined'}
"""

#############################################
# MAIN FUNCTION AND ARGUMENT PARSING       #
#############################################

def main():
    """Main function to handle command line arguments and execute the categorisation write-up task."""
    
    parser = argparse.ArgumentParser(
        description="Generate categorisation write-ups for prompt patterns using Azure OpenAI GPT models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=""":
Examples:
  # Logic overview (uses section_introduction template)
  python categorisation_write_up.py -logic "Beyond"
  
  # Category-specific write-up (uses category_subsection template)
  python categorisation_write_up.py -logic "In" -category "context_control" -task "Generate write-up for context control patterns"
  
  # With category data (LaTeX table included)
  python categorisation_write_up.py -logic "Over" -category "prompt_improvement"
  
  # Interactive chat mode
  python categorisation_write_up.py -chat -logic "Across" -category "classification"
  
  # Output to file - logic overview
  python categorisation_write_up.py -logic "Beyond" -outputfile "beyond_logic_overview.tex"
  
  # Output to file - category specific
  python categorisation_write_up.py -logic "Beyond" -category "synthesis" -outputfile "beyond_synthesis_writeup.tex"
  
  # List available logics
  python categorisation_write_up.py -list_logics
  
  # List all categories
  python categorisation_write_up.py -list_categories
  
  # List categories for specific logic
  python categorisation_write_up.py -list_categories "In"
  
  # Show category details
  python categorisation_write_up.py -show_category "Across" "argument"
  
  # Generate complete LaTeX write-up
  python categorisation_write_up.py -generate_latex "Across"
  
  # Generate LaTeX template for a logic
  python categorisation_write_up.py -generate_template "In"
  
  # Generate LaTeX write-up for a single category
  python categorisation_write_up.py -generate_category_latex "Across" "argument"
  
  # Generate template for a single category
  python categorisation_write_up.py -generate_category_template "In" "context_control"
  
  # Save output to default location (latex_writing folder)
  python categorisation_write_up.py -generate_category_latex "Across" "argument" -save
  
  # Save output to custom directory
  python categorisation_write_up.py -generate_category_latex "Across" "argument" -save "my_papers/drafts"
        """
    )
    
    # Core arguments
    parser.add_argument('-logic', type=str, 
                       help='Logic layer (In, Out, Over, Across, Beyond, At)')
    parser.add_argument('-category', type=str,
                       help='PP category under the specified logic (optional - if not provided, generates logic overview)')
    parser.add_argument('-task', type=str,
                       help='Specific task/request for the write-up (optional - auto-generated if not provided)')
    
    # Optional content arguments
    parser.add_argument('-context', type=str,
                       help='Additional context for the write-up')
    parser.add_argument('-system', type=str,
                       help='Custom system message')
    
    # Model and output arguments
    parser.add_argument('-model_version', type=str, default='gpt-4.1',
                       help='Azure OpenAI model version to use')
    parser.add_argument('-temperature', type=float, default=0.7,
                       help='Model temperature (0.0 to 1.0)')
    parser.add_argument('-outputfile', type=str,
                       help='Output file path (optional)')
    parser.add_argument('-save', type=str, nargs='?', const='default',
                       help='Save output to file (optional: specify custom directory path)')
    
    # Mode arguments
    parser.add_argument('-chat', action='store_true',
                       help='Start interactive chat mode')
    parser.add_argument('-debug', type=bool, default=False,
                       help='Enable debug mode')
    parser.add_argument('-few_shot', action='store_true',
                       help='Include few-shot examples in the prompt for better output quality')
    
    # Utility arguments
    parser.add_argument('-list_logics', action='store_true',
                       help='List available logic definitions')
    parser.add_argument('-list_categories', type=str, nargs='?', const='all',
                       help='List available categories (optional: specify logic)')
    parser.add_argument('-show_category', type=str, nargs=2, metavar=('LOGIC', 'CATEGORY'),
                       help='Show details for a specific category')
    parser.add_argument('-generate_latex', type=str,
                       help='Generate complete LaTeX write-up for specified logic')
    parser.add_argument('-generate_template', type=str,
                       help='Generate LaTeX template for specified logic')
    parser.add_argument('-generate_category_latex', type=str, nargs=2, metavar=('LOGIC', 'CATEGORY'),
                       help='Generate LaTeX write-up for a single category')
    parser.add_argument('-generate_category_template', type=str, nargs=2, metavar=('LOGIC', 'CATEGORY'),
                       help='Generate template for a single category')
    
    args = parser.parse_args()
    
    # Handle utility functions
    if args.list_logics:
        list_available_logics()
        return
    
    if args.list_categories:
        if args.list_categories == 'all':
            list_available_categories()
        else:
            list_available_categories(args.list_categories)
        return
    
    if args.show_category:
        logic, category = args.show_category
        show_category_details(logic, category)
        return
    
    if args.generate_latex:
        latex_content = generate_complete_logic_latex_writeup(args.generate_latex)
        print("\n" + "="*60)
        print(f"COMPLETE LATEX WRITE-UP: {args.generate_latex}")
        print("="*60)
        print(latex_content)
        print("="*60)
        
        # Save to file only if -save argument is provided
        if args.save is not None:
            filename = f"{args.generate_latex.lower()}_logic_writeup.tex"
            custom_path = None if args.save == 'default' else args.save
            saved_file = save_to_file(latex_content, filename, custom_path)
            if saved_file:
                print(f"✓ LaTeX write-up saved to: {saved_file}")
        return
    
    if args.generate_template:
        template_content = generate_logic_template(args.generate_template)
        print("\n" + "="*60)
        print(f"LATEX TEMPLATE: {args.generate_template}")
        print("="*60)
        print(template_content)
        print("="*60)
        
        # Save to file only if -save argument is provided
        if args.save is not None:
            filename = f"{args.generate_template.lower()}_logic_template.tex"
            custom_path = None if args.save == 'default' else args.save
            saved_file = save_to_file(template_content, filename, custom_path)
            if saved_file:
                print(f"✓ LaTeX template saved to: {saved_file}")
        return
    
    if args.generate_category_latex:
        logic, category = args.generate_category_latex
        latex_content = generate_single_category_latex_writeup(logic, category)
        print("\n" + "="*60)
        print(f"CATEGORY LATEX WRITE-UP: {category} ({logic})")
        print("="*60)
        print(latex_content)
        print("="*60)
        
        # Save to file only if -save argument is provided
        if args.save is not None:
            filename = f"{logic.lower()}_{category.lower()}_writeup.tex"
            custom_path = None if args.save == 'default' else args.save
            saved_file = save_to_file(latex_content, filename, custom_path)
            if saved_file:
                print(f"✓ Category LaTeX write-up saved to: {saved_file}")
        return
    
    if args.generate_category_template:
        logic, category = args.generate_category_template
        template_content = generate_category_template(logic, category)
        print("\n" + "="*60)
        print(f"CATEGORY TEMPLATE: {category} ({logic})")
        print("="*60)
        print(template_content)
        print("="*60)
        
        # Save to file only if -save argument is provided
        if args.save is not None:
            filename = f"{logic.lower()}_{category.lower()}_template.tex"
            custom_path = None if args.save == 'default' else args.save
            saved_file = save_to_file(template_content, filename, custom_path)
            if saved_file:
                print(f"✓ Category template saved to: {saved_file}")
        return
    
    # Validate required arguments for non-chat mode
    if not args.chat and not args.logic:
        print("Error: -logic is required for non-chat mode")
        parser.print_help()
        return
    
    # Validate logic if provided
    if args.logic and not validate_logic(args.logic):
        print(f"Error: Invalid logic '{args.logic}'")
        list_available_logics()
        return
    
    # Validate category if provided
    if args.logic and args.category and not validate_category(args.logic, args.category):
        print(f"Error: Invalid category '{args.category}' for logic '{args.logic}'")
        list_available_categories(args.logic)
        return
    
    # Initialize client
    try:
        client = CategorisationWriteUpClient(
            model_version=args.model_version,
            debug=args.debug
        )
        
        print(f"✓ Initialized with model: {args.model_version}")
        
    except Exception as e:
        print(f"✗ Error initializing client: {e}")
        return
    
    # Handle chat mode
    if args.chat:
        # If task is provided, execute it first, then start chat
        if args.task and args.logic and args.category:
            print("Executing initial task before starting chat...")
            result = execute_writeup_task(client, args)
            if result and args.outputfile:
                custom_path = None if args.save == 'default' else args.save if args.save else None
                save_to_file(result, args.outputfile, custom_path)
            print("\nStarting chat mode...")
        
        client.start_chat(logic=args.logic, category=args.category)
        return
    
    # Execute write-up task
    result = execute_writeup_task(client, args)
    
    if result:
        print("\n" + "="*60)
        print("GENERATED WRITE-UP")
        print("="*60)
        print(result)
        print("="*60)
        
        # Save to file if requested
        if args.outputfile:
            custom_path = None if args.save == 'default' else args.save if args.save else None
            saved_file = save_to_file(result, args.outputfile, custom_path)
            if saved_file:
                print(f"✓ Write-up saved to: {saved_file}")

def execute_writeup_task(client: CategorisationWriteUpClient, args) -> Optional[str]:
    """Execute the write-up generation task."""
    try:
        # Build task if not provided
        task = args.task
        if not task:
            if args.category:
                task = f"Generate a comprehensive academic write-up for the '{args.category}' category under the '{args.logic}' logic layer. Include detailed analysis, examples, and LaTeX formatting suitable for publication."
            else:
                task = f"Generate a comprehensive academic write-up for the '{args.logic}' logic layer, including an introduction to the logic and overview of all categories under this logic. Use LaTeX formatting suitable for publication."
        
        # Generate write-up
        result = client.generate_writeup(
            logic=args.logic,
            category=args.category,
            task=task,
            system_message=args.system,
            context=args.context,
            temperature=args.temperature
        )
        
        return result
        
    except Exception as e:
        print(f"✗ Error executing write-up task: {e}")
        return None

if __name__ == "__main__":
    main()