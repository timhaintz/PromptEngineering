'''
DESCRIPTION
Azure OpenAI Models Configuration Module

This module provides standardized access to Azure OpenAI models and endpoints.
It supports both direct API usage and AutoGen integration following Azure best practices.

Version:        2.0
Author:         Tim Haintz
Creation Date:  20250419
Updated:        20250707

LINKS
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity
https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
https://learn.microsoft.com/en-us/azure/ai-services/authentication-identity
'''

import os
import os
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any, List, Union, Iterator, Tuple, cast
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions
from azure.core.exceptions import AzureError
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
from autogen_core.models import ModelFamily
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ModelType(Enum):
    """Enum for different model types."""
    AZURE_OPENAI = "azure_openai"
    DIRECT_API = "direct_api"
    AZURE_FOUNDRY = "azure_foundry"


class AuthType(Enum):
    """Enum for authentication types."""
    MANAGED_IDENTITY = "managed_identity"
    API_KEY = "api_key"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    model_type: ModelType
    auth_type: AuthType
    endpoint_env: str
    model_env: Optional[str] = None
    api_version_env: Optional[str] = None
    key_env: Optional[str] = None
    default_api_version: str = "2024-10-21"
    token_param_name: str = "max_tokens"
    default_temperature: Optional[float] = 0.7
    min_temperature: Optional[float] = 0.0
    max_temperature: Optional[float] = 2.0
    max_tokens_limit: int = 4096
    reasoning_effort: Optional[str] = None
    supported_features: Optional[List[str]] = None
    supports_system_role: bool = True
    supports_streaming: bool = False
    model_info: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Post-initialization to set default values."""
        if self.supported_features is None:
            self.supported_features = ["chat", "completion"]


class AzureCredentialManager:
    """Manages Azure credentials with secure token caching."""
    
    _credential_cache: Dict[str, InteractiveBrowserCredential] = {}
    
    @classmethod
    def get_credential(cls, cache_name: str = "prompt_engineering_azure_cache") -> InteractiveBrowserCredential:
        """
        Get Azure credential with secure token caching following Azure best practices.
        
        Features:
        - Uses Azure Identity's built-in TokenCachePersistenceOptions for secure token storage
        - Encrypted storage via OS credential stores
        - Automatic token refresh and reuse across sessions
        - Secure application-level cache isolation
        
        Args:
            cache_name: Unique cache name for this application
            
        Returns:
            InteractiveBrowserCredential with secure token caching enabled
        """
        if cache_name in cls._credential_cache:
            return cls._credential_cache[cache_name]
        
        try:
            # Configure persistent token cache with Azure security best practices
            cache_options = TokenCachePersistenceOptions(
                name=cache_name,
                allow_unencrypted_storage=False  # Force encrypted storage only
            )
            
            logger.info("Creating Azure credential with encrypted token caching")
            
            # Create credential with secure caching enabled
            credential = InteractiveBrowserCredential(
                cache_persistence_options=cache_options,
                timeout=60  # 60 second timeout for browser authentication
            )
            
            cls._credential_cache[cache_name] = credential
            logger.info("Azure credential created with secure token caching enabled")
            return credential
            
        except Exception as e:
            logger.warning(f"Failed to create credential with persistent cache: {e}")
            logger.info("Falling back to in-memory token cache")
            
            # Fallback to in-memory cache if persistent cache fails
            credential = InteractiveBrowserCredential(timeout=60)
            cls._credential_cache[cache_name] = credential
            return credential


class ModelRegistry:
    """Registry for all model configurations."""
    
    _models: Dict[str, ModelConfig] = {}
    
    @classmethod
    def register_models(cls):
        """Register all model configurations."""
        # Azure OpenAI Models
        cls._register_azure_openai_models()
        
        # Direct API Models (DeepSeek)
        cls._register_direct_api_models()
        
        # Azure AI Foundry Models (Grok)
        cls._register_azure_foundry_models()
    
    @classmethod
    def _register_azure_openai_models(cls):
        """Register Azure OpenAI models."""
        azure_models = [
            ModelConfig(
                name="gpt-4.1",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
                model_env="AZUREVSEASTUS2_OPENAI_GPT41_MODEL",
                api_version_env="AZUREVSEASTUS2_OPENAI_GPT41_API_VERSION",
                default_api_version="2024-02-15-preview",
                default_temperature=0.2,
                max_tokens_limit=1000000,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="gpt-5",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
                model_env="AZUREVSEASTUS2_OPENAI_GPT5_MODEL",
                api_version_env="AZUREVSEASTUS2_OPENAI_GPT5_API_VERSION",
                default_api_version="2024-12-01-preview",
                token_param_name="max_completion_tokens",
                default_temperature=0.2,
                max_tokens_limit=270000,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="gpt-4.1-nano",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
                model_env="AZUREVSEASTUS2_OPENAI_GPT41_nano_MODEL",
                api_version_env="AZUREVSEASTUS2_OPENAI_GPT41_nano_API_VERSION",
                default_api_version="2025-01-01-preview",
                token_param_name="max_completion_tokens",
                default_temperature=0.2,
                max_tokens_limit=1000000,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="gpt-4.5-preview",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVS_OPENAI_GPT45PREVIEW_ENDPOINT",
                model_env="AZUREVS_OPENAI_GPT45PREVIEW_MODEL",
                api_version_env="AZUREVS_OPENAI_GPT45PREVIEW_API_VERSION",
                default_api_version="2023-12-01-preview",
                max_tokens_limit=128000,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="gpt-35-turbo",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVS_OPENAI_ENDPOINT",
                model_env="AZUREVS_OPENAI_MODEL",
                api_version_env="API_VERSION",
                default_api_version="2024-10-21",
                max_tokens_limit=16000,
                supported_features=["chat", "completion", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="gpt-4o",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVS_OPENAI_ENDPOINT",
                model_env="AZUREVS_OPENAI_GPT4o_MODEL",
                api_version_env="API_VERSION",
                default_api_version="2024-10-21",
                max_tokens_limit=128000,
                supported_features=["chat", "completion", "function_calling", "vision", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="o1-mini",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVS_OPENAI_ENDPOINT",
                model_env="AZUREVS_OPENAI_o1mini_MODEL",
                api_version_env="API_VERSION_o1mini",
                default_api_version="2025-01-01-preview",
                token_param_name="max_completion_tokens",
                default_temperature=1.0,
                min_temperature=1.0,
                max_temperature=1.0,
                reasoning_effort="high",
                supported_features=["chat", "completion", "streaming"],
                supports_system_role=False,
                supports_streaming=True
            ),
            ModelConfig(
                name="o3-mini",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVS_OPENAI_ENDPOINT",
                model_env="AZUREVS_OPENAI_o3mini_MODEL",
                api_version_env="API_VERSION_o3mini",
                default_api_version="2025-01-01-preview",
                token_param_name="max_completion_tokens",
                default_temperature=1.0,
                min_temperature=1.0,
                max_temperature=1.0,
                reasoning_effort="high",
                supported_features=["chat", "completion", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="o4-mini",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVSEASTUS2_OPENAI_ENDPOINT",
                model_env="AZUREVSEASTUS2_OPENAI_o4mini_MODEL",
                api_version_env="AZUREVSEASTUS2_OPENAI_o4mini_API_VERSION",
                default_api_version="2025-01-01-preview",
                token_param_name="max_completion_tokens",
                default_temperature=1.0,
                min_temperature=1.0,
                max_temperature=1.0,
                reasoning_effort="high",
                supported_features=["chat", "completion", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="vision",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVSAUSEAST_OPENAI_ENDPOINT",
                model_env="AZUREVSAUSEAST_OPENAI_VISION_MODEL",
                api_version_env="API_VERSION",
                default_api_version="2024-10-21",
                max_tokens_limit=128000,
                supported_features=["vision", "chat", "streaming"],
                supports_streaming=True
            ),
            ModelConfig(
                name="embedding-2",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVS_OPENAI_ENDPOINT",
                model_env="AZUREVS_OPENAI_EMBEDDING2_MODEL",
                api_version_env="API_VERSION",
                default_api_version="2024-10-21",
                default_temperature=None,
                min_temperature=None,
                max_temperature=None,
                max_tokens_limit=8191,
                supported_features=["embedding"]
            ),
            ModelConfig(
                name="embedding-3",
                model_type=ModelType.AZURE_OPENAI,
                auth_type=AuthType.MANAGED_IDENTITY,
                endpoint_env="AZUREVS_OPENAI_ENDPOINT",
                model_env="AZUREVS_OPENAI_EMBEDDING3_MODEL",
                api_version_env="API_VERSION",
                default_api_version="2024-10-21",
                default_temperature=None,
                min_temperature=None,
                max_temperature=None,
                max_tokens_limit=8191,
                supported_features=["embedding"]
            )
        ]
        
        for model in azure_models:
            cls._models[model.name] = model
    
    @classmethod
    def _register_direct_api_models(cls):
        """Register Direct API models (DeepSeek)."""
        direct_models = [
            ModelConfig(
                name="deepseek-r1",
                model_type=ModelType.DIRECT_API,
                auth_type=AuthType.API_KEY,
                endpoint_env="AZUREVS_DEEPSEEK_R1_ENDPOINT",
                key_env="AZUREVS_DEEPSEEK_R1_KEY",
                max_tokens_limit=8192,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True,
                model_info={
                    "vision": False,
                    "family": ModelFamily.R1,
                    "function_calling": True,
                    "json_output": True,
                    "structured_output": True,
                }
            ),
            ModelConfig(
                name="deepseek-v3",
                model_type=ModelType.DIRECT_API,
                auth_type=AuthType.API_KEY,
                endpoint_env="AZUREVS_DEEPSEEK_V3_ENDPOINT",
                key_env="AZUREVS_DEEPSEEK_V3_KEY",
                max_tokens_limit=8192,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True,
                model_info={
                    "vision": False,
                    "family": "unknown",
                    "function_calling": True,
                    "json_output": True,
                    "structured_output": True,
                }
            ),
            ModelConfig(
                name="deepseek-v3-0324",
                model_type=ModelType.DIRECT_API,
                auth_type=AuthType.API_KEY,
                endpoint_env="AZUREVS_DEEPSEEK_V3_ENDPOINT",
                key_env="AZUREVS_DEEPSEEK_V3_KEY",
                max_tokens_limit=8192,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True,
                model_info={
                    "vision": False,
                    "family": "unknown",
                    "function_calling": True,
                    "json_output": True,
                    "structured_output": True,
                }
            )
        ]
        
        for model in direct_models:
            cls._models[model.name] = model
    
    @classmethod
    def _register_azure_foundry_models(cls):
        """Register Azure AI Foundry models (Grok)."""
        foundry_models = [
            ModelConfig(
                name="grok-3",
                model_type=ModelType.AZURE_FOUNDRY,
                auth_type=AuthType.API_KEY,
                endpoint_env="AZUREVSEASTUS2_GROK3_ENDPOINT",
                model_env="AZUREVSEASTUS2_GROK3_MODEL",
                api_version_env="AZUREVSEASTUS2_GROK3_API_VERSION",
                key_env="AZUREVSEASTUS2_GROK3_KEY",
                default_api_version="2024-05-01-preview",
                token_param_name="max_completion_tokens",
                default_temperature=1.0,
                max_tokens_limit=130000,
                supported_features=["chat", "completion", "function_calling", "streaming"],
                supports_streaming=True,
                model_info={
                    "vision": False,
                    "family": "grok",
                    "function_calling": True,
                    "json_output": True,
                    "structured_output": True,
                }
            )
        ]
        
        for model in foundry_models:
            cls._models[model.name] = model
    
    @classmethod
    def get_model(cls, model_name: str) -> ModelConfig:
        """Get a model configuration by name."""
        if not cls._models:
            cls.register_models()
        
        if model_name not in cls._models:
            raise ValueError(f"Unsupported model: {model_name}. Available models: {list(cls._models.keys())}")
        
        return cls._models[model_name]
    
    @classmethod
    def get_all_models(cls) -> Dict[str, ModelConfig]:
        """Get all registered models."""
        if not cls._models:
            cls.register_models()
        return cls._models.copy()
    
    @classmethod
    def get_streaming_models(cls) -> List[str]:
        """Get all models that support streaming."""
        if not cls._models:
            cls.register_models()
        return [name for name, config in cls._models.items() if config.supports_streaming]


class BaseModelClient(ABC):
    """Abstract base class for model clients."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the specific client."""
        pass
    
    @abstractmethod
    def create_chat_completion(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Any:
        """Create a chat completion."""
        pass
    
    def supports_streaming(self) -> bool:
        """Check if the model supports streaming."""
        return self.config.supports_streaming


class AzureOpenAIClient(BaseModelClient):
    """Client for Azure OpenAI models using managed identity."""
    
    def _initialize_client(self):
        """Initialize Azure OpenAI client with managed identity and automatic token refresh."""
        try:
            endpoint = os.getenv(self.config.endpoint_env)
            if not endpoint:
                raise ValueError(f"Environment variable {self.config.endpoint_env} not set")
            
            # Get API version
            api_version = (
                os.getenv(self.config.api_version_env) if self.config.api_version_env 
                else self.config.default_api_version
            )
            
            # Get Azure credential with secure token caching - this handles automatic refresh
            self.credential = AzureCredentialManager.get_credential()
            
            # Create token provider function for automatic refresh
            def token_provider():
                return self.credential.get_token("https://cognitiveservices.azure.com/.default").token
            
            # Initialize client with token provider for automatic refresh
            self.client = AzureOpenAI(
                azure_ad_token_provider=token_provider,
                azure_endpoint=endpoint,
                api_version=api_version
            )
            
            logger.info(f"Azure OpenAI client initialized for {self.config.name} with automatic token refresh")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client for {self.config.name}: {e}")
            raise
    
    def create_chat_completion(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Any:
        """Create a chat completion using Azure OpenAI."""
        try:
            # Get deployment name from environment
            if not self.config.model_env:
                raise ValueError("Model environment variable not configured for this Azure OpenAI model")
            deployment_name = os.getenv(cast(str, self.config.model_env))
            if not deployment_name:
                raise ValueError(f"Environment variable {self.config.model_env} not set")
            
            # Validate streaming request
            if stream and not self.config.supports_streaming:
                logger.warning(f"Streaming requested but {self.config.name} doesn't support it. Falling back to non-streaming.")
                stream = False
            
            # Build parameters
            params = {
                "model": deployment_name,
                "messages": messages,
                "stream": stream,
                **kwargs
            }
            
            # Add temperature if supported
            if self.config.default_temperature is not None:
                params.setdefault("temperature", self.config.default_temperature)
            
            # Add reasoning effort for o-series models
            if self.config.reasoning_effort:
                params["reasoning_effort"] = self.config.reasoning_effort
            
            response = self.client.chat.completions.create(**params)
            
            if stream:
                return self._wrap_streaming_response(response)
            return response
            
        except Exception as e:
            logger.error(f"Error creating chat completion for {self.config.name}: {e}")
            raise
    
    def _wrap_streaming_response(self, response):
        """Wrap streaming response for consistent interface."""
        class StreamingWrapper:
            def __init__(self, openai_stream):
                self.openai_stream = openai_stream
                self.content = ""
                
            def __iter__(self):
                for chunk in self.openai_stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            chunk_content = delta.content
                            self.content += chunk_content
                            yield chunk_content
            
            @property
            def choices(self):
                return [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': self.content
                    })()
                })()]
        
        return StreamingWrapper(response)


class DirectAPIClient(BaseModelClient):
    """Client for direct API models (DeepSeek)."""
    
    def _initialize_client(self):
        """Initialize direct API client."""
        try:
            base_url = os.getenv(self.config.endpoint_env)
            api_key = os.getenv(self.config.key_env or "")
            
            if not base_url or not api_key:
                raise ValueError(f"Environment variables {self.config.endpoint_env} and {self.config.key_env} must be set")
            
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )
            
            logger.info(f"Direct API client initialized for {self.config.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize direct API client for {self.config.name}: {e}")
            raise
    
    def create_chat_completion(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Any:
        """Create a chat completion using direct API."""
        try:
            # Validate streaming request
            if stream and not self.config.supports_streaming:
                logger.warning(f"Streaming requested but {self.config.name} doesn't support it. Falling back to non-streaming.")
                stream = False
            
            # Build parameters
            params = {
                "model": self.config.name,
                "messages": messages,
                "stream": stream,
                **kwargs
            }
            
            # Add temperature if supported
            if self.config.default_temperature is not None:
                params.setdefault("temperature", self.config.default_temperature)
            
            response = self.client.chat.completions.create(**params)
            
            if stream:
                return self._wrap_streaming_response(response)
            return response
            
        except Exception as e:
            logger.error(f"Error creating chat completion for {self.config.name}: {e}")
            raise
    
    def _wrap_streaming_response(self, response):
        """Wrap streaming response for consistent interface."""
        class StreamingWrapper:
            def __init__(self, openai_stream):
                self.openai_stream = openai_stream
                self.content = ""
                
            def __iter__(self):
                for chunk in self.openai_stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            chunk_content = delta.content
                            self.content += chunk_content
                            yield chunk_content
            
            @property
            def choices(self):
                return [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': self.content
                    })()
                })()]
        
        return StreamingWrapper(response)


class AzureFoundryClient(BaseModelClient):
    """Client for Azure AI Foundry models (Grok)."""
    
    def _initialize_client(self):
        """Initialize Azure AI Foundry client."""
        try:
            base_url = os.getenv(self.config.endpoint_env)
            api_key = os.getenv(self.config.key_env or "")
            
            if not base_url or not api_key:
                raise ValueError(f"Environment variables {self.config.endpoint_env} and {self.config.key_env} must be set")
            
            # Ensure URL ends with /models for Azure AI Foundry
            if not base_url.endswith('/'):
                base_url += '/'
            if not base_url.endswith('models'):
                base_url += 'models'
            
            self.base_url = base_url
            self.api_key = api_key
            self.model_name = os.getenv(self.config.model_env) if self.config.model_env else self.config.name
            self.api_version = (
                os.getenv(self.config.api_version_env) if self.config.api_version_env 
                else self.config.default_api_version
            )
            
            logger.info(f"Azure AI Foundry client initialized for {self.config.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Foundry client for {self.config.name}: {e}")
            raise
    
    def create_chat_completion(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Any:
        """Create a chat completion using Azure AI Foundry API."""
        try:
            # Validate streaming request
            if stream and not self.config.supports_streaming:
                logger.warning(f"Streaming requested but {self.config.name} doesn't support it. Falling back to non-streaming.")
                stream = False
            
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "messages": messages,
                "model": self.model_name,
                "stream": stream,
                **kwargs
            }
            
            # Add temperature if supported
            if self.config.default_temperature is not None:
                data.setdefault("temperature", self.config.default_temperature)
            
            params = {"api-version": self.api_version}
            
            response = requests.post(url, headers=headers, json=data, params=params, stream=stream)
            response.raise_for_status()
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                result = response.json()
                return self._create_response_object(result)
                
        except Exception as e:
            logger.error(f"Error creating chat completion for {self.config.name}: {e}")
            raise
    
    def _handle_streaming_response(self, response):
        """Handle streaming response from Azure AI Foundry."""
        class StreamingResponse:
            def __init__(self, response):
                self.response = response
                self.content = ""
                
            def __iter__(self):
                for line in self.response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        chunk_content = delta['content']
                                        self.content += chunk_content
                                        yield chunk_content
                            except json.JSONDecodeError:
                                continue
            
            @property
            def choices(self):
                return [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': self.content
                    })()
                })()]
        
        return StreamingResponse(response)
    
    def _create_response_object(self, result):
        """Create a response object compatible with OpenAI format."""
        class MockResponse:
            def __init__(self, data):
                self.choices = [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': data['choices'][0]['message']['content']
                    })()
                })()]
        
        return MockResponse(result)


class ModelClientFactory:
    """Factory for creating model clients."""
    
    @staticmethod
    def create_client(model_name: str) -> BaseModelClient:
        """Create a client for the specified model."""
        config = ModelRegistry.get_model(model_name)
        
        if config.model_type == ModelType.AZURE_OPENAI:
            return AzureOpenAIClient(config)
        elif config.model_type == ModelType.DIRECT_API:
            return DirectAPIClient(config)
        elif config.model_type == ModelType.AZURE_FOUNDRY:
            return AzureFoundryClient(config)
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")


# Public API Functions
def get_model_client(model_name: str = "gpt-4.1") -> BaseModelClient:
    """
    Get a model client for the specified model.
    
    This is the main entry point for getting a model client.
    
    Args:
        model_name: The name of the model to use
        
    Returns:
        A model client that can be used to create chat completions
    """
    return ModelClientFactory.create_client(model_name)


def get_available_models() -> List[str]:
    """Get a list of all available models."""
    return list(ModelRegistry.get_all_models().keys())


def get_streaming_models() -> List[str]:
    """Get a list of models that support streaming."""
    return ModelRegistry.get_streaming_models()


def supports_streaming(model_name: str) -> bool:
    """Check if a model supports streaming."""
    try:
        config = ModelRegistry.get_model(model_name)
        return config.supports_streaming
    except ValueError:
        return False


def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get detailed information about a model."""
    config = ModelRegistry.get_model(model_name)
    return {
        "name": config.name,
        "type": config.model_type.value,
        "auth_type": config.auth_type.value,
        "supports_streaming": config.supports_streaming,
        "supports_system_role": config.supports_system_role,
        "supported_features": config.supported_features,
        "max_tokens_limit": config.max_tokens_limit,
        "default_temperature": config.default_temperature,
        "temperature_range": [config.min_temperature, config.max_temperature] if config.default_temperature is not None else None
    }


def get_autogen_config(model_name: str = "gpt-4.1") -> Dict[str, Any]:
    """
    Get configuration for AutoGen integration.
    
    Args:
        model_name: The model name to use
        
    Returns:
        A dictionary with AutoGen-compatible configuration
    """
    config = ModelRegistry.get_model(model_name)
    
    if config.model_type == ModelType.AZURE_OPENAI:
        # Create token provider function for automatic refresh
        def token_provider():
            credential = AzureCredentialManager.get_credential()
            return credential.get_token("https://cognitiveservices.azure.com/.default").token
        
        return {
            "model": os.getenv(config.model_env or ""),
            "azure_endpoint": os.getenv(config.endpoint_env),
            "api_version": os.getenv(config.api_version_env or "") or config.default_api_version,
            "azure_ad_token_provider": token_provider
        }
    elif config.model_type == ModelType.DIRECT_API:
        return {
            "model": config.name,
            "base_url": os.getenv(config.endpoint_env),
            "api_key": os.getenv(config.key_env or ""),
            "model_info": config.model_info
        }
    elif config.model_type == ModelType.AZURE_FOUNDRY:
        base_url = os.getenv(config.endpoint_env) or ""
        if not base_url:
            raise ValueError(f"Environment variable {config.endpoint_env} not set")
        if not base_url.endswith('/'):
            base_url += '/'
        if not base_url.endswith('models'):
            base_url += 'models'
        
        return {
            "model": os.getenv(config.model_env) if config.model_env else config.name,
            "base_url": base_url,
            "api_key": os.getenv(config.key_env or ""),
            "model_info": config.model_info
        }
    else:
        raise ValueError(f"Unsupported model type for AutoGen: {config.model_type}")


# Legacy compatibility functions (deprecated)
def create_azure_openai_client(model_version: str = "gpt-4.1", **kwargs) -> AzureOpenAI:
    """
    DEPRECATED: Use get_model_client() instead.
    Create an Azure OpenAI client with secure token caching.
    """
    logger.warning("create_azure_openai_client() is deprecated. Use get_model_client() instead.")
    client = get_model_client(model_version)
    if not isinstance(client, AzureOpenAIClient):
        raise ValueError(f"Model {model_version} is not an Azure OpenAI model")
    return client.client


def get_model_config(model_version: str = "gpt-4.1") -> Dict[str, Any]:
    """
    DEPRECATED: Use get_model_info() instead.
    Get the configuration for a specific model.
    """
    logger.warning("get_model_config() is deprecated. Use get_model_info() instead.")
    return get_model_info(model_version)


# Initialize model registry on module import
ModelRegistry.register_models()


# Example usage and simple test
if __name__ == "__main__":
    # Example of using the simplified API
    print("Available models:", get_available_models())
    print("Streaming models:", get_streaming_models())
    
    # Example of creating a client
    try:
        client = get_model_client("gpt-4.1")
        print(f"Successfully created client for gpt-4.1")
        print(f"Supports streaming: {client.supports_streaming()}")
    except Exception as e:
        print(f"Error creating client: {e}")
    
    # Example of getting model info
    try:
        info = get_model_info("gpt-4.1")
        print(f"Model info for gpt-4.1: {info}")
    except Exception as e:
        print(f"Error getting model info: {e}")