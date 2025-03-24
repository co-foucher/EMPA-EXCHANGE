import os
import re
from graphviz import Digraph


def replace_trailing_numbers_with_same_length_x(s):
    # Match files with or without extensions
    match = re.match(r'(.*?)(\d+)(\.[^.]+)?$', s)
    if match:
        base, numbers, extension = match.groups()
        extension = extension or ""  # Handle the case where there is no extension
        replacement = 'x' * len(numbers)  # Replace numbers with the same number of 'x'
        return f"{base}{replacement}{extension}"
    return s




def build_folder_structure_graph(start_path, graph=None, parent_node=None):
    """
    Recursively build the folder structure as a Graphviz graph.
    :param start_path: Path to start generating the structure.
    :param graph: The Graphviz Digraph object (initialized outside).
    :param parent_node: The parent node name in the graph (for recursion).
    """
    if graph is None:
        graph = Digraph(format='pdf', graph_attr={'rankdir': 'LR'}, node_attr={'shape': 'box'})

    #current_node = os.path.basename(start_path) or start_path
    current_node = os.path.basename(start_path)
    
    list_of_item = os.listdir(start_path)
    simplified = False
    if len(list_of_item) > 25:
        seventh_item = replace_trailing_numbers_with_same_length_x(list_of_item[5])
        list_of_item = list_of_item[:5] + [seventh_item] + list_of_item[-5:]
        simplified = True

    for item in list_of_item:
        item_path = os.path.join(start_path, item)
        if os.path.isdir(item_path):
            # Add folder node with a specific color
            graph.node(item, item, style="filled", fillcolor="lightyellow", shape="folder")
            graph.edge(current_node, item)
            build_folder_structure_graph(item_path, graph, item)
        else:
            if simplified:
                graph.node(item, item, style="filled", fillcolor="grey")
                graph.edge(current_node, item)  # Add files as leaf nodes
            elif item[-2:]=="py" or  item[-5:]=="ipynb":
                graph.node(item, item, style="filled", fillcolor="lightblue")
                graph.edge(current_node, item)  # Add files as leaf nodes
            else:
                graph.node(item, item)
                graph.edge(current_node, item)  # Add files as leaf nodes

            
    return graph



if __name__ == "__main__":
    # Get the directory where the script is saved
    script_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"Generating folder structure for: {script_directory}")

    # Build the folder structure graph
    folder_graph = build_folder_structure_graph(script_directory)

    # Save as a PDF
    output_filename = os.path.join(script_directory, "Folder_Structure")
    folder_graph.render(output_filename, view=True)  # Save and optionally open the PDF

    print(f"Folder structure saved to {output_filename}.pdf")



