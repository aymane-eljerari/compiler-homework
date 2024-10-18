import igraph as ig

# New function to add dominator sets next to each node
def generate_control_flow_with_dominators(graph_dict, dominator_dict):
    # Create an empty graph
    g = ig.Graph(directed=True)
    
    # Add vertices
    vertices = list(graph_dict.keys())
    g.add_vertices(len(vertices))
    g.vs['name'] = vertices
    
    # Add edges
    edges = []
    for source, targets in graph_dict.items():
        source_index = vertices.index(source)
        for target in targets:
            target_index = vertices.index(target)
            edges.append((source_index, target_index))
    g.add_edges(edges)
    
    # Define a custom layout
    layout = g.layout('rt')  # Use the Reingold-Tilford (rt) layout
    
    # Manually adjust the layout to place the first node at the top
    # layout[0] = (0, 1)  # Root node at the top-center
    
    # Color the root node orange and others blue
    g.vs['color'] = ['orange'] + ['lightblue'] * (len(vertices) - 1)
    
    # Modify labels to include dominators for each node
    labels_with_dominators = []
    for node in vertices:
        dominators = dominator_dict.get(node, set())  # Get dominators or empty set
        dominator_str = ', '.join(dominators) if dominators else 'None'
        label = f"{node}\n[{dominator_str}]"
        labels_with_dominators.append(label)
    
    # Save the plot as a PNG file with updated labels
    ig.plot(g, layout=layout, target='dominator_graph.png',
            title="Control Flow Graph with Dominators",
            vertex_label=labels_with_dominators, 
            vertex_color=g.vs['color'], 
            vertex_size=50,  # Increase node size
            bbox=(1000, 1000),  # Set the width and height of the image (width, height)
            margin=150)  # Add margin around the plot
    

def generate_dominance_tree_graph(graph_dict):
    # Create an empty directed graph
    g = ig.Graph(directed=True)

    # Add vertices
    vertices = list(graph_dict.keys())
    g.add_vertices(len(vertices))
    g.vs['name'] = vertices

    # Add edges based on the dictionary
    edges = []
    for parent, children in graph_dict.items():
        parent_index = vertices.index(parent)
        for child in children:
            # Check if child is not already in vertices
            if child not in vertices:
                vertices.append(child)
                g.add_vertices(1)
            child_index = vertices.index(child)
            edges.append((parent_index, child_index))
    g.add_edges(edges)

    # Define the Reingold-Tilford layout ('rt') for a tree structure
    layout = g.layout('rt')

    # Manually set the root node (first node in the dictionary) to be at the top
    # layout[0] = (0, 1)  # Top-center position for the first node

    # Set colors: root node is orange, others are blue
    g.vs['color'] = ['orange'] + ['lightblue'] * (len(vertices) - 1)

    # Plot the graph and save it as 'tree_graph.png'
    ig.plot(g, layout=layout, target='dominance_tree_graph.png',
            vertex_label=g.vs['name'],  # Label the vertices with their names
            vertex_color=g.vs['color'],  # Set the node colors
            vertex_size=50,  # Size of the nodes
            bbox=(1000, 1000),  # Size of the output image
            margin=150)  # Margin for spacing

