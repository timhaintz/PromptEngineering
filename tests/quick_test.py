#!/usr/bin/env python3
"""
Quick test script for Azure Models
Simple one-liner tests for GPT-4.1, Grok-3, and DeepSeek R1

Usage examples:
    python quick_test.py
    python quick_test.py gpt-4.1
    python quick_test.py grok-3
    python quick_test.py deepseek-r1
"""

import azure_models
import sys


def quick_test(model_name: str, prompt: str = "Hello! Tell me which model you are in one sentence."):
    """Quick test of a model."""
    try:
        print(f"Testing {model_name}...")
        client = azure_models.get_model_client(model_name)
        messages = [{"role": "user", "content": prompt}]
        response = client.create_chat_completion(messages)
        print(f"✅ {model_name}: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ {model_name}: {e}")
        return False


def main():
    models = ["gpt-4.1", "grok-3", "deepseek-r1"]
    
    if len(sys.argv) > 1:
        model = sys.argv[1]
        if model in models:
            quick_test(model)
        else:
            print(f"Unknown model: {model}")
            print(f"Available models: {', '.join(models)}")
    else:
        print("Testing all models...")
        success_count = 0
        for model in models:
            if quick_test(model):
                success_count += 1
            print()
        
        print(f"Summary: {success_count}/{len(models)} models working")


if __name__ == "__main__":
    main()
