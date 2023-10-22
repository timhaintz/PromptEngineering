'''
DESCRIPTION
Leverages the categorisation_logic_app_cat_pat.py file to create the opposite dictionaries for the mind map.
Output is to the categorisation_logic_cat_app_pat.py file.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  19/10/2023
LINKS:
https://resources.github.com/copilot-for-business/
HELP:
1. To use the categories dictionary, import the library using the following command:
```
from categorisation_logic import categoriesAndPatterns
```
This will use the categories dictionary.
2. To use the application dictionary, import the library using the following command:
```
from categorisation_logic import application
```
'''
from categorisation_logic_app_cat_pat import root_node, domain_applications, application_categories, categories_patterns

# The root node of the mind map
root_node

# The second node of the mind map. This is the first level of the mind map. Used to map the high level domains and categories.
domain_categories = {}
for domain, applications in domain_applications.items():
    categories = []
    for application in applications:
        if application in application_categories:
            categories.extend(application_categories[application])
    domain_categories[domain] = categories

# # Print the new dictionary
# # Now you have new a new dictionary called domain_categories where the keys and values are swapped and duplicates are removed
# print("domain_categories = {")
# for key, value in domain_categories.items():
#     print(f'\t\'{key}\': {value}' ',')
# print("}")

# The third node of the mind map. This is the second level of the mind map. Used to map the applications and categories.
# Create the categories_applications dictionaries
categories_applications = {}
for app, categories in application_categories.items():
    for category in categories:
        if category not in categories_applications:
            categories_applications[category] = [app]
        elif app not in categories_applications[category]:
            categories_applications[category].append(app)

# # Print the new dictionary
# # Now you have new a new dictionary called categories_applications where the keys and values are swapped and duplicates are removed
# print("categories_applications = {")
# for key, value in categories_applications.items():
#     print(f'\t\'{key}\': {value}' ',')
# print("}")


# The fourth node of the mind map. This is the third level of the mind map. Used to map the categories and patterns.
# # Create the application_patterns dictionary
# Create the application_patterns dictionary
applications_patterns = {}
for app, categories in application_categories.items():
    applications_patterns[app] = []
    for category, patterns in categories_patterns.items():
        if category in categories:
            applications_patterns[app].extend(patterns)

# Remove duplicates from the values in the application_patterns dictionary
applications_patterns = {k: list(set(v)) for k, v in applications_patterns.items()}

# # print application_patterns
# print("applications_patterns = { ")
# for i, (key, value) in enumerate(application_patterns.items()):
#     end = ',' if i < len(application_patterns) - 1 else ''
#     print(f'\t\'{key}\': {value}{end}')
# print('}')

# Not used in the mindmap. A dictionary of pattern descriptions if there is not a direct link of a prompt name to a research paper
pattern_descriptions = {
    'Multi-Criteria Rating': 'This pattern refers to Pattern Category: N/A and Pattern Name Expert #1 - #4 for the id:3 research paper in promptpatterns.json.',
}

# Read the file into a string
with open('categorisation_logic_cat_app_pat.py', 'r') as file:
    file_contents = file.read()

# Replace the placeholders with the string representations of your dictionaries
file_contents = file_contents.replace('"<<REPLACE DOMAIN_CATEGORIES>>"', str(domain_categories))
file_contents = file_contents.replace('"<<REPLACE CATEGORIES_APPLICATIONS>>"', str(categories_applications))
file_contents = file_contents.replace('"<<REPLACE APPLICATIONS_PATTERNS>>"', str(applications_patterns))

# Write the string back to the file
with open('categorisation_logic_cat_app_pat.py', 'w') as file:
    file.write(file_contents)