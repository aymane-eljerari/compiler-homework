import json
import sys
import utils

class DFA_Liveness:
    def __init__(self, bril):
        self.run_dfa(bril)

    def get_successors(self, block):
        # last instr in block
        instr = block[-1]
        # get successors
        if instr['op'] in ['jmp', 'br']:
            return instr['labels']
        # no successor
        elif instr['op'] == 'ret':
            return []
        else: 
            return

    def generate_graph(self, blocks):
        # init all to empty lists
        self.predecessors = {blk_id: [] for blk_id in blocks}
        self.successors = {blk_id: [] for blk_id in blocks}
        for name, block in blocks.items():
            # get all succcessors
            successors = self.get_successors(block)
            self.successors[name].extend(successors) 
            
            # make current block predecessors to all its successors
            for s in successors:
                self.predecessors[s].append(name)

    def analyze_dataflow(self, blocks):
        # generate successors and predecessors for every block
        self.generate_graph(blocks)

        blk_start = list(blocks.keys())[-1]
        in_set = self.successors
        out_set = self.predecessors

        # init first block
        self.in_set = {blk_start: set()}
        self.out_set = {blk: set() for blk in blocks}

        # iterative worklist dataflow algorithm
        worklist = list(blocks.keys())
        while worklist:
            blk = worklist.pop(0)

            # in values = merge all previous value 
            in_val = self.union_op(self.out_set[n] for n in in_set[blk])
            self.in_set[blk] = in_val
            
            # out values generated using the transfer function
            out_val = self.transfer_func(blocks[blk], in_val)

            # if there was a change
            if out_val != self.out_set[blk]:
                # update
                self.out_set[blk] = out_val
                # add item to the workloist
                worklist += out_set[blk]

        return self.out_set, self.in_set
        
    def transfer_func(self, block, set):
        return self.vars_used(block).union(set - self.vars_written(block))
    
    def union_op(self, sets):
        out = set()
        for s in sets:
            out.update(s)
        return out
        
    # run the data flow analysis
    def run_dfa(self, bril):
        for func in bril['functions']:
            # build the control flow graph
            blocks = utils.block_map(utils.form_blocks(func['instrs']))
            utils.add_terminators(blocks)

            # run the dataflow analysis
            in_, out = self.analyze_dataflow(blocks)
            # print the in and out values
            for block in blocks:
                print('{}:'.format(block))
                print('  in: ', utils.fmt(in_[block]))
                print('  out:', utils.fmt(out[block]))    

    # variables written to inside the block
    def vars_written(self, block):
        result = set()
        for instr in block:
            if 'dest' in instr:
                result.add(instr['dest'])
        return result

    # variables used before being written to in the block
    def vars_used(self, block):
        defined = set()
        used = set()
        for instr in block:
            # if instr has args
            for var in instr.get('args', []):
                # and those arguments were not reassigned before being used
                if var not in defined:
                    # add them to the seet
                    used.add(var)
            # add to defined set(), if an instr writes to a dest
            if 'dest' in instr:
                defined.add(instr['dest'])
        return used

if __name__ == "__main__":
    bril = json.load(sys.stdin)
    dfa = DFA_Liveness(bril)