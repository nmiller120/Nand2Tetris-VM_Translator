# CodeWriter.py

class CodeWriter:
    asmFile = None
    commandList = ["arithmetic", "push", "pop", "label", "goto", "if-goto",
                   "function", "return", "call"]
    writeMode = 2   # 0: write to console
                    # 1: write to console and file
                    # 2: write to file
    suppressComments = True

    lineNumber = 0
    eq_ct = 0
    lt_ct = 0
    gt_ct = 0
    fn_call_ct = 0
    functionName = ""
    fileName = ""

    segmentDictionary = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT",
                       "temp":"5", "pointer":"3", "static":"16"}

    def __init__(self, outputFile):
        # opens the output file and gets ready to write to it
        if self.writeMode != 0:
            self.asmFile = open(outputFile, "w")

        i = outputFile.find(".")
        self.staticName = outputFile[:i]
        self.write("//" + outputFile)
        self.write("")
        self.write("")

    def writeInit(self):
        self.write("//Bootstrap code... ")
        self.write("@256")
        self.write("D=A")
        self.write("@SP")
        self.write("M=D // set stack pointer *SP = 256")
        self.writeCall("Sys.init", 0)

    def change_vmFile(self, filename):
        self.write("//in file " + filename + "\n", show_lineNumber = False)
        self.fileName = filename
        self.functionName = None

    def writeLabel(self, label):
        self.write("//label " + label)
        if self.functionName is not "":
            self.write("(" + self.functionName + "$" + label + ")\n")
        else:
            self.write("(" + label + ")\n")

    def writeGoto(self, label):
        self.write("//goto " + label)
        if self.functionName is not "":
            self.write("@" + self.functionName + "$" + label)
        else:
            self.write("@" + label)
        self.write("0;JMP\n")

    def writeIf(self, label):
        self.write("//if-goto " + label)
        self.write("@SP")
        self.write("AM=M-1")
        self.write("D=M")
        if self.functionName is not "":
            self.write("@" + self.functionName + "$" + label)
        else:
            self.write("@" + label)
        self.write("D;JNE\n")

    def writeCall(self, functionName, numArgs):
        # push return address
        self.write("//in function call for " + functionName + ", Push return address to stack")
        self.write("@" + "FUNCTION_CALL_RETURN_" + str(self.fn_call_ct))
        self.write("D=A")
        self.pushValueInD()
        self.write("")

        self.write("//in function call for " + functionName + ", Push local value to stack")
        self.write("@LCL")
        self.write("D=M")
        self.pushValueInD()
        self.write("")

        self.write("//in function call for " + functionName + ", Push arg value to stack")
        self.write("@ARG")
        self.write("D=M")
        self.pushValueInD()
        self.write("")

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

        self.write("//in function call for " + functionName + ", goto function")
        self.write("@" + functionName)
        self.write("0;JMP\n")
        self.write("")

        self.write("//in function call for " + functionName + ", return label")
        self.write("(FUNCTION_CALL_RETURN_" + str(self.fn_call_ct) + ") //function call return for " + functionName + " \n")
        self.fn_call_ct += 1


    def pushValueInD(self):
        self.write("@SP") #@SP
        self.write("A=M") #A=SP
        self.write("M=D") #M=?
        self.write("D=A+1")#D=SP+1
        self.write("@SP")
        self.write("M=D")

    def writeReturn(self):
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
        self.functionName = functionName

        self.write("//function " + functionName + " " + str(numLocals))
        self.write("(" + functionName + ")\n")
        for x in range(numLocals):
            self.push("constant", 0)

    def writeArithmetic(self, command):
        # writes to the output file the assembly code that implements the given arithmetic
        # command

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
        segment

        line = "//" + self.commandList[command] + " " + segment + " " + str(index)
        self.write(line)
        if command == 1:
            self.push(segment, index)

        elif command == 2:
            self.pop(segment, index)

    def push(self, segment, index):
        # push segment index
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

