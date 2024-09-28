import json
import sys
import subprocess
from cfg import get_blocks, get_cfg

class LVN_Class:
    def __init__(self, input):
        self.input = self.parse_json(input)
        self.hash_table = {}
        self.vn2var = {}
        self.vn = 1

        self.print_hash_table()
        self.print_vn2var()

    def parse_json(self, input):
        return json.loads(input)

    def vn_gen(self, var):
        if var not in self.vn2var.keys():
            self.vn2var[var] = self.vn
            self.vn += 1
        return self.vn2var[var] 
    
    def lvn(self, block):
        for i, instr in enumerate(block):
            if "dest" in instr.keys():
                if "args" in instr.keys():
                    values = [self.vn_gen(arg) for arg in instr["args"]]
                    hash_entry = (instr["op"], *values)
                    canonical_var = instr["dest"]

                else:   
                    val = instr["value"]
                    values = [self.vn_gen(instr["dest"])]
                    hash_entry = (instr["op"], val)
                    canonical_var = instr["dest"]
                
                if hash_entry in self.hash_table.keys():
                    vn = self.hash_table[hash_entry]["vn"]
                    canonical_var = self.hash_table[hash_entry]["canncl_var"]
                    self.vn2var[instr["dest"]] = vn
                    block[i] = {
                                "dest": instr["dest"],
                                "op": "const",
                                "type": "int",
                                "value": canonical_var
                            }
                
                else:
                    new_vn = self.vn_gen(instr["dest"])
                    self.hash_table[hash_entry] = {"vn": new_vn, "canncl_var": canonical_var}
            else:
                continue
        return block
    
    def run_lvn(self):
        blocks = get_blocks(self.input)
        self.input["functions"][0]["instrs"] = self.lvn(list(blocks.values())[0])
        # for block in blocks.values():
        #     block = self.lvn(block)
        return self.input

    def print_hash_table(self):
        for key, value in self.hash_table.items():
            print(f"{key}: {value}")    

    def print_vn2var(self):
        for key, value in self.vn2var.items():
            print(f"{key}: {value}")    

if __name__ == "__main__":
    filename = sys.argv[1]
    text2bril = subprocess.check_output(f"bril2json < {filename}", shell=True)  

    filename = filename.replace("_t.bril", "_j.bril")
     
    lvn = LVN_Class(text2bril)
    after_dce = lvn.run_lvn()
    # after_dce = lvn.run_lvn()

    print(lvn.hash_table)    

    # output new program after running dce
    with open(f"{filename}_lvn", 'w') as json_file:
        json.dump(after_dce, json_file, indent=4)
    