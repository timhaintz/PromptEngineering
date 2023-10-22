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
https://dreampuf.github.io/GraphvizOnline/
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
python createMindMap.py graphvizFiles --function generate_dot_file_opinionated_app_cat_pat
4. To generate a dot file for the opinionated mind map, run the following command:
```
python createMindMap.py graphvizFiles --function generate_dot_file_opinionated_cat_app_pat
'''
import os
import datetime
import json
import pydot
import argparse
# Importing at the global level to avoid circular imports
from categorisation_logic_app_cat_pat import root_node, domain_applications, application_categories, categories_patterns
from categorisation_logic_cat_app_pat import root_node, domain_categories, categories_applications, applications_patterns


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

def generate_dot_file_opinionated_app_cat_pat(folder_path, root_node):
    # Create the graph object
    graph = pydot.Dot(graph_type='digraph', rankdir='LR', ranksep='10', nodesep='0.1')
    # Create the legend subgraph

    legend_subgraph = pydot.Cluster(graph_name='legend', label='Legend', shape='box', rank='min')
    graph.add_subgraph(legend_subgraph)

    box_node = pydot.Node('Box', shape='box', label='Root Node')
    legend_subgraph.add_node(box_node)

    ellipse_node = pydot.Node('Ellipse', shape='ellipse', label='Domain')
    legend_subgraph.add_node(ellipse_node)

    diamond_node = pydot.Node('Diamond', shape='diamond', label='Application')
    legend_subgraph.add_node(diamond_node)

    diamond_node = pydot.Node('Pentagon', shape='pentagon', label='Category')
    legend_subgraph.add_node(diamond_node)

    diamond_node = pydot.Node('Plaintext', shape='plaintext', label='Pattern')
    legend_subgraph.add_node(diamond_node)

    # Add the root node to the graph
    root_node_name = list(root_node.keys())[0]
    root_node_label = root_node[root_node_name]
    root_node = pydot.Node(root_node_name, shape='box', label=root_node_label)
    graph.add_node(root_node)

    # Create dictionaries to keep track of nodes and edges
    domain_nodes = {}
    application_nodes = {}
    category_nodes = {}
    pattern_nodes = {}
    edges = {}
    
    # Loop over the domain names
    for domain_name in domain_applications:
        # Check if the domain node has already been added
        if domain_name in domain_nodes:
            domain_node = domain_nodes[domain_name]
        else:
            domain_node = pydot.Node(domain_name, shape='ellipse')
            graph.add_node(domain_node)
            domain_nodes[domain_name] = domain_node
        # Connect the domain node to the root node
        edge_name = f"{root_node_name}_{domain_name}"
        if edge_name not in edges:
            edge = pydot.Edge(root_node, domain_node)
            graph.add_edge(edge)
            edges[edge_name] = edge

        # Loop over the application names
        for application_name in domain_applications[domain_name]:
            # Check if the application node has already been added
            if application_name in application_nodes:
                application_node = application_nodes[application_name]
            else:
                application_node = pydot.Node(application_name, shape='diamond')
                graph.add_node(application_node)
                application_nodes[application_name] = application_node
            # Connect the domain node to the application node
            edge_name = f"{domain_name}_{application_name}"
            if edge_name not in edges:
                edge = pydot.Edge(domain_node, application_node)
                graph.add_edge(edge)
                edges[edge_name] = edge

            # Loop over the category names
            for category_name in application_categories[application_name]:
                # Check if the category node has already been added
                if category_name in category_nodes:
                    category_node = category_nodes[category_name]
                else:
                    category_node = pydot.Node(category_name, shape='pentagon')
                    graph.add_node(category_node)
                    category_nodes[category_name] = category_node

                # Connect the application node to the category node
                edge_name = f"{application_name}_{category_name}"
                if edge_name not in edges:
                    edge = pydot.Edge(application_node, category_node)
                    graph.add_edge(edge)
                    edges[edge_name] = edge

                # Loop over the pattern names
                for pattern_name in categories_patterns[category_name]:
                    # Check if the pattern node has already been added
                    if pattern_name in pattern_nodes:
                        pattern_node = pattern_nodes[pattern_name]
                    else:
                        pattern_node = pydot.Node(pattern_name, shape='plaintext')
                        graph.add_node(pattern_node)
                        pattern_nodes[pattern_name] = pattern_node

                    # Connect the category node to the pattern node
                    edge_name = f"{category_name}_{pattern_name}"
                    if edge_name not in edges:
                        edge = pydot.Edge(category_node, pattern_node, arrowhead='none')
                        graph.add_edge(edge)
                        edges[edge_name] = edge

    # Write the DOT file to disk
    dot_file_path = os.path.join(folder_path, 'opinionated.dot')
    graph.write(dot_file_path)
    
def generate_dot_file_opinionated_cat_app_pat(folder_path, root_node):
    # Create the graph object
    graph = pydot.Dot(graph_type='digraph', rankdir='LR', ranksep='10', nodesep='0.1')
    # Create the legend subgraph

    legend_subgraph = pydot.Cluster(graph_name='legend', label='Legend', shape='box', rank='min')
    graph.add_subgraph(legend_subgraph)

    box_node = pydot.Node('Box', shape='box', label='Root Node')
    legend_subgraph.add_node(box_node)

    ellipse_node = pydot.Node('Ellipse', shape='ellipse', label='Domain')
    legend_subgraph.add_node(ellipse_node)

    diamond_node = pydot.Node('Diamond', shape='diamond', label='Category')
    legend_subgraph.add_node(diamond_node)

    diamond_node = pydot.Node('Pentagon', shape='pentagon', label='Application')
    legend_subgraph.add_node(diamond_node)

    diamond_node = pydot.Node('Plaintext', shape='plaintext', label='Pattern')
    legend_subgraph.add_node(diamond_node)

    # Add the root node to the graph
    root_node_name = list(root_node.keys())[0]
    root_node_label = root_node[root_node_name]
    root_node = pydot.Node(root_node_name, shape='box', label=root_node_label)
    graph.add_node(root_node)

    # Create dictionaries to keep track of nodes and edges
    domain_nodes = {}
    application_nodes = {}
    category_nodes = {}
    pattern_nodes = {}
    edges = {}
    
    # Loop over the domain names
    for domain_name in domain_categories:
        # Check if the domain node has already been added
        if domain_name in domain_nodes:
            domain_node = domain_nodes[domain_name]
        else:
            domain_node = pydot.Node(domain_name, shape='ellipse')
            graph.add_node(domain_node)
            domain_nodes[domain_name] = domain_node
        # Connect the domain node to the root node
        edge_name = f"{root_node_name}_{domain_name}"
        if edge_name not in edges:
            edge = pydot.Edge(root_node, domain_node)
            graph.add_edge(edge)
            edges[edge_name] = edge

        # Loop over the category names
        for category_name in domain_categories[domain_name]:
            # Check if the category node has already been added
            if category_name in category_nodes:
                category_node = category_nodes[category_name]
            else:
                category_node = pydot.Node(category_name, shape='pentagon')
                graph.add_node(category_node)
                category_nodes[category_name] = category_node

            # Connect the domain node to the category node
            edge_name = f"{domain_name}_{category_name}"
            if edge_name not in edges:
                edge = pydot.Edge(domain_node, category_node)
                graph.add_edge(edge)
                edges[edge_name] = edge

            # Loop over the application names
            for application_name in categories_applications[category_name]:
                # Check if the application node has already been added
                if application_name in application_nodes:
                    application_node = application_nodes[application_name]
                else:
                    application_node = pydot.Node(application_name, shape='diamond')
                    graph.add_node(application_node)
                    application_nodes[application_name] = application_node

                # Connect the category node to the application node
                edge_name = f"{category_name}_{application_name}"
                if edge_name not in edges:
                    edge = pydot.Edge(category_node, application_node)
                    graph.add_edge(edge)
                    edges[edge_name] = edge

                # Loop over the pattern names
                for pattern_name in applications_patterns[application_name]:
                    # Check if the pattern node has already been added
                    if pattern_name in pattern_nodes:
                        pattern_node = pattern_nodes[pattern_name]
                    else:
                        pattern_node = pydot.Node(pattern_name, shape='plaintext')
                        graph.add_node(pattern_node)
                        pattern_nodes[pattern_name] = pattern_node

                    # Connect the application node to the pattern node
                    edge_name = f"{application_name}_{pattern_name}"
                    if edge_name not in edges:
                        edge = pydot.Edge(application_node, pattern_node, arrowhead='none')
                        graph.add_edge(edge)
                        edges[edge_name] = edge

    # Write the DOT file to disk
    dot_file_path = os.path.join(folder_path, 'opinionated.dot')
    graph.write(dot_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create mind maps from JSON and dictionary data')
    parser.add_argument('data_file', type=str, help='JSON data file')
    parser.add_argument('--function', type=str, choices=['generate_dot_files_per_title', 'generate_dot_file_category_and_pattern', 'generate_dot_file_opinionated_app_cat_pat', 'generate_dot_file_opinionated_cat_app_pat'], default='generate_dot_files_per_title', help='function to call')
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
    elif args.function == 'generate_dot_file_opinionated_app_cat_pat':
        folder_path = get_folder_path("Opinionated")
        generate_dot_file_opinionated_app_cat_pat(folder_path, root_node)
    elif args.function == 'generate_dot_file_opinionated_cat_app_pat':
        folder_path = get_folder_path("Opinionated")
        generate_dot_file_opinionated_cat_app_pat(folder_path, root_node)