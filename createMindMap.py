'''
DESCRIPTION
Create MindMap from JSON and Python dictionary data
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
3. To generate a dot file for the opinionated mind map, run the following command:
```
python createMindMap.py graphvizFiles --function generate_dot_file_opinionated
'''
import os
import datetime
import json
import pydot
import argparse
# Importing at the global level to avoid circular imports
from categorisation_logic import root_node, domain, application, categories_and_patterns


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


def generate_dot_file_opinionated(folder_path):
    # Create the graph object
    graph = pydot.Dot(graph_type='digraph')

    # Add the root node to the graph
    root_node_name = list(root_node.keys())[0]
    root_node_label = root_node[root_node_name]
    root_node = pydot.Node(root_node_name, shape='box', label=root_node_label)
    graph.add_node(root_node)

    # Add the domain and application nodes to the graph
    for domain_name, application_names in domain.items():
        domain_node = pydot.Node(domain_name, shape='box')
        graph.add_node(domain_node)
        graph.add_edge(pydot.Edge(root_node, domain_node))
        for application_name in application_names:
            application_node = pydot.Node(application_name, shape='box')
            graph.add_node(application_node)
            graph.add_edge(pydot.Edge(domain_node, application_node))

            # Add the categories and patterns to the graph
            for category_name, pattern_names in categoriesAndPatterns.items():
                if category_name.startswith(application_name):
                    category_node = pydot.Node(category_name, shape='box')
                    graph.add_node(category_node)
                    graph.add_edge(pydot.Edge(application_node, category_node))
                    for pattern_name in pattern_names:
                        pattern_node = pydot.Node(pattern_name, shape='box')
                        graph.add_node(pattern_node)
                        graph.add_edge(pydot.Edge(category_node, pattern_node))

    # Write the DOT file to disk
    dot_file_path = os.path.join(folder_path, 'opinionated.dot')
    graph.write_dot(dot_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create mind maps from JSON and dictionary data')
    parser.add_argument('data_file', type=str, help='JSON data file')
    parser.add_argument('--function', type=str, choices=['generate_dot_files_per_title', 'generate_dot_file_category_and_pattern', 'generate_dot_file_opinionated'], default='generate_dot_files_per_title', help='function to call')
    args = parser.parse_args()

    # Load the JSON data from the file
    with open('promptpatterns.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Call the specified function
    if args.function == 'generate_dot_files_per_title':
        folder_path = get_folder_path("Titles")
        generate_dot_files_per_title(data, folder_path)
    elif args.function == 'generate_dot_file_category_and_pattern':
        folder_path = get_folder_path("CategoryAndPattern")
        generate_dot_file_category_and_pattern(data, folder_path)
    elif args.function == 'generate_dot_file_opinionated':
        folder_path = get_folder_path("Opinionated")
        generate_dot_file_opinionated(folder_path)