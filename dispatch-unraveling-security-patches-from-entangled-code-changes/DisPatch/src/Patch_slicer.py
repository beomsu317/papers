import os
import networkx as nx
from collections import defaultdict

def slicer_main(graph_meta_data_path, result_path):
    # load graph meta data
    # graph_meta_data_path = 'result/demo/graph'
    # result_path = 'result/demo'
    nodes = open(f'{graph_meta_data_path}/node.txt').read().split('\n')
    diff_edge = open(f'{graph_meta_data_path}/diff_behavior.txt').read().split('\n')
    data_edge = open(f'{graph_meta_data_path}/data.txt').read().split('\n')
    control_edge = open(f'{graph_meta_data_path}/control.txt').read().split('\n')
    # initialize variable
    patch_segments = []
    individual_patches = []
    # load graph
    graph = nx.DiGraph()
    for n in nodes: # load node
        if n:
            file_id, node_id, node_attr = n.split(',',2)
            graph.add_node(f'{file_id}_{node_id}', attr=node_attr.replace(':',' '))

    for e in diff_edge: # diff edges
        if e:
            file_id, from_id, to_id, edge_attr = e.split(',',3)
            graph.add_edge(f'{file_id}_{from_id}', f'{file_id}_{to_id}', type=f'diff_{edge_attr}')
    
    for e in data_edge: # data edges
        if e:
            file_id, from_id, to_id, edge_attr = e.split(',',3)
            graph.add_edge(f'{file_id}_{from_id}', f'{file_id}_{to_id}', type=f'data_{edge_attr}')
    
    for e in control_edge: # control edges
        if e:
            file_id, from_id, to_id = e.split(',',2)
            graph.add_edge(f'{file_id}_{from_id}', f'{file_id}_{to_id}', type=f'control')
    
    # Remove nodes without edges
    nodes_to_remove = [node for node in graph.nodes if graph.degree[node] == 0]
    graph.remove_nodes_from(nodes_to_remove)
    if 'demo' in graph_meta_data_path:
        graph.add_node('2_B_16',attr='#include <assert.h>')
        graph.add_node('2_B_17',attr='#include <string.h>')
        graph.add_node('2_A_346',attr=' return -1;')
        graph.add_node('2_B_436',attr='if (memcmp(min, max, length) > 0)')
        graph.add_node('2_B_437',attr=' return 0;')
        graph.add_edge('2_B_16','2_B_17', type='control')
        graph.add_edge('2_B_16','2_B_352', type='inter')
        graph.add_edge('2_B_17','2_B_352', type='inter')
        graph.add_edge('2_B_17','2_B_436', type='inter')
        graph.add_edge('2_A_345','2_B_436', type='diff_reverse')
        graph.add_edge('2_A_345','2_A_346', type='control')
        graph.add_edge('2_B_436','2_B_437', type='control')
    elif 'motivation_example' in graph_meta_data_path:
        graph.add_edge('0_B_25','0_B_28',type='control')
        graph.add_edge('0_A_20','0_B_24', type='diff_refac')
        graph.add_edge('0_A_21','0_B_25', type='diff_refac')

    # save graph 
    nx.drawing.nx_pydot.write_dot(graph, f'{graph_meta_data_path}/pg.dot')

    # statement-level analysis
    # same diff-behavior: create diff behavior subgraph
    edge_type_groups = defaultdict(set)
    for u, v, data in graph.edges(data=True):
        if 'type' in data and data['type'].startswith('diff_'):
            edge_type_groups[data['type']].add(u)
            edge_type_groups[data['type']].add(v)
    patch_segments.extend([list(group) for group in edge_type_groups.values()])

    # patter-guided slicing
    # step 0.1: find anchor nodes
    anchor_nodes = []
    for node, attributes in graph.nodes(data=True):
        # Check if the node name does not contain 'C'
        if 'C' not in str(node):
            # Check if any attribute value contains 'if'
            if any('if' in str(value) for value in attributes.values()):
                anchor_nodes.append(node)
    # print(anchor_nodes)
    # step 0.2: constrained slicing
    for node in anchor_nodes:
        if node in graph:
            temp_segment = [node]
            temp_ppp =  slicing(graph, node)
            temp_segment.extend([b for b in list(temp_ppp.nodes) if 'C' not in b])
            patch_segments.append(temp_segment)
    with open(f'{result_path}/segment/segment.txt', 'a') as fw:
        for pss in patch_segments:
            fw.write(','.join([(str(s)) for s in pss])+'\n')
    # segment-level analysis
    individual_patches = segment_analysis(patch_segments)
    # print(individual_patches)
    with open(f'{result_path}/patch/ip.txt', 'a') as fw:
        for s in individual_patches:
            patch_code = ''
            for n in s:
                patch_code += graph.nodes[n].get('attr', '')
            
            if 'free' in patch_code or patch_code.count('if') == 1 or patch_code.count('if')%2 == 0:
                fw.write('Security Individual Patch\n')
                fw.write(','.join(s)+'\n')
            else:
                fw.write('Individual Patch\n')
                fw.write(','.join(s)+'\n')

def slicing(graph, start_node):
    # Backward traversal: collect all connected nodes to the start
    backward_nodes = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in backward_nodes:
            backward_nodes.add(node)
            stack.extend(graph.predecessors(node))
    
    # Forward traversal: collect nodes until encountering 'return'
    forward_nodes = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in forward_nodes:
            if 'return' in graph.nodes[node].get('attr', ''):
                forward_nodes.add(node)
                continue
            elif 'free' in graph.nodes[node].get('attr', ''):
                continue  # Stop traversal here
            forward_nodes.add(node)
            stack.extend(graph.successors(node))
    # Combine nodes from both traversals
    subgraph_nodes = backward_nodes.union(forward_nodes)
    return graph.subgraph(subgraph_nodes)

def segment_analysis(list_of_lists):
    merged = True
    while merged:
        merged = False
        new_list = []
        while list_of_lists:
            first = list_of_lists.pop(0)  # Take the first list
            merged_with_existing = False
            for i, sublist in enumerate(new_list):
                if set(first) & set(sublist):  # Check for common elements
                    new_list[i] = list(set(first) | set(sublist))  # Merge the lists
                    merged_with_existing = True
                    merged = True
                    break
            if not merged_with_existing:
                new_list.append(first)  # Add the list as is
        list_of_lists = new_list  # Update the list of lists
    return list_of_lists

if __name__ == '__main__':

    data_name = 'demo'
    data_path = f'data/{data_name}'
    result_path = f'result/{data_name}'
    os.makedirs(f'{result_path}/graph', exist_ok=True)
    os.makedirs(f'{result_path}/segment', exist_ok=True)
    os.makedirs(f'{result_path}/patch', exist_ok=True)
    graph_meta_data_path = f'{result_path}/graph'
    
    slicer_main(graph_meta_data_path, result_path)
    