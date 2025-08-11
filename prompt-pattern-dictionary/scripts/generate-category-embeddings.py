#!/usr/bin/env python3
"""
Generate embeddings for category descriptions to enable semantic similarity comparison.
This script creates embeddings for all 25 categories defined in pattern-categories.json
using the same Azure OpenAI infrastructure as generate-embeddings-similarity.py.
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent directories to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

try:
    from azure_models import get_model_client, get_model_info, AzureOpenAIClient
    from azure.core.exceptions import AzureError, ServiceRequestError
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure azure_models.py is available and Azure SDK packages are installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CategoryEmbeddingGenerator:
    """Generate embeddings for category descriptions using Azure OpenAI."""
    
    def __init__(self, model_name: str = "embedding-3"):
        """Initialize the embedding generator."""
        self.model_name = model_name
        self.client = None
        self.model_info = None
        self.categories_data = None
        
    def initialize_model(self) -> bool:
        """Initialize the Azure OpenAI client."""
        try:
            logger.info(f"Initializing Azure OpenAI client for model: {self.model_name}")
            self.client = get_model_client(self.model_name)
            self.model_info = get_model_info(self.model_name)
            
            if not self.client:
                logger.error("Failed to initialize Azure OpenAI client")
                return False
                
            logger.info(f"Azure OpenAI client initialized successfully. Model supports: {self.model_info['supported_features']}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            return False
    
    def load_categories(self, categories_file: str) -> bool:
        """Load category definitions from pattern-categories.json."""
        try:
            logger.info(f"Loading categories from: {categories_file}")
            
            with open(categories_file, 'r', encoding='utf-8') as f:
                self.categories_data = json.load(f)
            
            total_categories = sum(logic['categoryCount'] for logic in self.categories_data['logics'])
            logger.info(f"Loaded {total_categories} categories across {len(self.categories_data['logics'])} logic groups")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading categories: {e}")
            return False
    
    def _create_category_embedding_text(self, category: Dict[str, Any], logic_context: Dict[str, Any]) -> str:
        """Create comprehensive text for category embedding."""
        # Start with category name and description
        parts = [
            f"Category: {category['name']}",
            f"Description: {category['description']}"
        ]
        
        # Add logic context for better semantic understanding
        parts.extend([
            f"Logic Group: {logic_context['name']}",
            f"Logic Focus: {logic_context['focus']}",
            f"Logic Description: {logic_context['description']}"
        ])
        
        # Combine all parts
        embedding_text = " ".join(parts)
        
        # Clean up text (remove newlines, extra spaces)
        embedding_text = " ".join(embedding_text.split())
        
        return embedding_text
    
    def _call_embedding_api(self, text: str) -> Dict[str, Any]:
        """
        Call Azure OpenAI embedding API using azure_models.py client.
        
        Uses the same approach as generate-embeddings-similarity.py with 
        the modern authentication from azure_models.py.
        """
        try:
            # For embedding models, we need to access the underlying Azure OpenAI client
            from azure_models import AzureOpenAIClient
            
            if not isinstance(self.client, AzureOpenAIClient):
                raise ValueError(f"Expected AzureOpenAIClient, got {type(self.client)}")
            
            # Get the underlying Azure OpenAI client
            azure_client = self.client.client
            
            # Get deployment name from environment variable
            model_env = self.client.config.model_env
            if not model_env:
                raise ValueError("Model environment variable name not configured")
                
            deployment_name = os.getenv(model_env)
            if not deployment_name:
                raise ValueError(f"Environment variable {model_env} not set")
            
            # Call the embeddings API - same pattern as generate-embeddings-similarity.py
            response = azure_client.embeddings.create(
                input=[text], 
                model=deployment_name
            )
            
            # Convert to dictionary format expected by the calling code
            return {
                'data': [{'embedding': response.data[0].embedding}],
                'usage': {
                    'total_tokens': response.usage.total_tokens if hasattr(response, 'usage') else len(text.split())
                }
            }
            
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI embeddings API: {e}")
            raise
    
    def generate_embeddings(self) -> Dict[str, Any]:
        """Generate embeddings for all categories."""
        if not self.client:
            raise RuntimeError("Embedding model not initialized")
        
        if not self.categories_data:
            raise RuntimeError("Categories data not loaded")
        
        logger.info("Starting category embedding generation")
        
        category_embeddings = {
            "metadata": {
                "model": self.model_name,
                "dimensions": 3072,  # text-embedding-3-large dimensions
                "generatedAt": None,  # Will be set by embedding model
                "totalCategories": 0,
                "logics": []
            },
            "categories": {}
        }
        
        total_categories = 0
        api_calls = 0
        
        for logic in self.categories_data['logics']:
            logic_info = {
                "name": logic['name'],
                "slug": logic['slug'],
                "categoryCount": logic['categoryCount']
            }
            category_embeddings["metadata"]["logics"].append(logic_info)
            
            logger.info(f"Processing logic group: {logic['name']} ({logic['categoryCount']} categories)")
            
            for category in logic['categories']:
                category_slug = category['slug']
                
                # Create embedding text
                embedding_text = self._create_category_embedding_text(category, logic)
                
                logger.info(f"Generating embedding for category: {category['name']} ({category_slug})")
                
                try:
                    # Generate embedding using the same pattern as generate-embeddings-similarity.py
                    embedding_result = self._call_embedding_api(embedding_text)
                    api_calls += 1
                    
                    if embedding_result and 'data' in embedding_result and embedding_result['data']:
                        category_embeddings["categories"][category_slug] = {
                            "name": category['name'],
                            "slug": category_slug,
                            "logic": logic['slug'],
                            "description": category['description'],
                            "embedding_text": embedding_text,
                            "embedding": embedding_result['data'][0]['embedding']
                        }
                        total_categories += 1
                        logger.info(f"✅ Generated embedding for {category['name']}")
                    else:
                        logger.error(f"❌ Failed to generate embedding for {category['name']}")
                        
                except Exception as e:
                    logger.error(f"❌ Error generating embedding for {category['name']}: {e}")
                    continue
        
        # Update metadata
        category_embeddings["metadata"]["totalCategories"] = total_categories
        category_embeddings["metadata"]["apiCalls"] = api_calls
        
        logger.info(f"Category embedding generation completed!")
        logger.info(f"Total categories processed: {total_categories}")
        logger.info(f"API calls made: {api_calls}")
        
        return category_embeddings
    
    def save_embeddings(self, embeddings: Dict[str, Any], output_file: str) -> bool:
        """Save category embeddings to file."""
        try:
            logger.info(f"Saving category embeddings to: {output_file}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(embeddings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Category embeddings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving embeddings: {e}")
            return False

def main():
    """Main execution function."""
    # File paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    categories_file = project_root / "public" / "data" / "pattern-categories.json"
    output_file = project_root / "public" / "data" / "category-embeddings.json"
    
    logger.info("🔮 Starting category embedding generation...")
    
    # Initialize generator
    generator = CategoryEmbeddingGenerator()
    
    # Initialize model
    if not generator.initialize_model():
        logger.error("❌ Failed to initialize embedding model")
        sys.exit(1)
    
    # Load categories
    if not generator.load_categories(str(categories_file)):
        logger.error("❌ Failed to load categories")
        sys.exit(1)
    
    try:
        # Generate embeddings
        embeddings = generator.generate_embeddings()
        
        # Save embeddings
        if generator.save_embeddings(embeddings, str(output_file)):
            logger.info("✅ Category embedding generation completed successfully!")
            print(f"📁 Output saved to: {output_file}")
            print(f"📊 Generated embeddings for {embeddings['metadata']['totalCategories']} categories")
            print(f"🔢 API calls made: {embeddings['metadata']['apiCalls']}")
        else:
            logger.error("❌ Failed to save embeddings")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error during embedding generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
