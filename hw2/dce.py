import json
import sys
import subprocess
from cfg import get_blocks, get_cfg

class DCE_Class:
    def __init__(self, input):
        self.input = self.parse_json(input)
        self.used = set()

    def parse_json(self, input):
        return json.loads(input)

    # perform deadcode elimination on a single block
    def block_dce(self, block):
        for instr in block:
            if "args" not in instr.keys():
                continue
            self.used.update(instr["args"])
        
        for i in range(len(block)-1, -1, -1):
            if "dest" in block[i].keys() and block[i]["dest"] not in self.used:
                rm_instr = block.pop(i)
                print(rm_instr)
                # print(f"Instruction removed:\n {rm_instr}. Destination {rm_instr["dest"]} was not used")   
        return block
    
    def run_dce(self):
        blocks = get_blocks(self.input)

        # this assumes the program only has a single block
        self.input["functions"][0]["instrs"] = self.block_dce(list(blocks.values())[0])

        # for block in blocks.values():
        #     block = self.block_dce(block)
        #     print(1)
        #     break
        return self.input
    

if __name__ == "__main__":
    filename = sys.argv[1]
    bril_in = subprocess.check_output(f"bril2json < {filename}", shell=True)  

    # filename = filename.replace("_t.bril", "_j.bril")
    
    dce = DCE_Class(bril_in)
    after_dce = dce.run_dce()
     
    # output new program after running dce
    with open(f"{filename}_dce", 'w') as json_file:
        json.dump(after_dce, json_file, indent=4)

        