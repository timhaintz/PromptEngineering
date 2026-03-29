"""Q2: Track where Analysis category patterns were redistributed."""
import json

with open('recategorization_report_20250730_110545.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The 15 patterns that were in 'Analysis' category before removal
analysis_patterns = [
    'Meta Language Creation', 'Template', 'Reflection', 'Persona',
    'Visualization Generator', 'Restrict', 'Cognitive Verifier', 
    'Question Refinement', 'Refusal Breaker', 'Alternative Approaches',
    'Contradiction', 'Fact Check List', 'Free-Form Questions', 'Recipe',
    'Output Automater'
]

print("=== Q2: Analysis Category Pattern Redistribution ===")
print("Before: All 15 patterns in 'Analysis' category")
print("After removal (commit 006f59c, 29 Jan 2024):")
print()

found = []
for change in data['analysis']['pattern_category_changes']:
    if change['pattern_name'] in analysis_patterns:
        found.append(change)
        print(f"  {change['pattern_name']}")
        print(f"    Original: {change['original_category']}")
        print(f"    Semantic: {change['semantic_category']} (conf: {change['confidence']:.4f})")
        print()

not_found = set(analysis_patterns) - set(c['pattern_name'] for c in found)
if not_found:
    print(f"Not found in recategorization report: {not_found}")

# Also check the original categories from paper 0 in promptpatterns.json
with open('promptpatterns.json', 'r', encoding='utf-8') as f:
    pp = json.load(f)

print("\n=== Current categories in promptpatterns.json (Paper 0 - White et al.) ===")
paper0 = pp['Source']['Titles'][0]
for cat in paper0['CategoriesAndPatterns']:
    patterns = [p['PatternName'] for p in cat['PromptPatterns']]
    matching = [p for p in patterns if p in analysis_patterns]
    if matching:
        print(f"  Category '{cat['PatternCategory']}': {matching}")
