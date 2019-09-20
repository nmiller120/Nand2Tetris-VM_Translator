# VM Translator
# input: filename.vm
# output: filename.asm

from Parser import *
from CodeWriter import *
import os
import sys

commandList = ["arithmetic", "push", "pop", "label", "goto", "if-goto",
               "function", "return", "call"]


def main():
    # init
    filepath = sys.argv[1]
    vmFiles = []
    projectName = ""

    if os.path.isdir(filepath):
        for item in os.scandir(filepath):
            if item.is_file():
                file = item.name
                i = file.find(".vm")
                if i > 0:
                    vmFiles.append(item.name)

        os.chdir(filepath)
        projectName = os.path.basename(filepath)

    else:
        os.chdir(os.path.dirname(filepath))
        vmName = os.path.basename(filepath)
        vmFiles.append(vmName)
        projectName = vmName[:len(vmName)-3]

    asmFile = projectName + ".asm"
    translator = CodeWriter(asmFile)
    translator.writeInit()
    for file in vmFiles:
        translator.change_vmFile(file)


        vmFile = Parser(file)
        while vmFile.hasMoreCommands:
            vmFile.advance()

            if vmFile.hasMoreCommands is True:
                typeCode = vmFile.commandType()
                cmdStr = commandList[typeCode]

                # if arithmetic
                if cmdStr == "arithmetic":
                    cmd = vmFile.arg1()
                    translator.writeArithmetic(cmd)



                # if push/pop
                elif cmdStr == "push" or cmdStr == "pop":
                    cmd = vmFile.commandType()
                    seg = vmFile.arg1()
                    ind = vmFile.arg2()
                    translator.writePushPop(cmd, seg, ind)


                # if label
                elif cmdStr == "label":
                    label = vmFile.arg1()
                    translator.writeLabel(label)


                # if goto
                elif cmdStr == "goto":
                    label = vmFile.arg1()
                    translator.writeGoto(label)


                # if if-goto
                elif cmdStr == "if-goto":
                    label = vmFile.arg1()
                    translator.writeIf(label)


                # if function
                elif cmdStr == "function":
                    functionName = vmFile.arg1()
                    numLocals = vmFile.arg2()
                    translator.writeFunction(functionName, numLocals)


                # if return
                elif cmdStr == "return":
                    translator.writeReturn()

                elif cmdStr == "call":
                    functionName = vmFile.arg1()
                    numArgs = vmFile.arg2()
                    translator.writeCall(functionName, numArgs)


        vmFile.close()

    translator.close()
if __name__ == '__main__':
    main()
