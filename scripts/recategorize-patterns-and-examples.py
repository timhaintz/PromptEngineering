#!/usr/bin/env python3
"""
Re-categorize patterns and examples based on semantic similarity analysis.

This script implements both pattern-level and example-level categorization:
- Option 1: Pattern-to-Category mapping using pattern semantic similarity
- Option 2: Example-to-Category mapping using individual example semantic similarity

Creates an enhanced patterns.json with:
- Original paper categories preserved as metadata
- New universal categories for patterns
- New universal categories for each example
- Confidence scores and similarity data
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np


def load_semantic_analysis_results(file_path: str) -> Dict[str, Any]:
    """Load the semantic similarity analysis results."""
    print(f"Loading semantic analysis results from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_patterns_data(file_path: str) -> List[Dict[str, Any]]:
    """Load the current patterns.json data."""
    print(f"Loading patterns data from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_category_definitions(file_path: str) -> Dict[str, Any]:
    """Load category definitions for reference."""
    print(f"Loading category definitions from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_pattern_categorization(pattern_id: str, semantic_results: Dict[str, Any]) -> Dict[str, Any]:
    """Get the semantic categorization for a specific pattern."""
    patterns = semantic_results.get('detailed_results', {}).get('patterns', [])
    for result in patterns:
        if result['pattern_id'] == pattern_id:
            # Convert top_categories format to similarities format
            similarities = []
            for cat_info in result.get('top_categories', []):
                similarities.append({
                    'category': cat_info[0],
                    'similarity': cat_info[1]
                })
            
            return {
                'semantic_category': result['predicted_category'],
                'confidence': result['confidence'],
                'top_3_categories': similarities[:3],
                'all_similarities': similarities
            }
    return None


def get_example_categorizations(pattern_id: str, semantic_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get semantic categorizations for all examples of a specific pattern."""
    example_categorizations = []
    examples = semantic_results.get('detailed_results', {}).get('examples', [])
    
    for result in examples:
        if result['pattern_id'] == pattern_id:
            # Convert top_categories format to similarities format
            similarities = []
            for cat_info in result.get('top_categories', []):
                similarities.append({
                    'category': cat_info[0],
                    'similarity': cat_info[1]
                })
            
            # Extract example index from example_id (format: "pattern_id-example_index")
            example_id = result.get('example_id', '')
            example_index = 0
            if '-' in example_id:
                parts = example_id.split('-')
                if len(parts) >= 4:
                    try:
                        example_index = int(parts[-1])
                    except ValueError:
                        example_index = 0
            
            example_categorizations.append({
                'example_index': example_index,
                'semantic_category': result['predicted_category'],
                'confidence': result['confidence'],
                'top_3_categories': similarities[:3],
                'all_similarities': similarities
            })
    
    return example_categorizations


def categorize_patterns_and_examples(patterns: List[Dict[str, Any]], 
                                   semantic_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Enhance patterns with both pattern-level and example-level categorizations."""
    enhanced_patterns = []
    
    pattern_stats = {
        'total_patterns': len(patterns),
        'patterns_with_semantic_category': 0,
        'examples_with_semantic_category': 0,
        'total_examples': 0
    }
    
    category_distribution = {
        'patterns': {},
        'examples': {}
    }
    
    for pattern in patterns:
        enhanced_pattern = pattern.copy()
        pattern_id = pattern['id']
        
        # Get pattern-level categorization (Option 1)
        pattern_categorization = get_pattern_categorization(pattern_id, semantic_results)
        
        if pattern_categorization:
            pattern_stats['patterns_with_semantic_category'] += 1
            
            # Add semantic category information to pattern
            enhanced_pattern['semantic_categorization'] = {
                'category': pattern_categorization['semantic_category'],
                'confidence': pattern_categorization['confidence'],
                'top_alternatives': pattern_categorization['top_3_categories']
            }
            
            # Track category distribution for patterns
            semantic_cat = pattern_categorization['semantic_category']
            if semantic_cat not in category_distribution['patterns']:
                category_distribution['patterns'][semantic_cat] = 0
            category_distribution['patterns'][semantic_cat] += 1
            
            # Preserve original category as metadata
            enhanced_pattern['original_paper_category'] = pattern.get('category', 'Unknown')
        
        # Get example-level categorizations (Option 2)
        example_categorizations = get_example_categorizations(pattern_id, semantic_results)
        
        if example_categorizations and 'examples' in enhanced_pattern:
            # Ensure we have the same number of examples as categorizations
            examples = enhanced_pattern.get('examples', [])
            pattern_stats['total_examples'] += len(examples)
            
            for i, example_cat in enumerate(example_categorizations):
                if i < len(examples):
                    example_index = example_cat['example_index']
                    if example_index < len(examples):
                        # Add semantic category information to each example
                        if 'semantic_categorization' not in examples[example_index]:
                            examples[example_index] = examples[example_index] if isinstance(examples[example_index], dict) else {'content': examples[example_index]}
                        
                        examples[example_index]['semantic_categorization'] = {
                            'category': example_cat['semantic_category'],
                            'confidence': example_cat['confidence'],
                            'top_alternatives': example_cat['top_3_categories']
                        }
                        
                        pattern_stats['examples_with_semantic_category'] += 1
                        
                        # Track category distribution for examples
                        semantic_cat = example_cat['semantic_category']
                        if semantic_cat not in category_distribution['examples']:
                            category_distribution['examples'][semantic_cat] = 0
                        category_distribution['examples'][semantic_cat] += 1
        
        enhanced_patterns.append(enhanced_pattern)
    
    return enhanced_patterns, pattern_stats, category_distribution


def generate_categorization_report(patterns: List[Dict[str, Any]], 
                                 pattern_stats: Dict[str, Any],
                                 category_distribution: Dict[str, Any],
                                 semantic_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive report on the re-categorization process."""
    
    # Calculate category changes for patterns
    pattern_category_changes = []
    for pattern in patterns:
        if 'semantic_categorization' in pattern and 'original_paper_category' in pattern:
            original = pattern['original_paper_category']
            semantic = pattern['semantic_categorization']['category']
            if original != semantic:
                pattern_category_changes.append({
                    'pattern_id': pattern['id'],
                    'pattern_name': pattern.get('patternName', 'Unknown'),
                    'original_category': original,
                    'semantic_category': semantic,
                    'confidence': pattern['semantic_categorization']['confidence']
                })
    
    # Calculate example-pattern category mismatches
    example_pattern_mismatches = []
    for pattern in patterns:
        if 'semantic_categorization' in pattern and 'examples' in pattern:
            pattern_category = pattern['semantic_categorization']['category']
            for i, example in enumerate(pattern['examples']):
                if isinstance(example, dict) and 'semantic_categorization' in example:
                    example_category = example['semantic_categorization']['category']
                    if pattern_category != example_category:
                        example_pattern_mismatches.append({
                            'pattern_id': pattern['id'],
                            'pattern_name': pattern.get('patternName', 'Unknown'),
                            'example_index': i,
                            'pattern_category': pattern_category,
                            'example_category': example_category,
                            'pattern_confidence': pattern['semantic_categorization']['confidence'],
                            'example_confidence': example['semantic_categorization']['confidence']
                        })
    
    return {
        'generation_info': {
            'timestamp': datetime.now().isoformat(),
            'script_version': '1.0.0',
            'approach': 'Dual categorization (patterns + examples)',
            'semantic_analysis_source': semantic_results.get('metadata', {})
        },
        'statistics': {
            'total_patterns': pattern_stats['total_patterns'],
            'patterns_with_semantic_category': pattern_stats['patterns_with_semantic_category'],
            'pattern_categorization_coverage': pattern_stats['patterns_with_semantic_category'] / pattern_stats['total_patterns'] * 100,
            'total_examples': pattern_stats['total_examples'],
            'examples_with_semantic_category': pattern_stats['examples_with_semantic_category'],
            'example_categorization_coverage': pattern_stats['examples_with_semantic_category'] / pattern_stats['total_examples'] * 100 if pattern_stats['total_examples'] > 0 else 0,
            'pattern_category_changes': len(pattern_category_changes),
            'example_pattern_mismatches': len(example_pattern_mismatches)
        },
        'category_distribution': category_distribution,
        'analysis': {
            'pattern_category_changes': pattern_category_changes[:20],  # Top 20 changes
            'example_pattern_mismatches': example_pattern_mismatches[:20],  # Top 20 mismatches
            'total_pattern_changes': len(pattern_category_changes),
            'total_example_mismatches': len(example_pattern_mismatches)
        },
        'insights': {
            'most_common_pattern_categories': sorted(category_distribution['patterns'].items(), key=lambda x: x[1], reverse=True)[:10],
            'most_common_example_categories': sorted(category_distribution['examples'].items(), key=lambda x: x[1], reverse=True)[:10],
            'category_diversity': {
                'pattern_categories_used': len(category_distribution['patterns']),
                'example_categories_used': len(category_distribution['examples']),
                'total_available_categories': 25
            }
        }
    }


def main():
    """Main execution function."""
    print("Starting pattern and example re-categorization process...")
    
    # File paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    semantic_results_path = os.path.join(base_dir, "analysis_results", "semantic_similarity_analysis_20250730_104123.json")
    patterns_path = os.path.join(base_dir, "prompt-pattern-dictionary", "public", "data", "patterns.json")
    categories_path = os.path.join(base_dir, "prompt-pattern-dictionary", "public", "data", "category-embeddings.json")
    
    # Output paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    enhanced_patterns_path = os.path.join(base_dir, f"enhanced_patterns_{timestamp}.json")
    report_path = os.path.join(base_dir, f"recategorization_report_{timestamp}.json")
    
    try:
        # Load data
        semantic_results = load_semantic_analysis_results(semantic_results_path)
        patterns = load_patterns_data(patterns_path)
        categories = load_category_definitions(categories_path)
        
        print(f"\nLoaded:")
        print(f"- {len(patterns)} patterns")
        print(f"- {len(categories['categories'])} category definitions")
        print(f"- Semantic analysis for {len(semantic_results.get('pattern_analysis', []))} patterns")
        print(f"- Semantic analysis for {len(semantic_results.get('example_analysis', []))} examples")
        
        # Perform dual categorization
        print("\nPerforming dual categorization (patterns + examples)...")
        enhanced_patterns, pattern_stats, category_distribution = categorize_patterns_and_examples(
            patterns, semantic_results
        )
        
        # Generate report
        print("Generating categorization report...")
        report = generate_categorization_report(
            enhanced_patterns, pattern_stats, category_distribution, semantic_results
        )
        
        # Save enhanced patterns
        print(f"\nSaving enhanced patterns to {enhanced_patterns_path}")
        with open(enhanced_patterns_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_patterns, f, indent=2, ensure_ascii=False)
        
        # Save report
        print(f"Saving categorization report to {report_path}")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n{'='*60}")
        print("DUAL CATEGORIZATION COMPLETE")
        print(f"{'='*60}")
        print(f"Pattern Coverage: {report['statistics']['pattern_categorization_coverage']:.1f}%")
        print(f"Example Coverage: {report['statistics']['example_categorization_coverage']:.1f}%")
        print(f"Pattern Category Changes: {report['statistics']['pattern_category_changes']}")
        print(f"Example-Pattern Mismatches: {report['statistics']['example_pattern_mismatches']}")
        print(f"\nTop Pattern Categories:")
        for cat, count in report['insights']['most_common_pattern_categories'][:5]:
            print(f"  {cat}: {count}")
        print(f"\nTop Example Categories:")
        for cat, count in report['insights']['most_common_example_categories'][:5]:
            print(f"  {cat}: {count}")
        print(f"\nFiles generated:")
        print(f"- Enhanced patterns: {enhanced_patterns_path}")
        print(f"- Detailed report: {report_path}")
        
    except Exception as e:
        print(f"Error during re-categorization: {str(e)}")
        raise


if __name__ == "__main__":
    main()
