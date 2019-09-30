# VM Translator
# input: filename.vm
# output: filename.asm

from Parser import *
from CodeWriter import *
import os
import sys


# List of all possible VM commands
commandList = ["arithmetic", "push", "pop", "label", "goto", "if-goto",
               "function", "return", "call"]


def main():

################################################################################
    # finding the .vm files on the given filepath

    # Filepath of VM code
    filepath = sys.argv[1]

    # list of project files
    vmFiles = []

    # name of VM project folder
    projectName = ""

    # if the provided filepath refers to a directory
    if os.path.isdir(filepath):

        # for each item in the directory,
        for item in os.scandir(filepath):

            # if the item is a file
            if item.is_file():

                # see if the filename ends in .vm
                file = item.name
                i = file.find(".vm")
                if i > 0:
                    # if it is, append the file to the list of project files
                    vmFiles.append(item.name)

        # change the current working directory to the project file and store
        # the name of the directory as the projectName
        os.chdir(filepath)
        projectName = os.path.basename(filepath)

    # if the provided path refers to a file
    else:
        # change the current working directory to the parent directory
        os.chdir(os.path.dirname(filepath))

        # append the name of the vm file to the vm file list
        vmName = os.path.basename(filepath)
        vmFiles.append(vmName)

        # make the project name the name of the vm file and remove ".vm"
        # extention
        projectName = vmName[:len(vmName)-3]

    # store the assembly file name
    asmFile = projectName + ".asm"


################################################################################
    # actual translating of VM code

    # for each file in the project
    for file in vmFiles:

        # write code comments for debugging that say what file we are opening
        translator.change_vmFile(file)

        # initialize a Parser object to parse the VM code
        vmFile = Parser(file)

        # while there is more commands
        while vmFile.hasMoreCommands:

            # advance to the next command
            vmFile.advance()

            # if we are not out of commands
            if vmFile.hasMoreCommands is True:

                # returns the command type of the current command
                commandCode = vmFile.commandType()
                cmdStr = commandList[commandCode]

                # if the command type is arithmetic, finish parsing and write
                # out the command to the assembly file
                if cmdStr == "arithmetic":
                    cmd = vmFile.arg1()
                    translator.writeArithmetic(cmd)


                # if the command type is push/pop, finish parsing and write
                # out the command to the assembly file
                elif cmdStr == "push" or cmdStr == "pop":
                    cmd = vmFile.commandType()
                    seg = vmFile.arg1()
                    ind = vmFile.arg2()
                    translator.writePushPop(cmd, seg, ind)

                # if label, finish parsing and write
                # out the command to the assembly file
                elif cmdStr == "label":
                    label = vmFile.arg1()
                    translator.writeLabel(label)

                # if goto, finish parsing and write
                # out the command to the assembly file
                elif cmdStr == "goto":
                    label = vmFile.arg1()
                    translator.writeGoto(label)


                # if if-goto, finish parsing and write
                # out the command to the assembly file
                elif cmdStr == "if-goto":
                    label = vmFile.arg1()
                    translator.writeIf(label)

                # if function, finish parsing and write
                # out the command to the assembly file
                elif cmdStr == "function":
                    functionName = vmFile.arg1()
                    numLocals = vmFile.arg2()
                    translator.writeFunction(functionName, numLocals)

                # if return, finish parsing and write
                # out the command to the assembly file
                elif cmdStr == "return":
                    translator.writeReturn()

                # if return, finish parsing and write
                # out the command to the assembly file
                elif cmdStr == "call":
                    functionName = vmFile.arg1()
                    numArgs = vmFile.arg2()
                    translator.writeCall(functionName, numArgs)

        # close the current VM file
        vmFile.close()

    # close the assembly file
    translator.close()

if __name__ == '__main__':
    main()
