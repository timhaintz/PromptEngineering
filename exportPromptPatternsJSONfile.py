'''
DESCRIPTION
Export the prompt patterns from the promptpatterns.json JSON file.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  26/7/2023
LINKS

'''

import json

# Open the JSON file
with open('promptpatterns.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Print the prompt patterns
for title in data['Source']['Titles']:
    print('Title:', title['Title'])
    for category in title['CategoriesAndPatterns']:
        print('\tPattern Category:', category['PatternCategory'])
        for pattern in category['PromptPatterns']:
            print('\t\tPattern Name:', pattern['PatternName'])
            print('\t\tExample Prompts:')
            for example in pattern['ExamplePrompts']:
                print('\t\t\t', example)
            print()