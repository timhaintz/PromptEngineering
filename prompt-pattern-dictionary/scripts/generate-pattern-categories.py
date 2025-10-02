#!/usr/bin/env python3
"""
Generate pattern-categories.json from the logic and category templates.

The resulting structure is organised by logic layers.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast


LogicDefinitions = Dict[str, Dict[str, Any]]
CategoryTemplates = Dict[str, Dict[str, Any]]
 
# Add the parent directory to Python path to import our modules
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from category_definitions import (
        across, at_logic, beyond_logic, in_logic, out_logic, over_logic,
        # Import all category definitions
        argument,
        assessment,
        calculation,
        categorising,
        classification,
        clustering,
        comparison,
        context_control,
        contradiction,
        cross_boundary,
        decomposed_prompting,
        error_identification,
        hypothesise,
        input_semantics,
        logical_reasoning,
        output_customisation,
        output_semantics,
        prediction,
        prompt_improvement,
        refactoring,
        requirements_elicitation,
        simulation,
        summarising,
        synthesis,
        translation,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)


def _extract_constant_from_module(
    module_path: Path,
    constant_name: str,
) -> Any:
    with module_path.open('r', encoding='utf-8') as f:
        source = f.read()
    tree = ast.parse(source, filename=str(module_path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == constant_name:
                    try:
                        return ast.literal_eval(node.value)
                    except Exception as exc:  # pragma: no cover
                        message = (
                            f"Failed to evaluate {constant_name} from "
                            f"{module_path}"
                        )
                        raise RuntimeError(message) from exc
    raise RuntimeError(
        f"Unable to locate {constant_name} in {module_path}"
    )


def load_logic_definitions() -> Tuple[LogicDefinitions, CategoryTemplates]:
    module_path = parent_dir / 'simple_categorisation_writeup.py'
    logic_defs = _extract_constant_from_module(
        module_path,
        'LOGIC_DEFINITIONS',
    )
    category_templates = _extract_constant_from_module(
        module_path,
        'CATEGORY_TEMPLATES',
    )
    return logic_defs, category_templates


LOGIC_DEFINITIONS, CATEGORY_TEMPLATES = load_logic_definitions()


def slugify(text: str) -> str:
    """Convert string to URL-friendly slug"""
    return text.lower().replace(' ', '-').replace('_', '-')


def get_category_description(category_name: str) -> str:
    """Get the description for a category from category_definitions.py"""
    category_var_name = (
        category_name.lower().replace(' ', '_').replace('-', '_')
    )
    
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
    
    return category_mapping.get(
        category_var_name,
        "No description available.",
    ).strip()


def get_logic_description(logic_name: str) -> str:
    """Get the description for a logic layer from category_definitions.py"""
    logic_mapping = {
        'Across': across,
        'At': at_logic,
        'Beyond': beyond_logic,
        'In': in_logic,
        'Out': out_logic,
        'Over': over_logic
    }

    return logic_mapping.get(
        logic_name,
        "No description available.",
    ).strip()


def process_patterns_from_source(
    source_data: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Extract pattern information from promptpatterns.json data"""
    patterns_by_category: Dict[str, Dict[str, Any]] = {}
    
    for paper in source_data.get('Source', {}).get('Titles', []):
        for category_group in paper.get('CategoriesAndPatterns', []):
            category_name = category_group.get('PatternCategory', '')
            if not category_name:
                continue
                
            category_slug = slugify(category_name)
            
            if category_slug not in patterns_by_category:
                empty_patterns: List[Dict[str, Any]] = []
                patterns_by_category[category_slug] = {
                    'name': category_name,
                    'slug': category_slug,
                    'patterns': empty_patterns,
                    'patternCount': 0
                }
            
            category_bucket = patterns_by_category[category_slug]
            patterns_list = cast(
                List[Dict[str, Any]],
                category_bucket['patterns'],
            )

            for pattern in category_group.get('PromptPatterns', []):
                pattern_info: Dict[str, Any] = {
                    'id': (
                        f"{paper.get('id', 0)}-"
                        f"{category_group.get('CategoryID', 0)}-"
                        f"{pattern.get('PatternID', 0)}"
                    ),
                    'name': pattern.get('PatternName', ''),
                    'description': pattern.get('Description', ''),
                    'exampleCount': len(pattern.get('ExamplePrompts', []))
                }
                patterns_list.append(pattern_info)
    
    # Update pattern counts
    for category_data in patterns_by_category.values():
        patterns_list = cast(List[Dict[str, Any]], category_data['patterns'])
        category_data['patternCount'] = len(patterns_list)
    
    return patterns_by_category


def generate_hierarchical_categories() -> Dict[str, Any]:
    """Build the hierarchical structure for logic layers and categories."""
    
    # Read the source data to get actual patterns
    source_file = parent_dir / 'promptpatterns.json'
    patterns_by_category: Dict[str, Dict[str, Any]] = {}
    
    if source_file.exists():
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
            patterns_by_category = process_patterns_from_source(source_data)
    
    logics_list: List[Dict[str, Any]] = []
    hierarchical_structure: Dict[str, Any] = {
        'meta': {
            'generatedAt': '2025-01-28T00:00:00Z',
            'description': (
                'Hierarchical categorization based on English language logic'
            ),
            'totalLogics': len(LOGIC_DEFINITIONS),
            'totalCategories': sum(
                len(categories)
                for categories in CATEGORY_TEMPLATES.values()
            ),
        },
        'logics': logics_list,
    }
    
    for logic_name, logic_def in LOGIC_DEFINITIONS.items():
        categories_list: List[Dict[str, Any]] = []
        logic_entry: Dict[str, Any] = {
            'name': logic_name,
            'slug': slugify(logic_name),
            'description': logic_def['description'],
            'focus': logic_def['focus'],
            'detailedDescription': get_logic_description(logic_name),
            'categories': categories_list,
        }
        
        # Get categories for this logic from CATEGORY_TEMPLATES
        if logic_name in CATEGORY_TEMPLATES:
            for category_name, category_data in CATEGORY_TEMPLATES[
                logic_name
            ].items():
                category_slug = slugify(category_name)
                
                # Get patterns for this category if they exist
                category_patterns = patterns_by_category.get(category_slug, {})
                category_entry: Dict[str, Any] = {
                    'name': category_name.replace('_', ' ').title(),
                    'slug': category_slug,
                    'description': get_category_description(category_name),
                    'patternCount': category_patterns.get('patternCount', 0),
                    'patterns': category_patterns.get('patterns', []),
                    'hasLatexTable': 'latex_table' in category_data
                }
                
                categories_list.append(category_entry)
        
        # Sort categories by name
        categories_list.sort(key=lambda item: item['name'])
        logic_entry['categoryCount'] = len(categories_list)
        
        logics_list.append(logic_entry)
    
    # Sort logics by name
    logics_list.sort(key=lambda item: item['name'])
    
    return hierarchical_structure


def main() -> None:
    """Generate the pattern category JSON artifacts."""
    
    # Generate the hierarchical structure
    categories_data: Dict[str, Any] = generate_hierarchical_categories()
    
    # Write to the output file
    output_dir = parent_dir / 'prompt-pattern-dictionary' / 'public' / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'pattern-categories.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, indent=2, ensure_ascii=False)
    
    print("Generated hierarchical pattern-categories.json")
    print(f"Output: {output_file}")
    logics_list = cast(List[Dict[str, Any]], categories_data['logics'])
    meta_info = cast(Dict[str, Any], categories_data['meta'])
    total_logics = len(logics_list)
    total_categories = meta_info['totalCategories']
    print(
        "Generated "
        f"{total_logics} logic layers with {total_categories} total categories"
    )
    
    # Also generate a flat version for backward compatibility if needed
    flat_categories: List[Dict[str, Any]] = []
    for logic in logics_list:
        categories_list = cast(List[Dict[str, Any]], logic['categories'])
        for category in categories_list:
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
