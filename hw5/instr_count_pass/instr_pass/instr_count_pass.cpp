#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Module.h"

using namespace llvm;

namespace {

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

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Instruction Count Pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(InstrCountPass());
                });
        }
    };
}
