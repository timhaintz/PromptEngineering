'''
DESCRIPTION
Create MindMap from JSON
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  21/8/2023
LINKS:
https://resources.github.com/copilot-for-business/
https://graphviz.org/
HELP:
1. To generate a dot file for each title, run the following command:
```
python createMindMap.py promptpatterns.json graphvizFiles --function generate_dot_files_per_title
```
This will generate a dot file for each title in the `graphvizFiles` folder.
2. To generate a dot file for the categories and patterns, run the following command:
```
python createMindMap.py promptpatterns.json graphvizFiles --function generate_dot_file_category_and_pattern
```
This will generate a dot file for the categories and patterns in the `graphvizFiles` folder.
'''
import os
import datetime
import json
import pydot
import argparse

def get_folder_path(folder_name=None):
    # Get the current UTC time
    now_utc = datetime.datetime.utcnow()

    # Format the UTC time as a string
    now_utc_str = now_utc.strftime('%Y-%m-%d_%H-%M-%S')

    # Create the folder path with the current date and time
    if folder_name is None:
        folder_path = os.path.join('graphvizFiles', now_utc_str)
    else:
        folder_path = os.path.join('graphvizFiles', now_utc_str + '_' + folder_name)

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path

def generate_dot_files_per_title(data, folder_path):
    # Loop through each title and create a dot file
    for title in data['Source']['Titles']:
        # Create a new graph
        graph = pydot.Dot(graph_type='digraph', rankdir='LR')

        # Add the title as the root node
        root_node = pydot.Node(title['Title'], shape='box')
        graph.add_node(root_node)

        # Loop through each category and pattern and add them as child nodes
        for category in title['CategoriesAndPatterns']:
            category_node = pydot.Node(category['PatternCategory'], shape='box')
            graph.add_node(category_node)
            graph.add_edge(pydot.Edge(root_node, category_node))
            for pattern in category['PromptPatterns']:
                pattern_node = pydot.Node(pattern['PatternName'], shape='box')
                graph.add_node(pattern_node)
                graph.add_edge(pydot.Edge(category_node, pattern_node))

        file_name = os.path.join(folder_path, title['Title'].replace(' ', '_').lower() + '.dot')                
        graph.write(file_name)

def generate_dot_file_category_and_pattern(data, folder_path):
    # Create a new graph
    graph = pydot.Dot(graph_type='digraph', rankdir='LR')

    # Loop through each category and pattern and add them as child nodes
    for title in data['Source']['Titles']:
        for category in title['CategoriesAndPatterns']:
            category_node = pydot.Node(category['PatternCategory'], shape='box')
            graph.add_node(category_node)
            for pattern in category['PromptPatterns']:
                pattern_node = pydot.Node(pattern['PatternName'], shape='box')
                graph.add_node(pattern_node)
                graph.add_edge(pydot.Edge(category_node, pattern_node))

    # Create the file name with the current date and time
    file_name = os.path.join(folder_path, 'CategoriesAndPatterns.dot')                
    graph.write(file_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create mind maps from JSON data')
    parser.add_argument('data_file', type=str, help='JSON data file')
    parser.add_argument('--function', type=str, choices=['generate_dot_files_per_title', 'generate_dot_file_category_and_pattern'], default='generate_dot_files_per_title', help='function to call')
    args = parser.parse_args()

    # Load the JSON data from the file
    with open('promptpatterns.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Call the specified function
    if args.function == 'generate_dot_files_per_title':
        folder_path = get_folder_path("Titles")
        generate_dot_files_per_title(data, folder_path)
    elif args.function == 'generate_dot_file_category_and_pattern':
        folder_path = get_folder_path("CattegoryAndPattern")
        generate_dot_file_category_and_pattern(data, folder_path)