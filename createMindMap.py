'''
DESCRIPTION
Create MindMap from JSON
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  21/8/2023
LINKS
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart?tabs=command-line&pivots=programming-language-python
https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-virtual-networks?tabs=portal
https://resources.github.com/copilot-for-business/
'''
import os
import datetime
import json
import pydot

# Get the current date and time
now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Create the folder path with the current date and time
folder_path = os.path.join('graphvizFiles', now)

# Create the folder if it does not exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Load the JSON data from the file
with open('promptpatterns.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Loop through each title and generate a DOT file for each title
for title in data['Source']['Titles']:
    # Create a new graph
    graph = pydot.Dot(graph_type='digraph')

    # Add the title as the root node
    root_node = pydot.Node(title['Title'])
    graph.add_node(root_node)

    # Loop through each category and pattern and add them as child nodes
    for category in title['CategoriesAndPatterns']:
        category_node = pydot.Node(category['PatternCategory'])
        graph.add_node(category_node)
        graph.add_edge(pydot.Edge(root_node, category_node))
        for pattern in category['PromptPatterns']:
            pattern_node = pydot.Node(pattern['PatternName'])
            graph.add_node(pattern_node)
            graph.add_edge(pydot.Edge(category_node, pattern_node))

            # Create the file name with the current date and time
            file_name = os.path.join(folder_path, title['Title'].replace(' ', '_').lower() + '.dot')
            graph.write(file_name)