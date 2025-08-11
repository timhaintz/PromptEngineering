#!/usr/bin/env python3
"""
Generate embeddings focused on EXAMPLES rather than pattern names.
This script creates embeddings for individual examples within patterns,
which provides much better semantic similarity for categorization.
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path to import azure_models
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

try:
    from azure_models import get_model_client, get_model_info
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExampleBasedEmbeddingGenerator:
    """Generate embeddings for pattern examples rather than pattern names."""
    
    def __init__(self, model_name: str = "embedding-3"):
        """Initialize the embedding generator."""
        self.model_name = model_name
        self.client = None
        self.model_info = None
        self.patterns_data = None
        
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
    
    def load_patterns(self, patterns_file: str) -> bool:
        """Load patterns data."""
        try:
            logger.info(f"Loading patterns from: {patterns_file}")
            
            with open(patterns_file, 'r', encoding='utf-8') as f:
                patterns_list = json.load(f)
            
            # Convert to dict for easier lookup
            self.patterns_data = {pattern['id']: pattern for pattern in patterns_list}
            
            logger.info(f"Loaded {len(self.patterns_data)} patterns")
            return True
            
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            return False
    
    def _call_embedding_api(self, text: str) -> Dict[str, Any]:
        """Call Azure OpenAI embedding API using azure_models.py client."""
        try:
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
            
            # Call the embeddings API
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
    
    def _create_example_embedding_text(self, pattern_data: Dict[str, Any]) -> str:
        """Create embedding text focused on examples rather than pattern name."""
        
        # Get all examples for this pattern
        examples = pattern_data.get('examples', [])
        
        if not examples:
            # Fallback to pattern name if no examples
            return pattern_data.get('patternName', '')
        
        # Create text that emphasizes the actual examples
        example_texts = [example.get('content', '') for example in examples if example.get('content')]
        
        if not example_texts:
            return pattern_data.get('patternName', '')
        
        # Combine examples with some context
        combined_text = " ".join(example_texts)
        
        # Optionally include category for context (but de-emphasize it)
        category = pattern_data.get('category', '')
        if category and len(combined_text) < 1000:  # Only if we have room
            combined_text = f"Category: {category}. Examples: {combined_text}"
        
        return combined_text
    
    def generate_example_embeddings(self, output_file: str) -> bool:
        """Generate embeddings for all patterns based on their examples."""
        try:
            if not self.client:
                logger.error("Azure OpenAI client not initialized")
                return False
                
            if not self.patterns_data:
                logger.error("Patterns data not loaded")
                return False
            
            # Create output directory
            output_dir = os.path.dirname(output_file)
            os.makedirs(output_dir, exist_ok=True)
            
            embeddings_data = {
                "metadata": {
                    "generatedAt": datetime.now().isoformat(),
                    "model": self.model_name,
                    "dimensions": 3072,  # text-embedding-3-large
                    "totalPatterns": len(self.patterns_data),
                    "embeddingType": "example-based",
                    "description": "Embeddings generated from pattern examples rather than pattern names"
                },
                "patterns": {}
            }
            
            processed = 0
            total_patterns = len(self.patterns_data)
            
            logger.info(f"Generating example-based embeddings for {total_patterns} patterns...")
            
            for pattern_id, pattern_data in self.patterns_data.items():
                try:
                    logger.info(f"Processing pattern {pattern_id}: {pattern_data.get('patternName', 'Unknown')}")
                    
                    # Create embedding text focused on examples
                    embedding_text = self._create_example_embedding_text(pattern_data)
                    
                    if not embedding_text.strip():
                        logger.warning(f"No text to embed for pattern {pattern_id}")
                        continue
                    
                    # Generate embedding
                    embedding_result = self._call_embedding_api(embedding_text)
                    
                    if embedding_result and 'data' in embedding_result and embedding_result['data']:
                        embeddings_data["patterns"][pattern_id] = {
                            "patternName": pattern_data.get('patternName', ''),
                            "category": pattern_data.get('category', ''),
                            "embedding": embedding_result['data'][0]['embedding'],
                            "embeddingText": embedding_text,
                            "exampleCount": len(pattern_data.get('examples', [])),
                            "tokensUsed": embedding_result.get('usage', {}).get('total_tokens', 0)
                        }
                        
                        processed += 1
                        logger.info(f"✅ Generated embedding for {pattern_id} ({processed}/{total_patterns})")
                    else:
                        logger.error(f"❌ Failed to generate embedding for {pattern_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing pattern {pattern_id}: {e}")
                    continue
                    
                # Progress update
                if processed % 50 == 0:
                    logger.info(f"Progress: {processed}/{total_patterns} patterns processed")
            
            # Update metadata
            embeddings_data["metadata"]["patternsProcessed"] = processed
            
            # Save embeddings
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(embeddings_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Example-based embeddings generation completed!")
            logger.info(f"📁 Saved to: {output_file}")
            logger.info(f"📊 Processed: {processed}/{total_patterns} patterns")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            return False

def main():
    """Main execution function."""
    # File paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    patterns_file = project_root / "public" / "data" / "patterns.json"
    output_file = project_root / "public" / "data" / "example-based-embeddings.json"
    
    logger.info("🎯 Starting Example-Based Embedding Generation...")
    
    # Initialize generator
    generator = ExampleBasedEmbeddingGenerator()
    
    # Initialize model
    if not generator.initialize_model():
        logger.error("❌ Failed to initialize embedding model")
        sys.exit(1)
    
    # Load patterns
    if not generator.load_patterns(str(patterns_file)):
        logger.error("❌ Failed to load patterns")
        sys.exit(1)
    
    try:
        # Generate embeddings
        if generator.generate_example_embeddings(str(output_file)):
            logger.info("🎉 Example-based embedding generation completed successfully!")
        else:
            logger.error("❌ Failed to generate embeddings")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error during embedding generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
