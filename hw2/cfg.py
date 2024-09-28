
from collections import OrderedDict

#Instructions that terminate a basic block.
TERMINATORS = 'br', 'jmp', 'ret'

def form_blocks(instrs):
    # Start with an empty block.
    cur_block = []

    for instr in instrs:
        if 'op' in instr:  # It's an instruction.
            # Add the instruction to the currently-being-formed block.
            cur_block.append(instr)

            # If this is a terminator (branching instruction), it's the
            # last instruction in the block. Finish this block and
            # start a new one.
            if instr['op'] in TERMINATORS:
                yield cur_block
                cur_block = []
        
        else:  # It's a label.
            # End the block here (if it contains anything).
            if cur_block:
                yield cur_block

            # Start a new block with the label.
            cur_block = [instr]

    # Produce the final block, if any.
    if cur_block:
        yield cur_block

def print_blocks(bril):
    """Given a Bril program, print out its basic blocks.
    """

    func = bril['functions'][0]  # We only process one function.
    for block in form_blocks(func['instrs']):
        # Mark the block.
        leader = block[0]
        if 'label' in leader:
            print( f"block {leader['label']}")
            block = block[1:]  # Hide the label
        else:
            print('anonymous block:')

        # Print the instructions.
        for instr in block:
            print(instr)



def block_map(blocks):
    """Given a sequence of basic blocks, which are lists of instructions,
    produce a `OrderedDict` mapping names to blocks.

    The name of the block comes from the label it starts with, if any.
    Anonymous blocks, which don't start with a label, get an
    automatically generated name. Blocks in the mapping have their
    labels removed.
    """
    by_name = OrderedDict()

    for block in blocks:
        # Generate a name for the block.
        if 'label' in block[0]:
            # The block has a label. Remove the label but use it for the
            # block's name.
            name = block[0]['label']
            block = block[1:]
        else:
            # Make up a new name for this anonymous block.
            name = f'gen_bk_{len(by_name)}'

        # Add the block to the mapping.
        by_name[name] = block

    return by_name

def build_cfg(ordered_blocks):
    cfg = {}

    labels = list(ordered_blocks.keys())

    for i, (block_name, block) in enumerate(ordered_blocks.items()):
        last = block[-1]
        op = last['op']

        if op == 'jmp':
            cfg[block_name] = last['labels']
        elif op == 'br':
            cfg[block_name] = last['labels']
        else:
            if i+1 < len(labels):  # last block does not fall through
                cfg[block_name] = [labels[i+1]]
            else:
                cfg[block_name] = []
    return cfg



def get_blocks(bril):
    blks = form_blocks(bril['functions'][0]['instrs'])
    od = block_map(blks)
    # for (name, instrs) in od.items():
        # print (name, instrs)
    return od

def get_cfg(bril):
    blks = form_blocks(bril['functions'][0]['instrs'])
    od = block_map(blks)
    cfg = build_cfg(od)
    # print(cfg)
    return cfg
