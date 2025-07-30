import re, os
# from utils import *
from difflib import SequenceMatcher
import tree_sitter_c
from tree_sitter import *

file_header_pattern = re.compile(r'^diff --git a/(.*?) b/\1')
hunk_pattern = re.compile(r'^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@')
pre_patch_file_pattern = re.compile(r'^--- (a/.*)')
post_patch_file_pattern = re.compile(r'^\+\+\+ (b/.*)')

C_LANGUAGE = Language(tree_sitter_c.language())
parser = Parser(C_LANGUAGE)

def control_edges(tree, version, result_path, change_lines, file_id):
    if not tree:
        return

    # Initialize a graph
    edges = [] 
    ret_edges = []

    ret_stmt_line = [] # record the return line, and remove all the edges start from return statement
    goto_stmt_line_dict = {} # record the goto stmt, and only keep the goto to label and remove the rest
    goto_stmt_line = []
    goto_label_line_dict = {}

    # Use a queue to traverse the tree level by level
    queue = [(tree, 0)]  # (node, depth)
    levels = {}

    while queue:
        current_node, depth = queue.pop(0)

        if depth not in levels:
            levels[depth] = {"left": [], "right": []}

        # Assuming the first child is considered "left" and the last child is "right"
        if current_node.children:
            # print(current_node.start_point.row, current_node.text)
            # terminate with return
            if 'return' in current_node.text.decode():
                ret_stmt_line.append(current_node.end_point.row)

            if current_node.type == 'labeled_statement':
                goto_label_line_dict[current_node.children[0].text.decode()] = current_node.children[0].start_point.row
            
            if current_node.type == 'goto_statement':
                goto_stmt_line.append(current_node.children[0].start_point.row)
                if current_node.children[-2].text.decode() in goto_stmt_line_dict:
                    goto_stmt_line_dict[current_node.children[-2].text.decode()].append(current_node.children[0].start_point.row)
                else:
                    goto_stmt_line_dict[current_node.children[-2].text.decode()] = [current_node.children[0].start_point.row]

            levels[depth]["left"].append(current_node.children[0].text)
            queue.append((current_node.children[0], depth + 1))
            edges.append([current_node.start_point.row, current_node.children[0].start_point.row]) # link the node with its root
            
            if current_node.type == 'compound_statement':
                if current_node.parent:
                    if current_node.parent.children[0].text.decode() == 'else':
                        if current_node.parent.parent.next_sibling:
                            edges.append([current_node.end_point.row, current_node.parent.parent.next_sibling.start_point.row]) # link the node with its root
                    elif current_node.parent.next_sibling:
                        edges.append([current_node.end_point.row, current_node.parent.next_sibling.start_point.row]) # link the node with its root

            
            if len(current_node.children) > 1: # right node
                levels[depth]["right"].append(current_node.children[-1].text)
                queue.append((current_node.children[-1], depth + 1))
                edges.append([current_node.children[-2].start_point.row, current_node.children[-1].start_point.row]) # link the node with its previous sibling
                
                if current_node.next_sibling:
                    edges.append([current_node.children[-1].start_point.row, current_node.next_sibling.start_point.row]) # link the node with its root's next sibling

        for i, child in enumerate(current_node.children[1:-1]):
            queue.append((child, depth + 1))
            if 'if' in current_node.children[i].text.decode() and 'else' in current_node.children[i].text.decode():
                pass
                # print([current_node.children[i].start_point.row, child.start_point.row])
            else:
                edges.append([current_node.children[i].start_point.row, child.start_point.row]) # link the node at the same level

    for e in edges: # deduplicate edges, remove return and goto out edges
        if e[0] != e[1] and e not in ret_edges:
            if e[0] in ret_stmt_line or e[0] in goto_stmt_line:
                continue
            ret_edges.append([e[0],e[1]])
    # add goto
    for a_goto_label in goto_stmt_line_dict:
        for a_from in goto_stmt_line_dict[a_goto_label]:
            ret_edges.append([a_from, goto_label_line_dict[a_goto_label]])
    
    with open(f'{result_path}/graph/control.txt','a') as fw:
        for edge in ret_edges :
            if edge[0]+1 in change_lines and edge[1]+1 in change_lines:
                fw.write(f'{file_id},{version}_{str(edge[0]+1)},{version}_{str(edge[1]+1)}\n')
            elif edge[0]+1 in change_lines and edge[1]+1 not in change_lines:
                fw.write(f'{file_id},{version}_{str(edge[0]+1)},C{version}_{str(edge[1]+1)}\n')
            elif edge[0]+1 not in change_lines and edge[1]+1 in change_lines:
                fw.write(f'{file_id},C{version}_{str(edge[0]+1)},{version}_{str(edge[1]+1)}\n')
            else:
                fw.write(f'{file_id},C{version}_{str(edge[0]+1)},C{version}_{str(edge[1]+1)}\n')

    return ret_edges

def is_left_of_assignment(target, code_line):
    """
    Checks if the given string is on the left side of a standalone '=' in the code line.

    Args:
        target (str): The string to check.
        code_line (str): The line of code to analyze.

    Returns:
        bool: True if the string is on the left of a standalone '=', False otherwise.
    """
    # Regular expression to find standalone '=' with a left-hand variable
    pattern = rf'\b{re.escape(target)}\b\s*='
    # Exclude cases where '=' is part of '==', '>=', '<=', or '!='
    exclude_pattern = r'(==|<=|>=|!=)'
    
    if re.search(exclude_pattern, code_line):
        return False
    
    # Match the standalone assignment '='
    match = re.search(pattern, code_line)
    if match:
        # Check if the matched '=' is not part of a chained assignment
        before_match = code_line[:match.start()]
        # Ensure no other '=' before the target in the line
        if '=' not in before_match:
            return True

    return False

def get_variable_declaration(node, leaves):
    """Traverse the tree-sitter AST and print all leaf nodes."""
    if len(node.children) == 0:  # Leaf node has no children
        if node.type == 'identifier' or node.type == 'field_identifier':
            # print(f"{node.type},{node.text},[{node.start_point.row},{node.end_point}]")
            leaves.append([node.text.decode(), node.type, node.start_point.row, 1]) # record the variables declaration
    else:
        for child in node.children:
            get_variable_declaration(child,leaves)

def get_variable_usage(node, vars, leaves):
    """Traverse the tree-sitter AST and print all leaf nodes."""
    if len(node.children) == 0:  # Leaf node has no children
        var = node.text.decode()
        if node.type == 'identifier':
            if var in vars:
                if node.parent.type == 'assignment_expression' and '=' in node.parent.text.decode():
                    if is_left_of_assignment(var, node.parent.text.decode()):
                        leaves.append([var, node.type, node.start_point.row, 1]) # record the variables usage
                else:
                    leaves.append([var, node.type, node.start_point.row, 0]) # record the variables usage
        elif node.type == 'field_identifier':
            leaves.append([var, node.type, node.start_point.row])

    else:
        for child in node.children:
            get_variable_usage(child,vars, leaves)


def data_edges(sub_root_node, version, result_path, change_lines, file_id):
    # record all data
    edges = []
    ret_edge = []
    variables_with_declaration_line = [] # var, var.type, var.start_point.row, update or not
    variables = []
    variables_usage = []

    for sub_sub_root in sub_root_node.children: # inside one function, find the function body
        # print(sub_sub_root.type)
        if sub_sub_root.type == 'pointer_declarator' or sub_sub_root.type == 'function_declarator':
            # print(sub_sub_root.text)
            get_variable_declaration(sub_sub_root,variables_with_declaration_line)
            variables_with_declaration_line = variables_with_declaration_line[1:] # exclude function name
            variables = {i[0]:i[2] for i in variables_with_declaration_line}

        if sub_sub_root.type == 'compound_statement':
            for statement in sub_sub_root.children: # inside the function body, traverse each statement
                if statement.type == 'declaration':
                    get_variable_declaration(statement,variables_with_declaration_line)
                    variables = {i[0]:i[2] for i in variables_with_declaration_line}
                else:
                    get_variable_usage(statement, variables, variables_usage)
                

    for each_usage in variables_usage:
        if each_usage[1] == 'identifier':
            edges.append([variables[each_usage[0]],each_usage[2], each_usage[0]])
            if each_usage[-1] == 1:
                variables[each_usage[0]] = each_usage[2]
        else:
            edges[-1][-1] += f', {edges[-1][-1]}->{each_usage[0]}'
    
    with open(f'{result_path}/graph/data.txt','a') as fw:
        for edge in edges:
            if edge[0] == edge[1]: continue
            if edge[0]+1 in change_lines and edge[1]+1 in change_lines:
                fw.write(f'{file_id},{version}_{str(edge[0]+1)},{version}_{str(edge[1]+1)},{edge[2]}\n')
                ret_edge.append(f'{file_id},{version}_{str(edge[0]+1)},{version}_{str(edge[1]+1)},{edge[2]}')
            elif edge[0]+1 in change_lines and edge[1]+1 not in change_lines:
                fw.write(f'{file_id},{version}_{str(edge[0]+1)},C{version}_{str(edge[1]+1)},{edge[2]}\n')
                ret_edge.append(f'{file_id},{version}_{str(edge[0]+1)},C{version}_{str(edge[1]+1)},{edge[2]}')
            elif edge[0]+1 not in change_lines and edge[1]+1 in change_lines:
                fw.write(f'{file_id},C{version}_{str(edge[0]+1)},{version}_{str(edge[1]+1)},{edge[2]}\n')
                ret_edge.append(f'{file_id},C{version}_{str(edge[0]+1)},{version}_{str(edge[1]+1)},{edge[2]}')
            else:
                fw.write(f'{file_id},C{version}_{str(edge[0]+1)},C{version}_{str(edge[1]+1)},{edge[2]}\n')
                ret_edge.append(f'{file_id},C{version}_{str(edge[0]+1)},C{version}_{str(edge[1]+1)},{edge[2]}')

    return ret_edge


def diff_behavior(diff_hunk, result_path, file_id):
    deleted_lines = [] # record the line and whether be considered as diff behavior
    added_lines = []
    hunk_match = hunk_pattern.match(diff_hunk[0])

    pre_start = int(hunk_match.group(1))
    post_start = int(hunk_match.group(3))

    ret_diff_behavior = []

    for line in diff_hunk[1:]:
        if line.startswith('-'):
            deleted_lines.append([file_id, pre_start, 'A', 0, line])
            pre_start += 1
        elif line.startswith('+'):
            added_lines.append([file_id, post_start, 'B', 0, line])
            post_start += 1

    
    for del_line in deleted_lines:
        del_line_code = del_line[-1][1:].strip('\n').strip(';').strip()
        for ad_line in added_lines:
            ad_line_code = ad_line[-1][1:].strip('\n').strip(';').strip()
            matcher = SequenceMatcher(None, del_line_code.replace(' ',''), ad_line_code.replace(' ',''))
            common_parts = [del_line_code[match.a:match.a + match.size] for match in matcher.get_matching_blocks() if match.size > 0]
            if len(common_parts) > 0 and del_line[-2] == 0 and ad_line[-2] == 0 and '*' not in ad_line_code: # to be extended
                if any(len(str(element)) > 1 for element in common_parts):
                    del_line[-2] = 1
                    ad_line[-2] = 1
                    with open(f'{result_path}/graph/diff_behavior.txt','a') as fw:
                        if '# define' in ad_line_code:
                            ret_diff_behavior.append(f'{file_id},A_{str(del_line[1])},B_{str(ad_line[1])},update version\n')
                            fw.write(f'{file_id},A_{str(del_line[1])},B_{str(ad_line[1])},update version\n')
                        elif 'free' in ad_line_code:
                            ret_diff_behavior.append(f'{file_id},A_{str(del_line[1])},B_{str(ad_line[1])},update function\n')
                            fw.write(f'{file_id},A_{str(del_line[1])},B_{str(ad_line[1])},update function\n')
                        else:
                            ret_diff_behavior.append(f'{file_id},A_{str(del_line[1])},B_{str(ad_line[1])},move{del_line_code}\n')
                            fw.write(f'{file_id},A_{str(del_line[1])},B_{str(ad_line[1])},move{del_line_code}\n')

    return ret_diff_behavior

def patchgraph_parser(file_diff, data_path, result_path, file_id):
    # parse the previous version file and post version file path
    pre_file_path = pre_patch_file_pattern.match(file_diff[2]).group(1)
    post_file_path = post_patch_file_pattern.match(file_diff[3]).group(1)
    print(pre_file_path)
    # read the previous version file and post version file
    pre_file_content = open(f'{data_path}/{pre_file_path}', 'rb').read()
    post_file_content = open(f'{data_path}/{post_file_path}', 'rb').read()
    # genenrate ast for the entire file
    pre_ast = parser.parse(pre_file_content) 
    post_ast = parser.parse(post_file_content)
    # generate data edges, control edges, and diff behaviors for each modified function and save under result/graph folder
    # step 1: get the modified scope of previous version file and post version file and diff behavior
    diff_hunk = []
    pre_change_lines = []
    all_pre_change_lines = []
    post_change_lines = []
    all_post_change_lines = []
    for diff_line in file_diff[4:]:
        hunk_match = hunk_pattern.match(diff_line)
        if hunk_match:
            old_start = int(hunk_match.group(1))
            old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
            new_start = int(hunk_match.group(3))
            new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1

            pre_change_lines = list(range(old_start, old_start + old_count))
            post_change_lines = list(range(new_start, new_start + new_count))
            all_pre_change_lines.extend(pre_change_lines)
            all_post_change_lines.extend(post_change_lines)

            # diff behavior of the previouse hunk
            if diff_hunk:
                diff_behavior(diff_hunk, result_path, file_id)
            # step 1.1: generate data edges, control edges for previous version file
            for sub_root_node in pre_ast.root_node.children: 
                if sub_root_node.type == 'function_definition': # find function
                    function_range_set = set(range(sub_root_node.start_point.row, sub_root_node.end_point.row))
                    if any(line_number in function_range_set for line_number in pre_change_lines):
                        # print(sub_root_node.start_point.row, sub_root_node.end_point.row)
                        data_edges(sub_root_node, 'A', result_path, pre_change_lines, file_id)
                        # cfg
                        for sub_sub_root in sub_root_node.children: # inside one function, find the function body
                            if sub_sub_root.type == 'compound_statement':
                                control_edges(sub_sub_root, 'A', result_path, pre_change_lines, file_id)
                                    

            # step 1.2: generate data edges, control edges for post version file
            for sub_root_node in post_ast.root_node.children: 
                if sub_root_node.type == 'function_definition': # find function
                    function_range_set = set(range(sub_root_node.start_point.row, sub_root_node.end_point.row))
                    if any(line_number in function_range_set for line_number in post_change_lines):
                        data_edges(sub_root_node, 'B', result_path, post_change_lines, file_id)
                        #cfg
                        for sub_sub_root in sub_root_node.children: # inside one function, find the function body
                            if sub_sub_root.type == 'compound_statement':
                                control_edges(sub_sub_root, 'B', result_path, post_change_lines, file_id)
            
            # renew for a new hunk
            diff_hunk = [diff_line]
            pre_change_lines = []
            post_change_lines = []
            


        else:
            diff_hunk.append(diff_line)
    
    # diff behavior of the last hunk
    diff_behavior(diff_hunk, result_path, file_id)

    # generate node
    with open(f'{result_path}/graph/node.txt','a') as fw:
        # previous version
        for i, line in enumerate(open(f'{data_path}/{pre_file_path}', 'r').read().split('\n')):
            if i+1 in all_pre_change_lines:
                fw.write(f'{file_id},A_{str(i+1)},{line}\n')
            else:
                fw.write(f'{file_id},CA_{str(i+1)},{line}\n')
        # post version
        for i, line in enumerate(open(f'{data_path}/{post_file_path}', 'r').read().split('\n')):
            if i+1 in all_post_change_lines:
                fw.write(f'{file_id},B_{str(i+1)},{line}\n')
            else:
                fw.write(f'{file_id},CB_{str(i+1)},{line}\n')


def pg_main(data_path, result_path):
    # data_path = 'data/demo'
    # result_path = 'result/demo'
    try:
        with open(f'{data_path}/diff_clean.txt', 'r', errors='ignore') as file:
            diff_content = file.readlines()
    except FileNotFoundError:
        print(f"Error: File  not found.")

    # process file by file
    file_diff = []
    file_id = 0
    for line in diff_content:
        file_match = file_header_pattern.match(line)
        if file_match:
            if file_diff:
                patchgraph_parser(file_diff, data_path, result_path, str(file_id))
                file_id += 1
            file_diff = [line]
        else:
            file_diff.append(line)
    
    if file_diff:
        patchgraph_parser(file_diff, data_path, result_path, str(file_id))
        

if __name__ == '__main__':
    # load the diff file, which contains all modified files
    data_name = 'motivation_example'
    data_path = f'data/{data_name}'
    result_path = f'result/{data_name}'
    os.makedirs(f'{result_path}/graph', exist_ok=True)
    os.makedirs(f'{result_path}/segment', exist_ok=True)
    os.makedirs(f'{result_path}/patch', exist_ok=True)

    pg_main(data_path, result_path)
