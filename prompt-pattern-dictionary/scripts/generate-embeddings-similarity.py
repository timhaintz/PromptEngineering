"""
DESCRIPTION
Azure OpenAI Embedding Generation for Prompt Pattern Dictionary

Generates embeddings for prompt patterns using Azure OpenAI text-embedding-3-large
with paper-based chunking, modern authentication, and Azure best practices.

This script processes promptpatterns.json and creates embeddings organized by paper ID
for efficient loading and similarity comparisons in the web application.

Version:        1.0
Author:         Generated for Prompt Pattern Dictionary
Creation Date:  20250729

FEATURES
- Paper-based chunking for efficient storage and loading
- Hash-based change detection to avoid unnecessary API calls
- Azure retry policies with exponential backoff
- Graceful error handling - continues on individual failures
- Modern authentication using InteractiveBrowserCredential
- Comprehensive logging for debugging
- Incremental updates for cost optimization

LINKS
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/embeddings
https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings
"""

import os
import sys
import json
import hashlib
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import traceback

# Add parent directory to path to import azure_models
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

try:
    from azure_models import get_model_client, get_model_info
    from azure.core.exceptions import AzureError, ServiceRequestError
    from azure.identity import InteractiveBrowserCredential
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure azure_models.py is available and Azure SDK packages are installed")
    sys.exit(1)

# Configure logging with Azure best practices
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('embedding_generation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result of embedding generation for a single item."""
    success: bool
    embedding: Optional[List[float]] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    
@dataclass
class PatternEmbedding:
    """Embedding data for a single pattern."""
    embedding: List[float]
    hash: str
    lastUpdated: str
    paperId: str
    
@dataclass
class ExampleEmbedding:
    """Embedding data for a single example."""
    embedding: List[float]
    hash: str
    lastUpdated: str
    patternId: str
    paperId: str

@dataclass
class EmbeddingStorage:
    """Storage format for paper-based embedding chunks."""
    metadata: Dict[str, Any]
    patterns: Dict[str, PatternEmbedding]
    examples: Dict[str, ExampleEmbedding]

class EmbeddingGenerator:
    """
    Azure OpenAI embedding generator with paper-based chunking and error resilience.
    
    Implements Azure best practices:
    - Modern authentication with automatic token refresh
    - Retry policies with exponential backoff
    - Circuit breaker pattern for rate limit protection
    - Graceful degradation on individual failures
    - Comprehensive logging and monitoring
    """
    
    def __init__(self, model_name: str = "embedding-3"):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Azure OpenAI embedding model to use (embedding-3 = text-embedding-3-large)
        """
        self.model_name = model_name
        self.client = None
        self.model_info = None
        self.source_file = Path(__file__).parent.parent.parent / "promptpatterns.json"
        self.output_dir = Path(__file__).parent.parent / "public" / "data" / "embeddings"
        self.index_file = Path(__file__).parent.parent / "public" / "data" / "embedding-index.json"
        self.stats_file = Path(__file__).parent.parent / "public" / "data" / "embedding-stats.json"
        
        # Error tracking for resilience
        self.failed_patterns = []
        self.failed_examples = []
        self.total_tokens_used = 0
        self.api_call_count = 0
        
        # Rate limiting and circuit breaker
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.circuit_breaker_open = False
        self.last_api_call_time = 0
        self.min_api_interval = 0.1  # Minimum 100ms between API calls
        
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Azure OpenAI client with error handling."""
        try:
            logger.info(f"Initializing Azure OpenAI client for model: {self.model_name}")
            self.client = get_model_client(self.model_name)
            self.model_info = get_model_info(self.model_name)
            logger.info(f"Client initialized successfully. Model supports: {self.model_info['supported_features']}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise
    
    def _check_circuit_breaker(self):
        """Check if circuit breaker should prevent API calls."""
        if self.circuit_breaker_open:
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.warning("Circuit breaker is open - too many consecutive failures")
                return False
            else:
                # Reset circuit breaker after some successful calls
                self.circuit_breaker_open = False
                logger.info("Circuit breaker reset")
        return True
    
    def _rate_limit_delay(self):
        """Implement rate limiting to respect Azure OpenAI limits."""
        time_since_last_call = time.time() - self.last_api_call_time
        if time_since_last_call < self.min_api_interval:
            sleep_time = self.min_api_interval - time_since_last_call
            time.sleep(sleep_time)
        self.last_api_call_time = time.time()
    
    def _generate_text_hash(self, text: str) -> str:
        """Generate SHA-256 hash for change detection."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _create_embedding_text(self, pattern_name: str, description: str = "", examples: Optional[List[str]] = None) -> str:
        """
        Create optimized text for embedding generation.
        
        Combines pattern name, description, and examples into a single text
        optimized for semantic similarity matching.
        """
        parts = [pattern_name]
        
        if description:
            parts.append(description)
        
        if examples is not None:
            # Include up to 3 examples to avoid token limit issues
            example_text = " ".join(examples[:3])
            parts.append(example_text)
        
        return " ".join(parts)
    
    def _generate_single_embedding(self, text: str, item_id: str) -> EmbeddingResult:
        """
        Generate embedding for a single text with Azure best practices.
        
        Implements:
        - Retry logic with exponential backoff
        - Rate limiting
        - Circuit breaker pattern
        - Comprehensive error logging
        """
        if not self._check_circuit_breaker():
            return EmbeddingResult(False, error="Circuit breaker open")
        
        self._rate_limit_delay()
        
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Generating embedding for {item_id} (attempt {attempt + 1})")
                
                # Call Azure OpenAI embedding API
                # Note: The actual implementation depends on the embedding client interface
                # This is a conceptual implementation - the actual API call would use the client
                response = self._call_embedding_api(text)
                
                if response and 'data' in response and len(response['data']) > 0:
                    embedding = response['data'][0]['embedding']
                    tokens_used = response.get('usage', {}).get('total_tokens', 0)
                    
                    self.total_tokens_used += tokens_used
                    self.api_call_count += 1
                    self.consecutive_failures = 0  # Reset failure counter
                    
                    logger.debug(f"Successfully generated embedding for {item_id} ({tokens_used} tokens)")
                    return EmbeddingResult(True, embedding=embedding, tokens_used=tokens_used)
                else:
                    raise ValueError("Invalid response format from Azure OpenAI")
                    
            except ServiceRequestError as e:
                # Azure-specific errors (rate limits, service issues)
                self.consecutive_failures += 1
                status_code = getattr(getattr(e, "response", None), "status_code", None)
                if status_code == 429:  # Rate limit
                    delay = base_delay * (2 ** attempt) + 5  # Extra delay for rate limits
                    logger.warning(f"Rate limit hit for {item_id}, retrying in {delay}s")
                elif status_code is not None and status_code >= 500:  # Server errors
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Server error for {item_id}: {e}, retrying in {delay}s")
                else:
                    logger.error(f"Client error for {item_id}: {e}")
                    break  # Don't retry client errors
                
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    self.failed_patterns.append(item_id) if 'pattern' in item_id else self.failed_examples.append(item_id)
                    return EmbeddingResult(False, error=f"Azure service error: {e}")
                    
            except Exception as e:
                self.consecutive_failures += 1
                logger.error(f"Unexpected error generating embedding for {item_id}: {e}")
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    return EmbeddingResult(False, error=f"Unexpected error: {e}")
        
        # Check if circuit breaker should open
        if self.consecutive_failures >= self.max_consecutive_failures:
            self.circuit_breaker_open = True
            logger.error("Circuit breaker opened due to consecutive failures")
        
        return EmbeddingResult(False, error="Max retries exceeded")
    
    def _call_embedding_api(self, text: str) -> Dict[str, Any]:
        """
        Call Azure OpenAI embedding API using azure_models.py client.
        
        Uses the same approach as categorisation_cosine_similarity.py but with 
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
            
            # Call the embeddings API - same pattern as categorisation_cosine_similarity.py
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
    
    def _load_existing_embeddings(self, paper_id: str) -> Optional[EmbeddingStorage]:
        """Load existing embeddings for a paper if they exist."""
        embedding_file = self.output_dir / f"paper-{paper_id}.json"
        
        if not embedding_file.exists():
            return None
        
        try:
            with open(embedding_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return EmbeddingStorage(
                    metadata=data['metadata'],
                    patterns={k: PatternEmbedding(**v) for k, v in data['patterns'].items()},
                    examples={k: ExampleEmbedding(**v) for k, v in data['examples'].items()}
                )
        except Exception as e:
            logger.warning(f"Failed to load existing embeddings for paper {paper_id}: {e}")
            return None
    
    def _save_paper_embeddings(self, paper_id: str, storage: EmbeddingStorage):
        """Save embeddings for a paper to disk."""
        embedding_file = self.output_dir / f"paper-{paper_id}.json"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Convert dataclasses to dict for JSON serialization
            data = {
                "metadata": storage.metadata,
                "patterns": {k: asdict(v) for k, v in storage.patterns.items()},
                "examples": {k: asdict(v) for k, v in storage.examples.items()}
            }
            
            with open(embedding_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved embeddings for paper {paper_id} to {embedding_file}")
            
        except Exception as e:
            logger.error(f"Failed to save embeddings for paper {paper_id}: {e}")
            raise
    
    def _needs_embedding_update(self, existing_hash: str, current_text: str) -> bool:
        """Check if embedding needs to be updated based on content hash."""
        current_hash = self._generate_text_hash(current_text)
        return existing_hash != current_hash
    
    def process_paper(self, paper_data: Dict[str, Any], paper_index: int) -> Tuple[int, int, int]:
        """
        Process a single paper and generate embeddings for its patterns and examples.
        
        Returns:
            Tuple of (patterns_processed, examples_processed, skipped_count)
        """
        paper_id = str(paper_index)
        logger.info(f"Processing paper {paper_id}: {paper_data.get('Title', 'Unknown')}")
        
        # Load existing embeddings for incremental updates
        existing_storage = self._load_existing_embeddings(paper_id)
        
        # Initialize new storage
        new_storage = EmbeddingStorage(
            metadata={
                "model": self.model_name,
                "dimensions": 3072,  # text-embedding-3-large dimensions
                "generatedAt": datetime.now().isoformat(),
                "totalPatterns": 0,
                "totalExamples": 0,
                "papers": [paper_id]
            },
            patterns={},
            examples={}
        )
        
        # Copy existing embeddings that haven't changed
        if existing_storage:
            new_storage.patterns = existing_storage.patterns.copy()
            new_storage.examples = existing_storage.examples.copy()
        
        patterns_processed = 0
        examples_processed = 0
        skipped_count = 0
        
        # Process categories and patterns
        for category_index, category in enumerate(paper_data.get('CategoriesAndPatterns', [])):
            for pattern_index, pattern in enumerate(category.get('PromptPatterns', [])):
                pattern_id = f"{paper_index}-{category_index}-{pattern_index}"
                
                # Generate pattern embedding
                pattern_text = self._create_embedding_text(
                    pattern.get('PatternName', ''),
                    pattern.get('Description', ''),
                    pattern.get('ExamplePrompts', [])
                )
                
                pattern_hash = self._generate_text_hash(pattern_text)
                
                # Check if we need to update this pattern's embedding
                if (pattern_id not in new_storage.patterns or 
                    self._needs_embedding_update(new_storage.patterns[pattern_id].hash, pattern_text)):
                    
                    embedding_result = self._generate_single_embedding(pattern_text, pattern_id)
                    
                    if embedding_result.success and embedding_result.embedding is not None:
                        new_storage.patterns[pattern_id] = PatternEmbedding(
                            embedding=embedding_result.embedding,
                            hash=pattern_hash,
                            lastUpdated=datetime.now().isoformat(),
                            paperId=paper_id
                        )
                        patterns_processed += 1
                        logger.debug(f"Generated embedding for pattern {pattern_id}")
                    else:
                        logger.warning(f"Failed to generate embedding for pattern {pattern_id}: {embedding_result.error}")
                        # Keep existing embedding if available
                        if pattern_id not in new_storage.patterns:
                            self.failed_patterns.append(pattern_id)
                else:
                    skipped_count += 1
                    logger.debug(f"Skipping unchanged pattern {pattern_id}")
                
                # Process examples
                for example_index, example in enumerate(pattern.get('ExamplePrompts', [])):
                    example_id = f"{pattern_id}-{example_index}"
                    example_hash = self._generate_text_hash(example)
                    
                    # Check if we need to update this example's embedding
                    if (example_id not in new_storage.examples or 
                        self._needs_embedding_update(new_storage.examples[example_id].hash, example)):
                        
                        embedding_result = self._generate_single_embedding(example, example_id)
                        
                        if embedding_result.success and embedding_result.embedding is not None:
                            new_storage.examples[example_id] = ExampleEmbedding(
                                embedding=embedding_result.embedding,
                                hash=example_hash,
                                lastUpdated=datetime.now().isoformat(),
                                patternId=pattern_id,
                                paperId=paper_id
                            )
                            examples_processed += 1
                            logger.debug(f"Generated embedding for example {example_id}")
                        else:
                            logger.warning(f"Failed to generate embedding for example {example_id}: {embedding_result.error}")
                            # Keep existing embedding if available
                            if example_id not in new_storage.examples:
                                self.failed_examples.append(example_id)
                    else:
                        skipped_count += 1
                        logger.debug(f"Skipping unchanged example {example_id}")
        
        # Update metadata
        new_storage.metadata.update({
            "totalPatterns": len(new_storage.patterns),
            "totalExamples": len(new_storage.examples),
        })
        
        # Save embeddings for this paper
        self._save_paper_embeddings(paper_id, new_storage)
        
        logger.info(f"Paper {paper_id} complete: {patterns_processed} patterns, {examples_processed} examples processed, {skipped_count} skipped")
        
        return patterns_processed, examples_processed, skipped_count
    
    def generate_master_index(self, paper_count: int):
        """Generate master index mapping pattern IDs to paper chunks."""
        try:
            index_data = {
                "metadata": {
                    "generatedAt": datetime.now().isoformat(),
                    "totalPapers": paper_count,
                    "embeddingModel": self.model_name,
                    "totalApiCalls": self.api_call_count,
                    "totalTokensUsed": self.total_tokens_used
                },
                "papers": {},
                "patternToPaper": {},
                "exampleToPaper": {}
            }
            
            # Scan all paper embedding files to build index
            for paper_id in range(paper_count):
                embedding_file = self.output_dir / f"paper-{paper_id}.json"
                if embedding_file.exists():
                    try:
                        with open(embedding_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        index_data["papers"][str(paper_id)] = {
                            "file": f"paper-{paper_id}.json",
                            "patternCount": len(data.get("patterns", {})),
                            "exampleCount": len(data.get("examples", {})),
                            "lastUpdated": data.get("metadata", {}).get("generatedAt")
                        }
                        
                        # Map patterns to papers
                        for pattern_id in data.get("patterns", {}):
                            index_data["patternToPaper"][pattern_id] = str(paper_id)
                        
                        # Map examples to papers  
                        for example_id in data.get("examples", {}):
                            index_data["exampleToPaper"][example_id] = str(paper_id)
                            
                    except Exception as e:
                        logger.error(f"Error reading paper {paper_id} for index: {e}")
            
            # Save master index
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Generated master index with {len(index_data['papers'])} papers")
            
        except Exception as e:
            logger.error(f"Failed to generate master index: {e}")
            raise
    
    def generate_statistics(self):
        """Generate comprehensive statistics about the embedding generation process."""
        stats = {
            "generatedAt": datetime.now().isoformat(),
            "model": self.model_name,
            "modelInfo": self.model_info,
            "apiCalls": self.api_call_count,
            "totalTokensUsed": self.total_tokens_used,
            "averageTokensPerCall": self.total_tokens_used / max(self.api_call_count, 1),
            "failedPatterns": len(self.failed_patterns),
            "failedExamples": len(self.failed_examples),
            "circuitBreakerTriggered": self.circuit_breaker_open,
            "consecutiveFailures": self.consecutive_failures,
            "errors": {
                "patterns": self.failed_patterns[:10],  # First 10 for debugging
                "examples": self.failed_examples[:10]
            }
        }
        
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Generated statistics: {self.api_call_count} API calls, {self.total_tokens_used} tokens used")
            
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
    
    def run(self) -> bool:
        """
        Main execution method with comprehensive error handling.
        
        Returns:
            True if successful (even with partial failures), False if complete failure
        """
        try:
            logger.info("Starting embedding generation for Prompt Pattern Dictionary")
            logger.info(f"Using model: {self.model_name}")
            logger.info(f"Source file: {self.source_file}")
            logger.info(f"Output directory: {self.output_dir}")
            
            # Load source data
            if not self.source_file.exists():
                logger.error(f"Source file not found: {self.source_file}")
                return False
            
            with open(self.source_file, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            
            papers = source_data.get('Source', {}).get('Titles', [])
            if not papers:
                logger.error("No papers found in source data")
                return False
            
            logger.info(f"Found {len(papers)} papers to process")
            
            # Process each paper
            total_patterns = 0
            total_examples = 0
            total_skipped = 0
            
            for paper_index, paper in enumerate(papers):
                try:
                    patterns, examples, skipped = self.process_paper(paper, paper_index)
                    total_patterns += patterns
                    total_examples += examples
                    total_skipped += skipped
                    
                    # Log progress every 10 papers
                    if (paper_index + 1) % 10 == 0:
                        logger.info(f"Progress: {paper_index + 1}/{len(papers)} papers processed")
                        
                except Exception as e:
                    logger.error(f"Failed to process paper {paper_index}: {e}")
                    logger.error(traceback.format_exc())
                    # Continue with next paper - don't let one failure stop everything
                    continue
            
            # Generate master index and statistics
            self.generate_master_index(len(papers))
            self.generate_statistics()
            
            # Log final results
            logger.info("Embedding generation completed!")
            logger.info(f"Results: {total_patterns} patterns, {total_examples} examples, {total_skipped} skipped")
            logger.info(f"API calls: {self.api_call_count}, Tokens used: {self.total_tokens_used}")
            logger.info(f"Failures: {len(self.failed_patterns)} patterns, {len(self.failed_examples)} examples")
            
            # Return success even if there were some failures
            return True
            
        except Exception as e:
            logger.error(f"Critical error in embedding generation: {e}")
            logger.error(traceback.format_exc())
            return False

def main():
    """Main entry point for the script."""
    try:
        generator = EmbeddingGenerator("embedding-3")
        success = generator.run()
        
        if success:
            print("✅ Embedding generation completed successfully")
            if generator.failed_patterns or generator.failed_examples:
                print(f"⚠️  Some embeddings failed: {len(generator.failed_patterns)} patterns, {len(generator.failed_examples)} examples")
                print("Check embedding_generation.log for details")
            sys.exit(0)
        else:
            print("❌ Embedding generation failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Embedding generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
