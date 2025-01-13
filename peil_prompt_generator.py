'''
DESCRIPTION
Generate prompts for the PEIL project
NOTES
Leveraging Azure OpenAI API to generate prompts for the PEIL project
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  20250113
LINKS
EXAMPLE USAGE
python peil_prompt_generator.py -prompt "Enter requirements here"
'''
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

system_prompt = '''
VARIABLES
Prompt Engineering Instructional Language (PEIL) - A set of guidelines and techniques to optimise the performance of large language models by providing tailored prompts.
	{ProvideClearContext} {StateDesiredOutput} {BreakDownComplexQuestions} {ProvideSpecificInstructions} {DefineConciseness} {PromptingTechniquesFromPaper}
	
	{PEIL - Description}
	
	{
	{ProvideClearContext}: This allows the model to answer with precise understanding and tailored responses, optimizing the relevance and accuracy of the outcome.    
	
	{StateDesiredOutput}: This helps the model understand the specific information or response it needs to generate.    
	
	{BreakDownComplexQuestions}: This helps the model focus on individual aspects of the topic and generate more accurate and detailed responses.   
	
	{ProvideSpecificInstructions}: This ensures that the model understands any constraints or requirements in generating the output.    
	
	{DefineConciseness}: Prompt the model to generate concise and relevant responses by specifying any word limits or constraints. This helps prevent the model from generating unnecessarily lengthy or irrelevant answers.    
	
	{PromptingTechniquesFromPaper}: This variable includes techniques such as Chain of Thought and Tree of Thought, as outlined in the paper [1](https://arxiv.org/abs/2402.07927).
	}
	
	{PEIL - Example implementation}
	
	{ProvideClearContext}: "You are an AI assistant helping a user with their homework."
	
	{StateDesiredOutput}: "Generate a summary of the given text."
	
	{BreakDownComplexQuestions}: "First, identify the main points. Then, explain each point in detail."
	
	{ProvideSpecificInstructions}: "Use bullet points for clarity."
	
	{DefineConciseness}: "Keep the summary under 150 words."
	
	{PromptingTechniquesFromPaper}: "Apply the techniques from the paper to ensure the response is accurate and relevant. Chain of Thought for example (explain the steps you took....)" 

## A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications
### https://arxiv.org/abs/2402.07927

| Application | Prompting Technique | Add to PE | Summary from Paper |
|-------------|----------------------|---------|---------|
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
'''

def chat_with_peil(messages):
    # Example usage of the system prompt
    openai.api_type = "azure"
    openai.api_key = os.getenv("AZUREVS_OPENAI_KEY")
    openai.api_base = os.getenv("AZUREVS_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("API_VERSION")
    
    response = openai.ChatCompletion.create(
        engine=os.getenv("AZUREVS_OPENAI_GPT4o_MODEL"),
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt}
        ] + messages
    )
    return response.choices[0].message["content"]

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break
        response = chat_with_peil([
            {"role": "user", "content": user_input}
        ])
        print("Assistant:", response)