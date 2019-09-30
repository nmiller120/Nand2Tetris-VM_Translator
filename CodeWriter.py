# CodeWriter.py

class CodeWriter:
    asmFile = None # name of the .asm file

    # list of VM commands
    commandList = ["arithmetic", "push", "pop", "label", "goto", "if-goto",
                   "function", "return", "call"]

    # output mode select switch used for debugging. In final implementation it
    # just needs to write to a file.
    writeMode = 2   # 0: write to console
                    # 1: write to console and file
                    # 2: write to file

    # determine if we are writing debug comments in output assembly code
    suppressComments = True

    # this is the current line number in the VM code, this value is written into
    # the assembly file as a comment to help chase bugs in the output file
    lineNumber = 0

    # Counters for jump statements and function calls, all jump labels are
    # numbered so they are unique
    eq_ct = 0
    lt_ct = 0
    gt_ct = 0
    fn_call_ct = 0

    # name of the current function
    functionName = ""

    # name of the current file
    fileName = ""

    # translates VM command arguments to their corresponding symbol in assembly
    segmentDictionary = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT",
                       "temp":"5", "pointer":"3", "static":"16"}

    def __init__(self, outputFile):
        # opens the output file and gets ready to write to it, if we aren't
        # writing our output strictly to console
        if self.writeMode != 0:
            self.asmFile = open(outputFile, "w")


        # truncate .vm from the output filename
        i = outputFile.find(".")

        # self.staticName = outputFile[:i]

        # write the current output filename to file
        self.write("//" + outputFile)
        self.write("")
        self.write("")

    def writeInit(self):
        # write the initialization code to file
        self.write("//Bootstrap code... ")

        # initialize stack pointer
        self.write("@256")
        self.write("D=A")
        self.write("@SP")
        self.write("M=D // set stack pointer *SP = 256")

        # call function Sys.init
        self.writeCall("Sys.init", 0)

    def change_vmFile(self, filename):
        # write the current filename to the output file and store the next
        # filename
        self.write("//in file " + filename + "\n", show_lineNumber = False)
        self.fileName = filename
        self.functionName = None

    def writeLabel(self, label):
        # method writes a label command to the output file

        # write a comment, labeling the label
        self.write("//label " + label)

        # if this label is within a function, write the label with a reference
        # to the function
        if self.functionName is not "":
            self.write("(" + self.functionName + "$" + label + ")\n")

        # otherwise just write the label as is provided
        else:
            self.write("(" + label + ")\n")

    def writeGoto(self, label):
        # method writes a goto command to the output file.

        # write a comment, labeling the goto
        self.write("//goto " + label)

        #  if the goto is written within a function, write the label with a
        # reference to the function
        if self.functionName is not "":
            self.write("@" + self.functionName + "$" + label)

        # otherwise just write the labels
        else:
            self.write("@" + label)

        # write a jump statment in assembly file
        self.write("0;JMP\n")

    def writeIf(self, label):
        # method writes an if-goto statement to the output file

        # write a comment, labeling the if-goto
        self.write("//if-goto " + label)

        # store the value at the top of the stack
        self.write("@SP")
        self.write("AM=M-1")
        self.write("D=M")

        # if in a function add a reference to the function to the label
        if self.functionName is not "":
            self.write("@" + self.functionName + "$" + label)

        # otherwise just write the label
        else:
            self.write("@" + label)

        # write an assembly command comparing the value to 0 (false) jump if the
        # the value at the top of the stack is not false
        self.write("D;JNE\n")

    def writeCall(self, functionName, numArgs):
        # method implements a function call in assembly

        # push return address to stack
        self.write("//in function call for " + functionName + ", Push return address to stack")
        self.write("@" + "FUNCTION_CALL_RETURN_" + str(self.fn_call_ct))
        self.write("D=A")
        self.pushValueInD()
        self.write("")

        # push local segment pointer to stack
        self.write("//in function call for " + functionName + ", Push local value to stack")
        self.write("@LCL")
        self.write("D=M")
        self.pushValueInD()
        self.write("")

        # push argument segment pointer to stack
        self.write("//in function call for " + functionName + ", Push arg value to stack")
        self.write("@ARG")
        self.write("D=M")
        self.pushValueInD()
        self.write("")

        # push this segment pointer to stack
        self.write("//in function call for " + functionName + ", Push this value to stack")
        self.write("@THIS")
        self.write("D=M")
        self.pushValueInD()
        self.write("")

        self.write("//in function call for " + functionName + ", Push that value to stack")
        self.write("@THAT")
        self.write("D=M")
        self.pushValueInD()
        self.write("")

        # get ready to begin new frame in the call stack, set the argument pointer
        # to point to the arguments of the calling code, set the local pointer
        # to point to the local variables of this function
        self.write("//in function call for " + functionName + ", Arg = SP - n - 5")
        self.write("@SP")
        self.write("D=M")
        self.write("@" + str(numArgs+5))
        self.write("D=D-A")
        self.write("@ARG")
        self.write("M=D")
        self.write("")
        self.write("//in function call for " + functionName + ", LCL = SP")
        self.write("@SP")
        self.write("D=M")
        self.write("@LCL")
        self.write("M=D")
        self.write("")

        # write the jump statement to goto the function code
        self.write("//in function call for " + functionName + ", goto function")
        self.write("@" + functionName)
        self.write("0;JMP\n")
        self.write("")

        # write the return label
        self.write("//in function call for " + functionName + ", return label")
        self.write("(FUNCTION_CALL_RETURN_" + str(self.fn_call_ct) + ") //function call return for " + functionName + " \n")
        self.fn_call_ct += 1


    def pushValueInD(self):
        # method used to implement pushing whatever value was in D register to the
        # stack
        self.write("@SP") #@SP
        self.write("A=M") #A=SP
        self.write("M=D") #M=?
        self.write("D=A+1")#D=SP+1
        self.write("@SP")
        self.write("M=D")

    def writeReturn(self):
        # method implements a function return statement

##        FRAME = LCL // FRAME is a temporary variable
##        RET = *(FRAME-5) // Put the return-address in a temp. var.
##        *ARG = pop() // Reposition the return value for the caller
##        SP = ARG+1 // Restore SP of the caller
##        THAT = *(FRAME-1) // Restore THAT of the caller
##        THIS = *(FRAME-2) // Restore THIS of the caller
##        ARG = *(FRAME-3) // Restore ARG of the caller
##        LCL = *(FRAME-4) // Restore LCL of the caller
##        goto RET
        self.write("//return")
        self.write("//R13(frame) = LCL")
        self.write("@LCL")
        self.write("D=M")
        self.write("@R13")
        self.write("M=D")
        self.write("")

        self.write("//R14(return addr) = *(Frame - 5)")
        self.write("@5")
        self.write("A=D-A")
        self.write("D=M")
        self.write("@R14")
        self.write("M=D")
        self.write("")

        self.write("//*ARG = pop()")
        self.write("@SP")
        self.write("A=M-1")
        self.write("D=M")
        self.write("@ARG")
        self.write("A=M")
        self.write("M=D //*ARG = *(SP-1)")
        self.write("")

        self.write("//SP = ARG+1")
        self.write("D=A+1")
        self.write("@SP")
        self.write("M=D")

        self.write("//that = *(frame-1)")
        self.write("@R13")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@THAT")
        self.write("M=D")

        self.write("//this = *(frame-2)")
        self.write("@R13")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@THIS")
        self.write("M=D")

        self.write("//arg = *(frame-3)")
        self.write("@R13")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@ARG")
        self.write("M=D")

        self.write("//lcl = *(frame-4)")
        self.write("@R13")
        self.write("AM=M-1")
        self.write("D=M")
        self.write("@LCL")
        self.write("M=D")

        self.write("//goto return address")
        self.write("@R14")
        self.write("A=M")
        self.write("0;JMP\n")


    def writeFunction(self, functionName, numLocals):
        # method implements a function declaration

        # change the name of the current function
        self.functionName = functionName

        # label the current function in the VM code
        self.write("//function " + functionName + " " + str(numLocals))

        # write a label for the current function
        self.write("(" + functionName + ")\n")

        # for each of the local variables, push them with a value of 0 to the
        # stack
        for x in range(numLocals):
            self.push("constant", 0)

    def writeArithmetic(self, command):
        # writes to the output file the assembly code that implements the given
        # arithmetic command.
        # Simplified explaination:
        # the command is to take the last 1 or 2 values on the stack as arguments
        # and pop them from the stack. Leaving behind the solution to the given
        # computation. So if "add" is being processed, the intended operation is
        # to pop the last two arguments from the stack, say 3 and 5, and push the
        # answer to the stack, so in this case 8. If the command takes 1 argument
        # it pops that value and pushes the solution, 8 becomes -8. All of these
        # operations are implemented in the assembly language

        self.write("//" + command) # show vm command

        if command == "neg":
            # -x
            self.write("@SP")
            self.write("A=M-1") #A = sp-1
            self.write("M=-M\n") #*(sp-1) = *(sp-1)*(-1)

        elif command == "not":
            # !x
            self.write("@SP")
            self.write("A=M-1") #A = sp-1
            self.write("M=!M\n")  #*(sp-1) = ~*(sp-1)*(-1)


        else: # two operand command

            if command == "eq" or command == "gt" or command == "lt":
                # store value if true in R13
                self.write("@R13")
                self.write("M=-1")

            # call up two operands from the stack; x is in memory register and y is in
            # data register

            self.write("@SP")
            self.write("A=M-1")
            self.write("D=M")
            self.write("A=A-1")

            if command == "eq" or command == "gt" or command == "lt":
                label_ct = ""
                if command =="eq":
                    label_ct = str(self.eq_ct)
                    self.eq_ct += 1
                elif command=="gt":
                    label_ct = str(self.gt_ct)
                    self.gt_ct += 1
                elif command=="lt":
                    label_ct = str(self.lt_ct)
                    self.lt_ct += 1

                self.write("D=M-D") #x = x-y; difference of x and y
                self.write("@END_" + command.upper() + label_ct)
                self.write("D; J" + command.upper())
                self.write("@R13")
                self.write("M=0")
                self.write("(END_" + command.upper() + label_ct + ")")
                self.write("@R13")
                self.write("D=M")

            elif command == "add":
                self.write("M=M+D") # x+y
            elif command == "sub":
                self.write("M=M-D") # x-y
            elif command == "and":
                self.write("M=M&D") # x&y
            elif command == "or":
                self.write("M=M|D") # x|y

            # call up stack pointer and decrement
            self.write("@SP")
            self.write("M=M-1") # SP--
            if command == "eq" or command == "gt" or command == "lt":
                self.write("A=M-1") # A = SP-1
                self.write("M=D") # *(sp-1) == value if true/false

            self.write("")

    def writePushPop(self, command, segment, index):
        # writes to the output file the assembly code that implements the given command
        # where the command is either push or pop

        # write comment labeling the push/pop statment
        line = "//" + self.commandList[command] + " " + segment + " " + str(index)
        self.write(line)

        # if push write push
        if command == 1:
            self.push(segment, index)

        # if pop write pop
        elif command == 2:
            self.pop(segment, index)

    def push(self, segment, index):
        # statement of form in VM code, push segment index

        # explaination of code:
        # function takes the specified memory segment and the index of the segment
        # and pushes that value onto the stack. So for example for the command
        # "push local 2" takes the pointer to the local segment, adds 2 to it,
        # retrieves that value from ram, and pushes it to the call stack. If
        # the statment is "push constant 2" the value of 2 is pushed to the stack
        # as a constant denotes that we are wanting to push an integer literal
        # this is all implemented in assembly commands.

        if segment == "static":
            self.write("@" + self.fileName[:len(self.fileName)-3] + "." + str(index))
            self.write("D=M")
        else:
            segmentDict = self.segmentDictionary
            self.write("@" + str(index)) # @ 6
            self.write("D=A") # D = 6

            if segment != "constant":
                if segment == "pointer" or segment == "temp":
                    self.write("@" + segmentDict[segment]) # @5
                    self.write("A=A+D")  # A = 5+6
                    self.write("D=M")

                else:
                    self.write("@" + segmentDict[segment])
                    self.write("A=M+D")
                    self.write("D=M")

        self.write("@SP") #@SP
        self.write("A=M") #A=SP
        self.write("M=D") #M=?
        self.write("D=A+1")#D=SP+1
        self.write("@SP")
        self.write("M=D\n")

    def pop(self, segment, index):
        # statement of form in VM code, pop segment index

        # explaination of code:
        # function takes the specified segment and index and pops the value at the
        # top of the stack into that memory address. So for example the statment
        # "pop local 4" we find the data pointed to by LCL pointer and add 4 to it.
        # then retrieve the value at the top of the stack and write it into the
        # address that we found. This operation is all implemented in assembly commands.

        if segment == "static":
            self.write("@" + self.fileName[:len(self.fileName)-3] + "." + str(index))
            self.write("D=A")

        else:
            segmentDict = self.segmentDictionary
            self.write("@" + segmentDict[segment])
            if segment == "pointer" or segment == "temp":
                self.write("D=A")
            else:
                self.write("D=M")
            # D = address of the beginning of the memory segment
            self.write("@" + str(index))
            self.write("D=D+A")
        # D = beginning of mem segment + index (or static var)
        self.write("@R13")
        self.write("M=D")
        self.write("@SP")
        self.write("A=M-1")
        self.write("D=M")
        self.write("@R13")
        self.write("A=M")
        self.write("M=D")
        self.write("@SP")
        self.write("M=M-1\n")

    def write(self, text, show_lineNumber = True):
        # method called to write data to output file. Makes it easier to change
        # the type of output we want. Output differs depending on if we choose to
        # supress comments, write to file, console, or both.
        if self.suppressComments:
            index = text.find("//")
            if text.find("//") is not -1:
                text = text[0:index]

            while text.find("\n") is (len(text)-1) and (len(text) != 0):
                text = text[0:len(text)-1]


        if len(text) > 0:
            if text[0] != "/" and text[0] != "(":
                self.lineNumber += 1

            elif text[0] != "(" and show_lineNumber:
                text = text + ", line " + str(self.lineNumber)

        if self.writeMode == 0:
            print(text)

        elif self.writeMode == 1:
            self.asmFile.write(text)
            self.asmFile.write("\n")
            print(text)

        elif self.writeMode == 2:
            if len(text) > 0:
                self.asmFile.write(text)
                self.asmFile.write("\n")

    def close(self):
        # closes the output file
        if self.writeMode == 0:
            pass

        else:
            self.asmFile.close()

