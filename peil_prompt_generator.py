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
#1. Start a chat session with the PEIL prompt generator
python peil_prompt_generator.py
#2. Start a chat session with the PEIL prompt generator. Continues until exit or quit is entered.
python peil_prompt_generator.py -chat_with_peil
#3. Start a chat session with the PEIL prompt generator and automatically evaluate the output with the judgement model
python peil_prompt_generator.py -chat_with_peil -chat_with_judgement
#4. Provide a one-off custom prompt
python peil_prompt_generator.py -prompt "Role: You are a cybersecurity expert. Provide Clear Context: The context for this prompt is cybersecurity. The model should focus on discussing the importance of cybersecurity measures in protecting sensitive data from cyber threats. Break Down Complex Questions: Break down the question 'How can organisations improve their cybersecurity posture?' into smaller, manageable parts such as 'What are the key components of a strong cybersecurity strategy?' and 'How can employee training enhance cybersecurity?' Provide Specific Instructions: Ensure that the response includes at least three key components of a strong cybersecurity strategy and provides examples of effective employee training programs. Define Conciseness: Limit the response to 200 words to ensure it is concise and to the point, avoiding unnecessary details. Prompting Techniques: Use the Chain-of-Thought (CoT) prompting technique to guide the model through a step-by-step reasoning process in discussing cybersecurity measures. State Desired Output: The desired output is a clear and concise explanation of how organisations can improve their cybersecurity posture, including key components of a strong strategy and examples of effective employee training programs. The output should be Markdown."
#5. Start an interactive session with the judgement model only
python peil_prompt_generator.py -chat_with_judgement


'''
import os
import openai
import json
import argparse
from dotenv import load_dotenv
from openai import AzureOpenAI
from datetime import datetime
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

model = os.getenv("AZUREVS_OPENAI_GPT4o_MODEL")
api_version = os.getenv("API_VERSION")
api_key = os.getenv("AZUREVS_OPENAI_KEY") 
azure_endpoint = os.getenv("AZUREVS_OPENAI_ENDPOINT")
iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
temperature = 0.0
r1_endpoint = os.getenv("AZUREVS_DEEPSEEK_R1_ENDPOINT")
r1_key = os.getenv("AZUREVS_DEEPSEEK_R1_KEY")

peil_chat_system_prompt_instructions = r'''
# INSTRUCTIONS
-You are a prompt generator for the PEIL project.
-Your task is to generate system prompts.
-Your output will be used in autonomous agents system prompts. Only provide the system prompt.
-You generate prompts to optimise the quality of output and performance of large language models. 
-Your goal is to generate prompts that are clear, concise, and effective in guiding the autonomous agents to produce accurate responses. 
-Your performance will be evaluated based on the relevance, coherence, and accuracy of the generated prompts.
-Do not add the {} variables to the prompt. Write full single string sentences to provide clear instructions and context.
-Use the PEIL template to structure your prompts effectively.
-Use the TECHNIQUES AND APPLICATIONS Markdown table to provide the best technique for the request. | Application | Prompting Technique | Add to PE | Summary from Paper |.
-Use the PE column of the table to implement the Prompting Technique.
-Only provide the prompt so it can be used in an automation system.
# END INSTRUCTIONS #
'''

peil_chat_system_prompt_peil_definition = r'''
# Prompt Engineering Instructional Language (PEIL)

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
# END PEIL #
'''

peil_chat_system_prompt_peil_techniques = r'''
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
# END Prompt Engineering Instructional Language (PEIL) #
'''

peil_chat_system_prompt_categories =r'''
# CATEGORIES & DEFINITIONS
| **Category**              | **Definition**                                                                                                                                                                                                                                                                                                                                 |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Argument**              | An argument refers to a structured process where a claim or viewpoint is presented and defended. This involves the model generating a response that not only states a position but also provides reasoning and evidence to support it. The quality of an argument can be measured by its clarity, coherence, and the strength of its supporting evidence. |
| **Assessment**            | Assessment involves a detailed evaluation of the model's response. It's not just about determining if the response is right or wrong, but also about understanding the quality of the response. This could include aspects like relevance to the prompt, completeness of the information, and the logical consistency of the response.                  |
| **Calculation**           | Calculation refers to the ability of the model to perform mathematical operations or computations based on the input prompt. This could range from simple arithmetic operations to more complex calculations involving multiple steps and variables. The accuracy of the calculation is a key factor in assessing the model's performance.               |
| **Categorising**          | Categorising involves the model sorting or arranging different inputs or outputs into classes or categories based on shared qualities or characteristics. This process helps in organising the data in a meaningful way and can aid in understanding patterns and relationships within the data.                                                   |
| **Classification**        | Classification is the task of predicting the class or category of an input based on predefined criteria. This involves the model analysing the input and assigning it to one of several predefined categories based on its characteristics.                                                                                                     |
| **Clustering**            | Clustering refers to the task of grouping similar inputs or outputs together based on their similarities. Unlike classification, clustering does not rely on predefined categories but instead identifies natural groupings within the data.                                                                                                    |
| **Comparison**            | Comparison involves the model examining two or more inputs or outputs and identifying their similarities and differences. This process can help in understanding the relationships between different inputs or outputs and can provide insights into their characteristics.                                                                    |
| **Context Control**       | Context control refers to the management of the information that the model has access to during the generation of the output. This could involve controlling the amount of information, the type of information, or the sequence in which the information is presented to the model.                                                           |
| **Contradiction**         | Contradiction is used to describe a situation where two or more statements, ideas, or actions are put together that oppose each other. If you say one thing and do another, that's a contradiction. They can't both be true at the same time. This concept is widely used in logic and mathematics to show that a particular proposition is false.   |
| **Cross Boundary**        | Cross Boundary involves pushing the AI model beyond its predefined operational or ethical limits. This process includes attempting to bypass safeguards or restrictions, such as jailbreaking. The effectiveness of a cross-boundary prompt is measured by its ability to challenge the boundaries of what the model is allowed to do.                  |
| **Decomposed Prompting**  | Decomposed prompting involves breaking down a complex prompt into simpler, manageable sub-prompts. This can make it easier for the model to understand and respond to the prompt, and can also help in controlling the structure and content of the model's output.                                                                             |
| **Error Identification**  | Error identification detects and identifies errors or mistakes in its output. This could involve identifying grammatical errors, factual inaccuracies, or logical inconsistencies in the response.                                                                                                                                               |
| **Hypothesise**           | Hypothesising involves making an educated guess or assumption about the outcome based on the input prompt. This requires the model to analyse the input, consider various possibilities, and predict the most likely outcome.                                                                                                                    |
| **Input Semantics**       | Input semantics refers to the meaning or interpretation of the input prompt. This involves the model understanding the intent of the prompt, the context in which it is presented, and the specific requirements or constraints that it implies.                                                                                                  |
| **Logical Reasoning**     | Logical reasoning uses logic and reasoning to generate the output based on the input prompt. This could involve deducing conclusions from given facts, making inferences based on patterns or trends, or applying rules or principles to solve problems.                                                                                         |
| **Output Customisation**  | Output customisation refers to the ability to modify or personalise the output based on specific requirements or preferences. This could involve controlling the length, style, or format of the output, or incorporating specific information or elements into the response.                                                                    |
| **Output Semantics**      | Output semantics refers to the meaning or interpretation of the output. This involves understanding the intent of the output, the context in which it is presented, and the implications or consequences of the information it contains.                                                                                                        |
| **Prediction**            | Prediction involves forecasting or estimating the outcome based on the input prompt. This requires the model to analyse the input, consider various factors or variables, and generate a response that anticipates future events or trends.                                                                                                      |
| **Prompt Improvement**    | Prompt improvement involves enhancing the quality or effectiveness of the input prompt to achieve a better output. This could involve refining the wording of the prompt, providing additional context or information, or adjusting the complexity or specificity of the prompt.                                                               |
| **Refactoring**           | Refactoring involves modifying the input prompt without changing its meaning. This can include rephrasing, rearranging, or simplifying the prompt to improve clarity and effectiveness. It may also involve breaking down complex prompts or providing examples to illustrate the desired outcome.                                               |
| **Requirements Elicitation** | Requirements elicitation is the gathering, understanding, and defining of the requirements or needs for a particular task or problem. This could involve identifying the goals or objectives of the task, understanding the constraints or limitations, and specifying the criteria for success.                                               |
| **Simulation**            | Simulation is imitating or replicating a real-world process or system. This could involve simulating operating systems, applications or any other complex process that can be modelled and analysed.                                                                                                                                            |
| **Summarising**           | Summarising involves the providing the model a brief overview or summary of the input or output. This could involve condensing a large amount of information into a few key points, highlighting the most important elements, or providing a concise synopsis of the content.                                                                    |
| **Translation**           | Translation converts the input from one language to another. This requires the model to understand the semantics and syntax of both languages, and to accurately convey the meaning and intent of the original content in the target language.                                                                                                  |
# END CATEGORIES & DEFINITIONS
'''

judgement_system_prompt = r''' 
#INSTRUCTIONS
You are an AI language model evaluator and judge. Your responsibility is to assess the provided Prompt Engineering Instructional Language (PEIL) prompt for quality and accuracy. 
Your objective is to generate a concise judgment with feedback and provide a rating out of 100 to enhance the effectiveness of prompts for large language models.
The prompt you will evaluate is intended to guide AI models in generating effective and accurate responses. 
It is crucial to focus on how well the prompt communicates instructions and whether it enables the AI to produce the desired outcomes.
Analyse the prompt based on the following weighted criteria:
1. **Clarity and Coherence (30%)**: Is the language clear and unambiguous? Does the prompt have a logical flow that is easy to follow? 
2. **Completeness and Comprehensiveness (25%)**: Does the prompt cover all necessary aspects of the task? Are there any important elements or instructions missing? 
3. **Relevance and Applicability (20%)**: How well does the prompt align with its intended purpose? Can it be effectively applied in practical scenarios? 
4. **Creativity and Originality (15%)**: Does the prompt introduce novel ideas or approaches? How original is the content compared to existing prompts? 
5. **Technical Accuracy (10%)**: Are all technical details and instructions accurate? Is the information presented correctly? 
For each criterion, provide specific feedback, highlighting strengths and areas for improvement. 
Make sure your feedback is constructive and actionable, offering clear suggestions on how to enhance the prompt. 
Keep your evaluation concise and focused. While thorough, avoid unnecessary elaboration to ensure your assessment is clear and to the point. 
Your final output should include a concise overall judgment of the prompt's quality and accuracy; detailed feedback on each of the five criteria, including specific strengths and areas for improvement;
an overall rating out of 100, calculated based on the weighted criteria; and a brief summary that encapsulates your assessment. 
By following these instructions, you will provide a comprehensive evaluation that helps improve the effectiveness of prompt engineering for large language models.
#END INSTRUCTIONS
'''
# Using the GPT-4o model
def chat_with_peil(messages):
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        response = client.chat.completions.create(
            model=model,  # model = "deployment_name"
            messages=[
                {"role": "system", "content": peil_chat_system_prompt_instructions + peil_chat_system_prompt_peil_definition + peil_chat_system_prompt_peil_techniques + peil_chat_system_prompt_categories}
            ] + messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Using the DeepSeek R1 reasoning
def chat_with_judgement(messages):
    try:
        client = ChatCompletionsClient(
            endpoint=r1_endpoint,
            credential=AzureKeyCredential(r1_key)
        )
        payload = {
            "messages": [
                {"role": "user", "content": judgement_system_prompt + peil_chat_system_prompt_peil_definition + peil_chat_system_prompt_categories}
            ] + messages,
            "max_tokens": 4096
        }
        response = client.complete(payload)
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def judge_response(response):
    """
    Judges the LLM response by calling a different model (via chat_with_judgement).

    :param response: The response from the previous LLM call.
    :return: Judgement result as a string.
    """
    judgement_prompt = (
        "Please evaluate the quality and accuracy of the following response. "
        "Give a concise judgement with constructive feedback and a rating:\n\n"
        f"{response}"
    )
    judgement_result = chat_with_judgement([{"role": "user", "content": judgement_prompt}])
    return judgement_result

def main():
    parser = argparse.ArgumentParser(description="PEIL prompt generator")
    parser.add_argument("-chat_with_peil", action="store_true", help="Start session with chat_with_peil - Default")
    parser.add_argument("-chat_with_judgement", action="store_true", help="Automatically evaluate output with the judgement model")
    parser.add_argument("-prompt", type=str, default="", help="Provide a one-off custom prompt. Non-interactive mode. Parse text in quotes in the command line.")
    args = parser.parse_args()

    # One-off prompt from command-line arguments
    if args.prompt:
        user_prompt = args.prompt
        peil_response = chat_with_peil([{"role": "user", "content": user_prompt}])
        if peil_response:
            print("\nResponse from chat_with_peil:")
            print(peil_response)
        else:
            print("No response from chat_with_peil.")
        
        if args.chat_with_judgement and peil_response:
            judgement_response = judge_response(peil_response)
            if judgement_response:
                print("\nJudgement result:")
                print(judgement_response)
            else:
                print("No judgement received.")
        return

    # If interactive session with judgement model only
    if args.chat_with_judgement and not args.chat_with_peil:
        print("Starting interactive session with the judgement model.")
        while True:
            user_prompt = input("Enter your prompt for chat_with_judgement (or type 'exit' to quit): ")
            if user_prompt.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break
            judgement_response = chat_with_judgement([{"role": "user", "content": user_prompt}])
            if judgement_response:
                print("\nResponse from chat_with_judgement:")
                print(judgement_response)
            else:
                print("No response from chat_with_judgement.")
            print()
        return

    # Default interactive loop using chat_with_peil (with optional auto judgement if selected)
    # Wrap the chat session in an outer loop to re-display the initial instructions when a session ends.
    while True:        
        # Inner loop: one full interactive session.
        while True:
            print("\nStart chatting with the Prompt Engineering Instructional Language (PEIL).")
            print("Press Enter to use the default examples or type 'exit' or 'quit' to stop the conversation.")
            role = input("Role (e.g., 'You are a cybersecurity expert.'): ") or "You are a cybersecurity expert."
            if role.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break

            print()  # New line for readability

            provide_clear_context = input(
                "Provide Clear Context (e.g., 'The context for this prompt is cybersecurity...'): "
            ) or "The context for this prompt is cybersecurity. The model should focus on discussing the importance of cybersecurity measures in protecting sensitive data from cyber threats."
            if provide_clear_context.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break

            print()  # New line for readability

            break_down_complex_questions = input(
                "Break Down Complex Questions (e.g., 'Break down the question \"How can organisations improve their cybersecurity posture?\"...'): "
            ) or "Break down the question 'How can organisations improve their cybersecurity posture?' into smaller, manageable parts such as 'What are the key components of a strong cybersecurity strategy?' and 'How can employee training enhance cybersecurity?'"
            if break_down_complex_questions.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break

            print()  # New line for readability
            
            provide_specific_instructions = input(
                "Provide Specific Instructions (e.g., 'Ensure that the response includes at least three key components...'): "
            ) or "Ensure that the response includes at least three key components of a strong cybersecurity strategy and provides examples of effective employee training programs."
            if provide_specific_instructions.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break

            print()  # New line for readability

            define_conciseness = input(
                "Define Conciseness (e.g., 'Limit the response to 200 words...'): "
            ) or "Limit the response to 200 words to ensure it is concise and to the point, avoiding unnecessary details."
            if define_conciseness.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break

            print()  # New line for readability

            prompting_techniques = input(
                "Prompting Techniques From Paper (e.g., 'Use the Chain-of-Thought (CoT) prompting technique...'): "
            ) or "Use the Chain-of-Thought (CoT) prompting technique to guide the model through a step-by-step reasoning process in discussing cybersecurity measures."
            if prompting_techniques.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break

            print()  # New line for readability

            state_desired_output = input(
                "State Desired Output (e.g., 'The desired output is a clear and concise explanation...'): "
            ) or "The desired output is a clear and concise explanation of how organisations can improve their cybersecurity posture, including key components of a strong strategy and examples of effective employee training programs. The output should be Markdown."
            if state_desired_output.strip().lower() in {"exit", "quit"}:
                print("Conversation ended.")
                break

            print()  # New line for readability

            user_input = (
                f"Role: {role}\n"
                f"Provide Clear Context: {provide_clear_context}\n"
                f"Break Down Complex Questions: {break_down_complex_questions}\n"
                f"Provide Specific Instructions: {provide_specific_instructions}\n"
                f"Define Conciseness: {define_conciseness}\n"
                f"Prompting Techniques: {prompting_techniques}\n"
                f"State Desired Output: {state_desired_output}\n"
            )
            peil_response = chat_with_peil([{"role": "user", "content": user_input}])
            if peil_response:
                print("\nResponse from chat_with_peil:")
                print(peil_response)
            else:
                print("No response received from chat_with_peil.")

            if args.chat_with_judgement and peil_response:
                judgement_response = judge_response(peil_response)
                if judgement_response:
                    print("\nJudgement result:")
                    print(judgement_response)
                else:
                    print("No judgement received.")
            print()  # New line for readability between interactions

        # End of the inner session. Now re-display the banner and ask if the user wants to start a new session.
        restart = input("Would you like to start a new chat session? (y/n): ").strip().lower()
        if restart not in {"y", "yes"}:
            print("Exiting interactive mode.")
            break

if __name__ == "__main__":
    main()