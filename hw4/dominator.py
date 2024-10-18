import sys
import json
import utils
import graph
import argparse
import subprocess

def get_successors(block):
    # last instr in block
    instr = block[-1]
    # get successors
    if instr['op'] in ['jmp', 'br']:
        return instr['labels']
    # no successor
    elif instr['op'] == 'ret':
        return []
    else: 
        return None

def generate_graph(blocks):
    # init all to empty lists
    predecessor_dict = {blk_id: [] for blk_id in blocks}
    successor_dict = {blk_id: [] for blk_id in blocks}
    for name, block in blocks.items():
        # get all succcessors
        successors = get_successors(block)
        successor_dict[name].extend(successors) 
        
        # make current block predecessors to all its successors
        for s in successors:
            predecessor_dict[s].append(name)

    return successor_dict, predecessor_dict

def get_dominators(blocks):
    # get block list and block set structures
    all_blks_l = list(blocks.keys())
    all_blks_s = set(all_blks_l)

    # get the firs block
    entry = next(iter(blocks))

    # init dominator dict
    dom = {name: all_blks_s for name in blocks.keys()} 
    dom[entry] = {entry}

    _, predecessors = generate_graph(blocks)

    changed = True
    while changed:
        changed = False
        # all vertices except the entry point
        for v in all_blks_l[1:]:
            intrsct = all_blks_s

            # get the common ancestors of all predecessors
            for pred in predecessors[v]:
                intrsct = intrsct.intersection(dom[pred])

            # self dominates
            new_dom = intrsct.union({v})

            # update the dominator tree entries
            if new_dom != dom[v]:
                dom[v] = new_dom
                changed = True

    return dom



def strictly_dominates(b1, b2, doms):
    return b1 in doms[b2] and b1 != b2

def build_dominance_tree(dom):
    # init dominator tree
    dom_tree = {node: [] for node in dom.keys()}

    for a in dom.keys():
        for b, b_doms in dom.items():
            if a != b:
                E_a_stric_dom_c = False
                # look at all dominators of b
                for c in b_doms:
                    # c != b
                    if c != b:
                        # check if a strictly dominates any of b's dominators
                        E_a_stric_dom_c = E_a_stric_dom_c or strictly_dominates(a, c, dom)

                # b1 strictly dominates 
                if a in b_doms and not E_a_stric_dom_c:
                    dom_tree[a].append(b)
    return dom_tree

def test_dominance(nodeA, nodeB, dom_tree):
    stack = [nodeA]
    
    while stack:
        current = stack.pop()
        if current == nodeB:
            return True
        # Add all nodes immediately dominated by the current node to the stack
        stack.extend(dom_tree[current])
    
    return False

def get_dominance_frontier(blks):
    # get predecessors and dominators for each block
    _, p = generate_graph(blks)
    doms = get_dominators(blks)

    # init the frontier dict
    frontier = {name: [] for name in doms.keys()}

    # loop over all nodes
    for node in doms:
        # get the dominators of all predecessors of the current node
        pred_doms = [doms[pred] for pred in p[node]]
        # if none, we can skip to the next node
        if len(pred_doms) == 0:
            continue

        # get the set intersection for dominators of all predecessors of current node
        intersection = set.intersection(*map(set,pred_doms))
        # get the set union for dominators of all predecessors of the current node
        union = set.union(*map(set,pred_doms)) 
        frontier_set = union - intersection
        
        # add nodes to the frontier dict
        for block in frontier_set:
            frontier[block].append(node)

    return frontier

def main(bril, args):
    for func in bril['functions']:
        # build the control flow graph
        blocks = utils.block_map(utils.form_blocks(func['instrs']))
        utils.add_terminators(blocks)
        s, _ = generate_graph(blocks)

        if args.doms: 
            dom = get_dominators(blocks)
            graph.generate_control_flow_with_dominators(s, dom)

        if args.dom_tree:
            dom_tree = build_dominance_tree(dom)
            graph.generate_dominance_tree_graph(dom_tree)

        if args.dom_frontier:
            dom_frontier = get_dominance_frontier(blocks)
            print("Dominance Frontier\n")
            print(dom_frontier)

        if args.test_dom:
            node1, node2 = args.nodes
            result = test_dominance(node1, node2, dom_tree)

            if result:
                print(f"{node1} dominates {node2}")
            else:
                print(f"{node1} doesn't dominate {node2}")


if __name__ == "__main__":

    # bril_file = "test5.bril"
    # result = subprocess.run(
    #     ["bril2json"], 
    #     stdin=open(bril_file, "r"), 
    #     stdout=subprocess.PIPE, 
    #     stderr=subprocess.PIPE, 
    #     text=True
    # )
    # bril = json.loads(result.stdout)
    
    parser = argparse.ArgumentParser(description="Run Dominance related algorithms on BRIL programs")

    parser.add_argument("--doms", action="store_true", help="Find the dominators")
    parser.add_argument("--dom_tree", action="store_true", help="Generate the dominator tree")
    parser.add_argument("--dom_frontier", action="store_true", help="Generate the dominance frontier")
    parser.add_argument("--test_dom", action="store_true", help="Test if node A dominates node B")
    parser.add_argument("--nodes", nargs=2, help="Input 2 nodes to test if the first dominates the second. (Requires --test_dom)")

    args = parser.parse_args()
    
    bril = json.load(sys.stdin)
    main(bril, args)