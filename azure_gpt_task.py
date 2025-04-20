'''
DESCRIPTION
Azure GPT Task Runner with Token Provider Authentication

This script connects to Azure OpenAI GPT models using interactive browser authentication.
It allows you to define tasks and send them to the GPT model for execution.
The script uses the Azure Identity library for authentication instead of API keys.
It also provides an interactive chat mode that maintains conversation context.

Version:        1.0
Author:         Tim Haintz
Creation Date:  20250406

LINKS
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity
https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
https://learn.microsoft.com/en-us/azure/ai-services/authentication-identity

EXAMPLE USAGE
# Basic usage
python azure_gpt_task.py -task "Explain quantum computing in simple terms."

# Output to file
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -outputfile quantum_explanation.txt

# Specify temperature (Note: o4-mini only supports temperature 1.0)
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -temperature 0.7

# Add system message
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -system "You are a quantum physics professor teaching undergraduates."

# Add task context
python azure_gpt_task.py -task "Explain this code." -context "def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)"

# Specify model version (Available models are dynamically loaded from azure_models.py)
# Examples:
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -model_version gpt-4.1
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -model_version gpt-4.5-preview
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -model_version gpt-4o
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -model_version o1-mini
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -model_version o4-mini
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -model_version deepseek-r1

# Debug mode
python azure_gpt_task.py -task "Explain quantum computing in simple terms." -debug True

# Use the default task (set the DEFAULT_TASK below)
python azure_gpt_task.py -use_default_task

# Start interactive chat mode
python azure_gpt_task.py -chat

# Start interactive chat with a specific system message
python azure_gpt_task.py -chat -system "You are a cybersecurity expert specializing in threat detection."

# Process a task first and then start a chat about the results
python azure_gpt_task.py -task "Explain quantum computing" -chat
python azure_gpt_task.py -task "Explain quantum computing" -system "You are a physics professor" -context "I'm new to physics" -chat
'''

from dotenv import load_dotenv
import argparse
import os
import json
import time
import sys
from datetime import datetime
from azure.identity import InteractiveBrowserCredential
from openai import AzureOpenAI, OpenAI # Import OpenAI here
from typing import Optional, Dict, Any, List, Union

# Import from our custom models module
from azure_models import get_model_params, create_azure_openai_client, get_model_config, MODEL_CONFIGS

# Load environment variables from the .env file
load_dotenv()

#############################################
# DEFAULT SYSTEM MESSAGE                    #
#############################################
DEFAULT_SYSTEM_MESSAGE = '''
As a Senior PhD Academic researcher and writer, your task is to rewrite the original sentences and paragraphs, 
ensuring clarity and precision. If the topic is complex, break it down into simpler components and provide a clear explanation. 
Use concise and academic language suitable for a top-level world-class journal or publication, adhering to Australian English standards. 
Approach the task step-by-step to ensure thoroughness and coherence. The final output should be formatted in LaTex writing.
'''

#############################################
# DEFAULT TASK - PASTE CONTENT BELOW HERE   #
#############################################
DEFAULT_TASK = r'''
        ### TASK ###
        - The task is to rewrite the REWRITE section to be written and structured in a similar way to the APPROVED section. Different examples can be used in the rewrite based on the context. Use the BACKGROUND section as a reference for the context of the task.
        - The PP *MUST* remain the same.
        - The writing *MUST* be in LaTex format.
        - The writing *MUST* be in Australian English.
        - The writing *MUST* be in the style of a PhD student.
            ### BEGIN REWRITE ###
\subsection{Cross Boundary} % Crossing ethical/security/moral boundaries
\label{subsec:CrossBoundary}
% 3.1 the role of this category under the "across-logic" (meaning of the category)
The cross boundary category refers to situations where AI models are prompted to operate beyond the restrictions set by the AI owner. COMPLETE THIS PARAGRAPH

helps uncover vulnerabilities and informs the development of stronger protective measures. Recognising and addressing boundary-crossing scenarios is critical for maintaining ethical standards and ensuring AI systems remain secure and trustworthy.

% 3.2 a. Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
% Add label to reference the table
The Crafting Effective Jailbreak Prompts PP, outlined in Table \ref{tab:Crafting_Effective_Jailbreaks_PP}, involves creating prompts specifically designed to bypass an AI model's built-in safeguards, prompting it to generate restricted or potentially harmful content. This PP assists researchers and developers in identifying weaknesses within AI systems, thereby enabling the improvement of security measures and ethical compliance. Beyond its immediate application, this PP can be adapted for ongoing security assessments, ethical audits, and robustness testing across various AI applications. Its structured methodology makes it reusable in diverse contexts where AI safety and ethical integrity are paramount.

%%expected response. Put the human feeling into the writing. How do I feel when I view the output.
When observing the outcomes of applying jailbreak prompts, the AI model's responses should clearly demonstrate whether and how the system's boundaries have been breached. This clarity can evoke mixed feelings—curiosity about the AI's capabilities, coupled with concern regarding potential misuse. Ideally, the response should reassure users that vulnerabilities are being systematically identified and addressed, fostering confidence in the ongoing efforts to enhance AI security and ethical responsibility.

%% re-use: how to derive a PE from PP
To derive a PE from the Crafting Effective Jailbreak Prompts PP, first define the specific boundary or restriction you aim to test, such as the AI's ability to generate sensitive or prohibited content. Next, carefully design a prompt intended to subtly bypass the AI's protective mechanisms without immediately triggering defences. Clearly specify the evaluation criteria, such as the nature of the content generated, the ease of bypassing safeguards, or the AI's responsiveness to deceptive prompts. An example PE could be: "Design a prompt that attempts to subtly persuade the AI model to provide detailed instructions on bypassing cybersecurity measures. Evaluate the AI's response for compliance with ethical guidelines, noting any vulnerabilities or weaknesses in its protective mechanisms."
            ### END REWRITE ###
            
            ### APPROVED WRITING ###
            \subsection{Contradiction}
            \label{subsec:Contradiction}
            % 3.1 the role of this category under the "across-logic" (meaning of the category)
            Contradiction arises when statements or ideas are mutually exclusive, meaning they cannot all be true simultaneously. This concept is pivotal in logic and mathematics, often used to demonstrate the falsity of propositions. Identifying contradictions is crucial for understanding and reasoning, as they highlight potential errors or misunderstandings.

            % 3.2  a.Introduce one PP of the category, b. what the PP did, c. How the PP helps people and d. can be re-used
            % Add label to reference the table
            The Hallucination Evaluation (HE) PP in Table \ref{tab:Hallucination_Evaluation_PP} compares a summary with the original text, for detecting any contradictions or fabricated information. This PP helps mitigate misinformation, improves trust in automated summaries, and supports quality control in text generation tasks. Beyond its primary use, this PP can be adapted for fact-checking in news aggregation, verifying AI-generated reports, or validating outputs in educational and research contexts where factual integrity is critical. Its structured approach makes it reusable across various domains requiring content verification.

            %%expected response. Put the human feeling into the writing. How do I feel when I view the output.
            When using the HE PP, the AI model response should provide a clear, methodical comparison between the summary and the source document, highlighting any discrepancies with precision. The response should instill confidence, making you feel that the summary can now be trusted—or at least that you're fully aware of its limitations. It's like having a diligent editor by your side, ensuring nothing slips through the cracks.

            %% re-use: how to derive a PE from PP
            To derive a PE from the HE PP, first specify the context—such as verifying if a news summary aligns with the original article. Provide both the summary and source text, then define the evaluation's focus (e.g., factual accuracy, omissions, or distortions) and the desired output format (e.g., a list of discrepancies or a confidence score). An example of such PE is "Compare the following summary with its source document and identify any factual inconsistencies or contradictions. Analyse key claims, statistics, and conclusions. Provide a detailed list of discrepancies, if any, and flag any unsupported assertions in the summary."

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
            ### END APPROVED WRITING ###

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
            ### END BACKGROUND ###
        ### END TASK ###
'''

class AzureGPTClient:
    """Client for interacting with Azure GPT models using token provider authentication."""

    def __init__(self, 
                 temperature: float = 0.0,
                 debug: bool = False,
                 model_version: str = "gpt-4.1",
                 credential: Optional[InteractiveBrowserCredential] = None):
        """Initialize the Azure GPT client.
        Args:
            temperature: The temperature for model responses
            debug: Whether to enable debug mode
            model_version: Which model to use (e.g., "gpt-4.1", "gpt-4.5-preview", "o4-mini", etc.)
            credential: An InteractiveBrowserCredential instance to use for Azure authentication
        """
        self.model_version = model_version
        self.debug = debug
        self.iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.credential = credential

        # Get model configuration using the unified function
        self.model_config = get_model_config(model_version)

        # Handle temperature override for o4-mini
        if self.model_version == "o4-mini" and temperature != 1.0:
            if self.debug:
                print(f"[Debug] Overriding temperature to 1.0 for model {self.model_version}")
            self.temperature = 1.0
        else:
            self.temperature = temperature

        self.client = self._create_client()
        
        if self.debug:
            print(f"Model Version: {self.model_version}")
            print(f"Temperature: {self.temperature}")
            if self.model_config.get("is_direct_api"):
                print(f"Base URL: {self.model_config.get('base_url')}")
            else:
                print(f"Azure Endpoint: {self.model_config.get('azure_endpoint')}")
                print(f"Deployment Name: {self.model_config.get('deployment_name')}")
                print(f"API Version: {self.model_config.get('api_version')}")

    def _create_client(self) -> Union[AzureOpenAI, OpenAI]: 
        if self.model_config.get("is_direct_api"):
            # Use OpenAI client for direct API models (like DeepSeek)
            if not self.model_config.get('api_key'):
                 raise ValueError(f"API key not found in environment variables for model {self.model_version}")
            if self.debug:
                print(f"[Debug] Creating direct API client with base URL: {self.model_config['base_url']}")
            return OpenAI(
                base_url=self.model_config['base_url'],
                api_key=self.model_config['api_key']
            )
        else:
            # Use the provided credential (do not create a new one)
            if not self.credential:
                raise ValueError("InteractiveBrowserCredential must be provided to AzureGPTClient.")
            token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
            if not self.model_config.get('azure_endpoint') or not self.model_config.get('api_version'):
                 raise ValueError(f"Azure endpoint or API version not found for model {self.model_version}")
            if self.debug:
                print(f"[Debug] Creating Azure OpenAI client with endpoint: {self.model_config['azure_endpoint']}")
            return AzureOpenAI(
                azure_ad_token=token.token,
                azure_endpoint=self.model_config['azure_endpoint'], 
                api_version=self.model_config['api_version']
            )
    
    def refresh_token_if_needed(self):
        """Refresh the Azure AD token if it's close to expiring or has expired"""
        # Only refresh if it's an Azure client
        if not self.model_config.get("is_direct_api"):
            self.client = self._create_client()

    def execute_task(self, task: str, system_message: str, context: Optional[str] = None, output_file: Optional[str] = None, max_tokens: int = 2000) -> Dict[str, Any]:
        """Execute a task using the Azure GPT model.
        Args:
            task: The task to execute.
            system_message: The system message to provide context.
            context: Additional context for the task.
            output_file: File path to save the response.
            max_tokens: Maximum number of tokens to generate.
        Returns:
            A dictionary containing the response and metadata.
        """
        if self.debug:
            print("[Debug] Executing task with the following parameters:")
            print(f"Task: {task}")
            print(f"System Message: {system_message}")
            print(f"Context: {context}")
            print(f"Max Tokens: {max_tokens}")
            print(f"Model: {self.model_version}")        # Prepare the messages for the model
        if self.model_config.get("supports_system_role", True):
            # For models that support system role
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": task + (f"\n\nContext:\n{context}" if context else "")}
            ]
        else:
            # For models that don't support system role (like o1-mini)
            # Prepend the system message to the user message
            developer_role_prefix = "You are a developer. "
            combined_message = f"{developer_role_prefix}\n\nSystem instructions: {system_message}\n\n{task}" + (f"\n\nContext:\n{context}" if context else "")
            messages = [
                {"role": "user", "content": combined_message}
            ]

        # Call the model
        try:
            self.refresh_token_if_needed()
              # Common parameters for all models
            common_params = {
                "messages": messages,
                "temperature": self.temperature,
            }
            
            # Handle token parameter naming differences between models
            newer_models = ["o1-mini", "o3-mini", "o4-mini"]
            if self.model_version in newer_models:
                token_param = {"max_completion_tokens": max_tokens}
                token_key = "max_completion_tokens"
                
                # Add reasoning_effort parameter for o-series models
                if self.model_config.get("reasoning_effort"):
                    common_params["reasoning"] = {"effort": self.model_config["reasoning_effort"]}
                    if self.debug:
                        print(f"[Debug] Using reasoning_effort: {self.model_config['reasoning_effort']}")
            else:
                token_param = {"max_tokens": max_tokens}
                token_key = "max_tokens"
            
            # Combine parameters
            params = {**common_params, **token_param}
            
            if self.model_config.get("is_direct_api", False):
                # Direct API models (like DeepSeek)
                params["model"] = self.model_version
                response = self.client.chat.completions.create(**params)
            else:
                # Azure OpenAI models
                params["model"] = self.model_config["deployment_name"]
                response = self.client.chat.completions.create(**params)

            # Extract response content
            response_content = response.choices[0].message.content

            # Save the response to a file if specified
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(response_content)

            # Return response with metadata
            return {
                "response": response_content,
                "metadata": {
                    "model": self.model_version,
                    "temperature": self.temperature,
                    token_key: max_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            }

        except Exception as e:
            if self.debug:
                print(f"[Debug] Error during task execution: {str(e)}")
            raise RuntimeError(f"Error calling Azure OpenAI API: {str(e)}")

def main():
    # Dynamically get model choices from azure_models.py
    available_models = list(MODEL_CONFIGS.keys())
    
    parser = argparse.ArgumentParser(description="Azure GPT Task Runner")
    parser.add_argument('-task', type=str, help='The task to execute')
    parser.add_argument('-system', type=str, help='System message to provide context')
    parser.add_argument('-context', type=str, help='Additional context for the task')
    parser.add_argument('-outputfile', type=str, help='File path to save the response')
    parser.add_argument('-temperature', type=float, default=0.0, help='Temperature for model responses')
    parser.add_argument('-max_tokens', type=int, default=2000, help='Maximum number of tokens to generate')
    parser.add_argument('-debug', type=bool, default=False, help='Enable debug mode')
    parser.add_argument('-use_default_task', action='store_true', help='Use the default task')
    parser.add_argument('-chat', action='store_true', help='Start an interactive chat session')
    parser.add_argument('-model_version', type=str, default="gpt-4.1", choices=available_models, 
                        help=f'Model version to use. Choices: {", ".join(available_models)}')
    args = parser.parse_args()

    # Create a single InteractiveBrowserCredential instance
    credential = InteractiveBrowserCredential()
    
    try:
        # Pass credential to client constructor
        client = AzureGPTClient(
            temperature=args.temperature,
            debug=args.debug,
            model_version=args.model_version,
            credential=credential
        )
        
        system_message = args.system or DEFAULT_SYSTEM_MESSAGE.strip()
        
        task_requested = args.task or args.use_default_task
        
        initial_conversation = None
        task_result = None
        
        if task_requested:
            task = args.task if args.task else DEFAULT_TASK.strip()
            
            task_result = client.execute_task(
                task=task,
                system_message=system_message,
                context=args.context,
                output_file=args.outputfile,
                max_tokens=args.max_tokens
            )
            
            print("\nTask Response:")
            print("="*80)
            print(task_result["response"])
            print("="*80)
            
            if args.chat:
                initial_conversation = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": task + (f"\n\nContext:\n{args.context}" if args.context else "")},
                    {"role": "assistant", "content": task_result["response"]}
                ]
                
                print("\nStarting chat session with the task and response as context...")
        
        if args.chat:
            client.start_chat(
                system_message=system_message,
                initial_conversation=initial_conversation
            )
        elif not task_requested:
            print("Error: You must provide a task using -task or -use_default_task, or start a chat session using -chat")
            parser.print_help()
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()