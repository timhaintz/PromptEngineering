#!/usr/bin/env python3
"""
Test script for Azure Models
Tests GPT-4.1, Grok-3, and DeepSeek R1 models using azure_models.py

Usage:
    python test_models.py
    python test_models.py --model gpt-4.1
    python test_models.py --streaming
    python test_models.py --custom-prompt "Your custom test prompt here"
"""

import azure_models
import argparse
import sys
import time
from typing import List, Dict, Any


def test_model(model_name: str, prompt: str, use_streaming: bool = False) -> Dict[str, Any]:
    """Test a specific model with the given prompt."""
    print(f"\n{'='*60}")
    print(f"Testing {model_name}")
    print(f"{'='*60}")
    
    result = {
        "model": model_name,
        "success": False,
        "response": None,
        "error": None,
        "supports_streaming": False,
        "response_time": 0
    }
    
    try:
        start_time = time.time()
        
        # Get model client
        client = azure_models.get_model_client(model_name)
        result["supports_streaming"] = client.supports_streaming()
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # Test streaming if requested and supported
        if use_streaming and client.supports_streaming():
            print(f"📡 Streaming response from {model_name}:")
            print("Response: ", end="", flush=True)
            
            response = client.create_chat_completion(messages, stream=True)
            full_response = ""
            
            for chunk in response:
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # New line after streaming
            result["response"] = full_response
            
        else:
            # Non-streaming request
            if use_streaming and not client.supports_streaming():
                print(f"⚠️  Streaming requested but {model_name} doesn't support it. Using non-streaming.")
            
            response = client.create_chat_completion(messages)
            result["response"] = response.choices[0].message.content
            print(f"Response: {result['response']}")
        
        end_time = time.time()
        result["response_time"] = end_time - start_time
        result["success"] = True
        
        print(f"✅ {model_name} test completed successfully!")
        print(f"⏱️  Response time: {result['response_time']:.2f} seconds")
        print(f"📊 Supports streaming: {result['supports_streaming']}")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ {model_name} test failed: {e}")
    
    return result


def print_summary(results: List[Dict[str, Any]]):
    """Print a summary of all test results."""
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if successful_tests:
        print(f"\n✅ Successful tests:")
        for result in successful_tests:
            print(f"  - {result['model']} ({result['response_time']:.2f}s)")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for result in failed_tests:
            print(f"  - {result['model']}: {result['error']}")
    
    # Performance comparison
    if len(successful_tests) > 1:
        print(f"\n📊 Performance comparison:")
        sorted_results = sorted(successful_tests, key=lambda x: x['response_time'])
        for i, result in enumerate(sorted_results, 1):
            print(f"  {i}. {result['model']}: {result['response_time']:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Test Azure Models")
    parser.add_argument("--model", type=str, help="Test specific model only")
    parser.add_argument("--streaming", action="store_true", help="Test streaming responses")
    parser.add_argument("--custom-prompt", type=str, 
                       help="Custom prompt to use for testing")
    parser.add_argument("--list-models", action="store_true", 
                       help="List all available models")
    
    args = parser.parse_args()
    
    # List available models
    if args.list_models:
        print("Available models:")
        for model in azure_models.get_available_models():
            print(f"  - {model}")
        return
    
    # Default test prompt
    default_prompt = "Hello! Please respond with a short greeting and tell me which model you are."
    prompt = args.custom_prompt or default_prompt
    
    # Models to test
    models_to_test = ["gpt-4.1", "grok-3", "deepseek-r1"]
    
    if args.model:
        if args.model in models_to_test:
            models_to_test = [args.model]
        else:
            print(f"Error: Model '{args.model}' not in supported test models.")
            print(f"Supported models: {', '.join(models_to_test)}")
            return
    
    print(f"🧪 Testing {len(models_to_test)} model(s)")
    print(f"📝 Prompt: {prompt}")
    print(f"📡 Streaming: {args.streaming}")
    
    # Run tests
    results = []
    for model in models_to_test:
        result = test_model(model, prompt, args.streaming)
        results.append(result)
        
        # Add delay between tests to be nice to the APIs
        if len(models_to_test) > 1:
            time.sleep(1)
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
