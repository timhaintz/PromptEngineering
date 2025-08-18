#!/usr/bin/env python3
"""
Analyze insights from the dual categorization results.
"""

import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Any


def load_enhanced_patterns(file_path: str) -> List[Dict[str, Any]]:
    """Load enhanced patterns with dual categorization."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_report(file_path: str) -> Dict[str, Any]:
    """Load the categorization report."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_pattern_example_mismatches(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze patterns where examples have different categories than the pattern."""
    mismatches = []
    total_patterns_with_examples = 0
    total_examples = 0
    
    for pattern in patterns:
        if 'examples' in pattern and pattern['examples'] and 'semantic_categorization' in pattern:
            total_patterns_with_examples += 1
            pattern_category = pattern['semantic_categorization']['category']
            
            for i, example in enumerate(pattern['examples']):
                total_examples += 1
                if isinstance(example, dict) and 'semantic_categorization' in example:
                    example_category = example['semantic_categorization']['category']
                    
                    if pattern_category != example_category:
                        mismatches.append({
                            'pattern_id': pattern['id'],
                            'pattern_name': pattern.get('patternName', 'Unknown'),
                            'pattern_category': pattern_category,
                            'pattern_confidence': pattern['semantic_categorization']['confidence'],
                            'example_index': i,
                            'example_category': example_category,
                            'example_confidence': example['semantic_categorization']['confidence'],
                            'confidence_diff': abs(pattern['semantic_categorization']['confidence'] - example['semantic_categorization']['confidence'])
                        })
    
    return {
        'total_mismatches': len(mismatches),
        'total_patterns_with_examples': total_patterns_with_examples,
        'total_examples': total_examples,
        'mismatch_rate': len(mismatches) / total_examples if total_examples > 0 else 0,
        'mismatches': mismatches
    }


def analyze_category_transitions(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze transitions from original categories to semantic categories."""
    transitions = defaultdict(lambda: defaultdict(int))
    
    for pattern in patterns:
        if 'original_paper_category' in pattern and 'semantic_categorization' in pattern:
            original = pattern['original_paper_category']
            semantic = pattern['semantic_categorization']['category']
            transitions[original][semantic] += 1
    
    # Find most common transitions
    common_transitions = []
    for original, semantic_dict in transitions.items():
        for semantic, count in semantic_dict.items():
            common_transitions.append({
                'from': original,
                'to': semantic,
                'count': count,
                'same_category': original == semantic
            })
    
    common_transitions.sort(key=lambda x: x['count'], reverse=True)
    
    return {
        'total_original_categories': len(transitions),
        'common_transitions': common_transitions[:20],
        'all_transitions': dict(transitions)
    }


def analyze_confidence_patterns(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze confidence score patterns."""
    pattern_confidences = []
    example_confidences = []
    
    for pattern in patterns:
        if 'semantic_categorization' in pattern:
            pattern_confidences.append(pattern['semantic_categorization']['confidence'])
        
        if 'examples' in pattern:
            for example in pattern['examples']:
                if isinstance(example, dict) and 'semantic_categorization' in example:
                    example_confidences.append(example['semantic_categorization']['confidence'])
    
    def get_confidence_stats(confidences):
        if not confidences:
            return {}
        return {
            'mean': sum(confidences) / len(confidences),
            'min': min(confidences),
            'max': max(confidences),
            'count': len(confidences),
            'high_confidence': len([c for c in confidences if c >= 0.6]),
            'medium_confidence': len([c for c in confidences if 0.3 <= c < 0.6]),
            'low_confidence': len([c for c in confidences if c < 0.3])
        }
    
    return {
        'patterns': get_confidence_stats(pattern_confidences),
        'examples': get_confidence_stats(example_confidences)
    }


def analyze_semantic_vs_original_accuracy(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare how many patterns kept their original category vs changed."""
    kept_same = 0
    changed = 0
    
    for pattern in patterns:
        if 'original_paper_category' in pattern and 'semantic_categorization' in pattern:
            if pattern['original_paper_category'] == pattern['semantic_categorization']['category']:
                kept_same += 1
            else:
                changed += 1
    
    total = kept_same + changed
    return {
        'kept_same': kept_same,
        'changed': changed,
        'total_analyzed': total,
        'change_rate': changed / total if total > 0 else 0,
        'kept_rate': kept_same / total if total > 0 else 0
    }


def find_interesting_examples(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find interesting examples that might provide insights."""
    high_confidence_mismatches = []
    cross_boundary_examples = []
    translation_patterns = []
    
    for pattern in patterns:
        # High confidence mismatches
        if 'semantic_categorization' in pattern and 'examples' in pattern:
            pattern_category = pattern['semantic_categorization']['category']
            pattern_confidence = pattern['semantic_categorization']['confidence']
            
            for i, example in enumerate(pattern['examples']):
                if isinstance(example, dict) and 'semantic_categorization' in example:
                    example_category = example['semantic_categorization']['category']
                    example_confidence = example['semantic_categorization']['confidence']
                    
                    if (pattern_category != example_category and 
                        example_confidence > 0.4 and pattern_confidence > 0.4):
                        high_confidence_mismatches.append({
                            'pattern_id': pattern['id'],
                            'pattern_name': pattern.get('patternName', 'Unknown'),
                            'pattern_category': pattern_category,
                            'example_category': example_category,
                            'pattern_confidence': pattern_confidence,
                            'example_confidence': example_confidence
                        })
        
        # Cross boundary patterns
        if ('semantic_categorization' in pattern and 
            pattern['semantic_categorization']['category'] == 'Cross Boundary'):
            cross_boundary_examples.append({
                'pattern_id': pattern['id'],
                'pattern_name': pattern.get('patternName', 'Unknown'),
                'original_category': pattern.get('original_paper_category', 'Unknown'),
                'confidence': pattern['semantic_categorization']['confidence']
            })
        
        # Translation patterns  
        if ('semantic_categorization' in pattern and 
            pattern['semantic_categorization']['category'] == 'Translation'):
            translation_patterns.append({
                'pattern_id': pattern['id'],
                'pattern_name': pattern.get('patternName', 'Unknown'),
                'original_category': pattern.get('original_paper_category', 'Unknown'),
                'confidence': pattern['semantic_categorization']['confidence']
            })
    
    return {
        'high_confidence_mismatches': sorted(high_confidence_mismatches, 
                                           key=lambda x: x['example_confidence'], reverse=True)[:10],
        'cross_boundary_patterns': sorted(cross_boundary_examples, 
                                        key=lambda x: x['confidence'], reverse=True)[:10],
        'translation_patterns': sorted(translation_patterns, 
                                     key=lambda x: x['confidence'], reverse=True)[:10]
    }


def main():
    """Generate comprehensive insights analysis."""
    print("Analyzing dual categorization insights...")
    
    # File paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    enhanced_patterns_path = os.path.join(base_dir, "enhanced_patterns_20250730_110545.json")
    report_path = os.path.join(base_dir, "recategorization_report_20250730_110545.json")
    
    # Load data
    patterns = load_enhanced_patterns(enhanced_patterns_path)
    report = load_report(report_path)
    
    # Perform analyses
    print("Analyzing pattern-example mismatches...")
    mismatch_analysis = analyze_pattern_example_mismatches(patterns)
    
    print("Analyzing category transitions...")
    transition_analysis = analyze_category_transitions(patterns)
    
    print("Analyzing confidence patterns...")
    confidence_analysis = analyze_confidence_patterns(patterns)
    
    print("Analyzing semantic vs original accuracy...")
    accuracy_analysis = analyze_semantic_vs_original_accuracy(patterns)
    
    print("Finding interesting examples...")
    interesting_examples = find_interesting_examples(patterns)
    
    # Compile comprehensive insights
    insights = {
        'summary': {
            'total_patterns': len(patterns),
            'patterns_analyzed': report['statistics']['patterns_with_semantic_category'],
            'examples_analyzed': report['statistics']['examples_with_semantic_category'],
            'category_change_rate': accuracy_analysis['change_rate'],
            'example_mismatch_rate': mismatch_analysis['mismatch_rate']
        },
        'pattern_example_mismatches': mismatch_analysis,
        'category_transitions': transition_analysis,
        'confidence_analysis': confidence_analysis,
        'accuracy_comparison': accuracy_analysis,
        'interesting_findings': interesting_examples,
        'category_distributions': report['category_distribution']
    }
    
    # Save insights
    insights_path = os.path.join(base_dir, f"dual_categorization_insights_analysis.json")
    with open(insights_path, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)
    
    # Print key insights
    print(f"\n{'='*80}")
    print("DUAL CATEGORIZATION INSIGHTS ANALYSIS")
    print(f"{'='*80}")
    
    print(f"\n📊 SUMMARY STATISTICS:")
    print(f"  • Total patterns analyzed: {insights['summary']['patterns_analyzed']}")
    print(f"  • Total examples analyzed: {insights['summary']['examples_analyzed']}")
    print(f"  • Pattern category change rate: {insights['summary']['category_change_rate']:.1%}")
    print(f"  • Example-pattern mismatch rate: {insights['summary']['example_mismatch_rate']:.1%}")
    
    print(f"\n🔄 TOP CATEGORY TRANSITIONS:")
    for transition in transition_analysis['common_transitions'][:5]:
        same_indicator = "✓" if transition['same_category'] else "→"
        print(f"  {same_indicator} {transition['from']} → {transition['to']}: {transition['count']} patterns")
    
    print(f"\n📈 CONFIDENCE ANALYSIS:")
    print(f"  Patterns - Mean: {confidence_analysis['patterns']['mean']:.3f}")
    print(f"    High confidence (≥0.6): {confidence_analysis['patterns']['high_confidence']}")
    print(f"    Medium confidence (0.3-0.6): {confidence_analysis['patterns']['medium_confidence']}")
    print(f"    Low confidence (<0.3): {confidence_analysis['patterns']['low_confidence']}")
    print(f"  Examples - Mean: {confidence_analysis['examples']['mean']:.3f}")
    print(f"    High confidence (≥0.6): {confidence_analysis['examples']['high_confidence']}")
    print(f"    Medium confidence (0.3-0.6): {confidence_analysis['examples']['medium_confidence']}")
    print(f"    Low confidence (<0.3): {confidence_analysis['examples']['low_confidence']}")
    
    print(f"\n🎯 HIGH-CONFIDENCE MISMATCHES (Pattern ≠ Example):")
    for mismatch in interesting_examples['high_confidence_mismatches'][:3]:
        print(f"  • {mismatch['pattern_name']} ({mismatch['pattern_id']})")
        print(f"    Pattern: {mismatch['pattern_category']} ({mismatch['pattern_confidence']:.3f})")
        print(f"    Example: {mismatch['example_category']} ({mismatch['example_confidence']:.3f})")
    
    print(f"\n🚀 TOP CROSS BOUNDARY PATTERNS:")
    for cb in interesting_examples['cross_boundary_patterns'][:3]:
        print(f"  • {cb['pattern_name']} (was: {cb['original_category']}) - {cb['confidence']:.3f}")
    
    print(f"\n🌐 TOP TRANSLATION PATTERNS:")
    for tr in interesting_examples['translation_patterns'][:3]:
        print(f"  • {tr['pattern_name']} (was: {tr['original_category']}) - {tr['confidence']:.3f}")
    
    print(f"\n📄 Full analysis saved to: {insights_path}")


if __name__ == "__main__":
    main()
