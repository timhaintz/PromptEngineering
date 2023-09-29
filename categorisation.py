'''
DESCRIPTION
Using the promptpatterns.json file, categorise the patterns into categories, subcategories and patterns.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  29/9/2023
LINKS:
https://resources.github.com/copilot-for-business/
HELP:
1. To generate a dot file for each title, run the following command:
```
python categorisation.py promptpatterns.json 
```
This will generate a dot file for each title in the `graphvizFiles` folder.
2. 
```
python categorisation.py promptpatterns.json ...........
```
'''
import os
import datetime
import json


def print_patterns_by_category(category):
    # Load the JSON data from the file
    with open('promptpatterns.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get the patterns for the specified category
    patterns = []
    for title in data['Source']['Titles']:
        for cat in title['CategoriesAndPatterns']:
            if cat['PatternCategory'] == category:
                patterns += [pattern['PatternName'] for pattern in cat['PromptPatterns']]

    # Print the patterns for the specified category
    if patterns:
        print(f"Patterns for {category}:")
        for pattern in patterns:
            print(f"- {pattern}")
    else:
        print(f"No patterns found for {category}")