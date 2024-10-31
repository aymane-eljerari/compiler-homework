
For this assignment, I implemented an LLVM pass to count the number of instructions in each basic block of all functions in a module. 


```
struct InstrCountPass : public PassInfoMixin<InstrCountPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M.functions()) {
            // print the name of each function it the module
            errs() << "Function: " << F.getName() << "\n";
            for (auto &BB : F) {
                // print the name of the basic block
                errs() << "  Basic Block: ";
                BB.printAsOperand(errs(), false);


                // Count and print the number of instructions in the basic block
                int InstrCount = 0;
                for (auto &I : BB) {
                    InstrCount++;
                }
                errs() << "    Number of instructions: " << InstrCount << "\n";
            }
        }
        return PreservedAnalyses::all();
    }
};
```

After compiling the pass and running it, we can see all function names in the module, as well as all the blocks along with the number of instructions per block.

```
$ clang -fpass-plugin=/home/eljeraria/compilers/instr_count_pass/build/instr_pass/InstrCountPass.so vec_add.c
Function: vec_add
  Basic Block: %0    Number of instructions: 24
  Basic Block: %18    Number of instructions: 4
  Basic Block: %22    Number of instructions: 9
  Basic Block: %29    Number of instructions: 4
  Basic Block: %32    Number of instructions: 2
  Basic Block: %33    Number of instructions: 4
  Basic Block: %37    Number of instructions: 14
  Basic Block: %50    Number of instructions: 4
  Basic Block: %53    Number of instructions: 3
Function: llvm.stacksave.p0
Function: llvm.stackrestore.p0
Function: main
  Basic Block: %0    Number of instructions: 4
```


My first attempt was to write a loop unrolling pass and compare the performance improvement of different unrolling factors. Unfortunately, I was not able to implement the pass successfully. 