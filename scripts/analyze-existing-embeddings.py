#!/usr/bin/env python3
"""
Analyze semantic similarity using existing embeddings.

This script uses the pre-generated embeddings in the paper files and category embeddings
to perform semantic similarity analysis without regenerating any embeddings.
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SimilarityResult:
    """Container for similarity analysis results."""
    pattern_id: str
    pattern_name: str
    current_category: str
    predicted_category: str
    confidence: float
    top_categories: List[Tuple[str, float]]
    paper_info: Dict[str, str]

@dataclass
class ExampleSimilarityResult:
    """Container for example similarity analysis results."""
    example_id: str
    pattern_id: str
    pattern_name: str
    example_content: str
    current_category: str
    predicted_category: str
    confidence: float
    top_categories: List[Tuple[str, float]]

class ExistingEmbeddingAnalyzer:
    """Analyze semantic similarity using existing embeddings."""
    
    def __init__(self, 
                 embeddings_dir: Path,
                 category_embeddings_file: Path,
                 patterns_file: Path,
                 output_dir: Path):
        self.embeddings_dir = embeddings_dir
        self.category_embeddings_file = category_embeddings_file
        self.patterns_file = patterns_file
        self.output_dir = output_dir
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data containers
        self.pattern_embeddings = {}
        self.example_embeddings = {}
        self.category_embeddings = {}
        self.patterns_data = {}
        
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        np_vec1 = np.array(vec1)
        np_vec2 = np.array(vec2)
        
        # Calculate dot product and magnitudes
        dot_product = np.dot(np_vec1, np_vec2)
        magnitude1 = np.linalg.norm(np_vec1)
        magnitude2 = np.linalg.norm(np_vec2)
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)
    
    def load_category_embeddings(self) -> bool:
        """Load category embeddings from the JSON file."""
        try:
            logger.info(f"Loading category embeddings from {self.category_embeddings_file}")
            
            with open(self.category_embeddings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            categories = data.get('categories', {})
            
            for category_slug, category_data in categories.items():
                if 'embedding' in category_data and category_data['embedding']:
                    self.category_embeddings[category_slug] = {
                        'name': category_data.get('name', category_slug),
                        'embedding': category_data['embedding'],
                        'logic': category_data.get('logic', ''),
                        'description': category_data.get('description', '')
                    }
            
            logger.info(f"Loaded {len(self.category_embeddings)} category embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load category embeddings: {e}")
            return False
    
    def load_patterns_data(self) -> bool:
        """Load pattern metadata from patterns.json."""
        try:
            logger.info(f"Loading patterns data from {self.patterns_file}")
            
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                patterns_list = json.load(f)
            
            # Convert to dict indexed by pattern ID
            for pattern in patterns_list:
                pattern_id = pattern.get('id')
                if pattern_id:
                    self.patterns_data[pattern_id] = pattern
            
            logger.info(f"Loaded data for {len(self.patterns_data)} patterns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load patterns data: {e}")
            return False
    
    def load_paper_embeddings(self) -> bool:
        """Load all paper embedding files."""
        try:
            logger.info(f"Loading paper embeddings from {self.embeddings_dir}")
            
            pattern_count = 0
            example_count = 0
            
            # Get all paper embedding files
            paper_files = list(self.embeddings_dir.glob("paper-*.json"))
            logger.info(f"Found {len(paper_files)} paper embedding files")
            
            for paper_file in paper_files:
                try:
                    with open(paper_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Load pattern embeddings
                    patterns = data.get('patterns', {})
                    for pattern_id, pattern_data in patterns.items():
                        if 'embedding' in pattern_data and pattern_data['embedding']:
                            self.pattern_embeddings[pattern_id] = pattern_data['embedding']
                            pattern_count += 1
                    
                    # Load example embeddings
                    examples = data.get('examples', {})
                    for example_id, example_data in examples.items():
                        if 'embedding' in example_data and example_data['embedding']:
                            self.example_embeddings[example_id] = example_data['embedding']
                            example_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to load {paper_file}: {e}")
                    continue
            
            logger.info(f"Loaded {pattern_count} pattern embeddings and {example_count} example embeddings")
            return pattern_count > 0 or example_count > 0
            
        except Exception as e:
            logger.error(f"Failed to load paper embeddings: {e}")
            return False
    
    def find_best_category(self, embedding: List[float], top_k: int = 3) -> List[Tuple[str, float]]:
        """Find the best matching categories for an embedding."""
        similarities = []
        
        for category_slug, category_data in self.category_embeddings.items():
            similarity = self.cosine_similarity(embedding, category_data['embedding'])
            similarities.append((category_slug, similarity))
        
        # Sort by similarity (descending) and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def analyze_pattern_similarities(self) -> List[SimilarityResult]:
        """Analyze semantic similarity for all patterns."""
        logger.info("Analyzing pattern similarities...")
        
        results = []
        processed_count = 0
        
        for pattern_id, embedding in self.pattern_embeddings.items():
            try:
                # Get pattern metadata
                pattern_data = self.patterns_data.get(pattern_id, {})
                pattern_name = pattern_data.get('patternName', 'Unknown')
                current_category = pattern_data.get('category', 'Unknown')
                paper_info = pattern_data.get('paper', {})
                
                # Find best matching categories
                top_categories = self.find_best_category(embedding)
                
                if top_categories:
                    predicted_category = top_categories[0][0]
                    confidence = top_categories[0][1]
                    
                    # Convert category slug to name for display
                    predicted_category_name = self.category_embeddings.get(predicted_category, {}).get('name', predicted_category)
                    top_categories_with_names = [
                        (self.category_embeddings.get(slug, {}).get('name', slug), score)
                        for slug, score in top_categories
                    ]
                    
                    result = SimilarityResult(
                        pattern_id=pattern_id,
                        pattern_name=pattern_name,
                        current_category=current_category,
                        predicted_category=predicted_category_name,
                        confidence=confidence,
                        top_categories=top_categories_with_names,
                        paper_info=paper_info
                    )
                    
                    results.append(result)
                    processed_count += 1
                    
                    if processed_count % 100 == 0:
                        logger.info(f"Processed {processed_count} patterns...")
                
            except Exception as e:
                logger.warning(f"Failed to analyze pattern {pattern_id}: {e}")
                continue
        
        logger.info(f"Completed analysis of {len(results)} patterns")
        return results
    
    def analyze_example_similarities(self) -> List[ExampleSimilarityResult]:
        """Analyze semantic similarity for all examples."""
        logger.info("Analyzing example similarities...")
        
        results = []
        processed_count = 0
        
        for example_id, embedding in self.example_embeddings.items():
            try:
                # Extract pattern ID from example ID (e.g., "0-0-0-0" -> "0-0-0")
                pattern_id = "-".join(example_id.split("-")[:-1])
                
                # Get pattern metadata
                pattern_data = self.patterns_data.get(pattern_id, {})
                pattern_name = pattern_data.get('patternName', 'Unknown')
                current_category = pattern_data.get('category', 'Unknown')
                
                # Find example content
                example_content = ""
                examples_list = pattern_data.get('examples', [])
                example_index = int(example_id.split("-")[-1])
                if example_index < len(examples_list):
                    example_content = examples_list[example_index].get('content', '')
                
                # Find best matching categories
                top_categories = self.find_best_category(embedding)
                
                if top_categories:
                    predicted_category = top_categories[0][0]
                    confidence = top_categories[0][1]
                    
                    # Convert category slug to name for display
                    predicted_category_name = self.category_embeddings.get(predicted_category, {}).get('name', predicted_category)
                    top_categories_with_names = [
                        (self.category_embeddings.get(slug, {}).get('name', slug), score)
                        for slug, score in top_categories
                    ]
                    
                    result = ExampleSimilarityResult(
                        example_id=example_id,
                        pattern_id=pattern_id,
                        pattern_name=pattern_name,
                        example_content=example_content[:200] + "..." if len(example_content) > 200 else example_content,
                        current_category=current_category,
                        predicted_category=predicted_category_name,
                        confidence=confidence,
                        top_categories=top_categories_with_names
                    )
                    
                    results.append(result)
                    processed_count += 1
                    
                    if processed_count % 200 == 0:
                        logger.info(f"Processed {processed_count} examples...")
                
            except Exception as e:
                logger.warning(f"Failed to analyze example {example_id}: {e}")
                continue
        
        logger.info(f"Completed analysis of {len(results)} examples")
        return results
    
    def generate_analysis_report(self, pattern_results: List[SimilarityResult], 
                               example_results: List[ExampleSimilarityResult]):
        """Generate comprehensive analysis report."""
        
        # Calculate statistics for patterns
        pattern_matches = sum(1 for r in pattern_results if r.current_category == r.predicted_category)
        pattern_accuracy = pattern_matches / len(pattern_results) if pattern_results else 0
        
        pattern_high_confidence = sum(1 for r in pattern_results if r.confidence > 0.8)
        pattern_medium_confidence = sum(1 for r in pattern_results if 0.6 <= r.confidence <= 0.8)
        pattern_low_confidence = sum(1 for r in pattern_results if r.confidence < 0.6)
        
        # Calculate statistics for examples
        example_matches = sum(1 for r in example_results if r.current_category == r.predicted_category)
        example_accuracy = example_matches / len(example_results) if example_results else 0
        
        example_high_confidence = sum(1 for r in example_results if r.confidence > 0.8)
        example_medium_confidence = sum(1 for r in example_results if 0.6 <= r.confidence <= 0.8)
        example_low_confidence = sum(1 for r in example_results if r.confidence < 0.6)
        
        # Generate report
        report = {
            "metadata": {
                "generatedAt": datetime.now().isoformat(),
                "analysisType": "existing_embeddings_semantic_similarity",
                "totalPatterns": len(pattern_results),
                "totalExamples": len(example_results),
                "categories": len(self.category_embeddings)
            },
            "pattern_analysis": {
                "accuracy": round(pattern_accuracy, 4),
                "correctMatches": pattern_matches,
                "totalPatterns": len(pattern_results),
                "confidenceDistribution": {
                    "high": pattern_high_confidence,
                    "medium": pattern_medium_confidence,
                    "low": pattern_low_confidence
                }
            },
            "example_analysis": {
                "accuracy": round(example_accuracy, 4),
                "correctMatches": example_matches,
                "totalExamples": len(example_results),
                "confidenceDistribution": {
                    "high": example_high_confidence,
                    "medium": example_medium_confidence,
                    "low": example_low_confidence
                }
            },
            "detailed_results": {
                "patterns": [
                    {
                        "pattern_id": r.pattern_id,
                        "pattern_name": r.pattern_name,
                        "current_category": r.current_category,
                        "predicted_category": r.predicted_category,
                        "confidence": round(r.confidence, 4),
                        "match": r.current_category == r.predicted_category,
                        "top_categories": [(cat, round(score, 4)) for cat, score in r.top_categories],
                        "paper_title": r.paper_info.get('title', '')
                    }
                    for r in pattern_results
                ],
                "examples": [
                    {
                        "example_id": r.example_id,
                        "pattern_id": r.pattern_id,
                        "pattern_name": r.pattern_name,
                        "example_content": r.example_content,
                        "current_category": r.current_category,
                        "predicted_category": r.predicted_category,
                        "confidence": round(r.confidence, 4),
                        "match": r.current_category == r.predicted_category,
                        "top_categories": [(cat, round(score, 4)) for cat, score in r.top_categories]
                    }
                    for r in example_results
                ]
            }
        }
        
        # Save report
        report_file = self.output_dir / f"semantic_similarity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis report saved to {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("SEMANTIC SIMILARITY ANALYSIS RESULTS")
        print("="*60)
        print(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nPattern Analysis:")
        print(f"  Total patterns analyzed: {len(pattern_results)}")
        print(f"  Correct predictions: {pattern_matches} ({pattern_accuracy:.1%})")
        print(f"  High confidence (>80%): {pattern_high_confidence}")
        print(f"  Medium confidence (60-80%): {pattern_medium_confidence}")
        print(f"  Low confidence (<60%): {pattern_low_confidence}")
        
        print(f"\nExample Analysis:")
        print(f"  Total examples analyzed: {len(example_results)}")
        print(f"  Correct predictions: {example_matches} ({example_accuracy:.1%})")
        print(f"  High confidence (>80%): {example_high_confidence}")
        print(f"  Medium confidence (60-80%): {example_medium_confidence}")
        print(f"  Low confidence (<60%): {example_low_confidence}")
        
        print(f"\nReport saved to: {report_file}")
        print("="*60)
        
        return report_file
    
    def run(self) -> bool:
        """Execute the complete analysis pipeline."""
        try:
            logger.info("Starting semantic similarity analysis using existing embeddings")
            
            # Load all required data
            if not self.load_category_embeddings():
                return False
            
            if not self.load_patterns_data():
                return False
            
            if not self.load_paper_embeddings():
                return False
            
            # Perform analysis
            pattern_results = self.analyze_pattern_similarities()
            example_results = self.analyze_example_similarities()
            
            if not pattern_results and not example_results:
                logger.error("No results generated from analysis")
                return False
            
            # Generate report
            self.generate_analysis_report(pattern_results, example_results)
            
            logger.info("Analysis completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze semantic similarity using existing embeddings")
    parser.add_argument("--embeddings-dir", 
                       default="prompt-pattern-dictionary/public/data/embeddings",
                       help="Directory containing paper embedding files")
    parser.add_argument("--category-embeddings", 
                       default="prompt-pattern-dictionary/public/data/category-embeddings.json",
                       help="Category embeddings file")
    parser.add_argument("--patterns-file", 
                       default="prompt-pattern-dictionary/public/data/patterns.json",
                       help="Patterns data file")
    parser.add_argument("--output-dir", 
                       default="analysis_results",
                       help="Output directory for analysis results")
    
    args = parser.parse_args()
    
    # Convert to Path objects
    embeddings_dir = Path(args.embeddings_dir)
    category_embeddings_file = Path(args.category_embeddings)
    patterns_file = Path(args.patterns_file)
    output_dir = Path(args.output_dir)
    
    # Validate input files
    if not embeddings_dir.exists():
        print(f"Error: Embeddings directory not found: {embeddings_dir}")
        return False
    
    if not category_embeddings_file.exists():
        print(f"Error: Category embeddings file not found: {category_embeddings_file}")
        return False
    
    if not patterns_file.exists():
        print(f"Error: Patterns file not found: {patterns_file}")
        return False
    
    # Run analysis
    analyzer = ExistingEmbeddingAnalyzer(
        embeddings_dir=embeddings_dir,
        category_embeddings_file=category_embeddings_file,
        patterns_file=patterns_file,
        output_dir=output_dir
    )
    
    success = analyzer.run()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
