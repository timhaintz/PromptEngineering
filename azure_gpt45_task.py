'''
DESCRIPTION
Azure GPT-4.5 Task Runner with Token Provider Authentication

This script connects to Azure OpenAI GPT-4.5 using interactive browser authentication.
It allows you to define tasks and send them to the GPT-4.5 model for execution.
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
python azure_gpt45_task.py -task "Explain quantum computing in simple terms."

# Output to file
python azure_gpt45_task.py -task "Explain quantum computing in simple terms." -outputfile quantum_explanation.txt

# Specify temperature
python azure_gpt45_task.py -task "Explain quantum computing in simple terms." -temperature 0.7

# Add system message
python azure_gpt45_task.py -task "Explain quantum computing in simple terms." -system "You are a quantum physics professor teaching undergraduates."

# Add task context
python azure_gpt45_task.py -task "Explain this code." -context "def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)"

# Debug mode
python azure_gpt45_task.py -task "Explain quantum computing in simple terms." -debug True

# Use the default task (set the DEFAULT_TASK below)
python azure_gpt45_task.py -use_default_task

# Start interactive chat mode
python azure_gpt45_task.py -chat

# Start interactive chat with a specific system message
python azure_gpt45_task.py -chat -system "You are a cybersecurity expert specializing in threat detection."

# Process a task first and then start a chat about the results
python azure_gpt45_task.py -task "Explain quantum computing" -chat
python azure_gpt45_task.py -task "Explain quantum computing" -system "You are a physics professor" -context "I'm new to physics" -chat
'''

from dotenv import load_dotenv
import argparse
import os
import json
import time
import sys
from datetime import datetime
from azure.identity import InteractiveBrowserCredential
from azure.core.credentials import TokenCredential
from openai import AzureOpenAI
from typing import Optional, Dict, Any, List, Union

# Load environment variables from the .env file
load_dotenv()

#############################################
# DEFAULT TASK - PASTE CONTENT BELOW HERE   #
#############################################
DEFAULT_TASK = """
Enter your task here. This allows you to easily paste large amounts of text
as a working pad. You can then run the script with -use_default_task flag.

Example:
Analyze the following log file and identify any security threats:

2023-04-06 12:34:56 ERROR [SecurityModule] Failed login attempt from IP 192.168.1.100
2023-04-06 12:35:10 ERROR [SecurityModule] Failed login attempt from IP 192.168.1.100
2023-04-06 12:35:25 ERROR [SecurityModule] Failed login attempt from IP 192.168.1.100
2023-04-06 12:35:40 WARNING [SecurityModule] Account lockout for user admin from IP 192.168.1.100
"""

#############################################
# DEFAULT SYSTEM MESSAGE                    #
#############################################
DEFAULT_SYSTEM_MESSAGE = """
You are a helpful AI assistant. Provide accurate, detailed, and concise responses.
"""

class AzureGPT45Client:
    """Client for interacting with Azure GPT-4.5 using token provider authentication."""

    def __init__(self, 
                 azure_endpoint: Optional[str] = None, 
                 deployment_name: Optional[str] = None, 
                 api_version: Optional[str] = None, 
                 temperature: float = 0.0,
                 debug: bool = False):
        """Initialize the Azure GPT-4.5 client.
        
        Args:
            azure_endpoint: The Azure OpenAI endpoint URL
            deployment_name: The deployment name for GPT-4.5 model
            api_version: The API version to use
            temperature: The temperature for model responses
            debug: Whether to enable debug mode
        """
        # Use provided values or environment variables
        self.azure_endpoint = azure_endpoint or os.getenv("AZUREVS_OPENAI_GPT45PREVIEW_ENDPOINT")
        if not self.azure_endpoint:
            raise ValueError("Azure endpoint not provided and AZUREVS_OPENAI_GPT45PREVIEW_ENDPOINT environment variable not found")
        
        self.deployment_name = deployment_name or os.getenv("AZUREVS_OPENAI_GPT45PREVIEW_MODEL")
        if not self.deployment_name:
            raise ValueError("Deployment name not provided and AZUREVS_OPENAI_GPT45PREVIEW_MODEL environment variable not found")
        
        self.api_version = api_version or os.getenv("AZUREVS_OPENAI_GPT45PREVIEW_API_VERSION") or "2023-12-01-preview"
        self.temperature = temperature
        self.debug = debug
        self.iso_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Initialize the token credential
        self.credential = InteractiveBrowserCredential()
        
        # Create the client with token authentication
        self.client = self._create_client()
        
        if self.debug:
            print(f"Azure Endpoint: {self.azure_endpoint}")
            print(f"Deployment Name: {self.deployment_name}")
            print(f"API Version: {self.api_version}")
            print(f"Temperature: {self.temperature}")
    
    def _create_client(self) -> AzureOpenAI:
        """Create the Azure OpenAI client with token authentication."""
        token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
        
        return AzureOpenAI(
            azure_ad_token=token.token,
            azure_endpoint=self.azure_endpoint, 
            api_version=self.api_version
        )
    
    def refresh_token_if_needed(self):
        """Refresh the Azure AD token if it's close to expiring or has expired"""
        # Recreate the client to get a fresh token
        self.client = self._create_client()
    
    def execute_task(self, 
                    task: str, 
                    system_message: Optional[str] = None, 
                    context: Optional[str] = None,
                    output_file: Optional[str] = None) -> Dict[str, Any]:
        """Execute a task using the GPT-4.5 model.
        
        Args:
            task: The task to execute
            system_message: Optional system message to provide context
            context: Optional additional context for the task
            output_file: Optional file path to save the response
            
        Returns:
            The model response
        """
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        else:
            messages.append({
                "role": "system", 
                "content": "You are a helpful AI assistant. Provide accurate, detailed, and concise responses."
            })
        
        # Combine task and context if provided
        user_content = task
        if context:
            user_content = f"{task}\n\nContext:\n{context}"
        
        messages.append({"role": "user", "content": user_content})
        
        if self.debug:
            print("Sending request with the following messages:")
            for msg in messages:
                print(f"{msg['role']}: {msg['content'][:50]}...")
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=self.temperature
            )
            
            # Extract the response content
            response_content = response.choices[0].message.content
            
            # Create a response dictionary
            result = {
                "task": task,
                "timestamp": self.iso_datetime,
                "response": response_content
            }
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                if self.debug:
                    print(f"Response saved to {output_file}")
            
            return result
        
        except Exception as e:
            error_message = f"Error calling Azure OpenAI API: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def start_chat(self, 
                   system_message: Optional[str] = None, 
                   initial_conversation: Optional[List[Dict[str, str]]] = None):
        """Start an interactive chat session that maintains conversation context.
        
        Args:
            system_message: Optional system message to initialize the chat
            initial_conversation: Optional initial conversation history
        """
        # Initialize conversation history
        if initial_conversation:
            conversation = initial_conversation
        else:
            conversation = []
            
            # Add system message if provided or not already in conversation
            if not any(msg.get("role") == "system" for msg in conversation):
                if system_message:
                    conversation.append({"role": "system", "content": system_message})
                else:
                    conversation.append({
                        "role": "system", 
                        "content": "You are a helpful AI assistant. Provide accurate, detailed, and concise responses."
                    })
        
        print(f"\n{'='*50}")
        print("Azure GPT-4.5 Chat Interface")
        print(f"{'='*50}")
        print("Type 'exit', 'quit', or 'bye' to end the conversation.")
        print("Type 'clear' to reset the conversation history.")
        print("Type 'debug' to toggle debug mode.")
        print("Type 'system: <message>' to change the system message.")
        print(f"{'='*50}\n")
        
        while True:
            try:
                user_input = input("\nYou: ")
                
                # Check for special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nEnding chat session. Goodbye!")
                    break
                    
                elif user_input.lower() == 'clear':
                    # Keep only the system message
                    system_content = next((msg["content"] for msg in conversation if msg["role"] == "system"), 
                                         "You are a helpful AI assistant. Provide accurate, detailed, and concise responses.")
                    conversation = [{"role": "system", "content": system_content}]
                    print("\nConversation history cleared.")
                    continue
                    
                elif user_input.lower() == 'debug':
                    self.debug = not self.debug
                    print(f"\nDebug mode {'enabled' if self.debug else 'disabled'}.")
                    continue
                
                elif user_input.lower().startswith('system:'):
                    new_system_message = user_input[7:].strip()
                    # Replace the system message if it exists
                    for i, msg in enumerate(conversation):
                        if msg["role"] == "system":
                            conversation[i] = {"role": "system", "content": new_system_message}
                            break
                    else:
                        # Insert system message at the beginning if it doesn't exist
                        conversation.insert(0, {"role": "system", "content": new_system_message})
                    print(f"\nSystem message updated.")
                    continue
                
                # Add user message to conversation
                conversation.append({"role": "user", "content": user_input})
                
                # Refresh token if needed
                self.refresh_token_if_needed()
                
                if self.debug:
                    print("\nSending request with conversation history:")
                    for idx, msg in enumerate(conversation):
                        content_preview = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                        print(f"{idx}. {msg['role']}: {content_preview}")
                
                try:
                    # Call the OpenAI API
                    response = self.client.chat.completions.create(
                        model=self.deployment_name,
                        messages=conversation,
                        temperature=self.temperature
                    )
                    
                    # Extract the response content
                    response_content = response.choices[0].message.content
                    
                    # Add the assistant's response to the conversation
                    conversation.append({"role": "assistant", "content": response_content})
                    
                    # Print the response
                    print(f"\nAssistant: {response_content}")
                    
                except Exception as e:
                    error_message = f"Error calling Azure OpenAI API: {str(e)}"
                    print(error_message)
                
            except KeyboardInterrupt:
                print("\n\nKeyboard interrupt detected. Ending chat session.")
                break
                
            except Exception as e:
                print(f"\nError: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Azure GPT-4.5 Task Runner")
    parser.add_argument('-task', type=str, help='The task to execute')
    parser.add_argument('-system', type=str, help='System message to provide context')
    parser.add_argument('-context', type=str, help='Additional context for the task')
    parser.add_argument('-outputfile', type=str, help='File path to save the response')
    parser.add_argument('-temperature', type=float, default=0.0, help='Temperature for model responses')
    parser.add_argument('-debug', type=bool, default=False, help='Enable debug mode')
    parser.add_argument('-use_default_task', action='store_true', help='Use the default task')
    parser.add_argument('-chat', action='store_true', help='Start an interactive chat session')
    args = parser.parse_args()
    
    # Initialize the client
    try:
        client = AzureGPT45Client(temperature=args.temperature, debug=args.debug)
        
        # Set system message
        system_message = args.system or DEFAULT_SYSTEM_MESSAGE.strip()
        
        # Check if a task was requested
        task_requested = args.task or args.use_default_task
        
        # Execute the task if requested
        initial_conversation = None
        task_result = None
        
        if task_requested:
            # Determine the task to execute
            task = args.task if args.task else DEFAULT_TASK.strip()
            
            # Execute the task
            task_result = client.execute_task(
                task=task,
                system_message=system_message,
                context=args.context,
                output_file=args.outputfile
            )
            
            # Print the response
            print("\nTask Response:")
            print("="*80)
            print(task_result["response"])
            print("="*80)
            
            # If chat is also requested, prepare the initial conversation
            if args.chat:
                initial_conversation = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": task + (f"\n\nContext:\n{args.context}" if args.context else "")},
                    {"role": "assistant", "content": task_result["response"]}
                ]
                
                print("\nStarting chat session with the task and response as context...")
        
        # Start chat if requested
        if args.chat:
            client.start_chat(
                system_message=system_message,
                initial_conversation=initial_conversation
            )
        elif not task_requested:
            # Neither task nor chat mode was specified
            print("Error: You must provide a task using -task or -use_default_task, or start a chat session using -chat")
            parser.print_help()
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()