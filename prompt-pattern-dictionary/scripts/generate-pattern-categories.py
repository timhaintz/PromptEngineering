#!/usr/bin/env python3
"""
Generate pattern-categories.json based on logic definitions and category templates
from the Python categorization system.

This script reads the logic definitions and category templates from the Python files
and generates a hierarchical pattern-categories.json structure organized by logic layers.
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import our modules
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from category_definitions import (
        across, at_logic, beyond_logic, in_logic, out_logic, over_logic,
        # Import all category definitions
        argument, assessment, calculation, categorising, classification, clustering,
        comparison, context_control, contradiction, cross_boundary, decomposed_prompting,
        error_identification, hypothesise, input_semantics, logical_reasoning,
        output_customisation, output_semantics, prediction, prompt_improvement,
        refactoring, requirements_elicitation, simulation, summarising, synthesis, translation
    )
    from simple_categorisation_writeup import LOGIC_DEFINITIONS, CATEGORY_TEMPLATES
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)

def slugify(text):
    """Convert string to URL-friendly slug"""
    return text.lower().replace(' ', '-').replace('_', '-')

def get_category_description(category_name):
    """Get the description for a category from category_definitions.py"""
    category_var_name = category_name.lower().replace(' ', '_').replace('-', '_')
    
    # Map of category names to their variable names in category_definitions.py
    category_mapping = {
        'argument': argument,
        'assessment': assessment,
        'calculation': calculation,
        'categorising': categorising,
        'classification': classification,
        'clustering': clustering,
        'comparison': comparison,
        'context_control': context_control,
        'contradiction': contradiction,
        'cross_boundary': cross_boundary,
        'decomposed_prompting': decomposed_prompting,
        'error_identification': error_identification,
        'hypothesise': hypothesise,
        'input_semantics': input_semantics,
        'logical_reasoning': logical_reasoning,
        'output_customisation': output_customisation,
        'output_semantics': output_semantics,
        'prediction': prediction,
        'prompt_improvement': prompt_improvement,
        'refactoring': refactoring,
        'requirements_elicitation': requirements_elicitation,
        'simulation': simulation,
        'summarising': summarising,
        'synthesis': synthesis,
        'translation': translation
    }
    
    return category_mapping.get(category_var_name, "No description available.").strip()

def get_logic_description(logic_name):
    """Get the description for a logic layer from category_definitions.py"""
    logic_mapping = {
        'Across': across,
        'At': at_logic,
        'Beyond': beyond_logic,
        'In': in_logic,
        'Out': out_logic,
        'Over': over_logic
    }
    
    return logic_mapping.get(logic_name, "No description available.").strip()

def process_patterns_from_source(source_data):
    """Extract pattern information from promptpatterns.json data"""
    patterns_by_category = {}
    
    for paper in source_data.get('Source', {}).get('Titles', []):
        for category_group in paper.get('CategoriesAndPatterns', []):
            category_name = category_group.get('PatternCategory', '')
            if not category_name:
                continue
                
            category_slug = slugify(category_name)
            
            if category_slug not in patterns_by_category:
                patterns_by_category[category_slug] = {
                    'name': category_name,
                    'slug': category_slug,
                    'patterns': [],
                    'patternCount': 0
                }
            
            for pattern in category_group.get('PromptPatterns', []):
                pattern_info = {
                    'id': f"{paper.get('id', 0)}-{category_group.get('CategoryID', 0)}-{pattern.get('PatternID', 0)}",
                    'name': pattern.get('PatternName', ''),
                    'description': pattern.get('Description', ''),
                    'exampleCount': len(pattern.get('ExamplePrompts', []))
                }
                patterns_by_category[category_slug]['patterns'].append(pattern_info)
    
    # Update pattern counts
    for category_data in patterns_by_category.values():
        category_data['patternCount'] = len(category_data['patterns'])
    
    return patterns_by_category

def generate_hierarchical_categories():
    """Generate the hierarchical category structure based on logic definitions"""
    
    # Read the source data to get actual patterns
    source_file = parent_dir / 'promptpatterns.json'
    patterns_by_category = {}
    
    if source_file.exists():
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
            patterns_by_category = process_patterns_from_source(source_data)
    
    hierarchical_structure = {
        'meta': {
            'generatedAt': '2025-01-28T00:00:00Z',
            'description': 'Hierarchical categorization based on English language logic',
            'totalLogics': len(LOGIC_DEFINITIONS),
            'totalCategories': sum(len(cats) for cats in CATEGORY_TEMPLATES.values())
        },
        'logics': []
    }
    
    for logic_name, logic_def in LOGIC_DEFINITIONS.items():
        logic_entry = {
            'name': logic_name,
            'slug': slugify(logic_name),
            'description': logic_def['description'],
            'focus': logic_def['focus'],
            'detailedDescription': get_logic_description(logic_name),
            'categories': []
        }
        
        # Get categories for this logic from CATEGORY_TEMPLATES
        if logic_name in CATEGORY_TEMPLATES:
            for category_name, category_data in CATEGORY_TEMPLATES[logic_name].items():
                category_slug = slugify(category_name)
                
                # Get patterns for this category if they exist
                category_patterns = patterns_by_category.get(category_slug, {})
                
                category_entry = {
                    'name': category_name.replace('_', ' ').title(),
                    'slug': category_slug,
                    'description': get_category_description(category_name),
                    'patternCount': category_patterns.get('patternCount', 0),
                    'patterns': category_patterns.get('patterns', []),
                    'hasLatexTable': 'latex_table' in category_data
                }
                
                logic_entry['categories'].append(category_entry)
        
        # Sort categories by name
        logic_entry['categories'].sort(key=lambda x: x['name'])
        logic_entry['categoryCount'] = len(logic_entry['categories'])
        
        hierarchical_structure['logics'].append(logic_entry)
    
    # Sort logics by name
    hierarchical_structure['logics'].sort(key=lambda x: x['name'])
    
    return hierarchical_structure

def main():
    """Main function to generate the pattern-categories.json file"""
    
    # Generate the hierarchical structure
    categories_data = generate_hierarchical_categories()
    
    # Write to the output file
    output_dir = parent_dir / 'prompt-pattern-dictionary' / 'public' / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'pattern-categories.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated hierarchical pattern-categories.json")
    print(f"Output: {output_file}")
    print(f"Generated {len(categories_data['logics'])} logic layers with {categories_data['meta']['totalCategories']} total categories")
    
    # Also generate a flat version for backward compatibility if needed
    flat_categories = []
    for logic in categories_data['logics']:
        for category in logic['categories']:
            flat_categories.append({
                'name': category['name'],
                'slug': category['slug'],
                'patternCount': category['patternCount'],
                'patterns': category['patterns'],
                'logic': logic['name'],
                'logicSlug': logic['slug']
            })
    
    flat_output_file = output_dir / 'pattern-categories-flat.json'
    with open(flat_output_file, 'w', encoding='utf-8') as f:
        json.dump(flat_categories, f, indent=2, ensure_ascii=False)
    
    print(f"Also generated flat version: {flat_output_file}")

if __name__ == '__main__':
    main()
