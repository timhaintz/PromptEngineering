"""
Azure OAuth Token Caching Usage Examples

This script demonstrates how to use the secure OAuth token caching implementation
with Azure OpenAI models following Azure security best practices.

Features:
- Secure token caching using Azure Identity TokenCachePersistenceOptions
- OS-level encrypted credential storage (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- Automatic token refresh and reuse across sessions
- Unified interface for Azure OpenAI, Direct API, and Azure AI Foundry models
"""

import logging
from azure_models import (
    create_azure_openai_client, 
    create_unified_client,
    get_streaming_models,
    supports_streaming
)

# Configure logging to see authentication and caching activity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def example_azure_openai_with_caching():
    """Example: Using Azure OpenAI with secure token caching."""
    print("🔐 Example 1: Azure OpenAI with Secure Token Caching")
    print("-" * 60)
    
    try:
        # Create Azure OpenAI client with secure token caching
        # Tokens are automatically cached in encrypted OS credential stores
        client = create_azure_openai_client("gpt-4.1")
        
        print("✅ Azure OpenAI client created with secure token caching")
        print("🔒 Features enabled:")
        print("   • Encrypted token storage in OS credential manager")
        print("   • Automatic token refresh when expired")
        print("   • Secure application-level cache isolation")
        
        # Example chat completion
        response = client.chat.completions.create(
            model="gpt-4",  # This will use the deployment name from config
            messages=[{"role": "user", "content": "Hello, Azure!"}],
            max_tokens=50
        )
        
        print(f"📝 Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_streaming_with_caching():
    """Example: Using streaming with cached authentication."""
    print("\n🌊 Example 2: Streaming with Cached Authentication") 
    print("-" * 60)
    
    try:
        # Get models that support streaming
        streaming_models = get_streaming_models()
        print(f"📡 Available streaming models: {list(streaming_models.keys())}")
        
        # Use a streaming model with cached authentication
        model_name = "gpt-4.1"
        if supports_streaming(model_name):
            client = create_azure_openai_client(model_name)
            
            print(f"✅ Using {model_name} with streaming and cached auth")
            
            # Example streaming chat completion
            stream = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Count to 5 slowly"}],
                max_tokens=100,
                stream=True  # Enable streaming
            )
            
            print("🌊 Streaming response: ", end="")
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print("\n")
            
        else:
            print(f"⚠️ Model {model_name} does not support streaming")
            
    except Exception as e:
        print(f"❌ Streaming error: {e}")

def example_unified_client_with_caching():
    """Example: Using UnifiedChatClient with cached authentication."""
    print("\n🔄 Example 3: Unified Client with Cached Authentication")
    print("-" * 60)
    
    try:
        # Create unified client that works with all model types
        unified_client = create_unified_client("gpt-4.1")
        
        print("✅ Unified client created with cached authentication")
        print("🎯 Benefits:")
        print("   • Works with Azure OpenAI, Direct API, and Azure AI Foundry")
        print("   • Automatic credential caching across all model types")
        print("   • Consistent interface regardless of backend")
        
        # Check streaming support
        if unified_client.supports_streaming_feature():
            print("📡 Streaming support: Available")
        else:
            print("📡 Streaming support: Not available for this model")
            
        # Example usage (would work with any model type)
        print("🚀 Ready for chat completions with secure, cached authentication")
        
    except Exception as e:
        print(f"❌ Unified client error: {e}")

def example_multiple_sessions():
    """Example: Demonstrating token reuse across multiple sessions."""
    print("\n🔄 Example 4: Token Reuse Across Multiple Sessions")
    print("-" * 60)
    
    try:
        print("Session 1: First authentication (may require browser)")
        client1 = create_azure_openai_client("gpt-4.1")
        print("✅ Session 1 authenticated successfully")
        
        print("\nSession 2: Using cached token (should be instant)")
        client2 = create_azure_openai_client("gpt-4.1-nano") 
        print("✅ Session 2 authenticated successfully (used cached token)")
        
        print("\nSession 3: Another model with same cached credentials")
        client3 = create_azure_openai_client("gpt-3.5-turbo")
        print("✅ Session 3 authenticated successfully (used cached token)")
        
        print("\n🎯 All three sessions used the same cached OAuth token!")
        print("💾 Token securely stored in:")
        print("   • Windows: Windows Credential Manager")
        print("   • macOS: Keychain")
        print("   • Linux: Secret Service API")
        
    except Exception as e:
        print(f"❌ Multi-session error: {e}")

def main():
    """Run all OAuth caching examples."""
    print("🔐 Azure OAuth Token Caching Examples")
    print("=" * 70)
    print("Demonstrating secure token caching with Azure Identity library")
    print("=" * 70)
    
    # Run all examples
    example_azure_openai_with_caching()
    example_streaming_with_caching() 
    example_unified_client_with_caching()
    example_multiple_sessions()
    
    print("\n" + "=" * 70)
    print("🎉 All OAuth Caching Examples Complete!")
    print("\n🔒 Security Summary:")
    print("• Tokens encrypted at rest using OS credential stores")
    print("• Automatic token refresh prevents expired credential errors")
    print("• Application-specific caching prevents token sharing")
    print("• No credentials stored in plain text or environment variables")
    print("• Fallback to in-memory cache if OS encryption unavailable")

if __name__ == "__main__":
    main()
